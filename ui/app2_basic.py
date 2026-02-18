# ui/app_simple.py
"""
⚡ SIMPLE DBZ SAGA SIMULATOR - PROOF OF CONCEPT ⚡
Minimal version to test core functionality
"""

import sys
import os
from pathlib import Path
import uuid
import time
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from schemas.state import GameState
from graph.builder import create_saga_graph
from langchain_core.messages import HumanMessage, AIMessage

# =========================================================
# SIMPLE SESSION STATE
# =========================================================
def init_session():
    """Initialize minimal session state"""
    if "graph" not in st.session_state:
        st.session_state.graph = create_saga_graph()
    if "game_state" not in st.session_state:
        st.session_state.game_state = None
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None
    if "game_started" not in st.session_state:
        st.session_state.game_started = False

# =========================================================
# MAIN APP
# =========================================================
def main():
    st.set_page_config(
        page_title="⚡ DBZ Saga Simulator - Simple Test ⚡",
        page_icon="⚡",
        layout="wide"
    )
    
    init_session()
    
    st.title("⚡ DRAGON BALL Z - SAGA SIMULATOR")
    st.markdown("---")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("🎮 Game Controls")
        
        if not st.session_state.game_started:
            st.subheader("Start New Game")
            saga = st.selectbox(
                "Choose Saga",
                ["Saiyan Saga", "Frieza Saga", "Cell Saga", "Buu Saga"]
            )
            player = st.text_input("Your Name", "Goku")
            
            if st.button("🚀 BEGIN TRAINING", type="primary"):
                # Create new game state
                st.session_state.game_state = GameState(
                    saga_name=saga,
                    player_name=player,
                    player_stats={"power_level": 1000, "ki_mastery": 30}
                )
                st.session_state.game_state.add_message(
                    HumanMessage(content=f"Start the {saga}. I am {player}.")
                )
                st.session_state.thread_id = f"saga_{uuid.uuid4().hex[:8]}"
                st.session_state.game_started = True
                st.rerun()
        else:
            if st.button("🔄 End Game"):
                st.session_state.game_started = False
                st.session_state.game_state = None
                st.rerun()
    
    # Main game area
    if st.session_state.game_started and st.session_state.game_state:
        game_state = st.session_state.game_state
        
        # Display current messages
        st.subheader(f"📖 {game_state.saga_name}")
        
        for msg in game_state.messages[-3:]:  # Show last 3 messages
            if isinstance(msg, HumanMessage):
                st.info(f"👤 You: {msg.content}")
            elif isinstance(msg, AIMessage):
                st.success(f"🤖 {msg.content}")
        
        # Show stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Power Level", game_state.player_stats.get("power_level", 0))
        with col2:
            st.metric("Ki Mastery", f"{game_state.player_stats.get('ki_mastery', 0)}%")
        with col3:
            st.metric("Scenes", game_state.scene_counter)
        
        # Simple choices
        st.markdown("---")
        st.subheader("⚡ What will you do?")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Train in Hyperbolic Time Chamber", use_container_width=True):
                # Process choice
                game_state.add_message(HumanMessage(content="Train in Hyperbolic Time Chamber"))
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                
                with st.spinner("Training..."):
                    try:
                        result = st.session_state.graph.graph.invoke(game_state, config)
                        if result:
                            st.session_state.game_state = result
                    except Exception as e:
                        st.error(f"Error: {e}")
                
                st.rerun()
        
        with col2:
            if st.button("Seek Guidance from King Kai", use_container_width=True):
                game_state.add_message(HumanMessage(content="Seek Guidance from King Kai"))
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                
                with st.spinner("Seeking guidance..."):
                    try:
                        result = st.session_state.graph.graph.invoke(game_state, config)
                        if result:
                            st.session_state.game_state = result
                    except Exception as e:
                        st.error(f"Error: {e}")
                
                st.rerun()
        
        # Debug info
        with st.expander("🔧 Debug Info"):
            st.json({
                "messages": len(game_state.messages),
                "plan_steps": len(game_state.current_plan),
                "current_index": game_state.plan_step_index,
                "thread_id": st.session_state.thread_id
            })
    
    else:
        st.info("👈 Start a new game from the sidebar!")

if __name__ == "__main__":
    main()