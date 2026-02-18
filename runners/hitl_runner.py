
"""
🤝 HUMAN-IN-THE-LOOP RUNNER - The Bridge Between AI and Player 🤝

This module handles all player interactions, approvals, and decision points:
- Tool call approvals (HITL mode)
- Player choice processing
- Game state persistence
- Checkpoint recovery
- Real-time streaming updates

It acts as the communication layer between your LangGraph and Streamlit UI.
"""

from typing import Dict, Any, Optional, List, Tuple, Union
from datetime import datetime
import json
import uuid
import time

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage, SystemMessage
from langgraph.graph.state import StateGraph

from schemas.state import GameState, PlanStep
from graph.builder import SagaGraph


class HITLRunner:
    """
    🎮 HUMAN-IN-THE-LOOP RUNNER - The Player's Direct Interface to the AI 🎮
    
    Responsibilities:
    - Starting new games with proper thread IDs
    - Processing player choices and actions
    - Handling tool approval/rejection
    - Managing checkpoint recovery
    - Streaming real-time updates to the UI
    - Saving/loading game state
    """
    
    def __init__(self, graph: SagaGraph):
        """
        Initialize the HITL runner with a compiled SagaGraph
        
        Args:
            graph: Your compiled SagaGraph instance with checkpointing
        """
        self.graph = graph
        self.current_thread_id: Optional[str] = None
        self.pending_tool_calls: List[Dict] = []
        self.last_updates: List[Dict] = []
        self.streaming_active = False
        
        print("✅ HITL Runner initialized")
    
    # =========================================================
    # 1. GAME LIFECYCLE MANAGEMENT
    # =========================================================
    
    def start_new_game(self, 
                       player_name: str, 
                       saga_name: str,
                       difficulty: str = "medium",
                       enable_hitl: bool = True) -> GameState:
        """
        🆕 Start a brand new game with a fresh state and thread ID
        
        Args:
            player_name: Name of the player character
            saga_name: Type of saga (Power Progression, Mystical Quest, etc.)
            difficulty: Easy, Normal, Hard, Nightmare
            enable_hitl: Whether to pause for tool approvals
            
        Returns:
            Initialized GameState ready for play
        """
        print(f"\n{'🎮'*50}")
        print(f"🎮 HITL: Starting new {saga_name} saga for {player_name}")
        print(f"{'🎮'*50}\n")
        
        # Generate unique thread ID for checkpointing
        self.current_thread_id = f"saga_{uuid.uuid4().hex[:8]}"
        self.pending_tool_calls = []
        self.last_updates = []
        
        # Create initial game state
        initial_state = GameState(
            player_name=player_name,
            saga_name=saga_name,
            player_stats={
                "power_level": 1000,
                "health": 100,
                "max_health": 100,
                "ki_mastery": 30,
                "level": 1,
                "experience": 0,
                "items": ["Senzu Bean"],
                "transformations": [],
                "techniques": ["Basic Ki Blast"]
            },
            world_flags={
                "mentor_met": False,
                "training_started": False,
                "first_battle": False,
                "transformation_unlocked": False
            },
            difficulty=difficulty,
            enable_hitl=enable_hitl,
            start_time=datetime.now()
        )
        
        # Add welcome message
        welcome_msg = AIMessage(
            content=f"🔥 Welcome, **{player_name}**! Your journey in the **{saga_name}** saga begins now. "
                    f"The path ahead is filled with challenges, growth, and legendary battles. "
                    f"Are you ready to transcend your limits?"
        )
        initial_state.add_message(welcome_msg)
        
        return initial_state
    
    def reset_game(self) -> None:
        """🔄 Reset the current game session"""
        self.current_thread_id = None
        self.pending_tool_calls = []
        self.last_updates = []
        print("🔄 HITL: Game reset")
    
    def get_current_state(self) -> Optional[GameState]:
        """📊 Get the current game state from checkpoint"""
        if not self.current_thread_id:
            return None
        return self.graph.get_state(self.current_thread_id)
    
    # =========================================================
    # 2. GRAPH EXECUTION WITH HITL SUPPORT
    # =========================================================
    # runners/hitl_runner.py - Replace the run_with_hitl method

    def run_with_hitl(self, 
                    initial_state: GameState,
                    max_steps: int = 50) -> Dict[str, Any]:
        """
        🚀 Run the graph with Human-in-the-Loop support
        
        This method:
        1. Starts or resumes graph execution
        2. Returns when graph completes or hits an interrupt
        3. Doesn't wait forever!
        """
        if not self.current_thread_id:
            self.current_thread_id = f"run_{uuid.uuid4().hex[:8]}"
        
        config = {
            "configurable": {
                "thread_id": self.current_thread_id,
                "checkpoint_ns": "saga_simulator"
            }
        }
        
        step_count = 0
        final_state = None
        interrupted = False
        
        print(f"\n{'🚀'*50}")
        print(f"🚀 HITL: Starting graph execution (Thread: {self.current_thread_id})")
        print(f"{'🚀'*50}\n")
        
        try:
            # IMPORTANT: Use invoke() instead of stream() for simplicity
            # This will run until completion or interrupt
            final_state = self.graph.graph.invoke(initial_state, config=config)
            
            # Check if we have pending tool calls (interrupt)
            if hasattr(final_state, 'messages') and final_state.messages:
                for msg in reversed(final_state.messages):
                    if isinstance(msg, AIMessage) and hasattr(msg, 'tool_calls') and msg.tool_calls:
                        interrupted = True
                        self.pending_tool_calls = msg.tool_calls
                        print(f"⏸️ HITL: Interrupt detected - waiting for approval")
                        break
            
            result = {
                "success": True,
                "final_state": final_state,
                "interrupted": interrupted,
                "pending_tool_calls": self.pending_tool_calls if interrupted else [],
                "thread_id": self.current_thread_id,
                "step_count": step_count
            }
            
            if interrupted:
                print(f"\n⏸️ HITL: Paused for approval - {len(self.pending_tool_calls)} tool(s) pending")
            else:
                print(f"\n✅ HITL: Graph execution complete")
            
            return result
            
        except Exception as e:
            print(f"❌ HITL Error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e),
                "final_state": final_state,
                "interrupted": False,
                "pending_tool_calls": [],
                "thread_id": self.current_thread_id,
                "step_count": step_count
            }
    
    # =========================================================
    # 3. TOOL APPROVAL HANDLING
    # =========================================================
    
    def approve_tools(self) -> Dict[str, Any]:
        """
        ✅ Approve pending tool calls and resume execution
        
        Returns:
            Result of resumed execution
        """
        if not self.pending_tool_calls:
            return {"success": False, "error": "No pending tool calls"}
        
        print(f"\n✅ HITL: Approving {len(self.pending_tool_calls)} tool call(s)")
        
        # Resume graph execution from checkpoint
        return self._resume_execution(approved=True)
    
    def reject_tools(self, feedback: Optional[str] = None) -> Dict[str, Any]:
        """
        ❌ Reject pending tool calls and provide feedback
        
        Args:
            feedback: Optional feedback for why tools were rejected
            
        Returns:
            Result of resumed execution with rejection message
        """
        if not self.pending_tool_calls:
            return {"success": False, "error": "No pending tool calls"}
        
        print(f"\n❌ HITL: Rejecting {len(self.pending_tool_calls)} tool call(s)")
        
        # Get current state
        current_state = self.get_current_state()
        if current_state:
            # Add rejection message to state
            rejection_msg = HumanMessage(
                content=f"[SYSTEM: Tools rejected by player]"
            )
            current_state.add_message(rejection_msg)
            
            # Update state in graph
            self.graph.update_state(self.current_thread_id, {
                "messages": current_state.messages
            })
        
        # Resume with rejection context
        return self._resume_execution(approved=False, feedback=feedback)
    
    def _resume_execution(self, approved: bool, feedback: Optional[str] = None) -> Dict[str, Any]:
        """
        🔄 Resume graph execution after approval/rejection
        
        Args:
            approved: Whether tools were approved
            feedback: Optional feedback message
            
        Returns:
            Result of resumed execution
        """
        if not self.current_thread_id:
            return {"success": False, "error": "No active thread"}
        
        config = {
            "configurable": {
                "thread_id": self.current_thread_id,
                "checkpoint_ns": "saga_simulator"
            }
        }
        
        # Add human decision message
        current_state = self.get_current_state()
        if current_state:
            decision_msg = HumanMessage(
                content=f"[HUMAN DECISION: {'Approved' if approved else 'Rejected'} tool calls]"
            )
            current_state.add_message(decision_msg)
            self.graph.update_state(self.current_thread_id, {"messages": current_state.messages})
        
        print(f"\n🔄 HITL: Resuming execution (Approved: {approved})")
        
        try:
            # Resume with input=None (continues from checkpoint)
            final_state = self.graph.graph.invoke(None, config=config)
            
            # Clear pending tools
            self.pending_tool_calls = []
            
            return {
                "success": True,
                "final_state": final_state,
                "approved": approved,
                "thread_id": self.current_thread_id
            }
            
        except Exception as e:
            print(f"❌ HITL Resume Error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "approved": approved,
                "thread_id": self.current_thread_id
            }
    
    # =========================================================
    # 4. PLAYER CHOICE HANDLING
    # =========================================================
    
    def process_player_choice(self, choice: str) -> Dict[str, Any]:
        """
        🎯 Process a player's choice and advance the story
        
        Args:
            choice: The player's chosen action text
            
        Returns:
            Result of graph execution after processing choice
        """
        if not self.current_thread_id:
            return {"success": False, "error": "No active game"}
        
        print(f"\n🎯 HITL: Processing player choice: '{choice[:50]}...'")
        
        # Get current state
        current_state = self.get_current_state()
        if not current_state:
            return {"success": False, "error": "Could not retrieve current state"}
        
        # Add player choice as HumanMessage
        player_msg = HumanMessage(content=choice)
        current_state.add_message(player_msg)
        
        # Update state in graph
        self.graph.update_state(self.current_thread_id, {
            "messages": current_state.messages,
            "should_continue": True
        })
        
        # Resume execution
        return self._resume_execution(approved=True)
    
    # =========================================================
    # 5. UTILITY METHODS
    # =========================================================
    
    def extract_choices_from_scene(self, state: GameState) -> List[str]:
        """
        🔀 Extract available choices from the current scene
        
        Args:
            state: Current game state
            
        Returns:
            List of choice strings
        """
        if not state or not state.messages:
            return []
        
        # Look for choices in the last AI message
        for msg in reversed(state.messages):
            if isinstance(msg, AIMessage):
                content = msg.content
                
                # Try to extract numbered choices (1. Choice)
                import re
                choices = re.findall(r'\d+\.\s+([^\n]+)', content)
                
                if choices:
                    return [c.strip() for c in choices]
                
                # Try bullet points
                choices = re.findall(r'[•\-]\s+([^\n]+)', content)
                if choices:
                    return [c.strip() for c in choices]
                
                # Try markdown list
                choices = re.findall(r'^\s*\*\s+(.+)$', content, re.MULTILINE)
                if choices:
                    return [c.strip() for c in choices]
                
                break
        
        # Fallback choices
        return [
            "Continue forward",
            "Take a moment to reflect",
            "Call out to see if anyone responds"
        ]
    
    def get_current_scene_text(self, state: GameState) -> Optional[str]:
        """
        📜 Extract the current scene text from state
        
        Args:
            state: Current game state
            
        Returns:
            Scene text or None if not found
        """
        if not state or not state.messages:
            return None
        
        # Find last AI message (scene)
        for msg in reversed(state.messages):
            if isinstance(msg, AIMessage):
                return msg.content
        
        return None
    
    def get_pending_tool_info(self) -> List[Dict[str, Any]]:
        """
        🔧 Get detailed info about pending tool calls for UI display
        
        Returns:
            List of tool call details with names, args, and descriptions
        """
        tool_info = []
        
        for tc in self.pending_tool_calls:
            info = {
                "name": tc.get("name", "Unknown"),
                "args": tc.get("args", {}),
                "id": tc.get("id", "unknown"),
                "description": self._get_tool_description(tc.get("name", ""))
            }
            tool_info.append(info)
        
        return tool_info
    
    def _get_tool_description(self, tool_name: str) -> str:
        """Get a human-readable description for a tool"""
        descriptions = {
            "web_search": "Search the web for current information",
            "multi_search": "Perform comprehensive research with multiple angles",
            "analyze_depth": "Determine how much research is needed",
            "save_findings": "Save research findings to a file",
            "battle_action": "Execute a battle move",
            "train": "Engage in training to increase power",
            "transform": "Unlock a new transformation"
        }
        return descriptions.get(tool_name, f"Execute {tool_name} tool")
    
    # =========================================================
    # 6. STREAMING SUPPORT
    # =========================================================
    
    def stream_game(self, 
                    initial_state: GameState,
                    callback: Optional[callable] = None) -> None:
        """
        📡 Stream game execution with real-time callbacks
        
        Args:
            initial_state: Starting game state
            callback: Optional function to call on each update
        """
        if not self.current_thread_id:
            self.current_thread_id = f"stream_{uuid.uuid4().hex[:8]}"
        
        config = {
            "configurable": {
                "thread_id": self.current_thread_id,
                "checkpoint_ns": "saga_simulator"
            }
        }
        
        self.streaming_active = True
        
        try:
            for step in self.graph.stream(initial_state, self.current_thread_id):
                if not self.streaming_active:
                    break
                
                if callback:
                    callback(step)
                    
        finally:
            self.streaming_active = False
    
    def stop_streaming(self):
        """🛑 Stop active streaming"""
        self.streaming_active = False
    
    # =========================================================
    # 7. SAVE/LOAD SUPPORT
    # =========================================================
    
    def save_game(self, slot_name: str = "autosave") -> Optional[str]:
        """
        💾 Save current game state to a file
        
        Args:
            slot_name: Save slot identifier
            
        Returns:
            Path to saved file or None if failed
        """
        state = self.get_current_state()
        if not state:
            return None
        
        import os
        os.makedirs("saves", exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"saves/{slot_name}_{timestamp}.json"
        
        try:
            # Convert state to serializable format
            game_data = state.to_serializable()
            
            save_data = {
                "meta": {
                    "slot": slot_name,
                    "timestamp": timestamp,
                    "thread_id": self.current_thread_id,
                    "player_name": state.player_name,
                    "saga_name": state.saga_name
                },
                "game_state": game_data
            }
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Game saved to {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Save failed: {e}")
            return None
    
    def load_game(self, filename: str) -> Optional[GameState]:
        """
        📂 Load a saved game state from file
        
        Args:
            filename: Path to save file
            
        Returns:
            Loaded GameState or None if failed
        """
        try:
            with open(filename, "r", encoding="utf-8") as f:
                save_data = json.load(f)
            
            # Extract game state
            if "game_state" in save_data:
                game_data = save_data["game_state"]
            else:
                game_data = save_data
            
            # Reconstruct GameState
            state = GameState.from_serializable(game_data)
            
            # Restore thread ID
            if "meta" in save_data and "thread_id" in save_data["meta"]:
                self.current_thread_id = save_data["meta"]["thread_id"]
            else:
                self.current_thread_id = f"loaded_{uuid.uuid4().hex[:8]}"
            
            print(f"✅ Game loaded from {filename}")
            return state
            
        except Exception as e:
            print(f"❌ Load failed: {e}")
            return None


# =========================================================
# 8. FACTORY FUNCTION
# =========================================================

def create_hitl_runner(graph: SagaGraph) -> HITLRunner:
    """
    🏭 Factory function to create a configured HITL runner
    
    Args:
        graph: Compiled SagaGraph instance
        
    Returns:
        Configured HITL runner
    """
    return HITLRunner(graph)


# =========================================================
# 9. EXAMPLE USAGE
# =========================================================

if __name__ == "__main__":
    """
    Example of how to use the HITL runner with your Streamlit app
    """
    from graph.builder import create_saga_graph
    
    # Create graph
    graph = create_saga_graph()
    
    # Create HITL runner
    runner = create_hitl_runner(graph)
    
    # Start new game
    initial_state = runner.start_new_game(
        player_name="Goku",
        saga_name="Power Progression",
        difficulty="Normal",
        enable_hitl=True
    )
    
    # Run with HITL
    result = runner.run_with_hitl(initial_state)
    
    if result["interrupted"]:
        print(f"\n⏸️ Game paused. Approve tools? (y/n)")
        # In real app, this would be handled by UI
        
        # Example approval:
        # if user approves:
        #     runner.approve_tools()