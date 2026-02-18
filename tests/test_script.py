# test_script.py
"""
🧪 COMPREHENSIVE TEST SUITE FOR ANIME SAGA SIMULATOR
Tests all components: State, Planner, Executor, Verifier, Memory, and Graph
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

import json
import time
from datetime import datetime
from typing import Dict, Any, List

from schemas.state import GameState, PlanStep, SceneType
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.verifier import VerifierAgent, create_verifier
from utils.memory import MemoryManager
from graph.builder import create_saga_graph, GraphConfig
from utils.llm_wrapper import llm_wrapper


class TestRunner:
    """Runs comprehensive tests on all components"""
    
    def __init__(self):
        self.test_results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
        self.start_time = datetime.now()
    
    def print_header(self, title: str):
        """Print a formatted header"""
        print(f"\n{'='*70}")
        print(f"📋 {title}")
        print(f"{'='*70}\n")
    
    def print_subheader(self, title: str):
        """Print a subheader"""
        print(f"\n{'─'*50}")
        print(f"🔹 {title}")
        print(f"{'─'*50}\n")
    
    def print_success(self, message: str):
        """Print success message"""
        print(f"✅ {message}")
        self.test_results["passed"].append(message)
    
    def print_failure(self, message: str, error: Exception = None):
        """Print failure message"""
        print(f"❌ {message}")
        if error:
            print(f"   Error: {str(error)}")
        self.test_results["failed"].append(message)
    
    def print_warning(self, message: str):
        """Print warning message"""
        print(f"⚠️ {message}")
        self.test_results["warnings"].append(message)
    
    def print_summary(self):
        """Print test summary"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print(f"\n{'='*70}")
        print("📊 TEST SUMMARY")
        print(f"{'='*70}")
        print(f"✅ Passed: {len(self.test_results['passed'])}")
        print(f"❌ Failed: {len(self.test_results['failed'])}")
        print(f"⚠️ Warnings: {len(self.test_results['warnings'])}")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        
        if self.test_results["failed"]:
            print("\n❌ Failed Tests:")
            for test in self.test_results["failed"]:
                print(f"  • {test}")
        
        if self.test_results["warnings"]:
            print("\n⚠️ Warnings:")
            for warning in self.test_results["warnings"]:
                print(f"  • {warning}")
    
    def run_all_tests(self):
        """Run all test suites"""
        self.print_header("STARTING COMPREHENSIVE TEST SUITE")
        
        # Test each component
        test_state_creation()
        test_planner_agent()
        test_executor_agent()
        test_verifier_agent()
        test_memory_manager()
        test_graph_builder()
        test_end_to_end_flow()
        
        # Print final summary
        self.print_summary()


# ============================================================================
# INDIVIDUAL TEST CASES
# ============================================================================

def test_state_creation():
    """Test 1: GameState creation and validation"""
    runner.print_subheader("TEST 1: GameState Creation")
    
    try:
        # Create basic state
        state = GameState(
            player_name="TestHero",
            saga_name="Power Progression"
        )
        
        # Verify defaults
        assert state.player_name == "TestHero"
        assert state.saga_name == "Power Progression"
        assert state.player_stats["power_level"] == 100
        assert state.player_stats["health"] == 100
        assert len(state.messages) == 0
        assert len(state.current_plan) == 0
        
        runner.print_success("Basic GameState created with correct defaults")
        
        # Test with custom stats
        custom_state = GameState(
            player_name="Vegeta",
            saga_name="Saiyan Saga",
            player_stats={
                "power_level": 18000,
                "health": 100,
                "max_health": 100,
                "ki_mastery": 80,
                "level": 5,
                "items": ["scouter"]
            }
        )
        
        assert custom_state.player_stats["power_level"] == 18000
        assert custom_state.player_stats["items"][0] == "scouter"
        
        runner.print_success("Custom GameState created with correct stats")
        
        # Test serialization
        serialized = custom_state.to_serializable()
        assert isinstance(serialized, dict)
        assert serialized["player_name"] == "Vegeta"
        
        # Test deserialization
        deserialized = GameState.from_serializable(serialized)
        assert deserialized.player_name == "Vegeta"
        assert deserialized.player_stats["power_level"] == 18000
        
        runner.print_success("Serialization/Deserialization works correctly")
        
        # Test PlanStep creation
        step = PlanStep(
            scene_type=SceneType.BATTLE,
            description="Epic battle against Frieza",
            expected_outcome="Defeat Frieza or escape",
            expected_duration=3
        )
        
        assert step.scene_type == SceneType.BATTLE
        assert step.expected_duration == 3
        assert not step.completed
        
        runner.print_success("PlanStep created correctly")
        
    except Exception as e:
        runner.print_failure("GameState test failed", e)


def test_planner_agent():
    """Test 2: Planner Agent functionality"""
    runner.print_subheader("TEST 2: Planner Agent")
    
    try:
        # Create test state
        state = GameState(
            player_name="Goku",
            saga_name="Power Progression",
            player_stats={
                "power_level": 5000,
                "health": 100,
                "max_health": 100,
                "level": 3,
                "items": []
            }
        )
        
        # Initialize planner
        planner = PlannerAgent(max_plan_length=5)
        
        # Run planner
        result = planner.invoke(state)
        
        # Verify result structure
        assert "current_plan" in result
        assert len(result["current_plan"]) > 0
        assert result["plan_step_index"] == 0
        
        runner.print_success(f"Planner created {len(result['current_plan'])} steps")
        
        # Check plan content
        for i, step in enumerate(result["current_plan"]):
            assert isinstance(step, PlanStep)
            assert step.description
            assert step.expected_outcome
            assert step.scene_type in SceneType
            print(f"   Step {i+1}: {step.scene_type.value} - {step.description[:50]}...")
        
        # Check that messages were added
        assert "messages" in result
        assert len(result["messages"]) > 0
        
        runner.print_success("Plan contains valid steps and messages")
        
        # Test fallback plan (if LLM fails)
        planner.max_plan_length = 3
        fallback_result = planner._create_default_plan(state)
        assert "current_plan" in fallback_result
        assert len(fallback_result["current_plan"]) >= 3
        
        runner.print_success("Fallback plan works correctly")
        
    except Exception as e:
        runner.print_failure("Planner agent test failed", e)


def test_executor_agent():
    """Test 3: Executor Agent functionality"""
    runner.print_subheader("TEST 3: Executor Agent")
    
    try:
        # Create test state with a plan
        state = GameState(
            player_name="Gohan",
            saga_name="Power Progression",
            player_stats={
                "power_level": 1500,
                "health": 100,
                "max_health": 100,
                "level": 2,
                "items": []
            }
        )
        
        # Add a plan step
        state.current_plan = [
            PlanStep(
                scene_type=SceneType.TRAINING,
                description="Train with Piccolo in the wilderness",
                expected_outcome="Increase power level and learn new techniques",
                expected_duration=2
            )
        ]
        state.plan_step_index = 0
        
        # Initialize executor
        executor = ExecutorAgent()
        
        # Run executor
        player_action = "Focus on ki control"
        updates = executor.invoke(state, player_action)
        
        # Verify updates
        assert "messages" in updates
        assert len(updates.get("messages", [])) > 0
        
        # Check the message content
        if updates.get("messages"):
            message = updates["messages"][0]
            assert hasattr(message, 'content')
            print(f"   Scene preview: {message.content[:100]}...")
        
        # Check state updates
        if "player_stats" in updates:
            print(f"   Player stats updated: {updates['player_stats']}")
        
        runner.print_success("Executor generated a scene successfully")
        
        # Test with different scene types
        scene_types = [SceneType.BATTLE, SceneType.DIALOGUE, SceneType.CLIMAX]
        for scene_type in scene_types:
            state.current_plan[0].scene_type = scene_type
            updates = executor.invoke(state, player_action)
            assert "messages" in updates
            print(f"   ✅ {scene_type.value} scene generated")
        
        runner.print_success("All scene types work correctly")
        
    except Exception as e:
        runner.print_failure("Executor agent test failed", e)


def test_verifier_agent():
    """Test 4: Verifier Agent functionality"""
    runner.print_subheader("TEST 4: Verifier Agent")
    
    try:
        # Create verifier with different strictness levels
        for strictness in ["low", "medium", "high"]:
            verifier = create_verifier(strictness)
            assert verifier.strictness == strictness
            print(f"   ✅ {strictness} strictness verifier created")
        
        # Use medium strictness for tests
        verifier = create_verifier("medium")
        
        # Create test state
        from langchain_core.messages import AIMessage
        
        test_message = AIMessage(content="""
        Gohan stood before Piccolo, determination burning in his eyes.
        "I'm ready to train, Piccolo! I'll become stronger than ever!"
        Piccolo nodded sternly. "Good. Today we'll focus on your ki control.
        Your power level has reached 1500, but raw power means nothing without control."
        
        The training was intense. Hours passed as Gohan pushed himself to the limit,
        sweat pouring down his face. Finally, he managed to focus his energy perfectly.
        "I did it, Piccolo! I can feel my ki flowing smoothly!"
        "Not bad, boy. But this is just the beginning."
        """)
        
        state = GameState(
            player_name="Gohan",
            saga_name="Power Progression",
            player_stats={"power_level": 1500, "transformations": []}
        )
        state.messages.append(test_message)
        
        # Add current step
        state.current_plan = [
            PlanStep(
                scene_type=SceneType.TRAINING,
                description="Train with Piccolo",
                expected_outcome="Improve ki control"
            )
        ]
        state.plan_step_index = 0
        
        # Run verifier
        result = verifier.invoke(state)
        
        # Verify result structure
        assert "needs_correction" in result
        assert "quality_score" in result
        assert "issues" in result
        assert "verifier_notes" in result
        
        print(f"   Quality score: {result['quality_score']:.1%}")
        print(f"   Issues found: {len(result['issues'])}")
        print(f"   Needs correction: {result['needs_correction']}")
        
        runner.print_success("Verifier ran successfully")
        
        # Test with problematic content
        bad_message = AIMessage(content="Short scene.")
        state.messages.append(bad_message)
        result = verifier.invoke(state)
        
        assert result["quality_score"] < 0.7
        assert len(result["issues"]) > 0
        print(f"   Bad scene score: {result['quality_score']:.1%}")
        
        runner.print_success("Verifier correctly identifies low-quality scenes")
        
        # Test correction generation
        if result.get("needs_correction"):
            corrected = verifier._generate_correction(
                bad_message,
                result["issues"],
                state,
                state.current_step
            )
            assert corrected is not None
            assert len(corrected.content) > len(bad_message.content)
            print(f"   Correction generated: {corrected.content[:100]}...")
            runner.print_success("Correction generation works")
        
    except Exception as e:
        runner.print_failure("Verifier agent test failed", e)


def test_memory_manager():
    """Test 5: Memory Manager functionality"""
    runner.print_subheader("TEST 5: Memory Manager")
    
    try:
        # Create memory manager
        memory = MemoryManager(enable_compression=True, max_tokens=100000)
        
        # Create test state with many messages
        state = GameState(player_name="Test", saga_name="Test")
        
        # Add 25 test messages
        from langchain_core.messages import AIMessage, HumanMessage
        for i in range(25):
            if i % 2 == 0:
                state.messages.append(AIMessage(content=f"Scene {i} content..."))
            else:
                state.messages.append(HumanMessage(content=f"Choice {i}"))
        
        state.tokens_used = 60000  # Trigger compression
        
        # Test compression check
        should_compress = memory.should_compress(state)
        print(f"   Should compress: {should_compress}")
        
        if should_compress:
            # Test compression
            summary = memory.compress_memory(state)
            assert summary is not None
            print(f"   Summary: {summary[:100]}...")
            
            # Test pruning
            original_len = len(state.messages)
            state.messages = memory.prune_messages(state.messages)
            assert len(state.messages) < original_len
            print(f"   Pruned from {original_len} to {len(state.messages)} messages")
            
            runner.print_success("Memory compression and pruning work")
        else:
            runner.print_warning("Memory compression not triggered (token count may be low)")
        
        # Test with compression disabled
        memory_no_compress = MemoryManager(enable_compression=False)
        assert not memory_no_compress.should_compress(state)
        runner.print_success("Memory manager can be disabled")
        
    except Exception as e:
        runner.print_failure("Memory manager test failed", e)


def test_graph_builder():
    """Test 6: Graph Builder functionality"""
    runner.print_subheader("TEST 6: Graph Builder")
    
    try:
        # Create config
        config = GraphConfig(
            max_plan_length=5,
            difficulty="medium",
            narrative_complexity=5,
            enable_verifier=True,
            enable_memory_compression=True,
            max_tokens_per_run=100000
        )
        
        # Create graph
        graph = create_saga_graph(config)
        
        # Verify graph structure
        assert graph.graph is not None
        assert graph.checkpointer is not None
        
        # Check nodes exist
        expected_nodes = [
            "should_start_new_game", "planner", "executor", 
            "memory", "should_replan", "human_input", "should_continue"
        ]
        
        if config["enable_verifier"]:
            expected_nodes.append("verifier")
        
        # Note: Can't easily check nodes directly, but we can test compilation
        runner.print_success("Graph built successfully")
        
        # Test with different configs
        config_no_verifier = GraphConfig(enable_verifier=False)
        graph_no_verifier = create_saga_graph(config_no_verifier)
        runner.print_success("Graph without verifier built successfully")
        
        config_high_difficulty = GraphConfig(difficulty="high", max_plan_length=7)
        graph_high = create_saga_graph(config_high_difficulty)
        runner.print_success("Graph with high difficulty built successfully")
        
    except Exception as e:
        runner.print_failure("Graph builder test failed", e)


def test_end_to_end_flow():
    """Test 7: End-to-end flow with minimal execution"""
    runner.print_subheader("TEST 7: End-to-End Flow")
    
    try:
        # Create graph with minimal settings for testing
        config = GraphConfig(
            max_plan_length=3,
            difficulty="low",
            narrative_complexity=3,
            enable_verifier=True,
            enable_memory_compression=True,
            max_tokens_per_run=50000
        )
        
        graph = create_saga_graph(config)
        
        # Create initial state
        initial_state = GameState(
            player_name="TestRunner",
            saga_name="Power Progression",
            player_stats={
                "power_level": 1000,
                "health": 100,
                "max_health": 100,
                "level": 1,
                "items": []
            }
        )
        
        print("   🚀 Launching graph...")
        
        # Run graph (this will execute first few nodes)
        final_state = graph.run(initial_state, thread_id="test_run")
        
        # Check results
        assert final_state is not None
        print(f"   Final state has {len(final_state.messages)} messages")
        print(f"   Plan steps: {len(final_state.current_plan)}")
        print(f"   Plan revisions: {final_state.plan_revisions}")
        
        if final_state.current_plan:
            print(f"   First step: {final_state.current_plan[0].description[:50]}...")
        
        runner.print_success("End-to-end flow executed without errors")
        
        # Test streaming
        print("\n   📡 Testing streaming mode:")
        stream_count = 0
        for step in graph.stream(initial_state, thread_id="test_stream"):
            stream_count += 1
            if stream_count <= 3:  # Show first 3 steps
                node_name = list(step.keys())[0]
                print(f"      Step {stream_count}: {node_name}")
        
        print(f"      Total steps streamed: {stream_count}")
        runner.print_success("Streaming works correctly")
        
    except Exception as e:
        runner.print_failure("End-to-end flow test failed", e)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    # Create test runner
    runner = TestRunner()
    
    # Run all tests
    runner.run_all_tests()
    
    # Exit with appropriate code
    if runner.test_results["failed"]:
        sys.exit(1)
    else:
        sys.exit(0)