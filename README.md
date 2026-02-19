# ⚡ Agentic-DBZ-Simulator ⚡

<p align="center">
  <strong>An Agentic AI Storyteller Powered by LangGraph</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/langgraph-0.0.45+-green.svg" alt="LangGraph Version">
  <img src="https://img.shields.io/badge/streamlit-1.28+-red.svg" alt="Streamlit Version">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

---

## 🎮 Experience Dragon Ball Z Like Never Before

Welcome to **Agentic-DBZ-Simulator**, a groundbreaking interactive storytelling engine that brings the Dragon Ball Z universe to life through advanced multi-agent AI. This isn't just a game—it's a demonstration of cutting-edge agentic architecture where multiple specialized agents collaborate in real-time to create dynamic, responsive narratives.

> "Every choice shapes your destiny, every battle tests your limits, every transformation unlocks new possibilities."

---

## 🏗️ The Agentic Architecture: A Symphony of AI Agents

At the heart of this project lies a sophisticated multi-agent system built with **LangGraph**, implementing the **ReAct (Reason + Act)** pattern. Five specialized agents work in concert to create a seamless storytelling experience:

### 🤖 The Agent Ecosystem
┌─────────────────────────────────────────────────────────────┐ │ REACT SAGA ENGINE │ ├───────────────┬───────────────────┬─────────────────────────┤ │ PLANNER │ EXECUTOR │ VERIFIER │ │ (Strategic) │ (Creative) │ (Quality Control) │ ├───────────────┼───────────────────┼─────────────────────────┤ │ MEMORY │ REPLANNER │ HUMAN INPUT │ │ (Context) │ (Adaptive) │ (Player Choices) │ └───────────────┴───────────────────┴─────────────────────────┘


### 🧠 Planner Agent - The Strategist

*   Analyzes player profile, power level, and saga type.
*   Creates 5-7 act story arcs with emotional pacing curves.
*   Seeds branching narratives and hidden objectives.
*   Calculates optimal scene distribution based on player preferences.

### 🎬 Executor Agent - The Storyteller

*   Brings scenes to life with immersive narration.
*   Generates dynamic player choices with meaningful consequences.
*   Manages battle sequences and power level progression.
*   Triggers transformations at key power thresholds (Over 9000!).

### ✅ Verifier Agent - The Quality Guardian

*   Ensures narrative consistency and character voice accuracy.
*   Checks power level plausibility and prevents plot holes.
*   Provides quality scoring (1-10) with configurable strictness.
*   Self-corrects issues by regenerating problematic scenes.

### 💾 Memory Agent - The Context Manager

*   Compresses long conversation histories to prevent token overflow.
*   Maintains essential context for the AI across dozens of turns.
*   Tracks important plot points and character relationships.
*   Optimizes token usage for LLM calls.

### 🔄 Replanner Agent - The Adaptive Director

*   Monitors for unexpected events and player deviations.
*   Dynamically adjusts remaining story beats.
*   Ensures coherent narrative flow despite player choices.

---

## ⚡ Key Features

### 🎯 Dynamic Storytelling

*   **Procedural Generation**: No two playthroughs are the same.
*   **Emotional Pacing**: Story intensity rises and falls like classic anime.
*   **Branching Narratives**: Every choice ripples through future scenes.
*   **Hidden Objectives**: Secret goals with unique rewards.

### 🦸 Character Progression

*   **Power Level System**: Start at 1,000 and transcend to 500,000+.
*   **Transformations**: Unlock Super Saiyan forms at key thresholds.
*   **Zenkai Boosts**: Power increases after near-death battles.
*   **Ki Mastery**: Improve energy control through training.

### ⚔️ Battle System

*   **Dynamic Combat**: Turn-based battles with power comparisons.
*   **Special Moves**: Execute Kamehameha, Galick Gun, and more.
*   **Victory Conditions**: Strategic choices determine outcomes.
*   **Battle Logs**: Track every clash and counter.

### 🎨 Immersive UI

*   **3D Visual Effects**: Floating sparkles, energy orbs, and particle systems.
*   **Power Level Meters**: Animated bars with "IT'S OVER 9000!" celebration.
*   **Scouter Displays**: Holographic readings of enemy power levels.
*   **Dragon Ball Collection**: Visual progress tracking.

### 💾 Save/Load System

*   **JSON Serialization**: Complete game state persistence.
*   **Multiple Save Slots**: Continue multiple adventures.
*   **Auto-backup**: Automatic saves at key moments.
*   **Cross-session Continuity**: Pick up where you left off.

---

## 🏗️ Project Structure

The project is organized into modules with clear responsibilities, promoting scalability and maintainability.
Agentic-DBZ-Simulator/
## 📂 Project Structure

```bash
Agentic-DBZ-Simulator/
├── 📁 agents/                      # AI Agents
│   ├── planner.py                  # Story arc generation
│   ├── executor.py                 # Scene execution
│   └── verifier.py                 # Quality control
│
├── 📁 graph/                       # LangGraph Orchestration
│   └── builder.py                  # Graph construction
│
├── 📁 runners/                     # Human-in-the-Loop
│   └── hitl_runner.py              # Player interaction management
│
├── 📁 schemas/                     # Pydantic Data Models
│   ├── state.py                    # Core GameState definition
│   ├── characters.py               # Player and NPC models
│   └── battle.py                   # Combat system schemas
│
├── 📁 utils/                       # Shared Utilities
│   ├── llm_wrapper.py              # LLM interaction with token tracking
│   ├── memory.py                   # Context compression logic
│   └── prompts.py                  # Centralized system prompts
│
├── 📁 ui/                          # Streamlit Frontend
│   ├── app_dbz_ultimate.py         # Main application UI
│   └── app_simple.py               # Simplified test version
│
├── 📁 saves/                       # Saved game data (JSON)
│
├── config.py                       # Application-wide configuration
├── requirements.txt                # Python dependencies
└── .env                            # API keys (user-created)
```


---

## 🚀 Quick Start

### Prerequisites

*   **Python 3.9+**
*   **Groq API Key** (for LLM access)

### Installation

1.  **Clone the repository:**
- git clone https://github.com/venukrishna-devadi/Agentic-DBZ-Simulator.git cd Agentic-DBZ-Simulator


2.  **Create and activate a virtual environment:**
- Create the environment - python -m venv venv
# Activate the environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate


3.  **Install the required dependencies:**
- pip install -r requirements.txt


4.  **Set up your environment variables:**
    Create a `.env` file in the root directory and add your Groq API key.
    s echo "GROQ_API_KEY=your_api_key_here" > .env

    *(Replace `your_api_key_here` with your actual Groq API key.)*

### Run the Game

Execute the main Streamlit application from your terminal.


**For the full, feature-rich experience**
- streamlit run ui/app1.py

**For the simplified test version**
- streamlit run ui/app2_basic.py


---

## 🎮 How to Play

#### 1️⃣ **Start Your Saga**

*   Choose your saga (e.g., Saiyan, Frieza, Cell, Buu, Tournament of Power).
*   Enter your warrior name.
*   Select the difficulty (Easy, Normal, Hard, or Legendary).
*   Click **"BEGIN TRAINING"** to start the adventure.

#### 2️⃣ **Experience the Story**

*   Read the AI-generated scene narrative.
*   Choose from 3-4 meaningful options that will shape the story.
*   Watch your power level grow with each decision and battle.
*   Unlock powerful transformations at key thresholds.

#### 3️⃣ **Master Combat**

*   Engage in dynamic, turn-based battles.
*   Choose your attack strategies wisely.
*   Execute iconic special moves like the Kamehameha and Final Flash.
*   Earn powerful Zenkai boosts after surviving near-death experiences.

#### 4️⃣ **Save Your Progress**

*   Click the **"SAVE"** button in the sidebar to preserve your adventure.
*   Load previous games anytime to continue different sagas.
*   Share your `.json` save files with friends to let them experience your journey.

