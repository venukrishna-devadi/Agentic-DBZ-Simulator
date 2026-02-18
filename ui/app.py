import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now your original imports will work
import streamlit as st
from datetime import datetime
from typing import List, Dict, Any, Optional
import json

from config import Config
from schemas.state import GameState, PlanStep, SceneType
from runners.hitl_runner import create_hitl_runner
from graph.builder import create_saga_graph


def init_session_state():
    """Initialize streamlit session state variables"""

    if "game_state" not in st.session_state:
        st.session_state.game_state = GameState()
    
    if "plan_history" not in st.session_state:
        st.session_state.plan_history = []

    if "show_debug" not in st.session_state:
        st.session_state.show_debug = False

    if "hitl_runner" not in st.session_state:
        graph = create_saga_graph()
        st.session_state.hitl_runner = create_hitl_runner(graph)



def display_header(game_state=None):
    """Display interactive app header with game + system info"""

    # ---------- Top Banner ----------
    st.markdown(
        """
        <style>
        .dbz-header {
            text-align: center;
            background: linear-gradient(90deg, #FFC107, #FF5722, #F44336); /* Fiery gradient */
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            font-size: 3.5em; /* Larger title */
            font-weight: 900; /* Bolder */
            text-shadow: 
                2px 2px #4CAF50, /* Greenish outline */
                -2px -2px #2196F3; /* Bluish outline */
            letter-spacing: 2px; /* More spaced out */
            margin-bottom: 0px;
            animation: pulse 1.5s infinite alternate; /* Subtle animation */
        }
        .dbz-slogan {
            font-size: 1.2em; /* Slightly larger slogan */
            color: #FFEB3B; /* Golden yellow */
            margin-top: 0px;
            font-style: italic;
            text-shadow: 1px 1px 2px #000000;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            100% { transform: scale(1.02); }
        }
        </style>
        <div style="text-align: center; padding: 20px 0; background-color: #1a1a2e; border-radius: 10px; margin-bottom: 20px;">
            <h1 class="dbz-header">ANIME DBZ SAGA SIMULATOR</h1>
            <p class="dbz-slogan">
                Unleash Your Inner Saiyan: Interactive AI Adventures Await!
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # ---------- Session Info ----------
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🎮 Game Info")
        if game_state:
            st.write(f"**Saga:** {game_state.get('saga_name', 'Not Started')}")
            st.write(f"**Current Scene:** {game_state.get('current_scene_id', 'N/A')}")
        else:
            st.write("Saga not started")

    with col2:
        st.markdown("### 🧠 Agent Status")
        if game_state:
            st.write(f"**Plan Steps:** {len(game_state.get('current_plan', []))}")
            st.write(f"**Iteration:** {game_state.get('iteration', 0)}")
        else:
            st.write("No active plan")

    with col3:
        st.markdown("### 🗂 Memory Status")
        if game_state:
            messages = game_state.get("messages", [])
            summary = game_state.get("summary", "")
            st.write(f"**Messages:** {len(messages)}")
            st.write(f"**Summary Length:** {len(summary)} chars")
        else:
            st.write("Memory empty")

    st.markdown("---")

    # ---------- Control Panel ----------
    with st.expander("⚙️ Session Controls", expanded=False):
        colA, colB, colC = st.columns(3)

        with colA:
            if st.button("🔄 Restart Saga"):
                st.session_state.clear()
                st.rerun()

        with colB:
            if st.button("💾 Save Game"):
                st.session_state["save_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.success("Game state saved locally (implement save logic).")

        with colC:
            if st.button("📂 Load Game"):
                st.info("Load logic not implemented yet.")

    # ---------- Architecture Info ----------
    with st.expander("🧠 Architecture Overview", expanded=False):
        st.markdown("""
        **This simulator uses a 3-layer AI architecture:**

        🧠 **Planning Layer**
        - Saga Planner
        - Dynamic Re-planner

        🎭 **Execution Layer**
        - Scene Executor
        - Battle Orchestrator

        🛡 **Quality Layer**
        - Memory Summarizer
        - Output Verifier
        - Power-Level Consistency Checker

        ---
        This demonstrates:
        - Planner–Executor architecture
        - Dynamic re-planning
        - Summarization memory
        - Structured output verification
        """)

    st.markdown("---")

import streamlit as st
from typing import Optional


def display_sidebar(
    *,
    start_new_game,
    reset_game,
    save_game,
    load_game,
    game_state: Optional[object] = None,
):
    """
    Full interactive sidebar for the Saga Simulator.

    Expects these callables:
      - start_new_game(saga_name: str, player_name: str, difficulty: str, enable_hitl: bool)
      - reset_game()
      - save_game(slot_name: str)
      - load_game(slot_name: str)

    game_state can be:
      - a Pydantic object with attributes, OR
      - a dict-like object
    """

    def gs_get(key, default=None):
        if game_state is None:
            return default
        if isinstance(game_state, dict):
            return game_state.get(key, default)
        return getattr(game_state, key, default)

    def safe_len(x):
        try:
            return len(x) if x is not None else 0
        except Exception:
            return 0

    with st.sidebar:
        st.header("🎮 Game Controls")

        # =========================
        # NEW GAME / SESSION SETUP
        # =========================
        st.subheader("🆕 New Game")

        saga_name = st.selectbox(
            "Choose Saga Type",
            ["Power Progression", "Mystical Quest", "Tournament Arc", "Survival Saga"],
            index=0,
            key="saga_select",
            help="This sets the tone and structure of the story arc the planner will generate.",
        )

        player_name = st.text_input(
            "Your Name",
            value=st.session_state.get("player_name", "Hero"),
            key="player_name",
            help="This name is used in narration and to personalize decisions.",
        )

        difficulty = st.select_slider(
            "Difficulty",
            options=["Easy", "Normal", "Hard", "Nightmare"],
            value=st.session_state.get("difficulty", "Normal"),
            key="difficulty",
            help="Controls how strict the verifier is and how aggressive opponents are (later).",
        )

        st.session_state.enable_hitl = st.toggle(
            "Human-in-the-loop tool approvals",
            value=st.session_state.get("enable_hitl", True),
            help="If ON: every tool call will pause for your approval (agentic mode).",
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✨ Start New Game", type="primary", use_container_width=True):
                st.session_state.player_name = player_name
                st.session_state.difficulty = difficulty
                start_new_game(saga_name, player_name, difficulty, st.session_state.enable_hitl)

        with col2:
            if st.button("🔄 Reset Game", type="secondary", use_container_width=True):
                reset_game()

        st.markdown("---")

        # =========================
        # QUICK ACTIONS
        # =========================
        st.subheader("⚡ Quick Actions")

        action_col1, action_col2 = st.columns(2)
        with action_col1:
            st.session_state.auto_continue = st.checkbox(
                "Auto-continue scenes",
                value=st.session_state.get("auto_continue", False),
                help="If enabled, the app will continue running turns automatically when it can.",
            )
        with action_col2:
            st.session_state.fast_mode = st.checkbox(
                "Fast mode",
                value=st.session_state.get("fast_mode", False),
                help="Reduces verbose debug output and keeps the UI cleaner.",
            )

        st.markdown("---")

        # =========================
        # GAME STATE PANEL
        # =========================
        st.subheader("📌 Game State")

        messages = gs_get("messages", [])
        summary = gs_get("summary", "")
        scene_counter = gs_get("scene_counter", gs_get("current_scene_id", 0))
        plan_progress = gs_get("plan_progress", None)
        plan_step_index = gs_get("plan_step_index", 0)
        current_plan = gs_get("current_plan", [])

        if safe_len(messages) > 0:
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Scenes", scene_counter if scene_counter is not None else 0)
            with c2:
                if plan_progress is None:
                    # Compute quick plan progress if not provided
                    total = safe_len(current_plan)
                    prog = (plan_step_index / total) if total else 0
                    st.metric("Plan Progress", f"{prog:.0%}")
                else:
                    st.metric("Plan Progress", f"{float(plan_progress):.0%}")

            # Memory indicators
            mem1, mem2 = st.columns(2)
            with mem1:
                st.caption(f"🗣 Messages: **{safe_len(messages)}**")
            with mem2:
                st.caption(f"🧠 Summary: **{len(summary) if summary else 0} chars**")

            # Visual progress bar (plan-based)
            total_steps = safe_len(current_plan)
            if total_steps:
                st.progress(min(1.0, max(0.0, plan_step_index / total_steps)))

            # Plan preview
            if total_steps:
                with st.expander("🧭 Current Plan (Preview)", expanded=False):
                    for i, step in enumerate(current_plan):
                        # step can be object or dict
                        desc = step.get("description") if isinstance(step, dict) else getattr(step, "description", "")
                        completed = step.get("completed") if isinstance(step, dict) else getattr(step, "completed", False)

                        if completed:
                            status = "✅"
                        elif i == plan_step_index:
                            status = "⏳"
                        else:
                            status = "⚪"

                        st.write(f"{status} **Step {i+1}:** {desc}")

        else:
            st.info("No active game yet. Start a new game to see state details.")

        st.markdown("---")

        # =========================
        # SAVE / LOAD PANEL
        # =========================
        st.subheader("💾 Save / Load")

        slot_name = st.text_input(
            "Save Slot Name",
            value=st.session_state.get("slot_name", "slot_1"),
            key="slot_name",
            help="Use different names to keep multiple saves.",
        )

        save_col, load_col = st.columns(2)
        with save_col:
            if st.button("💾 Save Game", use_container_width=True):
                save_game(slot_name)

        with load_col:
            if st.button("📂 Load Game", use_container_width=True):
                load_game(slot_name)

        st.markdown("---")

        # =========================
        # DEBUG / DEV TOOLS
        # =========================
        st.subheader("🧪 Debug")

        st.session_state.show_debug = st.checkbox(
            "Show Debug Info",
            value=st.session_state.get("show_debug", False),
            help="Shows node-by-node graph updates and raw tool outputs.",
        )

        st.session_state.show_raw_state = st.checkbox(
            "Show Raw State (JSON)",
            value=st.session_state.get("show_raw_state", False),
            help="Displays the entire state for inspection.",
        )

        st.session_state.show_messages_dump = st.checkbox(
            "Show Messages Dump",
            value=st.session_state.get("show_messages_dump", False),
            help="Shows the message list (Human/AI/Tool) for debugging memory behavior.",
        )

        # Optional: safety stop for long loops
        st.session_state.max_turns = st.slider(
            "Max turns per run",
            min_value=1,
            max_value=30,
            value=st.session_state.get("max_turns", 10),
            help="Prevents infinite loops during planning/execution.",
        )

        st.caption("Tip: Turn on Debug to see Planner → Executor → Replanner → Verifier flow.")

def start_new_game(
    saga_name: str,
    player_name: str,
    difficulty: str = "Normal",
    enable_hitl: bool = True,
    *,
    app=None,                      # optional: your compiled LangGraph app
    thread_id: Optional[str] = None,  # optional: checkpoint thread id
):
    """
    Full interactive start_new_game for your Streamlit DBZ/Anime Saga Simulator.

    What it does (interactive + robust):
    1) Creates a fresh GameState in st.session_state
    2) Creates a fresh thread_id for LangGraph checkpointing (optional)
    3) Adds a welcome AIMessage into messages
    4) Initializes UI-related session keys (pending approvals, debug logs, etc.)
    5) Optionally runs the graph once to generate the initial plan/scene
       - If HITL is enabled and it interrupts before tools, it sets pending tool calls
    6) Forces UI refresh with st.rerun()

    Assumptions:
    - You have a GameState class with:
        - fields: saga_name, player_name, start_time, difficulty, enable_hitl, ...
        - an add_message(msg) method (or you can append to .messages directly)
    - You might have st.session_state.app somewhere; we accept `app` optionally.
    """

    # ----------------------------
    # 0) Clean old session bits (optional but nice)
    # ----------------------------
    st.session_state.pending_tool_calls = []
    st.session_state.last_updates = []
    st.session_state.last_error = None
    st.session_state.game_started = True

    # ----------------------------
    # 1) Create / reset GameState
    # ----------------------------
    # If you use Pydantic GameState, import it here:
    # from src.state import GameState
    # For this snippet, we assume GameState already exists in scope.

    st.session_state.game_state = GameState(
        saga_name=saga_name,
        player_name=player_name,
        start_time=datetime.now(),
        difficulty=difficulty,
        enable_hitl=enable_hitl,
        scene_counter=0,
        plan_step_index=0,
        current_plan=[],
        summary="",
    )

    # ----------------------------
    # 2) Setup checkpoint thread_id
    # ----------------------------
    # This is important if you're using LangGraph checkpointer + resume flows.
    if thread_id is None:
        # Create a new thread_id per new game so checkpoint state doesn't mix
        import uuid
        thread_id = f"saga_{uuid.uuid4().hex[:8]}"

    st.session_state.thread_id = thread_id
    st.session_state.config = {"configurable": {"thread_id": thread_id}}

    # ----------------------------
    # 3) Add welcome message
    # ----------------------------
    from langchain_core.messages import AIMessage

    welcome_msg = AIMessage(
        content=(
            f"🔥 Welcome, **{player_name}**!\n\n"
            f"You have entered the **{saga_name}**.\n"
            f"Difficulty: **{difficulty}**\n\n"
            f"Your adventure begins الآن. Choose wisely…"
        )
    )

    # Use your helper if available, else append directly
    if hasattr(st.session_state.game_state, "add_message"):
        st.session_state.game_state.add_message(welcome_msg)
    else:
        st.session_state.game_state.messages.append(welcome_msg)

    # ----------------------------
    # 4) Optional: auto-run the graph once (generate initial plan/scene)
    # ----------------------------
    # This makes the "Start New Game" feel instant + impressive.
    # If you haven't wired the graph yet, this still works (it just won't run).
    if app is None:
        app = st.session_state.get("app", None)

    if app is not None:
        try:
            # Build an initial graph input from current state
            # NOTE: Your graph's state type may differ.
            # This assumes your graph can accept dict state like the earlier runner did.
            from langchain_core.messages import HumanMessage

            initial_input = {
                "messages": [HumanMessage(content=f"Start the {saga_name} saga for {player_name}.")],
                "research_topic": "",      # if not used, ignore
                "iteration": 0,
                # If you're using GameState instead of ResearchState, adapt accordingly
            }

            # Stream until interrupt or end (simple approach)
            last_values = None
            for mode, payload in app.stream(
                input=initial_input,
                config=st.session_state.config,
                stream_mode=["updates", "values"],
            ):
                if mode == "values":
                    last_values = payload
                    continue

                # updates
                event = payload
                node = list(event.keys())[0]
                delta = event[node]
                st.session_state.last_updates.append({"node": node, "delta": delta})

                # If graph uses interrupt_before=["tools"], it will pause here.
                if str(node).lower() in {"__interrupt__", "__interrupt"}:
                    # extract tool_calls from last AIMessage in last_values
                    msgs = last_values.get("messages", []) if isinstance(last_values, dict) else []
                    tool_calls = []
                    if msgs:
                        last = msgs[-1]
                        tool_calls = getattr(last, "tool_calls", None) or []
                    st.session_state.pending_tool_calls = tool_calls
                    break

            # Optionally: pull final checkpoint state (best effort)
            # This is safe and avoids the old bug where invoking initial state re-runs.
            # final_state = app.invoke(None, config=st.session_state.config)

        except Exception as e:
            st.session_state.last_error = str(e)

    # ----------------------------
    # 5) Rerun UI
    # ----------------------------
    st.rerun()


def _ensure_dirs():
    os.makedirs("saves", exist_ok=True)


def _new_thread_id(prefix: str = "saga") -> str:
    import uuid
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _reset_runtime_ui_flags():
    """Clear any runtime flags/logs related to HITL approvals, debug, etc."""
    st.session_state.pending_tool_calls = []
    st.session_state.last_updates = []
    st.session_state.last_error = None
    st.session_state.game_started = False


# ---------------------------------------------------------
# Reset Game (Interactive)
# ---------------------------------------------------------
def reset_game(*, clear_all_session: bool = False):
    """
    Reset the game safely.

    - Resets game_state and game_history
    - Clears HITL approvals / debug logs
    - Optionally clears the entire Streamlit session state (full restart)
    """
    if clear_all_session:
        st.session_state.clear()
        st.rerun()

    # Keep user preferences if you want
    difficulty = st.session_state.get("difficulty", "Normal")
    enable_hitl = st.session_state.get("enable_hitl", True)

    # Reset core state
    st.session_state.game_state = GameState(
        saga_name="",
        player_name="",
        start_time=None,
        difficulty=difficulty,
        enable_hitl=enable_hitl,
        scene_counter=0,
        plan_step_index=0,
        current_plan=[],
        summary="",
        messages=[],
    )
    st.session_state.game_history = []

    # Reset graph checkpoint thread_id (important!)
    st.session_state.thread_id = _new_thread_id("reset")
    st.session_state.config = {"configurable": {"thread_id": st.session_state.thread_id}}

    _reset_runtime_ui_flags()

    # Optional: toast
    try:
        st.toast("Game reset ✅")
    except Exception:
        pass

    st.rerun()


# ---------------------------------------------------------
# Save Game (Interactive)
# ---------------------------------------------------------
def save_game(
    *,
    slot_name: str = "slot_1",
    show_sidebar_feedback: bool = True,
) -> Optional[str]:
    """
    Save the current game_state to /saves as JSON.

    - Uses GameState.to_serializable()
    - Stores metadata (timestamp, slot_name)
    - Returns the file path (or None if nothing saved)
    """
    _ensure_dirs()

    if "game_state" not in st.session_state or st.session_state.game_state is None:
        if show_sidebar_feedback:
            st.sidebar.error("No game_state found to save.")
        return None

    # Convert to JSON-safe structure
    try:
        game_data = st.session_state.game_state.to_serializable()
    except Exception as e:
        if show_sidebar_feedback:
            st.sidebar.error(f"Save failed: {e}")
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_slot = "".join(c for c in slot_name if c.isalnum() or c in ("-", "_")).strip() or "slot_1"
    filename = f"{safe_slot}_{timestamp}.json"
    path = os.path.join("saves", filename)

    payload = {
        "meta": {
            "slot_name": safe_slot,
            "saved_at": timestamp,
            "thread_id": st.session_state.get("thread_id", ""),
        },
        "game_state": game_data,
    }

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        st.session_state.last_saved_file = path

        if show_sidebar_feedback:
            st.sidebar.success(f"✅ Game saved: {path}")

        # Optional: also offer a download button
        if show_sidebar_feedback:
            with open(path, "rb") as fb:
                st.sidebar.download_button(
                    label="⬇️ Download Save File",
                    data=fb,
                    file_name=filename,
                    mime="application/json",
                    use_container_width=True,
                )

        return path

    except Exception as e:
        if show_sidebar_feedback:
            st.sidebar.error(f"Save failed: {e}")
        return None


# ---------------------------------------------------------
# Load Game (Interactive)
# ---------------------------------------------------------
def load_game(
    *,
    slot_name: str = "slot_1",
    show_sidebar_feedback: bool = True,
):
    """
    Load a game from either:
    A) A file uploaded through Streamlit uploader
    B) A local file chosen from /saves directory (if present)

    This function is designed to be called from your sidebar UI.
    """
    _ensure_dirs()

    st.sidebar.markdown("### 📂 Load Game")

    # 1) Upload option
    uploaded_file = st.sidebar.file_uploader("Upload a save file", type="json", key="save_uploader")

    # 2) Local saves option
    local_files = sorted(
        [f for f in os.listdir("saves") if f.endswith(".json")],
        reverse=True
    )

    selected_local = None
    if local_files:
        selected_local = st.sidebar.selectbox(
            "Or load from local saves/",
            options=["(select a file)"] + local_files,
            index=0,
            key="local_save_select",
        )

    # Load button
    if st.sidebar.button("📥 Load Selected", use_container_width=True):
        try:
            payload = None

            # Load from upload
            if uploaded_file is not None:
                payload = json.load(uploaded_file)

            # Else load from local selection
            elif selected_local and selected_local != "(select a file)":
                path = os.path.join("saves", selected_local)
                with open(path, "r", encoding="utf-8") as f:
                    payload = json.load(f)

            else:
                if show_sidebar_feedback:
                    st.sidebar.warning("Please upload a file or select a local save.")
                return

            # Support both wrapped payload and raw game_state
            if isinstance(payload, dict) and "game_state" in payload:
                game_data = payload["game_state"]
                meta = payload.get("meta", {})
            else:
                game_data = payload
                meta = {}

            # Reconstruct game state
            st.session_state.game_state = GameState.from_serializable(game_data)

            # Restore thread_id (optional). Usually better to start a new thread_id
            # so graph checkpoints don't mix old tool calls.
            st.session_state.thread_id = _new_thread_id("loaded")
            st.session_state.config = {"configurable": {"thread_id": st.session_state.thread_id}}

            # Reset runtime flags/logs
            _reset_runtime_ui_flags()
            st.session_state.game_started = True

            if show_sidebar_feedback:
                loaded_at = meta.get("saved_at", "unknown time")
                st.sidebar.success(f"✅ Game loaded successfully! (saved_at={loaded_at})")

            st.rerun()

        except Exception as e:
            if show_sidebar_feedback:
                st.sidebar.error(f"Load failed: {e}")
            return


# ---------------------------------------------------------
# Optional: List saves utility for sidebar
# ---------------------------------------------------------
def list_saves_in_sidebar():
    """Small helper to show existing saves in sidebar."""
    _ensure_dirs()
    local_files = sorted([f for f in os.listdir("saves") if f.endswith(".json")], reverse=True)

    if not local_files:
        st.sidebar.caption("No saves found in /saves yet.")
        return

    with st.sidebar.expander("🗃 Saved Files", expanded=False):
        for f in local_files[:20]:
            st.sidebar.caption(f"• {f}")

import streamlit as st
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import random


# =========================================================
# MAIN CONTENT (FULL INTERACTIVE)
# =========================================================

def display_main_content(
    *,
    handle_choice_fn=None,   # optional override for choice handling
    run_graph_fn=None,       # optional: your LangGraph runner (planner/executor/replanner/verifier)
):
    """
    Full interactive main content area:
    - Welcome screen when no game yet
    - Game scene + choices panel (dynamic if available)
    - Player stats panel
    - Optional HITL approvals panel (if you store pending tool calls)
    """
    game_state = st.session_state.get("game_state", None)

    if game_state is None or not getattr(game_state, "messages", []):
        display_welcome_screen()
        return

    # Layout
    col_left, col_right = st.columns([3, 1], gap="large")
    with col_left:
        display_game_scene(game_state, handle_choice_fn=handle_choice_fn, run_graph_fn=run_graph_fn)

    with col_right:
        display_player_stats(game_state)

    # Optional: Debug / state view toggle
    if st.session_state.get("show_debug", False):
        display_debug_info(game_state)


# =========================================================
# WELCOME SCREEN
# =========================================================

def display_welcome_screen():
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 40px;
            border-radius: 16px;
            color: white;
            text-align: center;
            margin: 20px 0;
        ">
            <h1 style="color: white; margin-bottom: 10px;">Welcome to Anime Saga Simulator! 🐉</h1>
            <p style="font-size: 1.15em; opacity: 0.95;">
                An AI-powered adventure where every choice matters — with planning, re-planning, memory, and verification.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### 🎮 How to Play")

    c1, c2, c3 = st.columns(3, gap="large")

    with c1:
        st.markdown(
            """
            #### 1) Choose Your Saga
            Pick a vibe:
            - **Power Progression**
            - **Mystical Quest**
            - **Tournament Arc**
            - **Survival Saga**
            """
        )
    with c2:
        st.markdown(
            """
            #### 2) Make Choices
            Choices affect:
            - relationships
            - training paths
            - moral decisions
            - story direction
            """
        )
    with c3:
        st.markdown(
            """
            #### 3) Watch the AI Adapt
            The agent uses:
            - Planner → Executor
            - Dynamic Re-planning
            - Summarization Memory
            - Output Verification
            """
        )

    st.markdown("---")
    st.info("👈 Use the sidebar to start your adventure!")

    # Nice little demo teaser
    with st.expander("✨ What you’ll see once you start", expanded=False):
        st.markdown("- Cinematic scene text\n- Choice buttons\n- Stats panel\n- Plan progress + memory indicators\n- Debug view of Planner/Executor steps")


# =========================================================
# SCENE DISPLAY + CHOICES (INTERACTIVE)
# =========================================================

def display_game_scene(game_state, *, handle_choice_fn=None, run_graph_fn=None):
    """
    Displays:
    - last message as current scene
    - dynamic choices if your state has them
    - falls back to demo choices if not available
    - supports HITL approval panel if pending tool calls exist
    """
    from langchain_core.messages import AIMessage

    messages = getattr(game_state, "messages", [])
    if not messages:
        return

    # Find the latest AI "scene" message
    # (If you have ToolMessages etc, this filters a bit)
    latest_scene = None
    for m in reversed(messages):
        if isinstance(m, AIMessage) and (getattr(m, "content", "") or "").strip():
            latest_scene = m
            break
    if latest_scene is None:
        # fallback: just last message
        latest_scene = messages[-1]

    scene_counter = getattr(game_state, "scene_counter", 1)

    # Scene card
    st.markdown(
        f"""
        <div style="
            background: #1e1e2e;
            padding: 22px;
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.08);
            border-left: 6px solid #ff6b6b;
            margin: 10px 0 18px 0;
            color: #f8f8f2;
        ">
            <div style="display:flex; align-items:center; justify-content:space-between;">
                <h3 style="color: #ff79c6; margin:0;">Scene {scene_counter}</h3>
                <span style="opacity:0.8; font-size: 0.9em;">
                    Saga: <b>{getattr(game_state, "saga_name", "Unknown")}</b>
                </span>
            </div>
            <div style="margin-top: 12px; font-size: 1.07em; line-height: 1.65;">
                {getattr(latest_scene, "content", "")}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Optional: show current objective if present
    objective = getattr(game_state, "current_objective", None)
    if objective:
        st.info(f"🎯 Objective: {objective}")

    # Optional: HITL tool approval area if you use interrupt_before=["tools"]
    pending_tool_calls = st.session_state.get("pending_tool_calls", [])
    if pending_tool_calls:
        with st.container(border=True):
            st.warning("⏸️ Tool usage requested. Approve to continue.")
            for i, tc in enumerate(pending_tool_calls, 1):
                st.code(f"{i}) {tc.get('name')}({tc.get('args', {})})", language="json")

            a, d = st.columns(2)
            with a:
                if st.button("✅ Approve tools & continue", type="primary", use_container_width=True):
                    # Your run_graph_fn should resume from checkpoint (input=None)
                    if run_graph_fn:
                        run_graph_fn(resume=True)
                    # Clear pending calls regardless
                    st.session_state.pending_tool_calls = []
                    st.rerun()
            with d:
                if st.button("❌ Deny tools (stop)", use_container_width=True):
                    st.session_state.pending_tool_calls = []
                    st.info("Tools denied. You can pick a different choice or start a new session.")
                    st.rerun()

    st.markdown("### 🤔 What will you do?")

    # Try to get choices from state (preferred)
    # You can store them e.g. game_state.current_choices or game_state.last_choices
    choices = getattr(game_state, "current_choices", None) or getattr(game_state, "last_choices", None)

    # Fallback demo choices
    if not choices:
        choices = [
            "Train at the dojo",
            "Explore the city",
            "Visit your mentor",
            "Rest and recover",
        ]

    # Choice buttons
    for i, choice in enumerate(choices):
        # nicer layout with a tiny hint column
        c1, c2 = st.columns([6, 1], gap="small")
        with c1:
            if st.button(f"🔸 {choice}", key=f"choice_{scene_counter}_{i}", use_container_width=True):
                # Use injected handler if provided; else use built-in demo handler
                if handle_choice_fn:
                    handle_choice_fn(choice)
                else:
                    handle_player_choice(choice)

                # If you have a real graph runner, you can run next step after choice
                if run_graph_fn:
                    run_graph_fn(resume=False)

                st.rerun()
        with c2:
            st.caption(f"#{i+1}")


# =========================================================
# PLAYER STATS (INTERACTIVE)
# =========================================================

def display_player_stats(game_state):
    """
    Displays:
    - health / energy bars
    - metrics (power, level, xp)
    - form / items
    - world flags progress
    """
    st.markdown("### ⚡ Your Stats")

    stats = getattr(game_state, "player_stats", None)
    if stats is None:
        stats = {
            "health": 80,
            "max_health": 100,
            "energy": 60,
            "max_energy": 100,
            "power_level": 120,
            "level": 1,
            "experience": 0,
            "current_form": "base",
            "items": ["Senzu Bean", "Training Weights"],
        }

    # Health + Energy
    health = stats.get("health", 0)
    max_health = max(1, stats.get("max_health", 100))
    st.progress(health / max_health, text=f"Health: {health}/{max_health}")

    energy = stats.get("energy", 0)
    max_energy = max(1, stats.get("max_energy", 100))
    st.progress(energy / max_energy, text=f"Energy: {energy}/{max_energy}")

    # Metrics
    c1, c2 = st.columns(2, gap="small")
    with c1:
        st.metric("Power Level", stats.get("power_level", 0))
        st.metric("Level", stats.get("level", 1))
    with c2:
        st.metric("XP", stats.get("experience", 0))
        st.metric("Form", str(stats.get("current_form", "base")).title())

    # Items
    items = stats.get("items", [])
    if items:
        st.markdown("**Items:**")
        for item in items[:4]:
            st.caption(f"• {item}")
        if len(items) > 4:
            st.caption(f"...and {len(items) - 4} more")

    st.markdown("---")
    st.markdown("### 🏮 Story Progress")

    flags = getattr(game_state, "world_flags", None) or {
        "met_mentor": False,
        "found_artifact": False,
        "first_battle_won": False,
        "unlocked_transformation": False,
    }

    # Make flags readable
    for flag, active in flags.items():
        status = "✅" if active else "⏳"
        name = str(flag).replace("_", " ").title()
        st.caption(f"{status} {name}")


# =========================================================
# CHOICE HANDLER (DEMO VERSION)
# =========================================================

def handle_player_choice(choice: str):
    """Handle player's choice and advance the game"""
    game_state = st.session_state.get('game_state')
    runner = st.session_state.get('hitl_runner')
    
    if not game_state or not runner:
        st.error("Game not properly initialized")
        return
    
    # Prevent duplicate processing
    if st.session_state.get('processing_choice', False):
        print("⚠️ Already processing a choice, ignoring duplicate")
        return
    
    st.session_state.processing_choice = True
    
    with st.spinner(f"🌀 PROCESSING: {choice}..."):
        try:
            # Add the choice as a human message
            from langchain_core.messages import HumanMessage
            game_state.add_message(HumanMessage(content=choice))
            
            # Run the graph with the updated state
            result = runner.graph.run(
                game_state, 
                thread_id=st.session_state.thread_id,
                timeout=30
            )
            
            if result:
                st.session_state.game_state = result
                st.success("✨ Choice processed!")
            else:
                st.error("Failed to process choice")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            st.session_state.processing_choice = False
    
    st.rerun()


# =========================================================
# DEBUG INFO (INTERACTIVE)
# =========================================================

def display_debug_info(game_state):
    st.markdown("---")
    st.markdown("### 🐛 Debug Information")

    # Raw state
    with st.expander("Raw Game State (serializable)", expanded=False):
        if hasattr(game_state, "to_serializable"):
            st.json(game_state.to_serializable())
        else:
            # fallback: best effort
            st.json({k: str(getattr(game_state, k)) for k in dir(game_state) if not k.startswith("_")})

    # Messages dump
    with st.expander("Last Messages", expanded=False):
        msgs = getattr(game_state, "messages", [])
        for i, msg in enumerate(msgs[-8:]):
            st.caption(f"**[{len(msgs)-8+i}] {type(msg).__name__}:** {(getattr(msg, 'content', '') or '')[:160]}")

    # Node updates
    with st.expander("Graph Node Updates", expanded=False):
        st.json(st.session_state.get("last_updates", []))

    # Quick performance stats if present
    with st.expander("Performance", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Total Actions", getattr(game_state, "total_actions", 0))
            st.metric("Tokens Used", getattr(game_state, "tokens_used", 0))
        with c2:
            start_time = getattr(game_state, "start_time", None)
            if start_time:
                duration = (datetime.now() - start_time).total_seconds()
                st.metric("Game Duration", f"{duration:.1f}s")
            st.metric("Choices Made", len(getattr(game_state, "choices_made", [])))


# =========================================================
# OPTIONAL: MAIN() TEMPLATE (DROP-IN)
# =========================================================
import streamlit as st
import time
import random
import numpy as np
from streamlit_extras.let_it_rain import rain
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stylable_container import stylable_container
import base64

def generate_3d_background():
    """Generate WebGL-powered 3D dynamic background"""
    st.markdown("""
    <style>
    canvas#webgl-canvas {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -1000;
        pointer-events: none;
    }
    </style>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    
    <script>
    (function() {
        try {
            // Initialize Three.js scene with cosmic effects
            const scene = new THREE.Scene();
            scene.background = new THREE.Color(0x050510);
            
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.z = 30;
            
            const renderer = new THREE.WebGLRenderer({ 
                canvas: document.createElement('canvas'),
                antialias: true,
                alpha: false
            });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            renderer.setPixelRatio(window.devicePixelRatio);
            
            const canvas = renderer.domElement;
            canvas.id = 'webgl-canvas';
            document.body.prepend(canvas);
            
            // Dynamic lightning system
            const lightningSystem = [];
            class Lightning {
                constructor() {
                    this.points = [];
                    this.life = 0;
                    this.maxLife = 30 + Math.random() * 40;
                    this.generate();
                }
                
                generate() {
                    const startX = (Math.random() - 0.5) * 60;
                    const startY = 30;
                    const startZ = (Math.random() - 0.5) * 60;
                    
                    let x = startX, y = startY, z = startZ;
                    this.points = [{x, y, z}];
                    
                    while(y > -30) {
                        x += (Math.random() - 0.5) * 4;
                        y -= Math.random() * 3 + 1;
                        z += (Math.random() - 0.5) * 4;
                        this.points.push({x, y, z});
                    }
                }
                
                update() {
                    this.life++;
                    return this.life < this.maxLife;
                }
            }
            
            // Fire particles system
            const fireParticles = [];
            for(let i = 0; i < 200; i++) {
                fireParticles.push({
                    x: (Math.random() - 0.5) * 100,
                    y: Math.random() * 50 - 25,
                    z: (Math.random() - 0.5) * 100,
                    size: Math.random() * 2,
                    speed: Math.random() * 0.1 + 0.05,
                    life: Math.random()
                });
            }
            
            // Rain system
            const rainDrops = [];
            for(let i = 0; i < 1000; i++) {
                rainDrops.push({
                    x: (Math.random() - 0.5) * 200,
                    y: Math.random() * 100 - 50,
                    z: (Math.random() - 0.5) * 200,
                    speed: Math.random() * 0.5 + 0.3
                });
            }
            
            // Aurora borealis system
            const auroraPoints = [];
            for(let i = 0; i < 50; i++) {
                auroraPoints.push({
                    x: (Math.random() - 0.5) * 150,
                    y: Math.random() * 40 + 20,
                    z: (Math.random() - 0.5) * 150,
                    hue: Math.random() * 0.3 + 0.5
                });
            }
            
            // Create particle system for stars
            const starGeometry = new THREE.BufferGeometry();
            const starCount = 6000;
            const starPositions = new Float32Array(starCount * 3);
            const starColors = new Float32Array(starCount * 3);
            
            for(let i = 0; i < starCount * 3; i += 3) {
                starPositions[i] = (Math.random() - 0.5) * 600;
                starPositions[i+1] = (Math.random() - 0.5) * 600;
                starPositions[i+2] = (Math.random() - 0.5) * 600 - 200;
                
                const color = new THREE.Color().setHSL(Math.random() * 0.2 + 0.5, 0.8, 0.5);
                starColors[i] = color.r;
                starColors[i+1] = color.g;
                starColors[i+2] = color.b;
            }
            
            starGeometry.setAttribute('position', new THREE.BufferAttribute(starPositions, 3));
            starGeometry.setAttribute('color', new THREE.BufferAttribute(starColors, 3));
            
            const starMaterial = new THREE.PointsMaterial({
                size: 0.5,
                vertexColors: true,
                transparent: true,
                blending: THREE.AdditiveBlending,
                depthWrite: false
            });
            
            const stars = new THREE.Points(starGeometry, starMaterial);
            scene.add(stars);
            
            // Energy orbs
            const orbs = [];
            for(let i = 0; i < 20; i++) {
                const geometry = new THREE.SphereGeometry(0.5 + Math.random(), 32, 32);
                const material = new THREE.MeshPhongMaterial({
                    color: new THREE.Color().setHSL(Math.random(), 0.8, 0.6),
                    emissive: new THREE.Color().setHSL(Math.random(), 0.8, 0.3),
                    transparent: true,
                    opacity: 0.3 + Math.random() * 0.3,
                    wireframe: Math.random() > 0.7
                });
                
                const orb = new THREE.Mesh(geometry, material);
                orb.position.x = (Math.random() - 0.5) * 80;
                orb.position.y = (Math.random() - 0.5) * 80;
                orb.position.z = (Math.random() - 0.5) * 80 - 50;
                
                orb.userData = {
                    speed: 0.001 + Math.random() * 0.002,
                    rotationSpeed: (Math.random() - 0.5) * 0.02,
                    pulseSpeed: 0.01 + Math.random() * 0.02,
                    originalScale: 1
                };
                
                scene.add(orb);
                orbs.push(orb);
            }
            
            // Lightning bolts
            function createLightning(start, end) {
                const points = [];
                points.push(start);
                
                let current = start.clone();
                const direction = end.clone().sub(start);
                const distance = direction.length();
                direction.normalize();
                
                for(let i = 0; i < 20; i++) {
                    const segment = direction.clone().multiplyScalar((i + 1) * distance / 20);
                    const offset = new THREE.Vector3(
                        (Math.random() - 0.5) * 3,
                        (Math.random() - 0.5) * 3,
                        (Math.random() - 0.5) * 3
                    );
                    points.push(start.clone().add(segment).add(offset));
                }
                
                points.push(end);
                
                const geometry = new THREE.BufferGeometry().setFromPoints(points);
                const material = new THREE.LineBasicMaterial({ 
                    color: 0x88ccff,
                    transparent: true,
                    opacity: 0.8
                });
                
                return new THREE.Line(geometry, material);
            }
            
            // Dynamic lights
            const lights = [];
            for(let i = 0; i < 8; i++) {
                const light = new THREE.PointLight(
                    new THREE.Color().setHSL(Math.random(), 0.8, 0.6),
                    1,
                    50
                );
                light.position.x = (Math.random() - 0.5) * 60;
                light.position.y = (Math.random() - 0.5) * 60;
                light.position.z = (Math.random() - 0.5) * 60;
                
                light.castShadow = true;
                light.receiveShadow = true;
                
                scene.add(light);
                lights.push({
                    light,
                    speed: 0.002 + Math.random() * 0.004,
                    angle: Math.random() * Math.PI * 2,
                    radius: 20 + Math.random() * 30
                });
            }
            
            // Add ambient light
            const ambientLight = new THREE.AmbientLight(0x404060);
            scene.add(ambientLight);
            
            // Add directional light for shadows
            const dirLight = new THREE.DirectionalLight(0xffeedd, 1);
            dirLight.position.set(10, 20, 30);
            dirLight.castShadow = true;
            dirLight.receiveShadow = true;
            scene.add(dirLight);
            
            // Animation loop
            let time = 0;
            let weatherPhase = 0;
            
            function animate() {
                requestAnimationFrame(animate);
                
                time += 0.001;
                weatherPhase += 0.001;
                
                // Rotate stars
                stars.rotation.y += 0.0001;
                stars.rotation.x += 0.00005;
                
                // Animate orbs
                orbs.forEach((orb, i) => {
                    orb.position.x += Math.sin(time + i) * 0.01;
                    orb.position.y += Math.cos(time + i) * 0.01;
                    orb.position.z += Math.sin(time * 0.5 + i) * 0.01;
                    
                    orb.rotation.x += 0.01;
                    orb.rotation.y += 0.02;
                    orb.rotation.z += 0.015;
                    
                    const scale = 1 + Math.sin(time * orb.userData.pulseSpeed * 10) * 0.1;
                    orb.scale.set(scale, scale, scale);
                });
                
                // Animate lights
                lights.forEach((item, i) => {
                    item.angle += item.speed;
                    item.light.position.x = Math.cos(item.angle) * item.radius;
                    item.light.position.z = Math.sin(item.angle) * item.radius;
                    
                    // Color cycling
                    const hue = (time * 0.1 + i * 0.1) % 1;
                    item.light.color.setHSL(hue, 0.8, 0.6);
                });
                
                // Random lightning
                if(Math.random() < 0.02) {
                    const start = new THREE.Vector3(
                        (Math.random() - 0.5) * 80,
                        40,
                        (Math.random() - 0.5) * 80
                    );
                    const end = new THREE.Vector3(
                        (Math.random() - 0.5) * 80,
                        -40,
                        (Math.random() - 0.5) * 80
                    );
                    
                    const lightning = createLightning(start, end);
                    scene.add(lightning);
                    
                    setTimeout(() => {
                        scene.remove(lightning);
                    }, 100);
                }
                
                renderer.render(scene, camera);
            }
            
            animate();
            
            // Handle resize
            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });
        } catch(e) {
            console.error('3D Background error:', e);
        }
    })();
    </script>
    """, unsafe_allow_html=True)

def add_dynamic_weather_overlay():
    """Add dynamic weather effects overlay"""
    st.markdown("""
    <style>
    .weather-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 9000;
        mix-blend-mode: overlay;
    }
    
    .rain-overlay {
        background: repeating-linear-gradient(
            transparent,
            transparent 5px,
            rgba(100, 150, 255, 0.1) 6px,
            transparent 7px
        );
        animation: rain 0.5s linear infinite;
    }
    
    .fire-overlay {
        background: radial-gradient(circle at 20% 30%, rgba(255, 100, 0, 0.15) 0%, transparent 30%),
                    radial-gradient(circle at 80% 70%, rgba(255, 50, 0, 0.15) 0%, transparent 35%),
                    radial-gradient(circle at 40% 60%, rgba(255, 150, 0, 0.15) 0%, transparent 25%);
        animation: flicker 0.1s infinite alternate;
    }
    
    .lightning-overlay {
        background: rgba(255, 255, 255, 0.9);
        animation: lightningFlash 5s infinite;
        opacity: 0;
    }
    
    .snow-overlay {
        background: repeating-linear-gradient(
            45deg,
            transparent,
            transparent 10px,
            rgba(255, 255, 255, 0.1) 11px,
            transparent 12px
        );
        animation: snow 3s linear infinite;
    }
    
    .energy-overlay {
        background: repeating-conic-gradient(
            from 0deg,
            rgba(0, 255, 255, 0.05) 0deg 10deg,
            rgba(255, 0, 255, 0.05) 10deg 20deg,
            rgba(255, 255, 0, 0.05) 20deg 30deg
        );
        animation: rotate 60s linear infinite;
    }
    
    @keyframes rain {
        0% { background-position: 0 0; }
        100% { background-position: 0 20px; }
    }
    
    @keyframes snow {
        0% { background-position: 0 0; }
        100% { background-position: 20px 20px; }
    }
    
    @keyframes flicker {
        0% { opacity: 0.8; }
        100% { opacity: 1; }
    }
    
    @keyframes lightningFlash {
        0%, 95%, 98% { opacity: 0; }
        96%, 97% { opacity: 0.9; }
        99% { opacity: 0.3; }
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Glass morphism cards with dynamic lighting */
    .glass-card {
        background: rgba(10, 10, 30, 0.3);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .glass-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
        opacity: 0.5;
    }
    
    .glass-card:hover {
        background: rgba(20, 20, 50, 0.5);
        border-color: rgba(255, 215, 0, 0.5);
        box-shadow: 0 8px 32px 0 rgba(255, 215, 0, 0.2);
        transform: translateY(-5px);
    }
    
    /* Neon text with dynamic glow */
    .neon-text {
        color: #fff;
        text-shadow: 
            0 0 7px #fff,
            0 0 10px #fff,
            0 0 21px #fff,
            0 0 42px #0fa,
            0 0 82px #0fa,
            0 0 92px #0fa,
            0 0 102px #0fa,
            0 0 151px #0fa;
        animation: neonPulse 1.5s ease-in-out infinite alternate;
    }
    
    @keyframes neonPulse {
        from { text-shadow: 0 0 7px #fff, 0 0 10px #fff, 0 0 21px #fff, 0 0 42px #0fa, 0 0 82px #0fa, 0 0 92px #0fa, 0 0 102px #0fa, 0 0 151px #0fa; }
        to { text-shadow: 0 0 7px #fff, 0 0 10px #fff, 0 0 21px #fff, 0 0 42px #f0f, 0 0 82px #f0f, 0 0 92px #f0f, 0 0 102px #f0f, 0 0 151px #f0f; }
    }
    
    /* Dynamic border effects */
    .animated-border {
        position: relative;
        border: none;
        overflow: hidden;
    }
    
    .animated-border::after {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, 
            #ff0000, #ff7300, #fffb00, #48ff00, 
            #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000);
        background-size: 400% 400%;
        border-radius: 20px;
        z-index: -1;
        animation: borderGlow 3s ease infinite;
    }
    
    @keyframes borderGlow {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Particle cursor effect */
    .cursor-particle {
        position: fixed;
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background: radial-gradient(circle, #ff0, #f00);
        pointer-events: none;
        z-index: 99999;
        animation: fadeOut 1s forwards;
    }
    
    @keyframes fadeOut {
        from { opacity: 1; transform: scale(1); }
        to { opacity: 0; transform: scale(3); }
    }
    </style>
    
    <script>
    (function() {
        try {
            // Dynamic weather controller
            let currentWeather = 'cosmic';
            const weatherOverlay = document.createElement('div');
            weatherOverlay.className = 'weather-overlay';
            document.body.appendChild(weatherOverlay);
            
            function setWeather(type) {
                if (!weatherOverlay) return;
                weatherOverlay.className = 'weather-overlay';
                switch(type) {
                    case 'rain':
                        weatherOverlay.classList.add('rain-overlay');
                        break;
                    case 'fire':
                        weatherOverlay.classList.add('fire-overlay');
                        break;
                    case 'lightning':
                        weatherOverlay.classList.add('lightning-overlay');
                        break;
                    case 'snow':
                        weatherOverlay.classList.add('snow-overlay');
                        break;
                    case 'energy':
                        weatherOverlay.classList.add('energy-overlay');
                        break;
                    default:
                        weatherOverlay.className = 'weather-overlay';
                }
                currentWeather = type;
            }
            
            // Change weather every 10 seconds
            setInterval(() => {
                const weathers = ['rain', 'fire', 'lightning', 'snow', 'energy', 'cosmic'];
                const randomWeather = weathers[Math.floor(Math.random() * weathers.length)];
                setWeather(randomWeather);
            }, 10000);
            
            // Particle cursor effect
            document.addEventListener('mousemove', function(e) {
                if(Math.random() < 0.3) {
                    const particle = document.createElement('div');
                    particle.className = 'cursor-particle';
                    particle.style.left = e.clientX + 'px';
                    particle.style.top = e.clientY + 'px';
                    particle.style.background = `radial-gradient(circle, 
                        hsl(${Math.random() * 360}, 100%, 50%), 
                        hsl(${Math.random() * 360}, 100%, 50%))`;
                    document.body.appendChild(particle);
                    
                    setTimeout(() => {
                        if (particle.parentNode) {
                            particle.remove();
                        }
                    }, 1000);
                }
            });
            
            // Keyboard visual feedback
            document.addEventListener('keydown', function(e) {
                const ripple = document.createElement('div');
                ripple.style.position = 'fixed';
                ripple.style.left = e.clientX + 'px';
                ripple.style.top = e.clientY + 'px';
                ripple.style.width = '50px';
                ripple.style.height = '50px';
                ripple.style.borderRadius = '50%';
                ripple.style.background = 'radial-gradient(circle, rgba(255,255,255,0.8), transparent)';
                ripple.style.transform = 'translate(-50%, -50%)';
                ripple.style.animation = 'fadeOut 0.5s forwards';
                ripple.style.pointerEvents = 'none';
                ripple.style.zIndex = '99999';
                document.body.appendChild(ripple);
                
                setTimeout(() => {
                    if (ripple.parentNode) {
                        ripple.remove();
                    }
                }, 500);
            });
        } catch(e) {
            console.error('Weather overlay error:', e);
        }
    })();
    </script>
    """, unsafe_allow_html=True)

def add_holographic_ui():
    """Add holographic UI elements"""
    st.markdown("""
    <style>
    .holographic-panel {
        position: relative;
        background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 20px;
        padding: 20px;
        overflow: hidden;
    }
    
    .holographic-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255,255,255,0.2),
            transparent
        );
        animation: scan 3s infinite;
    }
    
    @keyframes scan {
        to { left: 200%; }
    }
    
    .digital-rain {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(0, 255, 0, 0.03) 3px,
            transparent 4px
        );
        pointer-events: none;
        z-index: 9500;
        animation: digitalRain 0.2s linear infinite;
    }
    
    @keyframes digitalRain {
        0% { background-position: 0 0; }
        100% { background-position: 0 20px; }
    }
    
    .energy-field {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at 50% 50%, 
            rgba(0, 255, 255, 0.05) 0%, 
            transparent 50%);
        pointer-events: none;
        z-index: 9400;
        animation: energyPulse 4s ease-in-out infinite;
    }
    
    @keyframes energyPulse {
        0%, 100% { opacity: 0.3; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(1.2); }
    }
    </style>
    
    <div class="digital-rain"></div>
    <div class="energy-field"></div>
    """, unsafe_allow_html=True)

def add_3d_power_visualizer(power_level):
    """Add 3D power level visualizer with error handling"""
    st.markdown(f"""
    <div id="power-visualizer-container" style="width: 100%; height: 200px; margin: 20px 0;"></div>
    <script>
    (function() {{
        try {{
            const container = document.getElementById('power-visualizer-container');
            if (!container) return;
            
            // Clear any existing canvas
            while (container.firstChild) {{
                container.removeChild(container.firstChild);
            }}
            
            const width = container.clientWidth || 400;
            const height = 200;
            
            const canvas = document.createElement('canvas');
            canvas.width = width;
            canvas.height = height;
            canvas.style.width = '100%';
            canvas.style.borderRadius = '10px';
            container.appendChild(canvas);
            
            const ctx = canvas.getContext('2d');
            let power = {power_level};
            let animationFrame;
            
            function drawPowerMeter() {{
                try {{
                    ctx.clearRect(0, 0, width, height);
                    
                    // Background
                    ctx.fillStyle = 'rgba(0,0,0,0.3)';
                    ctx.fillRect(0, 0, width, height);
                    
                    // Power bar with glow
                    const barWidth = (power / 10000) * width;
                    
                    // Glow effect
                    ctx.shadowBlur = 20;
                    ctx.shadowColor = '#ff0';
                    
                    // Gradient
                    const gradient = ctx.createLinearGradient(0, 0, barWidth, 0);
                    gradient.addColorStop(0, '#ff0000');
                    gradient.addColorStop(0.5, '#ffff00');
                    gradient.addColorStop(1, '#00ff00');
                    
                    ctx.fillStyle = gradient;
                    ctx.fillRect(0, 0, barWidth, height);
                    
                    // Reset shadow
                    ctx.shadowBlur = 0;
                    
                    // Particles
                    for(let i = 0; i < 20; i++) {{
                        const x = Math.random() * barWidth;
                        const y = Math.random() * height;
                        const size = Math.random() * 3 + 1;
                        
                        ctx.fillStyle = `rgba(255, 255, 0, ${{Math.random()}})`;
                        ctx.beginPath();
                        ctx.arc(x, y, size, 0, Math.PI * 2);
                        ctx.fill();
                    }}
                    
                    animationFrame = requestAnimationFrame(drawPowerMeter);
                }} catch (e) {{
                    console.error('Power visualizer draw error:', e);
                }}
            }}
            
            drawPowerMeter();
            
            // Cleanup on page unload
            window.addEventListener('beforeunload', function() {{
                if (animationFrame) {{
                    cancelAnimationFrame(animationFrame);
                }}
            }});
        }} catch (e) {{
            console.error('Failed to initialize power visualizer:', e);
        }}
    }})();
    </script>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="⚡ ANIME SAGA SIMULATOR - LEGENDARY EDITION ⚡",
        page_icon="⚔️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Generate 3D cosmic background
    generate_3d_background()
    
    # Add dynamic weather effects
    add_dynamic_weather_overlay()
    
    # Add holographic UI
    add_holographic_ui()

    # =========================================================
    # 🌌 ABSOLUTELY OVERKILL CSS STYLES
    # =========================================================
    st.markdown("""
    <style>
    /* Cyberpunk font */
    @import url('https://fonts.googleapis.com/css2?family=Audiowide&family=Monoton&family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Rajdhani', 'Orbitron', sans-serif;
    }
    
    .stApp {
        background: transparent !important;
    }
    
    /* Main container with glass effect */
    .main > div {
        background: rgba(5, 5, 20, 0.3);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 20px;
        margin: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
    }
    
    /* Anime power text */
    .power-text {
        font-family: 'Audiowide', cursive;
        font-size: 4em;
        background: linear-gradient(45deg, #ff0000, #ff9900, #ffff00, #00ff00, #0000ff, #4b0082, #8f00ff);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        animation: rainbow 3s linear infinite;
        text-shadow: 0 0 30px rgba(255,255,255,0.5);
    }
    
    @keyframes rainbow {
        0% { filter: hue-rotate(0deg); }
        100% { filter: hue-rotate(360deg); }
    }
    
    /* 3D transform cards */
    .tilt-card {
        transform-style: preserve-3d;
        transition: transform 0.3s;
        position: relative;
    }
    
    .tilt-card:hover {
        transform: perspective(1000px) rotateX(10deg) rotateY(10deg) translateZ(20px);
    }
    
    /* Liquid fill effect */
    .liquid-button {
        background: linear-gradient(45deg, #ff416c, #ff4b2b);
        position: relative;
        overflow: hidden;
    }
    
    .liquid-button::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(
            to bottom right,
            rgba(255,255,255,0) 45%,
            rgba(255,255,255,0.3) 50%,
            rgba(255,255,255,0) 55%
        );
        animation: liquid 3s linear infinite;
    }
    
    @keyframes liquid {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    /* Dynamic stat counters */
    .stat-counter {
        font-family: 'Orbitron', monospace;
        font-size: 2.5em;
        font-weight: 900;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        text-shadow: 0 0 20px rgba(102, 126, 234, 0.5);
        animation: counterPulse 2s ease-in-out infinite;
    }
    
    @keyframes counterPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    
    /* Cosmic particle field */
    .cosmic-particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 9001;
    }
    
    /* Energy shield effect */
    .energy-shield {
        position: relative;
        overflow: hidden;
    }
    
    .energy-shield::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #ff0, #f0f, #0ff, #ff0);
        background-size: 400% 400%;
        border-radius: inherit;
        z-index: -1;
        animation: energyShield 3s ease infinite;
        opacity: 0.7;
    }
    
    @keyframes energyShield {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }
    
    /* Scanning line effect */
    .scan-line {
        position: relative;
        overflow: hidden;
    }
    
    .scan-line::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, transparent, #0ff, transparent);
        animation: scan 2s linear infinite;
    }
    
    @keyframes scan {
        to { left: 200%; }
    }
    
    /* Glitch text effect */
    .glitch-text {
        position: relative;
        animation: glitch 3s infinite;
    }
    
    .glitch-text::before,
    .glitch-text::after {
        content: attr(data-text);
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
    }
    
    .glitch-text::before {
        animation: glitchTop 1s infinite;
        clip-path: polygon(0 0, 100% 0, 100% 33%, 0 33%);
        color: #ff00ff;
    }
    
    .glitch-text::after {
        animation: glitchBottom 1.5s infinite;
        clip-path: polygon(0 67%, 100% 67%, 100% 100%, 0 100%);
        color: #00ffff;
    }
    
    @keyframes glitchTop {
        2%, 64% { transform: translate(2px, -2px); }
        4%, 60% { transform: translate(-2px, 2px); }
        62% { transform: translate(13px, -1px) skew(-13deg); }
    }
    
    @keyframes glitchBottom {
        2%, 64% { transform: translate(-2px, 2px); }
        4%, 60% { transform: translate(2px, -2px); }
        62% { transform: translate(-13px, 1px) skew(13deg); }
    }
    
    /* Ripple effect */
    .ripple {
        position: relative;
        overflow: hidden;
    }
    
    .ripple:after {
        content: "";
        display: block;
        position: absolute;
        width: 100%;
        height: 100%;
        top: 0;
        left: 0;
        pointer-events: none;
        background-image: radial-gradient(circle, #fff 10%, transparent 10.01%);
        background-repeat: no-repeat;
        background-position: 50%;
        transform: scale(10, 10);
        opacity: 0;
        transition: transform .3s, opacity .5s;
    }
    
    .ripple:active:after {
        transform: scale(0, 0);
        opacity: .3;
        transition: 0s;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #ff416c, #ff4b2b);
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(255, 75, 43, 0.5);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #ff4b2b, #ff416c);
    }
    
    /* Loading animation */
    .anime-loading {
        display: inline-block;
        width: 50px;
        height: 50px;
        border: 3px solid rgba(255,255,255,.3);
        border-radius: 50%;
        border-top-color: #ff0;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize session state with epic stats
    if "game_started" not in st.session_state:
        st.session_state.game_started = False
    if "power_level" not in st.session_state:
        st.session_state.power_level = random.randint(1000, 5000)
    if "spirit_bombs" not in st.session_state:
        st.session_state.spirit_bombs = 0
    if "combat_tier" not in st.session_state:
        st.session_state.combat_tier = "E Rank"
    if "zenkai_boosts" not in st.session_state:
        st.session_state.zenkai_boosts = 0
    if "saga_arc" not in st.session_state:
        st.session_state.saga_arc = "Origin Arc"
    if "ki_mastery" not in st.session_state:
        st.session_state.ki_mastery = random.randint(1, 100)
    if "divine_interventions" not in st.session_state:
        st.session_state.divine_interventions = 0
    if "show_debug" not in st.session_state:
        st.session_state.show_debug = False

    # =========================================================
    # 🎮 WELCOME PAGE - MAXIMUM OVERKILL
    # =========================================================
    if not st.session_state.game_started:
        
        # Epic header with particle effects
        st.markdown("""
        <div class="energy-shield" style="
            text-align: center;
            padding: 60px 20px;
            margin-bottom: 40px;
            position: relative;
            background: rgba(0,0,0,0.3);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 30px;
            overflow: hidden;
        ">
            <div style="position: relative; z-index: 2;">
                <h1 class="power-text" style="font-size: 5.5em; margin-bottom: 20px;">
                    ⚡ ANIME SAGA ⚡
                </h1>
                <h1 class="power-text" style="font-size: 4.5em; animation-delay: 0.5s;">
                    SIMULATOR X
                </h1>
                <div style="display: flex; justify-content: center; gap: 30px; margin-top: 40px;">
                    <span style="font-size: 3em; animation: bounce 1s infinite;">🔥</span>
                    <span style="font-size: 3em; animation: bounce 1s infinite; animation-delay: 0.2s;">⚡</span>
                    <span style="font-size: 3em; animation: bounce 1s infinite; animation-delay: 0.4s;">🌪️</span>
                    <span style="font-size: 3em; animation: bounce 1s infinite; animation-delay: 0.6s;">💫</span>
                    <span style="font-size: 3em; animation: bounce 1s infinite; animation-delay: 0.8s;">✨</span>
                    <span style="font-size: 3em; animation: bounce 1s infinite; animation-delay: 1s;">🌠</span>
                </div>
            </div>
        </div>
        
        <style>
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-20px); }
        }
        </style>
        """, unsafe_allow_html=True)

        # 3D power chamber
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div class="glass-card tilt-card" style="
                text-align: center;
                margin: 40px 0;
                position: relative;
            ">
                <h2 style="
                    font-size: 3em;
                    background: linear-gradient(45deg, #ff0, #f0f);
                    -webkit-background-clip: text;
                    background-clip: text;
                    color: transparent;
                    margin-bottom: 30px;
                    font-family: 'Audiowide', cursive;
                ">
                    ⚡ HYPER DIMENSIONAL POWER CHAMBER ⚡
                </h2>
            """, unsafe_allow_html=True)

            # Power level slider with 3D visualizer
            power_level = st.slider(
                "🌀 COSMIC ENERGY FLOW 🌀",
                min_value=0,
                max_value=10000,
                value=st.session_state.power_level,
                step=100,
                key="power_slider_3d",
                help="Channel your inner spirit energy!"
            )
            st.session_state.power_level = power_level
            
            # Add 3D power visualizer
            add_3d_power_visualizer(power_level)
            
            # Dynamic power effects with particle system
            power_percentage = power_level / 10000 * 100
            
            # Multi-stage power reactions
            if power_level >= 9000:
                st.balloons()
                st.snow()
                st.markdown("""
                <div style="
                    background: radial-gradient(circle, rgba(255,215,0,0.9), rgba(255,69,0,0.9), rgba(255,0,0,0.9));
                    padding: 30px;
                    border-radius: 20px;
                    text-align: center;
                    animation: pulse 0.5s infinite;
                    border: 5px solid white;
                    box-shadow: 0 0 100px rgba(255,215,0,0.8);
                    margin-top: 20px;
                ">
                    <h1 style="color: white; font-size: 3.5em; text-shadow: 0 0 30px black;">
                        🎉 IT'S OVER 9000!!! 🎉
                    </h1>
                    <h2 style="color: white; font-size: 2.5em; text-shadow: 0 0 20px black;">
                        SUPER SAIYAN BLUE EVOLUTION UNLOCKED!
                    </h2>
                    <div style="display: flex; justify-content: center; gap: 20px; margin-top: 20px;">
                        <span style="font-size: 3em;">👑</span>
                        <span style="font-size: 3em;">⚡</span>
                        <span style="font-size: 3em;">🔥</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.session_state.combat_tier = "Z+ RANK (GOD OF DESTRUCTION)"
                
            elif power_level >= 8000:
                st.markdown("""
                <div style="
                    background: linear-gradient(45deg, rgba(0,255,255,0.9), rgba(0,0,255,0.9));
                    padding: 25px;
                    border-radius: 20px;
                    text-align: center;
                    animation: pulse 1s infinite;
                    border: 3px solid cyan;
                    box-shadow: 0 0 80px rgba(0,255,255,0.6);
                    margin-top: 20px;
                ">
                    <h2 style="color: white; font-size: 2.5em;">💎 ULTRA INSTINCT SIGN 💎</h2>
                    <p style="color: white; font-size: 1.5em;">Your body moves before your mind!</p>
                </div>
                """, unsafe_allow_html=True)
                st.session_state.combat_tier = "Z RANK (ULTRA INSTINCT)"
                
            elif power_level >= 7000:
                st.success("🌟 LEGENDARY SUPER SAIYAN! You radiate divine energy! 🌟")
                st.session_state.combat_tier = "S+ RANK (LEGENDARY)"
                
            elif power_level >= 6000:
                st.info("⚔️ SUPER SAIYAN GOD! Your power transcends mortal limits! ⚔️")
                st.session_state.combat_tier = "S RANK (GOD TIER)"
                
            elif power_level >= 5000:
                st.warning("💫 SUPER SAIYAN 3! Your aura shakes dimensions! 💫")
                st.session_state.combat_tier = "A+ RANK (TRANSCENDENT)"
                
            elif power_level >= 4000:
                st.info("💪 SUPER SAIYAN 2! Lightning crackles around you! 💪")
                st.session_state.combat_tier = "A RANK (ELITE)"
                
            elif power_level >= 3000:
                st.info("⚡ SUPER SAIYAN! Your hair turns GOLDEN! ⚡")
                st.session_state.combat_tier = "B+ RANK (ASCENDED)"
                
            elif power_level >= 2000:
                st.info("✨ POWERED UP! Your ki is overflowing! ✨")
                st.session_state.combat_tier = "B RANK (ADVANCED)"
                
            elif power_level >= 1000:
                st.info("🔥 KI AWAKENED! You've unlocked your inner power! 🔥")
                st.session_state.combat_tier = "C RANK (WARRIOR)"
                
            else:
                st.info("🌀 CHANNELING... Focus your energy to awaken your power! 🌀")
            
            st.markdown("</div>", unsafe_allow_html=True)

        # Ultra HD feature grid with 3D transforms
        st.markdown("""
        <h2 style="
            text-align: center;
            font-size: 4em;
            margin: 80px 0 40px;
            background: linear-gradient(45deg, #ff0, #ff00ff, #00ffff, #ff0);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            font-family: 'Audiowide', cursive;
            animation: rainbow 5s linear infinite;
        ">
            ⚡ COSMIC ABILITIES UNLOCKED ⚡
        </h2>
        
        <div style="
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            padding: 20px;
            perspective: 1000px;
        ">
        """, unsafe_allow_html=True)
        
        features = [
            {
                "icon": "🌀",
                "title": "QUANTUM REALITY ENGINE",
                "desc": "Every decision spawns parallel universes! Your choices create infinite timelines with our quantum AI that processes 1,000,000 scenarios/second! 🌌",
                "color": "#00ffff"
            },
            {
                "icon": "⚡",
                "title": "DIVINE POWER SCALING",
                "desc": "Real-time power progression from E Rank to GOD TIER! 100+ transformation levels with unique visual effects and ability unlocks! 📈",
                "color": "#ffff00"
            },
            {
                "icon": "🧬",
                "title": "EMOTIONAL SYNTHESIS AI",
                "desc": "Characters with genuine feelings! Our neural network generates complex emotional responses, rivalries, friendships, and epic betrayals! 💔",
                "color": "#ff00ff"
            },
            {
                "icon": "🌍",
                "title": "LIVING MULTIVERSE",
                "desc": "7 connected dimensions that evolve in real-time! Wars, peace treaties, natural disasters, and civilizations rise and fall! 🏰",
                "color": "#00ff00"
            },
            {
                "icon": "🎬",
                "title": "CINEMATIC BATTLE ENGINE",
                "desc": "Frame-by-frame 4K action sequences! Dynamic camera angles, particle effects, slow-motion finishers, and destructible environments! 💥",
                "color": "#ff0000"
            },
            {
                "icon": "🤖",
                "title": "LANGGRAPH 7.0 QUANTUM CORE",
                "desc": "Next-gen agentic AI with 1 trillion parameters! Real-time planning, execution, verification, and evolution of storylines! 🚀",
                "color": "#ff9900"
            },
            {
                "icon": "💎",
                "title": "INFINITE ITEM SYNTHESIS",
                "desc": "Craft legendary weapons from 10,000+ materials! Each item has unique stats, appearances, and evolution paths! ⚔️",
                "color": "#ff69b4"
            },
            {
                "icon": "🎵",
                "title": "DYNAMIC SOUNDTRACK",
                "desc": "Procedurally generated anime OST! Music adapts to battle intensity, emotional moments, and exploration! 🎸",
                "color": "#8a2be2"
            }
        ]
        
        for feature in features:
            st.markdown(f"""
            <div class="tilt-card" style="
                background: linear-gradient(135deg, rgba(10,10,30,0.8), rgba(20,20,50,0.8));
                backdrop-filter: blur(10px);
                border: 2px solid {feature['color']};
                border-radius: 30px;
                padding: 30px;
                transition: all 0.3s;
                position: relative;
                overflow: hidden;
                box-shadow: 0 0 30px rgba(0,0,0,0.5);
            ">
                <div style="position: relative; z-index: 2;">
                    <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
                        <span style="font-size: 4em; filter: drop-shadow(0 0 20px {feature['color']});">
                            {feature['icon']}
                        </span>
                        <h3 style="
                            color: {feature['color']};
                            font-size: 1.8em;
                            font-weight: 900;
                            text-shadow: 0 0 15px {feature['color']};
                            margin: 0;
                        ">
                            {feature['title']}
                        </h3>
                    </div>
                    <p style="
                        color: white;
                        font-size: 1.2em;
                        line-height: 1.6;
                        margin: 0;
                        text-shadow: 0 0 10px rgba(0,0,0,0.5);
                    ">
                        {feature['desc']}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

        # Epic CTA with particle explosion
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <div style="
                background: radial-gradient(circle, rgba(255,215,0,0.2), transparent);
                padding: 50px;
                margin: 60px 0;
                border-radius: 50px;
                text-align: center;
            ">
            """, unsafe_allow_html=True)
            
            if st.button("🔥 AWAKEN YOUR DESTINY NOW! 🔥", key="start_saga_overkill", use_container_width=True):
                # Multi-stage animation
                with st.spinner("🌀 INITIALIZING QUANTUM SAGA ENGINE..."):
                    time.sleep(0.5)
                with st.spinner("⚡ CHANNELING COSMIC ENERGY..."):
                    time.sleep(0.5)
                with st.spinner("🌟 UNLOCKING DIVINE INTERVENTION..."):
                    time.sleep(0.5)
                with st.spinner("✨ FORGING YOUR LEGENDARY PATH..."):
                    time.sleep(0.5)
                
                st.balloons()
                st.snow()
                
                st.markdown("""
                <div style="
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: radial-gradient(circle, rgba(0,0,0,0.95), rgba(75,0,130,0.95));
                    z-index: 99999;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    animation: fadeIn 1s;
                ">
                    <h1 style="color: #FFD700; font-size: 5em; text-align: center; animation: pulse 0.5s infinite;">
                        ⚡ SAGA INITIALIZED ⚡
                    </h1>
                    <h2 style="color: white; font-size: 3em; text-align: center;">
                        Welcome, Legendary Warrior!
                    </h2>
                </div>
                """, unsafe_allow_html=True)
                
                time.sleep(2)
                st.session_state.game_started = True
                st.session_state.zenkai_boosts = 0
                st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

    # =========================================================
    # 🎮 GAME PAGE - ABSOLUTE CINEMA
    # =========================================================
    else:
        # Dynamic saga header with real-time stats
        st.markdown(f"""
        <div class="energy-shield" style="
            text-align: center;
            padding: 40px;
            margin-bottom: 30px;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(20px);
            border: 3px solid rgba(255,215,0,0.5);
            border-radius: 30px;
            position: relative;
            overflow: hidden;
        ">
            <div style="position: relative; z-index: 2;">
                <h1 style="
                    font-size: 4em;
                    background: linear-gradient(45deg, #FFD700, #FF4500, #FF1493);
                    -webkit-background-clip: text;
                    background-clip: text;
                    color: transparent;
                    text-shadow: 0 0 30px rgba(255,215,0,0.5);
                    margin-bottom: 20px;
                    font-family: 'Audiowide', cursive;
                ">
                    ⚔️ SAGA MODE: {st.session_state.saga_arc} ⚔️
                </h1>
                
                <div style="
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 30px;
                    margin-top: 30px;
                ">
                    <div style="
                        background: rgba(255,215,0,0.1);
                        border: 2px solid #FFD700;
                        border-radius: 20px;
                        padding: 20px;
                        backdrop-filter: blur(10px);
                    ">
                        <p style="color: #FFD700; font-size: 1.2em;">POWER LEVEL</p>
                        <p class="stat-counter">{st.session_state.power_level}</p>
                    </div>
                    <div style="
                        background: rgba(255,69,0,0.1);
                        border: 2px solid #FF4500;
                        border-radius: 20px;
                        padding: 20px;
                        backdrop-filter: blur(10px);
                    ">
                        <p style="color: #FF4500; font-size: 1.2em;">COMBAT RANK</p>
                        <p class="stat-counter">{st.session_state.combat_tier}</p>
                    </div>
                    <div style="
                        background: rgba(0,255,255,0.1);
                        border: 2px solid #00FFFF;
                        border-radius: 20px;
                        padding: 20px;
                        backdrop-filter: blur(10px);
                    ">
                        <p style="color: #00FFFF; font-size: 1.2em;">SPIRIT BOMBS</p>
                        <p class="stat-counter">{st.session_state.spirit_bombs}</p>
                    </div>
                    <div style="
                        background: rgba(255,20,147,0.1);
                        border: 2px solid #FF1493;
                        border-radius: 20px;
                        padding: 20px;
                        backdrop-filter: blur(10px);
                    ">
                        <p style="color: #FF1493; font-size: 1.2em;">KI MASTERY</p>
                        <p class="stat-counter">{st.session_state.ki_mastery}%</p>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Main game interface with holographic panels
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.markdown("""
            <div class="holographic-panel" style="
                padding: 30px;
                border-radius: 30px;
                margin-bottom: 30px;
            ">
                <h3 style="
                    color: #00ffff;
                    font-size: 2.2em;
                    margin-bottom: 20px;
                    text-shadow: 0 0 20px cyan;
                ">
                    📖 LIVING NARRATIVE ENGINE 📖
                </h3>
            """, unsafe_allow_html=True)
            
            # Dynamic story content based on power level
            if st.session_state.power_level >= 9000:
                story = "The heavens tremble as you ascend beyond mortal comprehension! Gods themselves bow before your divine aura! The multiverse recognizes its new protector!"
            elif st.session_state.power_level >= 7000:
                story = "You've transcended the limits of Super Saiyan! Divine ki flows through every fiber of your being. The angels take notice of your evolution!"
            elif st.session_state.power_level >= 5000:
                story = "Golden energy explodes around you! Your hair flows with cosmic power! You've achieved the legendary Super Saiyan transformation!"
            elif st.session_state.power_level >= 3000:
                story = "Your ki surges exponentially! The ground cracks beneath your feet! You're approaching the legendary threshold!"
            elif st.session_state.power_level >= 1000:
                story = "Your training bears fruit! You can feel the energy of the universe flowing through your veins!"
            else:
                story = "Your journey begins on a small island. Master Roshi observes your potential. 'There's something special about this one...'"
            
            st.markdown(f"""
            <div style="
                background: rgba(0,0,0,0.3);
                border-left: 5px solid #FFD700;
                padding: 25px;
                border-radius: 15px;
                margin: 20px 0;
            ">
                <p style="color: white; font-size: 1.4em; line-height: 1.8; font-style: italic;">
                    "{story}"
                </p>
                <p style="color: #FFD700; margin-top: 20px; font-size: 1.2em;">
                    ⚔️ Power Level: {st.session_state.power_level} | Rank: {st.session_state.combat_tier}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Epic action input
            user_action = st.text_area(
                "🌀 WHAT IS YOUR ULTIMATE MOVE? 🌀",
                placeholder="e.g., 'I unleash a 100x Kaioken Kamehameha!' or 'I teleport behind the enemy and use Final Flash!'...",
                height=120,
                key="epic_action_input",
                help="Your words manifest reality itself!"
            )
            
            # Transform buttons with particle effects
            button_col1, button_col2 = st.columns(2)
            
            with button_col1:
                if st.button("⚡ EXECUTE ULTIMATE TECHNIQUE ⚡", key="execute_epic", use_container_width=True):
                    if user_action:
                        # Power calculations
                        power_gain = random.randint(300, 1000)
                        st.session_state.power_level += power_gain
                        st.session_state.spirit_bombs += 1
                        st.session_state.zenkai_boosts += 1
                        
                        # Ki mastery improvement
                        st.session_state.ki_mastery = min(100, st.session_state.ki_mastery + random.randint(1, 5))
                        
                        # Rank progression
                        if st.session_state.power_level >= 9000:
                            st.session_state.combat_tier = "Z+ RANK (GOD OF DESTRUCTION)"
                            st.session_state.saga_arc = "God of Destruction Arc"
                        elif st.session_state.power_level >= 8000:
                            st.session_state.combat_tier = "Z RANK (ULTRA INSTINCT)"
                            st.session_state.saga_arc = "Ultra Instinct Arc"
                        elif st.session_state.power_level >= 7000:
                            st.session_state.combat_tier = "S+ RANK (LEGENDARY)"
                            st.session_state.saga_arc = "Legendary Super Saiyan Arc"
                        elif st.session_state.power_level >= 6000:
                            st.session_state.combat_tier = "S RANK (GOD TIER)"
                            st.session_state.saga_arc = "Super Saiyan God Arc"
                        elif st.session_state.power_level >= 5000:
                            st.session_state.combat_tier = "A+ RANK (TRANSCENDENT)"
                            st.session_state.saga_arc = "Super Saiyan 3 Arc"
                        elif st.session_state.power_level >= 4000:
                            st.session_state.combat_tier = "A RANK (ELITE)"
                            st.session_state.saga_arc = "Super Saiyan 2 Arc"
                        elif st.session_state.power_level >= 3000:
                            st.session_state.combat_tier = "B+ RANK (ASCENDED)"
                            st.session_state.saga_arc = "Super Saiyan Arc"
                        elif st.session_state.power_level >= 2000:
                            st.session_state.combat_tier = "B RANK (ADVANCED)"
                            st.session_state.saga_arc = "Namek Arc"
                        elif st.session_state.power_level >= 1000:
                            st.session_state.combat_tier = "C RANK (WARRIOR)"
                            st.session_state.saga_arc = "Saiyan Arc"
                        
                        # Epic battle sequence
                        with st.spinner("🌀 CHARGING COSMIC ENERGY..."):
                            time.sleep(1)
                        with st.spinner("⚡ EXECUTING DIVINE TECHNIQUE..."):
                            time.sleep(1)
                        with st.spinner("💥 IMPACT DETECTED!"):
                            time.sleep(0.5)
                        
                        st.balloons()
                        st.snow()
                        
                        # Battle result
                        st.markdown(f"""
                        <div style="
                            background: linear-gradient(45deg, #FFD700, #FF4500);
                            padding: 30px;
                            border-radius: 20px;
                            text-align: center;
                            animation: pulse 0.5s infinite;
                            border: 3px solid white;
                            margin-top: 20px;
                        ">
                            <h1 style="color: white; font-size: 2.5em; text-shadow: 2px 2px 0 black;">
                                ⚡ ULTIMATE MOVE EXECUTED! ⚡
                            </h1>
                            <h2 style="color: white; font-size: 2em; margin: 20px 0;">
                                {user_action.upper()}
                            </h2>
                            <p style="color: white; font-size: 1.5em;">
                                POWER INCREASED BY {power_gain}! 🔥
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Random event
                        events = [
                            "💥 VEGETA: 'MY BULMA! WHAT HAVE YOU DONE TO MY BULMA?!'",
                            "✨ WHIS: 'Impressive. Lord Beerus might actually have a challenge.'",
                            "👑 KING KAI: 'THAT'S A 100x KAIOKEN?! YOUR BODY CAN'T HANDLE IT!'",
                            "🔥 FRIEZA: 'IMPOSSIBLE! HOW DID YOU BECOME A SUPER SAIYAN?!'",
                            "🌌 ZENO: 'WOW! THIS WARRIOR IS AMAZING! I SHOULD PROBABLY NOT ERASE THIS UNIVERSE!'",
                            "⚡ JIREN: 'Finally... a worthy opponent. Our battle will be legendary!'",
                            "🌀 GOKU: 'HEHEH... I WAS JUST PLAYING AROUND BEFORE. NOW I'M SERIOUS!'"
                        ]
                        
                        st.info(f"🎲 RANDOM ENCOUNTER: {random.choice(events)}")
                        st.success(f"✨ ZENKAI BOOST ACTIVATED! Power level multiplier: {st.session_state.zenkai_boosts}x! ✨")
                        
                        st.rerun()
            
            with button_col2:
                if st.button("🌀 MEDITATE & FOCUS ENERGY 🌀", key="meditate_epic", use_container_width=True):
                    meditation_gain = random.randint(50, 200)
                    st.session_state.power_level += meditation_gain
                    st.session_state.ki_mastery = min(100, st.session_state.ki_mastery + random.randint(2, 8))
                    
                    with st.spinner("🧘 CHANNELING INNER ENERGY..."):
                        time.sleep(2)
                    
                    st.success(f"✨ KI MASTERY INCREASED! +{meditation_gain} power! ✨")
                    st.rerun()
        
        with col2:
            # Character stats with animated bars
            st.markdown("""
            <div class="holographic-panel" style="
                padding: 30px;
                border-radius: 30px;
                margin-bottom: 30px;
            ">
                <h3 style="
                    color: #ff69b4;
                    font-size: 2.2em;
                    margin-bottom: 20px;
                    text-shadow: 0 0 20px deeppink;
                ">
                    👤 WARRIOR STATISTICS 👤
                </h3>
            """, unsafe_allow_html=True)
            
            # Power bar
            st.markdown(f"**🔥 POWER LEVEL**")
            st.progress(min(st.session_state.power_level / 10000, 1.0))
            
            # Ki mastery
            st.markdown(f"**💫 KI MASTERY**")
            st.progress(st.session_state.ki_mastery / 100)
            
            # Zenkai boost multiplier
            st.markdown(f"**⚡ ZENKAI BOOST**")
            st.progress(min(st.session_state.zenkai_boosts / 10, 1.0))
            
            # Spirit bombs
            st.markdown(f"**💎 SPIRIT BOMBS COLLECTED**")
            st.progress(min(st.session_state.spirit_bombs / 100, 1.0))
            
            # Achievement badges
            st.markdown("""
            <div style="
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 30px;
            ">
            """, unsafe_allow_html=True)
            
            badges = []
            if st.session_state.power_level >= 9000:
                badges.append(("👑", "God of Destruction", "#FFD700"))
            if st.session_state.spirit_bombs >= 10:
                badges.append(("💎", "Spirit Bomb Master", "#00FFFF"))
            if st.session_state.zenkai_boosts >= 5:
                badges.append(("⚡", "Zenkai God", "#FF4500"))
            if st.session_state.ki_mastery >= 80:
                badges.append(("🧘", "Ki Sage", "#00FF00"))  # FIXED: changed from balances to badges
            
            for icon, title, color in badges:
                st.markdown(f"""
                <div style="
                    background: {color}20;
                    border: 2px solid {color};
                    border-radius: 50px;
                    padding: 10px 20px;
                    display: inline-flex;
                    align-items: center;
                    gap: 10px;
                    backdrop-filter: blur(5px);
                ">
                    <span style="font-size: 1.5em;">{icon}</span>
                    <span style="color: {color}; font-weight: bold;">{title}</span>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Divine debug console
            st.session_state.show_debug = st.toggle(
                "🔮 AWAKEN COSMIC CONSCIOUSNESS 🔮",
                value=st.session_state.get('show_debug', False),
                help="Perceive the true nature of reality..."
            )
            
            if st.session_state.show_debug:
                st.markdown("""
                <div style="
                    background: rgba(0,0,0,0.9);
                    border: 2px solid #00ffff;
                    border-radius: 20px;
                    padding: 25px;
                    margin-top: 20px;
                    box-shadow: 0 0 30px rgba(0,255,255,0.3);
                ">
                    <h4 style="
                        color: #00ffff;
                        font-size: 1.8em;
                        margin-bottom: 20px;
                        text-align: center;
                        font-family: 'Orbitron', monospace;
                    ">
                        🌀 QUANTUM CONSCIOUSNESS MATRIX 🌀
                    </h4>
                """, unsafe_allow_html=True)
                
                col_json, col_meta = st.columns(2)
                
                with col_json:
                    st.json({
                        "power_level": st.session_state.power_level,
                        "combat_tier": st.session_state.combat_tier,
                        "spirit_bombs": st.session_state.spirit_bombs,
                        "zenkai_boosts": st.session_state.zenkai_boosts,
                        "ki_mastery": f"{st.session_state.ki_mastery}%",
                        "saga_arc": st.session_state.saga_arc,
                        "divine_interventions": st.session_state.divine_interventions
                    })
                
                with col_meta:
                    st.metric("Cosmic Alignment", f"{random.randint(85, 100)}%", "+12%")
                    st.metric("Destiny Threads", f"{random.randint(1000, 9999)}", f"+{random.randint(100, 500)}")
                    st.metric("Timeline Branches", f"{random.randint(50, 999)}", f"+{random.randint(10, 50)}")
                
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Epic ending button
        col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
        with col3:
            if st.button("🏁 TRANSCEND THIS SAGA 🏁", key="end_saga_divine", use_container_width=True):
                # Cinematic ending sequence
                with st.spinner("🌀 COMPRESSING 1000 YEARS OF MEMORIES..."):
                    time.sleep(1.5)
                with st.spinner("⚡ ARCHIVING LEGENDARY BATTLES..."):
                    time.sleep(1.5)
                with st.spinner("🌟 CALCULATING FINAL POWER LEVEL..."):
                    time.sleep(1.5)
                
                st.markdown(f"""
                <div style="
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: radial-gradient(circle, rgba(0,0,0,0.98), rgba(75,0,130,0.98));
                    z-index: 99999;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    animation: fadeIn 2s;
                ">
                    <h1 style="color: #FFD700; font-size: 6em; text-align: center; animation: pulse 1s infinite;">
                        ✨ LEGEND STATUS ✨
                    </h1>
                    <h2 style="color: white; font-size: 4em; text-align: center; margin: 40px 0;">
                        {st.session_state.combat_tier}
                    </h2>
                    <div style="display: flex; gap: 80px; margin: 60px 0;">
                        <div style="text-align: center;">
                            <p style="color: #FFD700; font-size: 1.5em;">FINAL POWER</p>
                            <p style="color: white; font-size: 4em; font-weight: bold;">{st.session_state.power_level}</p>
                        </div>
                        <div style="text-align: center;">
                            <p style="color: #FFD700; font-size: 1.5em;">SPIRIT BOMBS</p>
                            <p style="color: white; font-size: 4em; font-weight: bold;">{st.session_state.spirit_bombs}</p>
                        </div>
                        <div style="text-align: center;">
                            <p style="color: #FFD700; font-size: 1.5em;">ZENKAI BOOSTS</p>
                            <p style="color: white; font-size: 4em; font-weight: bold;">{st.session_state.zenkai_boosts}</p>
                        </div>
                    </div>
                    <p style="color: #00ffff; font-size: 2em; margin-top: 60px;">
                        "Your legend will echo through eternity..."
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                time.sleep(4)
                
                # Reset for next adventure
                st.session_state.game_started = False
                st.session_state.power_level = random.randint(1000, 5000)
                st.session_state.spirit_bombs = 0
                st.session_state.zenkai_boosts = 0
                st.session_state.ki_mastery = random.randint(1, 50)
                st.session_state.combat_tier = "E Rank"
                st.session_state.saga_arc = "Origin Arc"
                st.rerun()

if __name__ == "__main__":
    main()