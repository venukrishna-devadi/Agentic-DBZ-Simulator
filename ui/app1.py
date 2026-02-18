# ui/app_dbz_ultimate.py
"""
⚡ DRAGON BALL Z SAGA SIMULATOR - ULTIMATE EDITION ⚡
The most epic DBZ-themed UI with 3D effects, power level visualizers, 
transformation sequences, and dynamic battle animations!
"""

import sys
import os
from pathlib import Path
import uuid
import time
import threading
import queue
from datetime import datetime
# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
from datetime import datetime
from typing import List, Dict, Any, Optional
import json
import time
import random
import numpy as np
import base64
import uuid

from config import Config
from schemas.state import GameState, PlanStep, SceneType
from runners.hitl_runner import create_hitl_runner
from graph.builder import create_saga_graph
from langchain_core.messages import HumanMessage, AIMessage

# =========================================================
# INITIALIZATION
# =========================================================
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
    if "pending_tool_calls" not in st.session_state:
        st.session_state.pending_tool_calls = []
    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None
    if "game_started" not in st.session_state:
        st.session_state.game_started = False
    
    # DBZ-specific stats
    if "power_level" not in st.session_state:
        st.session_state.power_level = 1000
    if "zenkai_boosts" not in st.session_state:
        st.session_state.zenkai_boosts = 0
    if "transformations" not in st.session_state:
        st.session_state.transformations = ["Base Form"]
    if "current_form" not in st.session_state:
        st.session_state.current_form = "Base Form"
    if "spirit_bombs" not in st.session_state:
        st.session_state.spirit_bombs = 0
    if "saga_progress" not in st.session_state:
        st.session_state.saga_progress = 0
    if "battle_power" not in st.session_state:
        st.session_state.battle_power = 0
    if "ki_charge" not in st.session_state:
        st.session_state.ki_charge = 100

# =========================================================
# CSS INJECTION (Your existing CSS - unchanged)
# =========================================================
def inject_dbz_css():
    """Inject mind-blowing DBZ-themed CSS"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bangers&family=Black+Ops+One&family=Kanit:wght@300;400;600;800&family=Orbitron:wght@400;700;900&display=swap');
    
    /* ===== BASE STYLES ===== */
    .stApp {
        background: #0A0F1E !important;
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(255, 100, 0, 0.1) 0%, transparent 30%),
            radial-gradient(circle at 80% 70%, rgba(255, 215, 0, 0.1) 0%, transparent 40%),
            radial-gradient(circle at 40% 50%, rgba(255, 50, 0, 0.05) 0%, transparent 50%),
            repeating-linear-gradient(45deg, rgba(255, 215, 0, 0.02) 0px, rgba(255, 215, 0, 0.02) 2px, transparent 2px, transparent 10px) !important;
    }
    
    /* ===== POWER LEVEL METER ===== */
    .power-level-container {
        background: #1A1F30;
        border: 2px solid #FFD700;
        border-radius: 50px;
        padding: 5px;
        margin: 15px 0;
        box-shadow: 0 0 30px rgba(255, 215, 0, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .power-level-bar {
        height: 30px;
        background: linear-gradient(90deg, #FF4500, #FFD700, #00FF00);
        border-radius: 50px;
        width: 0%;
        transition: width 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        position: relative;
    }
    
    .power-level-bar::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(90deg, 
            rgba(255,255,255,0.2) 0%, 
            rgba(255,255,255,0.5) 50%,
            rgba(255,255,255,0.2) 100%);
        animation: shimmer 2s infinite;
    }
    
    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .power-level-text {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.5em;
        font-weight: 900;
        color: #FFD700;
        -webkit-text-stroke: 1px #A12C00;
        text-shadow: none;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        z-index: 2;
    }
    
    /* ===== DRAGON BALL HEADER ===== */
    .dbz-header {
        text-align: center;
        padding: 30px;
        background: rgba(0, 0, 0, 0.5);
        border-radius: 30px;
        margin-bottom: 30px;
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 215, 0, 0.3);
    }
    
    .dbz-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 215, 0, 0.2) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    
    .dbz-title {
        font-family: 'Bangers', cursive;
        font-size: 5em;
        background: linear-gradient(45deg, #FFD700, #FF4500, #FF1493);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        -webkit-text-stroke: 2px #1c0000;
        text-shadow: none;
        letter-spacing: 4px;
        animation: titlePulse 2s ease-in-out infinite;
        position: relative;
        z-index: 2;
    }
    
    @keyframes titlePulse {
        0%, 100% { transform: scale(1); filter: brightness(1); }
        50% { transform: scale(1.05); filter: brightness(1.3); }
    }
    
    .dbz-subtitle {
        font-family: 'Black Ops One', cursive;
        font-size: 2em;
        color: #FFF;
        -webkit-text-stroke: 1px #A12C00;
        text-shadow: none;
        margin-top: -10px;
    }
    
    /* ===== SAGA CARDS ===== */
    .saga-card {
        background: rgba(26, 31, 48, 0.8);
        backdrop-filter: blur(10px);
        border: 2px solid #FFD700;
        border-radius: 20px;
        padding: 25px;
        margin: 20px 0;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    .saga-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(255, 215, 0, 0.3);
        border-color: #FF4500;
    }
    
    .saga-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, 
            transparent, 
            rgba(255, 215, 0, 0.2), 
            transparent);
        animation: scan 3s infinite;
    }
    
    @keyframes scan {
        to { left: 200%; }
    }
    
    /* ===== KI ENERGY BUTTONS ===== */
    .ki-button {
        background: linear-gradient(135deg, #FFD700, #FF4500);
        border: none;
        color: white;
        font-family: 'Kanit', sans-serif;
        font-weight: 800;
        font-size: 1.2em;
        padding: 15px 30px;
        border-radius: 50px;
        position: relative;
        overflow: hidden;
        cursor: pointer;
        transition: all 0.3s;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 5px 20px rgba(255, 69, 0, 0.5);
    }
    
    .ki-button::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.8) 0%, transparent 70%);
        animation: rotate 4s linear infinite;
        opacity: 0.3;
    }
    
    .ki-button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 30px rgba(255, 215, 0, 0.8);
    }
    
    .ki-button:active {
        transform: scale(0.95);
    }
    
    /* ===== POWER LEVEL SPARKLES ===== */
    .sparkle {
        position: fixed;
        width: 4px;
        height: 4px;
        background: #FFD700;
        border-radius: 50%;
        pointer-events: none;
        animation: sparkleFloat 3s infinite;
        box-shadow: 0 0 15px #FFD700;
    }
    
    @keyframes sparkleFloat {
        0% { transform: translateY(0) rotate(0deg); opacity: 1; }
        100% { transform: translateY(-100vh) rotate(720deg); opacity: 0; }
    }
    
    /* ===== TRANSFORMATION AURA ===== */
    .aura-effect {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 50%;
        animation: auraPulse 1.5s infinite;
        pointer-events: none;
    }
    
    @keyframes auraPulse {
        0% { box-shadow: 0 0 20px 5px #FFD700; }
        50% { box-shadow: 0 0 40px 15px #FF4500; }
        100% { box-shadow: 0 0 20px 5px #FFD700; }
    }
    
    /* ===== BATTLE DAMAGE EFFECT ===== */
    .damage-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle, rgba(255, 0, 0, 0.1) 0%, transparent 70%);
        pointer-events: none;
        animation: damageFlash 0.5s;
        z-index: 9999;
    }
    
    @keyframes damageFlash {
        0%, 100% { opacity: 0; }
        50% { opacity: 0.5; }
    }
    
    /* ===== SCOUTER METER ===== */
    .scouter-panel {
        background: #1A2F3F;
        border: 3px solid #00FF00;
        border-radius: 20px;
        padding: 20px;
        margin: 20px 0;
        box-shadow: 0 0 30px rgba(0, 255, 0, 0.3);
        position: relative;
    }
    
    .scouter-panel::before {
        content: 'SCOUTER READING';
        position: absolute;
        top: -10px;
        left: 20px;
        background: #1A2F3F;
        padding: 0 10px;
        color: #00FF00;
        -webkit-text-stroke: 0.5px #005a00;
        font-family: 'Orbitron', monospace;
        font-size: 0.8em;
    }
    
    .scouter-number {
        font-family: 'Orbitron', monospace;
        font-size: 3em;
        color: #00FF00;
        -webkit-text-stroke: 1.5px #005a00;
        text-shadow: none;
        text-align: center;
        animation: scouterPulse 1s infinite;
    }
    
    @keyframes scouterPulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    /* ===== KAMEHAMEHA WAVE ===== */
    .kamehameha {
        position: relative;
        height: 200px;
        background: linear-gradient(90deg, #FFD700, #FF4500, #FF1493);
        border-radius: 100px;
        filter: blur(20px);
        animation: wavePulse 2s infinite;
    }
    
    @keyframes wavePulse {
        0%, 100% { transform: scaleX(1); opacity: 0.5; }
        50% { transform: scaleX(1.2); opacity: 0.8; }
    }
    
    /* ===== DRAGON BALL COLLECTION ===== */
    .dragon-ball {
        display: inline-block;
        width: 30px;
        height: 30px;
        background: radial-gradient(circle at 30% 30%, #FFD700, #FF4500);
        border-radius: 50%;
        margin: 5px;
        animation: ballGlow 2s infinite;
        border: 2px solid white;
    }
    
    .dragon-ball.complete {
        background: radial-gradient(circle at 30% 30%, #FFD700, #FF0000);
        box-shadow: 0 0 30px #FFD700;
    }
    
    @keyframes ballGlow {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.5); }
    }
    
    /* ===== ZENKAI BOOST EFFECT ===== */
    .zenkai-flash {
        animation: zenkaiFlash 1s;
    }
    
    @keyframes zenkaiFlash {
        0% { filter: brightness(1); }
        50% { filter: brightness(3); }
        100% { filter: brightness(1); }
    }
    
    /* ===== HYPERBOLIC TIME CHAMBER ===== */
    .time-chamber {
        background: linear-gradient(135deg, #FFF, #AAA);
        border: 2px solid white;
        border-radius: 20px;
        padding: 30px;
        animation: chamberPulse 10s infinite;
    }
    
    @keyframes chamberPulse {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.2); }
    }
    
    /* ===== CUSTOM SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1A1F30;
        border: 1px solid #FFD700;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #FFD700, #FF4500);
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #FF4500, #FFD700);
    }
    
    /* ===== SCENE ANIMATIONS ===== */
    .scene-text {
        font-family: 'Kanit', sans-serif;
        font-size: 1.2em;
        line-height: 1.8;
        color: #FFF;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.5);
        animation: fadeInUp 0.5s;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* ===== POWER LEVEL CLASSES ===== */
    .power-saiyan { color: #FFD700; -webkit-text-stroke: 1px #B38600; }
    .power-saiyan2 { color: #FF4500; -webkit-text-stroke: 1px #A12C00; }
    .power-saiyan3 { color: #FF1493; -webkit-text-stroke: 1px #930058; }
    .power-god { color: #FF00FF; -webkit-text-stroke: 1px #A300A3; }
    .power-blue { color: #00FFFF; -webkit-text-stroke: 1px #007C7C; }
    .power-ultra { color: #FFFFFF; -webkit-text-stroke: 1.5px #007C7C; text-shadow: none; }
    
    /* ===== BUTTON STYLES ===== */
    .stButton > button {
        background: linear-gradient(135deg, #FFD700, #FF4500) !important;
        color: white !important;
        font-family: 'Kanit', sans-serif !important;
        font-weight: 600 !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 15px 30px !important;
        transition: all 0.3s !important;
        text-transform: uppercase !important;
        letter-spacing: 2px !important;
        box-shadow: 0 5px 20px rgba(255, 69, 0, 0.5) !important;
        -webkit-text-stroke: 0.5px #000;
    }
    
    .stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 10px 30px rgba(255, 215, 0, 0.8) !important;
    }
    
    .stButton > button:active {
        transform: scale(0.95) !important;
    }
    
    /* ===== SELECT BOX ===== */
    .stSelectbox > div > div {
        background: #1A1F30 !important;
        border: 2px solid #FFD700 !important;
        color: white !important;
        border-radius: 10px !important;
    }
    
    /* ===== METRICS ===== */
    [data-testid="stMetricValue"] {
        font-family: 'Orbitron', monospace !important;
        font-size: 2.5em !important;
        color: #FFD700 !important;
        -webkit-text-stroke: 1px #A12C00;
        text-shadow: none !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'Kanit', sans-serif !important;
        font-size: 1.1em !important;
        color: #AAA !important;
        text-shadow: 1px 1px 2px #000;
    }
    
    /* ===== PROGRESS BARS ===== */
    .stProgress > div > div {
        background: linear-gradient(90deg, #FFD700, #FF4500) !important;
        height: 10px !important;
        border-radius: 5px !important;
    }
    
    /* ===== EXPANDERS ===== */
    .streamlit-expanderHeader {
        background: #1A1F30 !important;
        border: 2px solid #FFD700 !important;
        color: white !important;
        border-radius: 10px !important;
        font-family: 'Kanit', sans-serif !important;
    }
    
    .streamlit-expanderContent {
        background: #0A0F1E !important;
        border: 2px solid #FFD700 !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
    }
    </style>
    
    <script>
    // Create floating sparkles
    (function() {
        for(let i = 0; i < 50; i++) {
            const sparkle = document.createElement('div');
            sparkle.className = 'sparkle';
            sparkle.style.left = Math.random() * 100 + '%';
            sparkle.style.top = Math.random() * 100 + '%';
            sparkle.style.animationDelay = Math.random() * 2 + 's';
            sparkle.style.width = (Math.random() * 6 + 2) + 'px';
            sparkle.style.height = sparkle.style.width;
            document.body.appendChild(sparkle);
        }
    })();
    </script>
    """, unsafe_allow_html=True)

# =========================================================
# UI COMPONENTS (Your existing display functions)
# =========================================================
def display_dbz_header():
    """Display epic DBZ header with power meter"""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="dbz-header">
            <h1 class="dbz-title">⚡ DRAGON BALL ⚡</h1>
            <h2 class="dbz-subtitle">SAGA SIMULATOR</h2>
            <div style="margin-top: 30px;">
                <div class="dragon-ball complete"></div>
                <div class="dragon-ball complete"></div>
                <div class="dragon-ball complete"></div>
                <div class="dragon-ball"></div>
                <div class="dragon-ball"></div>
                <div class="dragon-ball"></div>
                <div class="dragon-ball"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def display_power_level(power: int, max_power: int = 10000):
    """Display animated power level meter"""
    percentage = min(100, (power / max_power) * 100)
    
    if power >= 9000:
        tier_class = "power-saiyan"
        message = "IT'S OVER 9000!!!"
    elif power >= 5000:
        tier_class = "power-saiyan2"
        message = "SUPER SAIYAN!"
    elif power >= 3000:
        tier_class = "power-saiyan3"
        message = "ASCENDED!"
    elif power >= 1000:
        tier_class = "power-god"
        message = "ELITE WARRIOR"
    else:
        tier_class = "power-blue"
        message = "RISING WARRIOR"
    
    st.markdown(f"""
    <div class="power-level-container">
        <div class="power-level-bar" style="width: {percentage}%;"></div>
        <div class="power-level-text">{power:,}</div>
    </div>
    <div style="text-align: center; margin-top: -10px; margin-bottom: 20px;">
        <span class="{tier_class}" style="font-family: 'Orbitron'; font-size: 1.2em;">{message}</span>
    </div>
    """, unsafe_allow_html=True)

def display_scouter_meter(value: int, label: str, color: str = "#00FF00"):
    """Display scouter-style meter"""
    stroke_color = "#005a00" if color == "#00FF00" else "#B38600"
    st.markdown(f"""
    <div class="scouter-panel" style="border-color: {color}; box-shadow: 0 0 30px {color}33;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="color: #AAA; font-family: 'Orbitron'; text-shadow: 1px 1px 2px #000;">{label}</span>
            <span class="scouter-number" style="color: {color}; -webkit-text-stroke: 1.5px {stroke_color};">{value:,}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_transformations(current_form: str, available_forms: List[str]):
    """Display transformation buttons"""
    st.markdown("<h3 style='color: #FFD700; font-family: Bangers; -webkit-text-stroke: 1.5px #2A0000;'>🌀 TRANSFORMATIONS</h3>", unsafe_allow_html=True)
    
    cols = st.columns(len(available_forms))
    for i, form in enumerate(available_forms):
        with cols[i]:
            if st.button(form, key=f"transform_{i}", use_container_width=True):
                if form != current_form:
                    st.balloons()
                    st.session_state.current_form = form
                    if form == "Super Saiyan":
                        st.session_state.power_level += 5000
                    elif form == "Super Saiyan 2":
                        st.session_state.power_level += 10000
                    elif form == "Super Saiyan 3":
                        st.session_state.power_level += 20000
                    elif form == "Super Saiyan God":
                        st.session_state.power_level += 50000
                    st.rerun()

def display_battle_scene(player_power: int, enemy_power: int):
    """Display animated battle scene"""
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div style="text-align: center;">
            <h3 style="color: #00FFFF; -webkit-text-stroke: 1px #007C7C;">YOU</h3>
            <div class="aura-effect" style="position: relative; width: 100px; height: 100px; margin: 0 auto;"></div>
            <span class="scouter-number">{player_power}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center;">
            <h1 style="color: #FFD700; font-size: 3em; -webkit-text-stroke: 1.5px #2A0000;">⚡ VS ⚡</h1>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="text-align: center;">
            <h3 style="color: #FF4500; -webkit-text-stroke: 1px #A12C00;">ENEMY</h3>
            <div class="aura-effect" style="position: relative; width: 100px; height: 100px; margin: 0 auto; border-color: #FF4500;"></div>
            <span class="scouter-number" style="color: #FF4500; -webkit-text-stroke: 1px #A12C00;">{enemy_power}</span>
        </div>
        """, unsafe_allow_html=True)

def display_dbz_scene(game_state):
    """Display current scene with DBZ styling"""
    if not game_state or not hasattr(game_state, 'messages') or not game_state.messages:
        return
    
    from langchain_core.messages import AIMessage
    
    # Get the latest AI message that has content
    latest_scene = None
    for msg in reversed(game_state.messages):
        if isinstance(msg, AIMessage) and msg.content and len(msg.content) > 10:
            latest_scene = msg
            break
    
    if not latest_scene:
        return
    
    scene_counter = getattr(game_state, 'scene_counter', 1)
    saga_name = getattr(game_state, 'saga_name', 'Dragon Ball')
    
    # Update session state power level
    st.session_state.power_level = game_state.player_stats.get('power_level', 1000)
    
    st.markdown(f"""
    <div class="saga-card">
        <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
            <span style="color: #FFD700; font-family: 'Bangers'; font-size: 1.5em; -webkit-text-stroke: 1px #2A0000;">
                ⚡ SCENE {scene_counter}
            </span>
            <span style="color: #AAA; font-family: 'Orbitron'; text-shadow: 1px 1px 2px #000;">
                {saga_name} SAGA
            </span>
        </div>
        <div class="scene-text">
            {latest_scene.content}
        </div>
        <div style="margin-top: 20px; text-align: right;">
            <span style="color: #FFD700; font-family: 'Kanit'; -webkit-text-stroke: 0.5px #2A0000;">
                Power Level: {st.session_state.power_level:,}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_dbz_choices(choices: List[str], on_choice):
    """Display choices as DBZ-style buttons"""
    st.markdown("<h3 style='color: #FFD700; font-family: Bangers; -webkit-text-stroke: 1.5px #2A0000; margin: 30px 0 20px;'>⚡ CHOOSE YOUR PATH</h3>", unsafe_allow_html=True)
    
    for i, choice in enumerate(choices):
        if st.button(f"⚡ {choice}", key=f"dbz_choice_{i}", use_container_width=True):
            on_choice(choice)
            st.balloons()

def display_dbz_stats(game_state):
    """Display DBZ-themed stats panel"""
    stats = getattr(game_state, 'player_stats', {})
    
    # Update session state from game state
    st.session_state.power_level = stats.get('power_level', 1000)
    st.session_state.zenkai_boosts = stats.get('zenkai_boosts', 0)
    st.session_state.spirit_bombs = stats.get('spirit_bombs', 0)
    st.session_state.current_form = stats.get('current_form', 'Base Form')
    st.session_state.transformations = stats.get('transformations', ['Base Form'])
    
    # Main stats grid
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Power Level", f"{st.session_state.power_level:,}")
        st.metric("Zenkai Boosts", st.session_state.zenkai_boosts)
        st.metric("Spirit Bombs", st.session_state.spirit_bombs)
    
    with col2:
        st.metric("Current Form", st.session_state.current_form)
        st.metric("Ki Charge", f"{st.session_state.ki_charge}%")
        st.metric("Saga Progress", f"{st.session_state.saga_progress}%")
    
    # Power level bar
    display_power_level(st.session_state.power_level)
    
    # Scouter readings
    display_scouter_meter(stats.get('ki_mastery', 0), "KI MASTERY", "#FFD700")
    display_scouter_meter(stats.get('level', 1), "WARRIOR LEVEL", "#00FFFF")
    
    # Items
    items = stats.get('items', [])
    if items:
        st.markdown("<h3 style='color: #FFD700; font-family: Bangers; -webkit-text-stroke: 1.5px #2A0000;'>📦 SENZU BEANS & ITEMS</h3>", unsafe_allow_html=True)
        for item in items:
            st.markdown(f"<p style='color: #FFF; margin: 5px 0; text-shadow: 1px 1px 2px #000;'>• {item}</p>", unsafe_allow_html=True)

def display_dbz_welcome():
    """Display epic DBZ welcome screen"""
    st.markdown("""
    <div class="saga-card" style="text-align: center;">
        <h2 style="color: #FFD700; font-family: 'Bangers'; font-size: 3em; -webkit-text-stroke: 1.5px #2A0000;">WELCOME, WARRIOR!</h2>
        <div style="width: 100px; height: 4px; background: linear-gradient(90deg, #FFD700, #FF4500); margin: 20px auto;"></div>
        <p style="color: #FFF; font-size: 1.3em; font-family: 'Kanit'; text-shadow: 1px 1px 2px #000;">
            Your journey begins now. Choose your saga and unleash your inner Saiyan!
        </p>
    </div>
    
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 40px 0;">
        <div class="saga-card" style="text-align: center;">
            <h3 style="color: #FFD700; -webkit-text-stroke: 1px #2A0000;">⚔️ POWER PROGRESSION</h3>
            <p style="color: #AAA; text-shadow: 1px 1px 2px #000;">Train, fight, and transcend your limits</p>
        </div>
        <div class="saga-card" style="text-align: center;">
            <h3 style="color: #FFD700; -webkit-text-stroke: 1px #2A0000;">🌀 MYSTICAL QUEST</h3>
            <p style="color: #AAA; text-shadow: 1px 1px 2px #000;">Discover ancient secrets and divine powers</p>
        </div>
        <div class="saga-card" style="text-align: center;">
            <h3 style="color: #FFD700; -webkit-text-stroke: 1px #2A0000;">🏆 TOURNAMENT ARC</h3>
            <p style="color: #AAA; text-shadow: 1px 1px 2px #000;">Compete against the strongest warriors</p>
        </div>
        <div class="saga-card" style="text-align: center;">
            <h3 style="color: #FFD700; -webkit-text-stroke: 1px #2A0000;">🔥 SURVIVAL SAGA</h3>
            <p style="color: #AAA; text-shadow: 1px 1px 2px #000;">Overcome impossible odds and protect Earth</p>
        </div>
    </div>
    
    <div style="text-align: center;">
        <div class="dragon-ball complete"></div>
        <div class="dragon-ball complete"></div>
        <div class="dragon-ball complete"></div>
        <div class="dragon-ball complete"></div>
        <div class="dragon-ball complete"></div>
        <div class="dragon-ball complete"></div>
        <div class="dragon-ball complete"></div>
        <p style="color: #FFD700; margin-top: 20px; font-family: 'Bangers'; -webkit-text-stroke: 1px #2A0000;">SUMMON THE DRAGON!</p>
    </div>
    """, unsafe_allow_html=True)

def display_dbz_sidebar():
    """Display DBZ-themed sidebar with working callbacks"""
    with st.sidebar:
        st.markdown("""
        <h2 style="color: #FFD700; font-family: 'Bangers'; text-align: center; -webkit-text-stroke: 1px #2A0000;">
            ⚡ DBZ MENU ⚡
        </h2>
        """, unsafe_allow_html=True)
        
        st.markdown("<hr style='border-color: #FFD700;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #FFD700; -webkit-text-stroke: 1px #2A0000;'>🆕 NEW SAGA</h3>", unsafe_allow_html=True)
        
        saga_name = st.selectbox(
            "Choose Your Saga",
            ["Saiyan Saga", "Frieza Saga", "Cell Saga", "Buu Saga", "Tournament of Power"],
            key="saga_select_dbz"
        )
        
        player_name = st.text_input("Warrior Name", value="Goku")
        
        difficulty = st.select_slider(
            "Difficulty",
            options=["Easy", "Normal", "Hard", "Legendary"],
            value="Normal"
        )
        
        if st.button("⚡ BEGIN TRAINING ⚡", use_container_width=True):
            start_new_game(saga_name, player_name, difficulty, enable_hitl=True)
        
        st.markdown("<hr style='border-color: #FFD700;'>", unsafe_allow_html=True)
        
        if st.session_state.get('game_started', False):
            st.markdown("<h3 style='color: #FFD700; -webkit-text-stroke: 1px #2A0000;'>⚔️ CURRENT POWER</h3>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div style="background: #1A1F30; border: 1px solid #FFD700; border-radius: 10px; padding: 15px;">
                <p style="color: #FFD700; -webkit-text-stroke: 0.5px #2A0000;">Power: {st.session_state.power_level}</p>
                <p style="color: #00FFFF; -webkit-text-stroke: 0.5px #007C7C;">Form: {st.session_state.current_form}</p>
                <p style="color: #FF4500; -webkit-text-stroke: 0.5px #A12C00;">Zenkai: x{st.session_state.zenkai_boosts}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<hr style='border-color: #FFD700;'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 SAVE", use_container_width=True):
                save_game()
        with col2:
            if st.button("📂 LOAD", use_container_width=True):
                load_game()
        
        st.markdown("<hr style='border-color: #FFD700;'>", unsafe_allow_html=True)
        
        st.session_state.show_debug = st.checkbox("👁️ SCOUTER DEBUG", value=False)

def display_kamehameha_charger():
    """Interactive Kamehameha charging mini-game"""
    st.markdown("<h3 style='color: #FFD700; font-family: Bangers; -webkit-text-stroke: 1.5px #2A0000;'>🌀 KAMEHAMEHA CHARGE</h3>", unsafe_allow_html=True)
    
    charge = st.session_state.ki_charge
    
    st.markdown(f"""
    <div class="power-level-container">
        <div class="power-level-bar" style="width: {charge}%;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⚡ CHARGE", use_container_width=True):
            st.session_state.ki_charge = min(100, charge + random.randint(10, 30))
            st.rerun()
    with col2:
        if st.button("🔥 FIRE", use_container_width=True):
            if charge >= 100:
                st.balloons()
                st.markdown('<div class="kamehameha"></div>', unsafe_allow_html=True)
                st.session_state.power_level += 5000
                st.session_state.ki_charge = 0
                time.sleep(1)
                st.rerun()
            else:
                st.warning("Not enough ki!")
    with col3:
        if st.button("🌀 MAX", use_container_width=True):
            st.session_state.ki_charge = 100
            st.rerun()

def display_hitl_approval():
    """Display HITL approval interface when tools are requested"""
    st.markdown("""
    <div class="saga-card" style="border-color: #FF4500;">
        <h3 style="color: #FF4500; text-align: center;">⏸️ TOOL USAGE REQUESTED</h3>
    """, unsafe_allow_html=True)
    
    pending_calls = st.session_state.get('pending_tool_calls', [])
    
    for i, tc in enumerate(pending_calls, 1):
        st.code(f"{i}) {tc.get('name')}({tc.get('args', {})})", language="json")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ APPROVE TOOLS", use_container_width=True):
            runner = st.session_state.hitl_runner
            result = runner.approve_tools()
            if result["success"]:
                st.session_state.game_state = result["final_state"]
            st.session_state.pending_tool_calls = []
            st.rerun()
    
    with col2:
        if st.button("❌ DENY TOOLS", use_container_width=True):
            runner = st.session_state.hitl_runner
            result = runner.reject_tools()
            if result["success"]:
                st.session_state.game_state = result["final_state"]
            st.session_state.pending_tool_calls = []
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# GAME LOGIC FUNCTIONS
# =========================================================

def start_new_game(saga_name: str, player_name: str, difficulty: str = "Normal", enable_hitl: bool = True):
    """
    🎮 Start a new game by combining robust graph execution with complete state initialization.
    - Uses threading with a timeout to prevent the UI from freezing (from Option A).
    - Initializes a full, explicit GameState to prevent future errors (from Option B).
    - Provides a fallback demo scene if the graph fails or times out (from Option A).
    """
    # 1. Clear previous game states (Good practice from both)
    st.session_state.pending_tool_calls = []
    st.session_state.last_updates = []
    st.session_state.last_error = None
    st.session_state.game_started = True

    # 2. Generate unique thread ID for checkpointing (Good practice from both)
    thread_id = f"saga_{uuid.uuid4().hex[:8]}"
    st.session_state.thread_id = thread_id
    st.session_state.config = {"configurable": {"thread_id": thread_id}}

    # 3. Determine starting power based on difficulty (Good practice from both)
    base_power = {
        "Easy": 3000,
        "Normal": 1000,
        "Hard": 500,
        "Legendary": 100
    }.get(difficulty, 1000)

    # 4. BEST OF B: Create a complete and explicit initial game state.
    # This prevents potential KeyErrors later if other parts of the app
    # expect fields like 'ki_mastery' to exist.
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
        player_stats={
            "power_level": base_power,
            "health": 100,
            "max_health": 100,
            "ki_mastery": 30,  # Explicitly defined
            "spirit_bombs": 0,
            "zenkai_boosts": 0,
            "level": 1,
            "experience": 0,
            "items": ["Senzu Bean"],
            "transformations": ["Base Form"],
            "techniques": ["Basic Ki Blast"],
            "current_form": "Base Form",
            "momentum": 0.5
        },
        world_flags={
            "mentor_met": False,
            "training_started": False,
            "first_battle": False,
            "transformation_unlocked": False
        }
    )

    # 5. Add the initial user message to kick off the AI (Good practice from both)
    initial_message = HumanMessage(
        content=f"Start the {saga_name}. I am {player_name}, ready to begin my journey."
    )
    st.session_state.game_state.add_message(initial_message)

    # 6. BEST OF A: Run the graph asynchronously with a timeout.
    # This is crucial for a good user experience in Streamlit, as a direct
    # .invoke() call would freeze the entire UI.
    with st.spinner("🌀 SUMMONING SHENRON... The saga is about to begin!"):
        result = None
        try:
            runner = st.session_state.hitl_runner
            runner.current_thread_id = thread_id

            result_queue = queue.Queue()

            def run_graph_in_thread():
                try:
                    # Use the custom runner method from Option A
                    res = runner.run_with_hitl(st.session_state.game_state)
                    result_queue.put(("success", res))
                except Exception as e:
                    result_queue.put(("error", str(e)))

            graph_thread = threading.Thread(target=run_graph_in_thread)
            graph_thread.daemon = True
            graph_thread.start()
            graph_thread.join(timeout=15) # Generous 15-second timeout

            if graph_thread.is_alive():
                # Timeout occurred
                st.error("⏰ The Z-Fighters are taking too long to assemble... (AI response timed out).")
                result = {"success": False, "error": "timeout"}
            else:
                # Thread finished, get the result
                status, data = result_queue.get_nowait()
                if status == "success":
                    result = data
                else:
                    st.error(f"💥 A powerful ki blast disrupted the connection! (Graph Error: {data})")
                    result = {"success": False, "error": data}

        except Exception as e:
            st.error(f"💥 A powerful ki blast disrupted the connection! (Error: {str(e)})")
            import traceback
            traceback.print_exc()
            result = {"success": False, "error": str(e)}

        # 7. Handle the result, with a robust fallback mode (from Option A)
        if result and result.get("success"):
            if result.get("final_state"):
                st.session_state.game_state = result["final_state"]
            if result.get("interrupted", False):
                st.session_state.pending_tool_calls = result.get("pending_tool_calls", [])
            st.success("✨ The saga begins!")
        else:
            # Fallback mode - but use the actual saga name!
            st.warning("Using Capsule Corp. backup generator... (Fallback Mode)")
            
            # Create a more dynamic fallback based on the chosen saga
            saga_intros = {
                "Saiyan Saga": "Vegeta and Nappa are approaching Earth!",
                "Frieza Saga": "The Namekian Dragon Balls have been detected!",
                "Cell Saga": "The Androids have been sighted in South City!",
                "Buu Saga": "A strange magical energy is awakening!",
                "Tournament of Power": "The multiverse tournament is about to begin!"
            }
            
            intro = saga_intros.get(saga_name, "A new threat emerges!")
            
            demo_scene = AIMessage(content=(
                f"The {saga_name} begins! {player_name} stands at the crossroads of destiny.\n\n"
                f"{intro}\n\n"
                f"Your training starts now, warrior! What will you do?\n\n"
                f"1. Train in the Hyperbolic Time Chamber\n"
                f"2. Seek guidance from King Kai\n"
                f"3. Gather the Z-fighters\n"
                f"4. Scout the area for enemies"
            ))
            st.session_state.game_state.add_message(demo_scene)

    # Rerun to update the UI with the new scene
    time.sleep(1) # Brief pause to let user read messages
    st.rerun()


def reset_game():
    """Reset the current game"""
    st.session_state.game_started = False
    st.session_state.game_state = GameState()
    st.session_state.pending_tool_calls = []
    st.session_state.thread_id = None
    st.session_state.power_level = 1000
    st.session_state.current_form = "Base Form"
    st.session_state.zenkai_boosts = 0
    st.session_state.spirit_bombs = 0
    st.rerun()

def save_game():
    """Save the current game state"""
    if not st.session_state.get('game_state'):
        st.sidebar.error("No game to save!")
        return
    
    try:
        game_data = st.session_state.game_state.to_serializable()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dbz_save_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(game_data, f, indent=2)
        
        st.sidebar.success(f"Game saved to {filename}")
    except Exception as e:
        st.sidebar.error(f"Save failed: {e}")

def load_game():
    """Load a saved game state"""
    try:
        import glob
        save_files = glob.glob("dbz_save_*.json")
        
        if not save_files:
            st.sidebar.warning("No save files found!")
            return
        
        # Load the most recent save
        latest_save = max(save_files, key=os.path.getctime)
        
        with open(latest_save, "r") as f:
            game_data = json.load(f)
        
        st.session_state.game_state = GameState.from_serializable(game_data)
        st.session_state.game_started = True
        st.sidebar.success(f"Game loaded from {latest_save}")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Load failed: {e}")

def extract_choices_from_state(game_state):
    """Extract available choices from the game state"""
    if not game_state or not game_state.messages:
        return []
    
    from langchain_core.messages import AIMessage
    
    # Look for choices in the last AI message
    for msg in reversed(game_state.messages):
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
            
            # Try the "CHOOSE YOUR PATH" format
            if "CHOOSE YOUR PATH" in content:
                lines = content.split('\n')
                for line in lines:
                    if '⚡' in line and len(line.strip()) > 5:
                        choice = line.replace('⚡', '').strip()
                        if choice and len(choice) < 100:
                            return [choice]
            
            break
    
    # Fallback to default DBZ choices
    return [
        "Train in 100x Gravity",
        "Meditate with King Kai",
        "Fight in the Tournament",
        "Seek the Dragon Balls",
        "Enter Hyperbolic Time Chamber"
    ]
def process_choice(self, state: GameState, choice: str, thread_id: str) -> GameState:
    """Process a player choice and return updated state"""
    from langchain_core.messages import HumanMessage
    
    # Add the choice
    state.add_message(HumanMessage(content=choice))
    
    # Run the graph
    config = {"configurable": {"thread_id": thread_id}}
    return self.graph.graph.invoke(state, config)

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
            
            # FIX: Use runner.graph.graph.invoke() instead of runner.graph.run()
            # The runner has the graph as an attribute, and the graph has the compiled graph
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            result = runner.graph.graph.invoke(game_state, config)
            
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

def dbz_game_loop():
    """Main DBZ game loop using actual game state"""

    print(f"\n🔄 DBZ GAME LOOP - State: {st.session_state.get('game_started')}")
    print(f"   Processing choice: {st.session_state.get('processing_choice', False)}")
    game_state = st.session_state.get('game_state')
    
    if not game_state:
        st.error("No game state found. Please start a new game.")
        return
    print(f"   Messages: {len(game_state.messages)}")
    print(f"   Plan: {len(game_state.current_plan)} steps")
    
    # Check for HITL approval first
    if st.session_state.get('pending_tool_calls'):
        display_hitl_approval()
        return
    
    # ===== SCENE DISPLAY =====
    if game_state.messages:
        # Filter out system messages and get the last AI message
        ai_messages = [m for m in game_state.messages 
                      if isinstance(m, AIMessage) and m.content]
        
        if ai_messages:
            latest_scene = ai_messages[-1]
            
            # Update session state power level from game state
            st.session_state.power_level = game_state.player_stats.get('power_level', 1000)
            
            # Display the scene with proper formatting
            st.markdown(f"""
            <div class="saga-card">
                <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
                    <span style="color: #FFD700; font-family: 'Bangers'; font-size: 1.5em; -webkit-text-stroke: 1px #2A0000;">
                        ⚡ SCENE {game_state.scene_counter}
                    </span>
                    <span style="color: #AAA; font-family: 'Orbitron'; text-shadow: 1px 1px 2px #000;">
                        {game_state.saga_name} SAGA
                    </span>
                </div>
                <div class="scene-text">
                    {latest_scene.content}
                </div>
                <div style="margin-top: 20px; text-align: right;">
                    <span style="color: #FFD700; font-family: 'Kanit'; -webkit-text-stroke: 0.5px #2A0000;">
                        Power Level: {st.session_state.power_level:,}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("The saga is unfolding...")
    else:
        st.warning("No scenes yet. The saga is generating...")
    
    # ===== EXTRACT CHOICES FROM GAME STATE =====
    choices = extract_choices_from_state(game_state)
    
    # ===== KAMEHAMEHA CHARGER =====
    display_kamehameha_charger()
    
    # ===== CHOICES =====
    display_dbz_choices(choices, handle_player_choice)
    
    # ===== STATS =====
    display_dbz_stats(game_state)
    
    # ===== TRANSFORMATIONS =====
    available_forms = game_state.player_stats.get('transformations', ["Base Form"])
    display_transformations(
        game_state.player_stats.get('current_form', "Base Form"),
        available_forms
    )

# =========================================================
# MAIN APP
# =========================================================
def main():
    st.set_page_config(
        page_title="⚡ DRAGON BALL Z - SAGA SIMULATOR ⚡",
        page_icon="⚡",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    inject_dbz_css()
    init_session_state()
    display_dbz_header()
    display_dbz_sidebar()
    
    if not st.session_state.get('game_started', False):
        display_dbz_welcome()
    else:
        dbz_game_loop()
    
    if st.session_state.get('show_debug', False):
        with st.expander("👁️ SCOUTER DEBUG", expanded=False):
            if st.session_state.get('game_state'):
                st.json(st.session_state.game_state.to_serializable())
            else:
                st.json({
                    "power_level": st.session_state.power_level,
                    "current_form": st.session_state.current_form,
                    "zenkai_boosts": st.session_state.zenkai_boosts,
                    "spirit_bombs": st.session_state.spirit_bombs,
                    "ki_charge": st.session_state.ki_charge,
                    "transformations": st.session_state.transformations,
                    "game_started": st.session_state.game_started,
                    "pending_tools": len(st.session_state.pending_tool_calls)
                })

if __name__ == "__main__":
    main()