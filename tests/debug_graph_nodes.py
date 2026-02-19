#!/usr/bin/env python
"""
🔍 COMPREHENSIVE GRAPH ROUTING TESTER
Tests the full graph flow with detailed debugging output
"""

import sys
import os
import time
import threading
import queue
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
import traceback

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from graph.builder import create_saga_graph, SagaGraph
from schemas.state import GameState, PlanStep, SceneType
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent

# =========================================================
# TEST CONFIGURATION
# =========================================================
TEST_CONFIG = {
    "timeout_seconds": 30,
    "verbose": True,
    "player_name": "TestGoku",
    "saga_name": "Saiyan Saga",
    "starting_power": 1000
}

class GraphFlowTester:
    """Tests the complete graph flow step by step"""
    
    def __init__(self):
        self.graph = None
        self.state = None
        self.step_count = 0
        self.start_time = None
        
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{'='*80}")
        print(f"🔍 {title}")
        print(f"{'='*80}\n")
    
    def print_step(self, step_name: str, details: str = ""):
        """Print a step with timing"""
        self.step_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"\n[{timestamp}] 📍 STEP {self.step_count}: {step_name}")
        if details:
            print(f"   └─ {details}")
    
    def print_state_summary(self, state: GameState, label: str = "Current State"):
        """Print a summary of the game state"""
        print(f"\n📊 {label}:")
        print(f"   ├─ Messages: {len(state.messages)}")
        print(f"   ├─ Plan Steps: {len(state.current_plan)}")
        print(f"   ├─ Current Index: {state.plan_step_index}")
        print(f"   ├─ Plan Completed: {state.plan_completed}")
        print(f"   ├─ Total Actions: {state.total_actions}")
        print(f"   └─ Power Level: {state.player_stats.get('power_level', 'N/A')}")
        
        # Show last message if exists
        if state.messages:
            last_msg = state.messages[-1]
            msg_type = type(last_msg).__name__
            content = last_msg.content[:100] + "..." if len(last_msg.content) > 100 else last_msg.content
            print(f"      └─ Last Message [{msg_type}]: {content}")
    
    def print_plan_details(self, state: GameState):
        """Print details of the current plan"""
        if not state.current_plan:
            print("   └─ No plan yet")
            return
        
        print(f"\n📋 Current Plan ({len(state.current_plan)} steps):")
        for i, step in enumerate(state.current_plan):
            marker = "▶️" if i == state.plan_step_index else "  "
            status = "✅" if step.completed else "⏳"
            print(f"   {marker} {status} Step {i+1}: {step.description[:60]}...")
    
    def initialize_graph(self):
        """Initialize the graph and test state"""
        self.print_step("Initializing Graph")
        
        # Create graph
        self.graph = create_saga_graph()
        print(f"   ├─ Graph type: {type(self.graph)}")
        print(f"   └─ Graph nodes: {list(self.graph.graph.nodes.keys())}")
        
        # Create initial state
        self.state = GameState(
            player_name=TEST_CONFIG["player_name"],
            saga_name=TEST_CONFIG["saga_name"],
            player_stats={
                "power_level": TEST_CONFIG["starting_power"],
                "health": 100,
                "max_health": 100,
                "ki_mastery": 30,
                "level": 1,
                "experience": 0,
                "items": ["Senzu Bean"]
            }
        )
        
        # Add initial message
        self.state.add_message(HumanMessage(
            content=f"Start the {TEST_CONFIG['saga_name']}. I am {TEST_CONFIG['player_name']}, ready to begin my journey."
        ))
        
        print(f"   └─ Initial state created for {TEST_CONFIG['player_name']}")
        self.print_state_summary(self.state, "Initial State")
    
    def run_graph_with_trace(self) -> Dict[str, Any]:
        """Run the graph with detailed tracing"""
        self.print_step("Starting Graph Execution")
        
        config = {"configurable": {"thread_id": f"test_{datetime.now().timestamp()}"}}
        result_queue = queue.Queue()
        trace_log = []
        
        def trace_callback(node_name: str, state_snapshot: Any):
            """Callback to trace graph execution"""
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            trace_log.append({
                "timestamp": timestamp,
                "node": node_name,
                "state": state_snapshot
            })
            
            # Print in real-time
            if hasattr(state_snapshot, 'plan_step_index'):
                plan_info = f" (step {state_snapshot.plan_step_index}/{len(state_snapshot.current_plan)})"
            else:
                plan_info = ""
            
            print(f"      📍 Node executed: {node_name}{plan_info}")
        
        def run_graph():
            try:
                # We can't directly trace, but we'll simulate by tracking state changes
                current_state = self.state
                
                # Run the graph
                result = self.graph.graph.invoke(current_state, config)
                
                # Log the result
                trace_callback("FINAL", result)
                result_queue.put(("success", result, trace_log))
                
            except Exception as e:
                result_queue.put(("error", str(e), traceback.format_exc()))
        
        # Run in thread with timeout
        thread = threading.Thread(target=run_graph)
        thread.daemon = True
        thread.start()
        thread.join(timeout=TEST_CONFIG["timeout_seconds"])
        
        if thread.is_alive():
            print(f"\n❌ GRAPH TIMEOUT after {TEST_CONFIG['timeout_seconds']} seconds!")
            print("   The graph got stuck. Here's what happened before timeout:")
            for log in trace_log[-5:]:  # Show last 5 events
                print(f"   • {log['timestamp']} - {log['node']}")
            return {"success": False, "error": "timeout", "trace": trace_log}
        
        try:
            status, result, trace = result_queue.get_nowait()
            if status == "success":
                print(f"\n✅ Graph completed successfully!")
                print(f"   Total nodes executed: {len(trace)}")
                return {"success": True, "result": result, "trace": trace}
            else:
                print(f"\n❌ Graph error: {result}")
                return {"success": False, "error": result, "trace": trace}
        except queue.Empty:
            return {"success": False, "error": "unknown", "trace": trace_log}
    
    def analyze_execution(self, result: Dict[str, Any]):
        """Analyze the graph execution results"""
        self.print_step("Analyzing Results")
        
        if not result["success"]:
            print(f"❌ Execution failed: {result.get('error', 'Unknown error')}")
            return
        
        final_state = result["result"]
        trace = result.get("trace", [])
        
        print(f"\n📊 Execution Statistics:")
        print(f"   ├─ Total nodes executed: {len(trace)}")
        print(f"   ├─ Final messages: {len(final_state.messages)}")
        print(f"   ├─ Plan steps: {len(final_state.current_plan)}")
        print(f"   ├─ Final index: {final_state.plan_step_index}")
        print(f"   └─ Power level: {final_state.player_stats.get('power_level', 'N/A')}")
        
        # Show execution timeline
        print(f"\n⏱️ Execution Timeline:")
        for i, log in enumerate(trace[-10:]):  # Last 10 events
            print(f"   {i+1}. {log['timestamp']} - {log['node']}")
        
        # Show final messages
        print(f"\n📝 Final Messages:")
        ai_messages = [m for m in final_state.messages if isinstance(m, AIMessage)]
        for i, msg in enumerate(ai_messages[-3:]):  # Last 3 AI messages
            print(f"\n   [{i+1}] AI Message:")
            print(f"   {msg.content[:200]}...")
        
        # Show plan status
        self.print_plan_details(final_state)
    
    def test_single_turn(self):
        """Test just the first turn (planning + first scene)"""
        self.print_header("TEST 1: Single Turn (Planner + First Scene)")
        
        self.initialize_graph()
        result = self.run_graph_with_trace()
        self.analyze_execution(result)
        
        return result
    
    def test_two_turns(self):
        """Test two complete turns (with player choice)"""
        self.print_header("TEST 2: Two Complete Turns")
        
        # First turn
        self.initialize_graph()
        result1 = self.run_graph_with_trace()
        
        if not result1["success"]:
            print("❌ First turn failed, aborting test")
            return
        
        state = result1["result"]
        
        # Simulate player choice
        print(f"\n{'='*60}")
        print("🎮 SIMULATING PLAYER CHOICE")
        print(f"{'='*60}")
        
        # Extract a choice from the last AI message
        ai_messages = [m for m in state.messages if isinstance(m, AIMessage)]
        if ai_messages:
            last_msg = ai_messages[-1].content
            # Look for a choice pattern
            import re
            choices = re.findall(r'\d+\.\s+([^\n]+)', last_msg)
            if choices:
                player_choice = choices[0]
            else:
                player_choice = "Train in 100x Gravity"
        else:
            player_choice = "Train in 100x Gravity"
        
        print(f"🎯 Player chooses: '{player_choice}'")
        
        # Add choice to state
        state.add_message(HumanMessage(content=player_choice))
        
        # Second turn
        self.print_step("Second Turn")
        self.state = state
        result2 = self.run_graph_with_trace()
        
        self.analyze_execution(result2)
        
        return result2
    
    def test_routing_logic(self):
        """Test the routing logic directly"""
        self.print_header("TEST 3: Direct Routing Logic Test")
        
        # Create a graph instance to access routing functions
        graph = SagaGraph()
        
        # Test 1: Empty plan
        print("\n📋 Test 1: Empty plan")
        state = GameState()
        state.current_plan = []
        state.plan_step_index = 0
        route = graph._route_from_saga_check(state)
        print(f"   Route: {route} (should be needs_plan)")
        
        # Test 2: During execution
        print("\n📋 Test 2: During execution")
        step = PlanStep(
            scene_type=SceneType.INTRODUCTION,
            description="The adventure begins in a small village",
            expected_outcome="Meet the mentor and begin training"
        )
        state.current_plan = [step] * 5
        state.plan_step_index = 2
        route = graph._route_from_saga_check(state)
        print(f"   Route: {route} (should be continue_saga)")
        
        # Test 3: After completion
        print("\n📋 Test 3: After completion")
        state.plan_step_index = 5
        route = graph._route_from_saga_check(state)
        print(f"   Route: {route} (should be needs_plan)")
        
        # Test 4: Replan check
        print("\n📋 Test 4: Replan check")
        state.plan_revisions = 6
        route = graph._route_from_replan_check(state)
        print(f"   Route: {route} (should be replan)")
        
        # Test 5: Continuation check
        print("\n📋 Test 5: Continuation check")
        state.should_continue = True
        route = graph._route_from_continuation(state)
        print(f"   Route: {route} (should be continue)")
    
    def run_all_tests(self):
        """Run all tests"""
        self.start_time = datetime.now()
        
        print("\n" + "🔥"*50)
        print("🔥 COMPREHENSIVE GRAPH ROUTING TESTER")
        print("🔥"*50 + "\n")
        
        # Test 1: Routing logic
        self.test_routing_logic()
        
        # Test 2: Single turn
        result1 = self.test_single_turn()
        
        # Test 3: Two turns (if first succeeded)
        if result1 and result1["success"]:
            self.test_two_turns()
        
        # Summary
        elapsed = (datetime.now() - self.start_time).total_seconds()
        print(f"\n{'='*60}")
        print(f"✅ ALL TESTS COMPLETED in {elapsed:.2f} seconds")
        print(f"{'='*60}")
        
        if result1 and result1["success"]:
            print("\n🎉 SUCCESS! The graph is working correctly!")
            print("   You can now run your Streamlit app:")
            print("   streamlit run ui/app_dbz_ultimate.py")
        else:
            print("\n❌ Tests failed. Check the output above for errors.")

# =========================================================
# RUN TESTS
# =========================================================
if __name__ == "__main__":
    tester = GraphFlowTester()
    tester.run_all_tests()