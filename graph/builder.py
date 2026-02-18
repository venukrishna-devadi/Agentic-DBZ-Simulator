
import threading
import queue    
from typing import List, Any, Dict, Optional, Literal, TypedDict, Mapping
from datetime import datetime
import json
import traceback

from langgraph.graph import END, START, StateGraph
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from schemas.state import GameState, PlanStep, SceneType
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.verifier import VerifierAgent
from utils.llm_wrapper import llm_wrapper
from utils.memory import MemoryManager


# Configuration defaults
DEFAULT_GRAPH_CONFIG = {
    "max_plan_length": 5,
    "difficulty": "medium",
    "narrative_complexity": 5,
    "enable_verifier": True,
    "enable_memory_compression": True,
    "max_tokens_per_run": 100000,
    "verifier_strictness": "medium",
    "unexpected_event_threshold": 3,  # FIXED: Added config
    "max_plan_revisions": 5,           # FIXED: Added config
    "memory_compression_threshold": 50000,  # FIXED: Added config
    "max_messages_before_prune": 20    # FIXED: Added config
}


class GraphConfig(TypedDict):
    """Configuration for the langgraph"""
    max_plan_length: int
    difficulty: str
    narrative_complexity: int
    enable_verifier: bool
    enable_memory_compression: bool
    max_tokens_per_run: int


class SagaGraph:
    """
    ⚡ THE MASTER ORCHESTRATOR ⚡
    
    Builds and manages the LangGraph that powers the entire Anime Saga Simulator.
    This graph coordinates:
    - PLANNER: Creates epic story arcs
    - EXECUTOR: Brings scenes to life
    - VERIFIER: Ensures narrative quality
    - MEMORY: Compresses and manages context
    - HUMAN: Handles player input and approvals
    """

    def __init__(self, config: Optional[GraphConfig] = None):
        """Initialize the graph with all its agents and components"""

        # Default Configuration
        self.config = config or GraphConfig(
            max_plan_length=7,
            difficulty="medium",
            narrative_complexity=5,
            enable_verifier=True,
            enable_memory_compression=True,
            max_tokens_per_run=100000
        )
        
        # Store additional config values
        self.unexpected_event_threshold = DEFAULT_GRAPH_CONFIG["unexpected_event_threshold"]
        self.max_plan_revisions = DEFAULT_GRAPH_CONFIG["max_plan_revisions"]
        self.memory_compression_threshold = DEFAULT_GRAPH_CONFIG["memory_compression_threshold"]
        self.max_messages_before_prune = DEFAULT_GRAPH_CONFIG["max_messages_before_prune"]

        # Initialize agents
        print("🎬 Initializing SAGA GRAPH components...")

        self.planner = PlannerAgent(
            max_plan_length=self.config["max_plan_length"],
            difficulty=self.config["difficulty"],
            narrative_complexity=self.config["narrative_complexity"]
        )

        self.executor = ExecutorAgent()

        if self.config["enable_verifier"]:
            self.verifier = VerifierAgent(strictness=DEFAULT_GRAPH_CONFIG["verifier_strictness"])

        self.memory_manager = MemoryManager(
            enable_compression=self.config["enable_memory_compression"],
            max_tokens=self.config["max_tokens_per_run"]
        )

        # Build the graph
        self.graph = self._build_graph()
        print("✅ SAGA GRAPH initialized successfully!")

    def _trace_node(self, node_name: str, state: GameState) -> GameState:
        """Trace node execution with timing and state changes"""
        import time
        from datetime import datetime
        import traceback
        
        start = time.time()
        print(f"\n{'='*60}")
        print(f"🔄 ENTERING: {node_name} at {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")
        print(f"   Plan: {len(state.current_plan)} steps, Index: {state.plan_step_index}")
        print(f"   Messages: {len(state.messages)}")
        
        # Call the actual node function with error catching
        try:
            if node_name == "should_start_new_game":
                result = self._check_saga_start(state)
            elif node_name == "planner":
                print("   ⚠️ PLANNER STARTING - THIS SHOULD RUN QUICKLY")
                result = self._run_planner(state)
                print(f"   ✅ PLANNER FINISHED - Plan now has {len(result.current_plan)} steps")
            elif node_name == "executor":
                print("   ⚠️ EXECUTOR STARTING - THIS SHOULD RUN NEXT")
                result = self._run_executor(state)
                print(f"   ✅ EXECUTOR FINISHED - Power: {result.player_stats.get('power_level')}")
            elif node_name == "verifier":
                result = self._run_verifier(state)
            elif node_name == "memory":
                result = self._run_memory_management(state)
            elif node_name == "should_replan":
                result = self._check_replan_needed(state)
            elif node_name == "human_input":
                result = self._handle_human_input(state)
            elif node_name == "should_continue":
                result = self._check_continuation(state)
            else:
                result = state
        except Exception as e:
            print(f"❌ ERROR in {node_name}: {str(e)}")
            traceback.print_exc()
            result = state
        
        elapsed = time.time() - start
        print(f"   ✅ EXITING: {node_name} in {elapsed:.2f}s")
        print(f"   Plan: {len(result.current_plan)} steps, Index: {result.plan_step_index}")
        print(f"   Messages: {len(result.messages)}")
        print(f"{'='*60}")
        return result

    def _build_graph(self) -> StateGraph:
        """
        🏗️ Construct the LangGraph with all nodes and edges
        
        Graph Structure:
        START -> should_start_new_saga? 
               ├─> [Yes] -> planner -> executor -> verifier -> memory -> human_input -> (loop)
               └─> [No]  -> executor -> verifier -> memory -> human_input -> (loop)
        """
        print("\n🔨 Building graph with nodes:")
        print("  - should_start_new_game")
        print("  - planner")
        print("  - executor")
        if self.config["enable_verifier"]:
            print("  - verifier")
        print("  - memory")
        print("  - should_replan")
        print("  - human_input")
        print("  - should_continue")

        # Create the graph with GameState
        workflow = StateGraph(GameState)

        # =========================================================
        # 1. ADD ALL NODES
        # =========================================================

        # # Decision Nodes
        # workflow.add_node("should_start_new_game", self._check_saga_start)
        # workflow.add_node("should_replan", self._check_replan_needed)
        # workflow.add_node("should_continue", self._check_continuation)

        # # core agent nodes
        # workflow.add_node("planner", lambda s: self._trace_node("planner", s))
        # workflow.add_node("executor", lambda s: self._trace_node("executor", s))
        # workflow.add_node("verifier", lambda s: self._trace_node("verifier", s))
        # workflow.add_node("memory", lambda s: self._trace_node("memory", s))
        # workflow.add_node("should_replan", lambda s: self._trace_node("should_replan", s))
        # workflow.add_node("human_input", lambda s: self._trace_node("human_input", s))
        # workflow.add_node("should_continue", lambda s: self._trace_node("should_continue", s))
        # workflow.add_node("should_start_new_game", lambda s: self._trace_node("should_start_new_game", s))

        # Decision Nodes - WITH TRACING
        workflow.add_node("should_start_new_game", lambda s: self._trace_node("should_start_new_game", s))
        workflow.add_node("should_replan", lambda s: self._trace_node("should_replan", s))
        workflow.add_node("should_continue", lambda s: self._trace_node("should_continue", s))

        # Core agent nodes - WITH TRACING
        workflow.add_node("planner", lambda s: self._trace_node("planner", s))
        workflow.add_node("executor", lambda s: self._trace_node("executor", s))

        if self.config["enable_verifier"]:
            workflow.add_node("verifier", lambda s: self._trace_node("verifier", s))

        workflow.add_node("memory", lambda s: self._trace_node("memory", s))
        workflow.add_node("human_input", lambda s: self._trace_node("human_input", s))

        # =========================================================
        # 2. DEFINE ALL EDGES
        # =========================================================

        # START -> should_start_new_saga
        workflow.add_edge(START, "should_start_new_game")

        # FIXED: Typo in comment
        # conditional edges from should start new game
        # workflow.add_conditional_edges(
        #     "should_start_new_game",
        #     self._route_from_saga_check,
        #     {
        #         "needs_plan": "planner",
        #         "continue_saga": "executor",
        #         "end_saga": END
        #     }
        # )
        workflow.add_conditional_edges(
            "should_start_new_game",
            self._route_from_saga_check,
            {
                "needs_plan": "planner",
                "continue_saga": "executor",
                "end_saga": END
            }
        )

        workflow.add_conditional_edges(
            "planner",
            lambda state: "executor",
            {"executor": "executor"}
)

        # FIXED: Typo in comment
        # executor to verifier next (if verifier is enabled) if not directly to memory
        if self.config["enable_verifier"]:
            workflow.add_edge("executor", "verifier")
            workflow.add_edge("verifier", "memory")
        else:
            workflow.add_edge("executor", "memory")

        # then from memory if we go to if we need to replan
        workflow.add_edge("memory", "should_replan")

        # then from should replan we do a conditional edge
        workflow.add_conditional_edges(
            "should_replan",
            self._route_from_replan_check,
            {
                "replan": "planner",
                "continue": "human_input"
            }
        )

        # then if it is human_input, from human input to should_continue
        workflow.add_edge("human_input", "should_continue")

        # then another conditional edge from should continue
        workflow.add_conditional_edges(
            "should_continue",
            self._route_from_continuation,
            {
                "continue": "executor",  # loop back from next scene
                "end": END
            }
        )

        # =========================================================
        # 3. COMPILE WITH CHECKPOINTING
        # =========================================================

        # add memory saver for checkpointing
        self.checkpointer = InMemorySaver()

        # now we will compile the graph
        return workflow.compile(checkpointer=self.checkpointer)

    # =========================================================
    # NODE IMPLEMENTATIONS
    # =========================================================

    def _check_saga_start(self, state: GameState) -> GameState:
        """
        🔍 Check if we need to start a new saga or continue existing one
        
        This node examines:
        - If current_plan is empty → need new plan
        - If plan is completed → maybe need new plan
        - If game just started → need new plan
        """

        print(f"\n{'='*60}")
        print(f"🔍 SAGA CHECKPOINT: Analyzing current state...")
        print(f"{'='*60}")

        # Log current state for debugging
        print(f"📊 Current Plan Length: {len(state.current_plan)}")
        print(f"📊 Plan Step Index: {state.plan_step_index}")
        print(f"📊 Plan Completed: {state.plan_completed}")
        print(f"📊 Total Actions: {state.total_actions}")

        # no state change needed, this is just a routing node
        return state

    def _run_planner(self, state: GameState) -> GameState:
        """
        🧠 Run the planner agent to create a new saga plan
        """

        print(f"\n{'='*60}")
        print(f"🧠 PLANNER NODE: Crafting Legendary Saga...")
        print(f"{'='*60}")

        print(f"Plan index BEFORE planner: {state.plan_step_index}")

        # invoke the planner node
        updates = self.planner.invoke(state)

        # apply updates to state
        for key, value in updates.items():
            if hasattr(state, key):
                setattr(state, key, value)

        # add the plan message
        if "messages" in updates:
            for msg in updates["messages"]:
                state.add_message(msg)

        # increment plan revisions
        state.plan_revisions += 1
        
        # CRITICAL: Reset index to 0 for new plan
        state.plan_step_index = 0
        print(f"✅ Reset plan index to 0 for new plan")

        print(f"✅ PLANNER COMPLETE: {len(state.current_plan)} steps created")

        return state

    def _run_executor(self, state: GameState) -> GameState:
        """
        🎬 Run the executor agent to play out the current scene
        
        The executor generates narrative, handles player choices,
        updates stats, and manages battle sequences.
        """

        print(f"\n{'='*60}")
        print(f"🎬 EXECUTOR NODE: Bringing Scene to Life...")
        print(f"{'='*60}")

        print(f"Current step index BEFORE: {state.plan_step_index}")
        
        # get the last human message as player action
        player_action = None
        for msg in reversed(state.messages):
            # FIXED: Safe attribute access
            msg_type = getattr(msg, 'type', None)
            if msg_type == "human" or isinstance(msg, HumanMessage):
                player_action = msg.content
                break

        # invoke the executor
        updates = self.executor.invoke(state, player_action)

        # apply updates to state
        for key, value in updates.items():
            if key == "messages":
                # FIXED: Handle both single message and list
                if isinstance(value, list):
                    for msg in value:
                        state.add_message(msg)
                else:
                    state.add_message(value)
            # FIXED: Check if key exists in state, not if state has attribute 'value'
            elif hasattr(state, key):
                setattr(state, key, value)
        
        # CRITICAL FIX: Advance the plan index after successful execution
        # Only advance if we haven't already passed the end
        if state.plan_step_index < len(state.current_plan):
            # Mark the current step as completed (should already be done by executor)
            if state.current_step and not state.current_step.completed:
                state.current_step.completed = True
            
            # Advance to next step
            old_index = state.plan_step_index
            state.plan_step_index += 1
            print(f"✅ Advanced plan index from {old_index} to {state.plan_step_index}")
        else:
            print(f"⚠️ Cannot advance plan - already at end (index {state.plan_step_index})")

        # increment action counter
        state.total_actions += 1

        print(f"✅ EXECUTOR COMPLETE: Now at step {state.plan_step_index} of {len(state.current_plan)}")

        return state

    def _run_verifier(self, state: GameState) -> GameState:
        """
        ✅ Run the verifier agent to ensure narrative quality
        
        The verifier checks:
        - Consistency with previous events
        - Character voice accuracy
        - Plot hole prevention
        - Quality standards
        """
        print(f"\n{'='*60}")
        print(f"✅ VERIFIER NODE: Ensuring Narrative Excellence...")
        print(f"{'='*60}")

        if hasattr(self, "verifier"):
            # invoke the verifier
            updates = self.verifier.invoke(state)

            # apply any corrections
            if updates.get("needs_correction", False):
                print(f"⚠️ Verifier found issues: {updates.get('issues', [])}")

                # update state with corrections
                if "corrected_narratives" in updates:
                    # replace last AI message with corrected version
                    for i, msg in enumerate(reversed(state.messages)):
                        msg_type = getattr(msg, 'type', None)
                        if msg_type == "ai" or isinstance(msg, AIMessage):
                            state.messages[-1 - i] = updates["corrected_narratives"]
                            break

                # Add verifier notes
                if updates.get("verifier_notes"):
                    state.add_message(AIMessage(
                        content=f"*[Narrative Resonance Check: {updates['verifier_notes']}]*"
                    ))

        return state

    def _run_memory_management(self, state: GameState) -> GameState:
        """
        💾 Run memory compression and management
        
        This node:
        - Compresses old conversations
        - Updates memory summary
        - Manages token usage
        - Prunes unnecessary history
        """

        print(f"\n{'='*60}")
        print(f"💾 MEMORY NODE: Compressing and Managing Context...")
        print(f"{'='*60}")

        # FIXED: Use configured threshold instead of hardcoded 50000
        if self.config["enable_memory_compression"] and state.tokens_used > self.memory_compression_threshold:

            # update memory summary
            state.memory_summary = self.memory_manager.compress_memory(state)

            # prune the old messages but keep recent ones
            if len(state.messages) > self.max_messages_before_prune:
                # keep last N messages
                state.messages = state.messages[-self.max_messages_before_prune:]

                # add a system message indicating compression has been done on messages
                state.add_message(SystemMessage(
                    content=f"[Memory Compressed: Earlier events summarized as '{state.memory_summary[:100]}...']"
                ))

        print(f"✅ MEMORY COMPLETE: Tokens used: {state.tokens_used}")

        return state

    def _handle_human_input(self, state: GameState) -> GameState:
        """
        👤 Handle human input node
        
        This is a special node that waits for human input.
        In Streamlit, this is handled by the UI, but in the graph
        it's a placeholder that routes to the next appropriate node.
        """

        print(f"\n{'='*60}")
        print(f"👤 HUMAN INPUT NODE: Awaiting Player Decision...")
        print(f"{'='*60}")

        # In a real implementation, this would wait for UI input
        # For now, it's just a routing node

        return state

    def _check_replan_needed(self, state: GameState) -> GameState:
        """
        🔄 Check if we need to replan based on unexpected events
        """
        print(f"\n{'='*60}")
        print(f"🔄 REPLAN CHECK: Analyzing Story Coherence...")
        print(f"{'='*60}")

        # SAFETY: Only access current_step if it exists
        current_step = None
        if state.current_plan and 0 <= state.plan_step_index < len(state.current_plan):
            current_step = state.current_plan[state.plan_step_index]

        # check if we need to replan
        replan_needed = False
        replan_reason = ""

        if current_step:
            # too many unexpected events in current step
            if len(current_step.unexpected_events) > self.unexpected_event_threshold:
                replan_needed = True
                replan_reason = f"Too many unexpected events: {current_step.unexpected_events}"

        # Check overall plan progress
        if state.plan_revisions > self.max_plan_revisions:
            replan_needed = True
            replan_reason = "Too many revisions. Starting fresh"

        # Check if plan is completed but we're still going
        if state.plan_completed and state.should_continue:
            replan_needed = True
            replan_reason = "Current plan completed. Starting new game plan"
        
        # Check if we're at the end of the plan
        if state.plan_step_index >= len(state.current_plan):
            replan_needed = True
            replan_reason = "Reached end of plan"

        if replan_needed:
            print(f"⚠️ REPLAN NEEDED: {replan_reason}")
            # Store the reason in state for debugging
            state.error_message = f"Replan: {replan_reason}"
        else:
            print(f"✅ Story on track - continuing with current plan")

        return state

    def _check_continuation(self, state: GameState) -> GameState:
        """
        🏁 Check if we should continue the saga or end it
        
        End conditions:
        - Player chooses to end
        - Maximum actions reached
        - Critical error
        - Story naturally concludes
        """

        print(f"\n{'='*60}")
        print(f"🏁 CONTINUATION CHECK: Should the saga continue?")
        print(f"{'='*60}")

        # check end conditions
        should_end = False
        end_reason = ""

        if not state.should_continue:
            should_end = True
            end_reason = "Player requested end"
        elif state.error_message:
            should_end = True
            end_reason = f"Critical error: {state.error_message}"
        elif state.total_actions > 100:  # Max actions safety
            should_end = True
            end_reason = "Maximum saga length reached"
        elif state.plan_completed and len(state.current_plan) == 0:
            should_end = True
            end_reason = "Story naturally concluded"

        if should_end:
            print(f"🏁 ENDING SAGA: {end_reason}")
            state.should_continue = False
        else:
            print(f"✅ Saga continues! Next scene awaits...")

        return state

    # =========================================================
    # ROUTING FUNCTIONS
    # =========================================================

    def _route_from_saga_check(self, state: GameState) -> Literal["needs_plan", "continue_saga", "end_saga"]:
        """
        🧭 Route from saga check based on state
        """
        print(f"\n🧭 ROUTING CHECK - Plan length: {len(state.current_plan)}, Index: {state.plan_step_index}")
        
        # If no plan exists, we need a new plan
        if not state.current_plan or len(state.current_plan) == 0:
            print("🧭 ROUTING: Needs new plan (empty current_plan)")
            return "needs_plan"
        
        # FIX: If we have a plan and index is within bounds, continue to executor
        if state.plan_step_index < len(state.current_plan):
            print(f"🧭 ROUTING: Continuing saga - step {state.plan_step_index + 1} of {len(state.current_plan)}")
            return "continue_saga"
        
        # If we've completed all steps, we need a new plan
        if state.plan_step_index >= len(state.current_plan):
            print("🧭 ROUTING: All steps completed - needs new plan")
            return "needs_plan"
        
        # Check if we should end
        if not state.should_continue:
            print("🧭 ROUTING: Ending saga")
            return "end_saga"
        
        # Default fallback
        print("🧭 ROUTING: Continuing current saga")
        return "continue_saga"

    def _route_from_replan_check(self, state: GameState) -> Literal["replan", "continue"]:
        """
        🧭 Route from replan check based on whether replanning is needed
        """
        print(f"\n🧭 REPLAN CHECK - Plan length: {len(state.current_plan)}, Index: {state.plan_step_index}")
        
        # SAFETY: Check if current_step exists before accessing
        current_step = None
        if state.current_plan and 0 <= state.plan_step_index < len(state.current_plan):
            current_step = state.current_plan[state.plan_step_index]
        
        # check if we need to replan
        replan_needed = False
        replan_reason = []

        # Only check current_step if it exists
        if current_step:
            if len(current_step.unexpected_events) > self.unexpected_event_threshold:
                replan_needed = True
                replan_reason.append(f"Too many unexpected events: {len(current_step.unexpected_events)}")

        # Check overall plan progress
        if state.plan_revisions > self.max_plan_revisions:
            replan_needed = True
            replan_reason.append(f"Too many revisions: {state.plan_revisions}")

        # Check if plan is completed - use property, don't set it
        if state.plan_completed or state.plan_step_index >= len(state.current_plan):
            replan_needed = True
            replan_reason.append("Plan completed")

        if replan_needed:
            reasons = ", ".join(replan_reason)
            print(f"⚠️ REPLAN NEEDED: {reasons}")
            return "replan"
        else:
            print(f"✅ Story on track - continuing to human input")
            return "continue"

    def _route_from_continuation(self, state: GameState) -> Literal["continue", "end"]:
        """
        🧭 Route from continuation check
        """
        # Check if we have more steps to execute
        if state.current_plan and state.plan_step_index < len(state.current_plan):
            print(f"🧭 ROUTING: Continuing to next scene (step {state.plan_step_index + 1})")
            return "continue"
        elif state.should_continue:
            # No more steps but should continue - need to go back to saga check
            # which will route to planner for new plan
            print("🧭 ROUTING: No more steps - going back to saga check for new plan")
            return "continue"  # This goes back to should_start_new_game
        else:
            print("🧭 ROUTING: Ending graph execution")
            return "end"
        
    def _coerce_to_gamestate(self, obj):
        """LangGraph may return dict. Always return GameState."""
        if isinstance(obj, GameState):
            return obj
        if isinstance(obj, dict):
            # Pydantic v2
            if hasattr(GameState, "model_validate"):
                return GameState.model_validate(obj)
            # fallback (older)
            return GameState(**obj)
        return obj

    # =========================================================
    # PUBLIC METHODS
    # =========================================================


    def run(self, initial_state: GameState, thread_id: str = "default", timeout: int = 30) -> GameState:

        """
        🚀 Run the saga graph with timeout
        
        Args:
            initial_state: The starting game state
            thread_id: Unique ID for this conversation thread
            timeout: Maximum seconds to wait for graph completion
        
        Returns:
            Final state after graph execution
        """
        print(f"\n{'🔥'*30}")
        print(f"🔥 LAUNCHING SAGA GRAPH - Thread: {thread_id} 🔥")
        print(f"{'🔥'*30}\n")

        config = {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": "saga_simulator"
            }
        }

        result_queue = queue.Queue()
        
        def run_graph():
            try:
                out = self.graph.invoke(initial_state, config)
                final_state = self._coerce_to_gamestate(out)
                result_queue.put(("success", final_state))
            except Exception as e:
                result_queue.put(("error", str(e)))
        
        graph_thread = threading.Thread(target=run_graph)
        graph_thread.daemon = True
        graph_thread.start()
        
        graph_thread.join(timeout=timeout)
        
        if graph_thread.is_alive():
            print(f"❌ Graph execution timed out after {timeout} seconds")
            initial_state.error_message = f"Graph execution timed out after {timeout} seconds"
            initial_state.should_continue = False
            return initial_state
        
        try:
            status, result = result_queue.get_nowait()
            if status == "success":
                print(f"\n{'✨'*30}")
                print(f"✨ SAGA GRAPH COMPLETED SUCCESSFULLY ✨")
                print(f"{'✨'*30}\n")
                return self._coerce_to_gamestate(result)
            else:
                print(f"❌ Graph error: {result}")
                initial_state.error_message = str(result)
                initial_state.should_continue = False
                return initial_state
        except queue.Empty:
            print("❌ Unknown error in graph execution")
            initial_state.error_message = "Unknown graph error"
            initial_state.should_continue = False
            return initial_state

    def stream(self, initial_state: GameState, thread_id: str = "default"):
        """
        📡 Stream the graph execution for real-time updates
        
        Args:
            initial_state: The starting game state
            thread_id: Unique ID for this conversation thread
        
        Yields:
            Each step of graph execution
        """
        config = {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": "saga_simulator"
            }
        }

        for step in self.graph.stream(initial_state, config):
            yield step

    def get_state(self, thread_id: str) -> Optional[GameState]:
        config = {"configurable": {"thread_id": thread_id, "checkpoint_ns": "saga_simulator"}}
        try:
            s = self.graph.get_state(config)
            if not s:
                return None
            # s.values is typically dict
            return self._coerce_to_gamestate(s.values)
        except:
            return None

    def update_state(self, thread_id: str, updates: Dict[str, Any]) -> None:
        """
        📝 Update the state for a given thread (for manual intervention)
        """
        config = {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": "saga_simulator"
            }
        }

        self.graph.update_state(config, updates)


# =========================================================
# FACTORY FUNCTION
# =========================================================



def create_saga_graph(config: Optional[Mapping[str, Any]] = None) -> SagaGraph:
    """
    🏭 Factory function to create a new SagaGraph instance
    
    Args:
        config: Optional graph configuration
    
    Returns:
        Configured SagaGraph ready to run
    """
    merged = {**DEFAULT_GRAPH_CONFIG, **(dict(config) if config else {})}
    return SagaGraph(merged)

def debug_graph_structure(self):
    """Print the graph structure for debugging"""
    print("\n🔍 GRAPH STRUCTURE DEBUG:")
    print("=" * 50)
    
    # Print all nodes
    print("📌 NODES:")
    for node in self.graph.nodes:
        print(f"  - {node}")
    
    # Print edges if accessible (might need to dig into graph structure)
    print("\n🔗 Checking connections...")
    
    # Check if planner has an outgoing edge
    print("\n🔄 PLANNER CONNECTIONS:")
    # This is tricky - LangGraph doesn't expose edges directly
    # But we can check by seeing if executor ever runs
    
    print("\n⚠️ To fix: Make sure you have:")
    print("   workflow.add_edge('planner', 'executor')")
    print("   in your _build_graph method")


# =========================================================
# EXAMPLE USAGE
# =========================================================

if __name__ == "__main__":
    """
    Example of how to use the graph builder
    """
    from schemas.state import GameState

    # Create initial state
    initial_state = GameState(
        player_name="Goku",
        saga_name="Power Progression",
        player_stats={
            "power_level": 5000,
            "health": 100,
            "max_health": 100,
            "ki_mastery": 50,
            "spirit_bombs": 0,
            "zenkai_boosts": 0,
            "level": 1,
            "items": []
        }
    )

    # Create graph with custom config
    config = GraphConfig(
        max_plan_length=7,
        difficulty="legendary",
        narrative_complexity=5,
        enable_verifier=True,
        enable_memory_compression=True,
        max_tokens_per_run=100000
    )

    # Build and run
    graph = create_saga_graph(config)
    final_state = graph.run(initial_state, thread_id="goku_saga_001")

    print(f"\nFinal Power Level: {final_state.player_stats['power_level']}")
    print(f"Total Actions: {final_state.total_actions}")