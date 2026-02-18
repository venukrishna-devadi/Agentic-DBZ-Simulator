
# Think of this state.py file as the "Brain" or the "Master Save File" of your AI-powered game.

# In a standard game, the computer needs to remember if you’ve talked to a certain character, how much health you have, and where you are in the story. This code does exactly that, but in a way that an AI (like a Large Language Model) can understand and update.

# Here is the breakdown in simple English:

# 1. What are the main parts?
# SceneType (The Categories)

# Think of this as a drop-down menu. Instead of letting the AI type whatever it wants for a scene, we force it to pick from a specific list: INTRODUCTION, BATTLE, TRAINING, etc.

# Why? It prevents typos and makes sure the code knows exactly what kind of scene is happening so it can apply the right rules.

# PlanStep (The To-Do List)

# This represents a single goal in the story. It tracks what should happen (e.g., "Meet the Master"), who needs to be there, and whether it’s finished yet.

# Why? It allows the AI to "plan" ahead. Instead of just reacting, the AI can look at the list and say, "Okay, I've finished the Training, now I need to start the Battle."

# GameState (The Master Record)

# This is the big container that holds everything. It keeps track of:

# Messages: Every word you and the AI have said.

# World Flags: True/False switches (e.g., final_battle_begun: False).

# Player Stats: Your name, health, and power level.

# NPCs: Information about your mentor or rivals.

# 2. Why do we use Pydantic (BaseModel)?
# You'll notice most classes inherit from BaseModel. Think of Pydantic as a Strict Librarian.

# If you try to set your "Health" to a piece of text (like "Super High") instead of a number, Pydantic will throw an error immediately.

# The Benefit: It prevents the game from crashing later because of "bad data." It ensures that every piece of information is in the correct format before the game even tries to use it.

# 3. What is "Serialization" (to_serializable)?
# Python objects are complex "living" things in your computer's memory. However, if you want to save your game to a database or send it over the internet, you have to turn that complex object into a simple string of text (JSON).

# to_serializable: Turns the "living" GameState into a simple text dictionary.

# from_serializable: Takes that text and "breathes life" back into it, turning it back into a Python object you can interact with.

# 4. How does this work with LangGraph?
# Since you are using LangGraph, this GameState is the object that gets passed around between different AI functions (nodes).

# Node A (The Planner) looks at the GameState, sees the player's health is high, and adds a PlanStep for a BATTLE.

# Node B (The Narrator) reads the current_step from the GameState and writes a story about a fight.

# Node C (The Accountant) updates the player_stats in the GameState based on how the fight went.

# Summary: Why do we code it this way?
# Organization: It keeps all game data in one place instead of scattered variables.

# Safety: It catches bugs early by validating that data (like health or names) is correct.

# Persistence: It makes it easy to save the game and load it exactly where the player left off.

# AI Clarity: It gives the AI a clear "status report" so it doesn't forget who the player is or what is happening in the story.
######################################################################################################################################################################################


# In basic Python, you might use a simple dictionary like player = {"hp": 100}. But dictionaries are "dumb"—they don't care if you accidentally change the HP to a word like "pancake". This code uses Pydantic, which makes your data "smart" by adding rules, safety checks, and extra powers.

# 1. The Building Blocks: What is what?
# SceneType(str, Enum) — The Restricted List

# Think of this as a fixed menu at a restaurant.

# The Coding Part: An Enum (Enumeration) is a way to say: "This variable can only be one of these specific things."

# Why use it? If you type SCENE = "battel" (a typo), Python won't care. But if you use SceneType.BATTLE, your code editor will catch the typo immediately.

# PlanStep(BaseModel) — The Specific Form

# Imagine a job application form. It has specific blanks for "Name," "Date," and "Experience."

# The Coding Part: BaseModel defines what fields an object must have.

# Field(default_factory=...): This is a fancy way of saying: "If I don't give you a value, run this little bit of code to create one." For example, it generates a unique ID using the current time.

# @field_validator: This is like a Security Guard. Before the data is saved, it checks the "Description." If it’s shorter than 10 characters, the guard kicks it back and says, "Not good enough!"

# GameState(BaseModel) — The Master Save File

# This is the big one. It holds the player’s stats, the history of the conversation, and the game world’s "Flags" (switches that tell the game if something has happened yet).

# 2. The Flow: How the data moves
# In an AI system like LangGraph, the data doesn't just sit there. It flows in a loop.

# Start: The GameState is created with default values (Health = 100, Story = "Introduction").

# User Input: You say, "I want to train with the Master."

# AI Logic: The AI looks at the GameState. It sees world_flags["training_completed"] is False.

# Update: The AI calls advance_plan() or update_player_stat().

# Save: The GameState is updated. Next time you talk to the AI, it "remembers" you finished training because it reads the updated state.


# 3. Explaining the "Advanced" Python parts
# Here are the parts that usually confuse people new to intermediate Python:

#########.  Optional[str]	This variable could be a piece of text (string), or it could be empty (None).	A "Middle Name" field on a form—some people have one, some don't.
######  @property	A function that acts like a variable. You don't have to "call" it with ().	A car's Speedometer. You don't "do" anything to it; you just look at it to see the current state.
#######  Serialization	Turning complex Python objects into a simple text format (JSON) so they can be saved.	Taking a Lego castle apart and putting it in a flat box so you can move it to a new house.
####### @field_validator	 A function that checks if the data is correct before it's saved.	 A security guard at a club checking IDs before letting people in.
####### default_factory	A way to automatically generate a value if you don't provide one.	 A vending machine that gives you a random snack if you don't choose one.
#######. self	Refers to the specific object you are currently working with.	If I say "My arm hurts," 'My' is like self. It points to the specific person speaking.


# 4. Why go through all this trouble?
# Why not just use a simple list? Predictability.

# When you are building an AI game, the AI is unpredictable. It might try to hallucinate that you have 1,000,000 health or that the scene is called "Outer Space."

# By using this state.py file:

# You set the boundaries: The AI has to play by your rules defined in the GameState.

# Easy Debugging: If the game crashes, you can look at the "Master Save File" and see exactly where the data went wrong.

# Persistence: Because of the to_serializable methods, you can turn the whole game into a text file, turn off your computer, come back tomorrow, and load it exactly where you were.








#############
# gemini conversation link- https://gemini.google.com/share/3e75dd06c543

from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum
from langchain_core.messages import BaseMessage
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage

class SceneType(str, Enum):
    """Types of game scenes"""
    INTRODUCTION = "introduction"
    EXPLORATION = "exploration"
    DIALOGUE = "dialogue"
    BATTLE = "battle"
    TRAINING = "training"
    CLIMAX = "climax"
    RESOLUTION = "resolution"

# That code snippet is a common way to keep complex logic (like game states) organized.

# Here is a breakdown of what’s happening in "plain English."

# 1. What is this class doing?
# Think of SceneType as a fixed menu.

# Instead of typing the word "battle" or "introduction" manually every time—where you might make a typo like "battel"—you create a central list of "official" names.

# In your LangGraph project, this ensures that your AI agent always knows exactly which state it is in. It prevents bugs caused by messy strings.

# 2. What is an Enum?
# Enum is short for Enumeration. It is a way to create a group of related constants.

# The "str" part: Tells Python that these items should behave like strings.

# The "Enum" part: Tells Python this is a special list that cannot be changed while the program is running.







class PlanStep(BaseModel):
    """A single step in the execution plan"""

    # --- THE SETUP (What we expect to happen) ---
    id: str = Field(default_factory=lambda: f"step_{datetime.now().timestamp()}")
    scene_type: SceneType
    description: str
    expected_outcome: str
    required_characters: List[str] = Field(default_factory=list)
    expected_duration: int = Field(default=1, ge=1, le=10)

    # ✨ NEW: Enhanced PlanStep fields for richer storytelling
    emotional_intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    archetype: Optional[str] = None
    branching_options: List[Dict[str, str]] = Field(default_factory=list)
    rewards: Dict[str, Any] = Field(default_factory=dict)
    # FIX: Better error message and clamping
    difficulty_modifier: float = Field(
        default=1.0, 
        ge=0.5, 
        le=3.0,
        description="Difficulty multiplier for the scene (0.5 = easier, 3.0 = harder)"
    )
    narrative_weight: float = Field(default=1.0, ge=0.0, le=2.0)
    hidden_objectives: Optional[Dict[str, str]] = None

    # --- THE TRACKER (What actually happened) ---
    completed: bool = False
    completion_time: Optional[datetime] = None
    actual_outcome: Optional[str] = None
    unexpected_events: List[str] = Field(default_factory=list)

    # ✨ NEW: Track player choices and performance
    player_choice_made: Optional[str] = None
    performance_rating: Optional[float] = None  # 0-1 rating of how well player did
    rewards_earned: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError("Description must be at least 10 characters long")
        return v

    @field_validator("emotional_intensity")
    @classmethod
    def validate_emotional_intensity(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("Emotional intensity must be between 0 and 1")
        return v
    
    # FIX: Add validator for difficulty_modifier with clamping
    @field_validator("difficulty_modifier", mode="before")
    @classmethod
    def validate_difficulty_modifier(cls, v: float) -> float:
        """Ensure difficulty modifier is within bounds"""
        if v < 0.5:
            return 0.5
        if v > 3.0:
            return 3.0
        return v
    
    # ---- The Actions (What the agent can do) ----

    # ✨ NEW: Enhanced completion tracking
    def mark_completed_with_choice(self, 
                                  outcome: str, 
                                  choice: str,
                                  performance: float,
                                  rewards: Dict[str, Any],
                                  unexpected: List[str] = None):
        """Mark step completed with player choice and performance tracking"""
        self.completed = True
        self.completion_time = datetime.now()
        self.actual_outcome = outcome
        self.player_choice_made = choice
        self.performance_rating = performance
        self.rewards_earned = rewards
        if unexpected:
            self.unexpected_events.extend(unexpected)

    def mark_completed(self, outcome: str, unexpected: List[str] = None):
        """Mark this step as completed with the actual outcome"""
        self.completed = True
        self.completion_time = datetime.now()
        self.actual_outcome = outcome
        if unexpected:
            self.unexpected_events.extend(unexpected)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "scene_type": self.scene_type.value,
            "description": self.description,
            "expected_outcome": self.expected_outcome,
            "required_characters": self.required_characters,
            "expected_duration": self.expected_duration,
            "emotional_intensity": self.emotional_intensity,
            "archetype": self.archetype,
            "branching_options": self.branching_options,
            "rewards": self.rewards,
            "difficulty_modifier": self.difficulty_modifier,
            "narrative_weight": self.narrative_weight,
            "hidden_objectives": self.hidden_objectives,
            "completed": self.completed,
            "completion_time": self.completion_time.isoformat() if self.completion_time else None,
            "actual_outcome": self.actual_outcome,
            "unexpected_events": self.unexpected_events,
            "player_choice_made": self.player_choice_made,
            "performance_rating": self.performance_rating,
            "rewards_earned": self.rewards_earned
        }
# Why this is helpful for your project:

# Safety: If your AI tries to set expected_duration to 99, Python will throw an error immediately because of the le=10 rule.

# Tracking: In LangGraph, you can pass a list of these PlanStep objects around. You can easily filter them to see which ones are not completed yet to decide what the agent should do next.

# Memory: By storing actual_outcome and unexpected_events, the agent can "learn" from what happened in Step 1 before it tries to do Step 2.




#########################################################################################################################################################################


# This GameState class is the "Master Brain" of your LangGraph project.

# In Agentic AI, the agent needs to remember who it's talking to, what the plan is, and what the world looks like. This class is the container that holds all that information as it moves from one node in your graph to the next.

# 1. What is this class doing?
# Think of GameState as a Save Game File that is constantly being updated.

# Every time your AI makes a move, it looks at this class to see:

# Memory: "What did we just talk about?" (messages)

# Stats: "How much health does the hero have?" (player_stats)

# Progress: "Are we on step 1 or step 2 of the plan?" (plan_step_index)

# Logic: "Has the villain been introduced yet?" (world_flags)


# 3. How do the "Helper Methods" work?
# These are small "shortcut" functions inside the class that make it easier to interact with the data.

# Example: advance_plan

# Python
# def advance_plan(self):
#     self.plan_step_index += 1
#     self.scene_counter += 1
# English: Instead of manually changing two numbers every time a scene ends, you just call state.advance_plan(). It's like clicking the "Next" button on a slideshow.

# Example: current_step (The @property)

# Python
# @property
# def current_step(self):
#     return self.current_plan[self.plan_step_index]
# English: This is a "smart variable." You don't have to calculate which step is current; you just ask for state.current_step, and it looks at the index and the list for you.

# 4. Why are to_serializable and from_serializable there?
# AI agents speak "Python objects," but databases and web browsers speak "JSON" (simple text).

# to_serializable: Turns the complex class into a simple dictionary so you can save it to a file.

# from_serializable: Takes that saved file and turns it back into a "smart" Python object so the AI can work with it again.

# When you define your graph, you will tell it: workflow = StateGraph(GameState). This tells LangGraph that every single node in your AI's brain will receive an instance of this GameState class to read and update.


class GameState(BaseModel):
    """Main game state using Pydantic for validation.
    This is the central data structure that flows through our LangGraph."""

    # ===== MESSAGES & MEMORY =====
    # A list of actual chat messages (Human says X, AI says Y).
    messages: List[BaseMessage]= Field(description= "Conversation history between player and AI",
                                       default_factory= list)
    
    # A text string that summarizes everything that happened so far 
    # so the AI doesn't have to re-read thousands of messages.
    memory_summary: str = Field(
        default="",
        description="Compressed summary of past events"
    )

    # ===== PLANNING SYSTEM =====
    # A list of the PlanStep objects we discussed earlier.
    current_plan: List[PlanStep] = Field(
        default_factory= list,
        description="The current plan the AI is trying to execute"
    )

    # Which step are we currently on? (Step 0, Step 1, etc.)
    plan_step_index: int = Field(
        default=0,
        ge=0,
        description="Index of the current step in the plan"
    )

    # Tracks how many times the AI had to change its mind and rewrite the plan.
    plan_revisions: int = Field(
        default=0,
        ge=0,
        description="How many times the AI had to revise the plan"
    )

    # ===== GAME WORLD =====
    saga_name: str = Field(default="The Saiyan Saga", description="Name of the current saga")

    # Total count of scenes finished since the very start.
    scene_counter: int = Field(default=0, ge=0, description="Total number of scenes completed")

    # These are "Story Switches." For example: if villain_introduced is True, 
    # the AI knows it should stop being friendly and start being scary.

     # ✨ NEW: Track total actions (what your executor needs!)
    total_actions: int = Field(default=0, ge=0, description="Total number of player actions taken")

    world_flags: Dict[str, bool] = Field(
        default_factory=lambda: {
            "villain_introduced": False,
            "training_completed": False,
            "transformation_unlocked": False,
            "final_battle_begun": False,
            # ✨ NEW: Additional useful flags
            "mentor_met": False,
            "rival_defeated": False,
            "ancient_power_awakened": False,
            "ally_saved": False,
            "secret_uncovered": False
        }
    )

    # ✨ NEW: Track relationships with characters
    relationships: Dict[str, float] = Field(
        default_factory=lambda: {
            "mentor": 0.5,
            "rival": 0.3,
            "villain": -0.2,
            "ally": 0.6
        },
        description="Relationship values with key characters (-1 to 1)"
    )

    # ===== CHARACTERS =====
    player_name: str = Field(default="Vegeta", description="Name of the player character")

    # A dictionary to hold player stats like health and power level.
    player_stats: Dict[str, Any] = Field(
        default_factory=lambda: {
            "power_level": 5000,
            "health": 100,
            "max_health": 100,
            "ki_mastery": 50,
            "spirit_bombs": 0,
            "zenkai_boosts": 0,
            "level": 1,
            "experience": 0,
            "items": [],
            # ✨ NEW: Enhanced stats
            "techniques": ["Basic Ki Blast"],
            "transformations": [],
            "titles": ["Rookie Warrior"],
            "momentum": 0.5  # Story momentum 0-1
        }
    )

    # Information about other people in the game (NPCs).
    npcs: Dict[str, Dict[str, Any]] = Field(
        default_factory=lambda: {
            "mentor": {
                "name": "Master Roshi", 
                "power_level": 3000, 
                "alive": True,
                "location": "Kame House",
                "mood": "wise",
                "last_interaction": None
            },
            "rival": {
                "name": "Goku", 
                "power_level": 5500, 
                "alive": True,
                "location": "Unknown",
                "mood": "competitive",
                "last_interaction": None
            }
        }
    )

    # ===== BATTLE STATE =====
    # A simple switch: Is a fight happening right now?
    in_battle: bool = Field(default=False, description="Is the player currently in a battle?")

    # If a fight IS happening, this holds the battle details (like who's turn it is).
    battle_state: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Details about the current battle, if in_battle is True"
    )

    # ===== METRICS & DEBUGGING =====
    # Tracks how much "money" (tokens) you are spending on the AI API.
    tokens_used: int = Field(default=0, ge=0, description="Total tokens used in API calls")
    start_time: datetime = Field(default_factory=datetime.now, description="When the game started")

    # ✨ NEW: Performance metrics
    average_response_time: float = Field(default=0.0, description="Average LLM response time")
    api_calls: int = Field(default=0, ge=0, description="Total API calls made")
    cache_hits: int = Field(default=0, ge=0, description="Cache hits for performance")
    errors_recovered: int = Field(default=0, ge=0, description="Number of errors gracefully handled")

    # ===== GRAPH CONTROL =====
    # If this is False, LangGraph will stop running the loop.
    should_continue: bool = Field(default=True, description="Control flag to stop the graph loop")
    error_message: Optional[str] = Field(default=None, description="If something goes wrong, this holds the error details")

    # ===== ✨ NEW: Narrative Context Tracking =====
    active_plot_threads: List[str] = Field(
        default_factory=list,
        description="Ongoing plot threads that need resolution"
    )
    
    foreshadowing_hints: List[str] = Field(
        default_factory=list,
        description="Hints planted for future events"
    )
    
    dramatic_tension: float = Field(
        default=0.3,
        ge=0.0,
        le=1.0,
        description="Current story tension level"
    )
    
    time_of_day: str = Field(
        default="day",
        description="Current time in game world: dawn, day, dusk, night"
    )
    
    location: str = Field(
        default="Unknown Area",
        description="Player's current location"
    )

    class Config:
        """Tells Pydantic how to handle special types like Datetime or LangChain messages"""
        arbitrary_types_allowed = True

    ### Helper Methods for Game Logic ###
    
    @property
    def current_step(self) -> Optional[PlanStep]:
        """Shortcut to get the exact task the agent is currently working on."""
        if (self.current_plan and 0 <= self.plan_step_index and len(self.current_plan)):
            return self.current_plan[self.plan_step_index]
        return None

# This helper function is like a "GPS Marker" for your AI. It looks at the big list of things to do (the plan) and points to the one specific task the agent is supposed to be working on right now.

# Here is the breakdown of the logic in simple English:

# 1. The "Safety Check" (if statement)

# Before the code tries to grab a task, it asks two "safety" questions to prevent the program from crashing:

# self.current_plan: "Is there even a plan?"

# If the list is empty, there is no "current step" to give back.

# 0 <= self.plan_step_index < len(self.current_plan): "Is our current index valid?"

# If your plan has 5 steps, but your index is 10 (maybe because the game ended), trying to find "Step 10" would cause an error. This ensures the "pointer" is actually pointing at something inside the list.

# 2. The "Fetch" (return statement)

# return self.current_plan[self.plan_step_index]: If the safety checks pass, it goes into the list and pulls out the PlanStep object at that specific position.

# 3. The "Fallback" (return None)

# If the plan is empty or we've finished all the steps, the function returns None. This tells the AI: "Hey, there's nothing left on the to-do list!"

# A Real-World Analogy

# Imagine you have a Recipe Book (this is your current_plan).

# plan_step_index is your finger pointing at a line on the page.

# The if statement checks: "Are you actually holding a book? And is your finger pointing at a real line, or did you slip off the bottom of the page?"

# current_step returns the instruction your finger is pointing at (e.g., "Preheat the oven").

# Why use a "Shortcut" (Property)?

# Notice the @property tag usually sits above this in your code. This allows you to write: print(state.current_step) instead of: print(state.current_plan[state.plan_step_index])

    @property
    def plan_completed(self)-> bool:
        """A quick way to check if the agent has finished all the steps in the current plan.
        """
        if not self.current_plan:
            return False
        return self.plan_step_index >= len(self.current_plan)
# This helper function is the "Finish Line Detector." Its job is to tell the rest of your program whether the AI agent has run out of tasks to perform.

# Here is the step-by-step logic in simple English:

# 1. The Empty Plan Check

# Python
# if not self.current_plan:
#     return False
# The Logic: If there is no plan at all (the list is empty), you haven't technically "completed" a plan—you just never started one.

# The Result: It returns False because there's nothing to be "complete."

# 2. The Comparison (The Core Logic)

# Python
# return self.plan_step_index >= len(self.current_plan)
# This is where the math happens. To understand this, remember that Python starts counting lists at 0.

# Imagine a plan with 3 steps:

# Step 0: "Meet the King"

# Step 1: "Get the Sword"

# Step 2: "Fight the Dragon"

# len(self.current_plan) (The total count) is 3.

# How the index moves:

# If plan_step_index is 0, 1, or 2, you are still working. 0 >= 3 is False.

# If you call advance_plan() after the final step, your plan_step_index becomes 3.

# The Check: 3 >= 3 is True.

# Conclusion: If your "finger" (the index) has moved past the last item in the list, the plan is finished!

# Why use >= (Greater than or equal to)?

# In a perfect world, the index would exactly equal the length when finished. However, programmers use >= as a safety net. If for some reason a bug caused the index to jump to 4 or 5, the function would still correctly say, "Yes, we are definitely done with the 3-step plan."
# In LangGraph, you will use this function to decide which path to take next. For example:

# If state.plan_completed is True → Go to the "Ending" node.

# If state.plan_completed is False → Go to the "Execute Next Step" node.


    @property
    def plan_progress(self)-> float:
        """Returns a number between 0 and 1 representing how much of the current plan is completed."""
        if not self.current_plan:
            return 0.0
        completed = sum(1 for step in self.current_plan if step.completed)
        return completed / len(self.current_plan)
    
    @property
    def power_level_percentage(self) -> float:
        """Get power level as percentage of 10k (for UI)"""
        return min(1.0, self.player_stats.get("power_level", 0) / 10000)
    

    
    def get_battle_summary(self) -> Optional[str]:
        """Get a summary of current battle state"""
        if not self.in_battle or not self.battle_state:
            return None
        return f"Battle vs {self.battle_state.get('opponent', 'Unknown')}, Turn {self.battle_state.get('turn_count', 0)}"
 
    def advance_plan(self):
        """Call this to move the game forward to the next step in the checklist."""
        if self.current_step:
            self.plan_step_index += 1
            self.scene_counter += 1

# This helper function is the "Page Turner." It’s the action that moves your AI agent from the task it just finished to the very next one on the list.

# Here is the logic broken down into simple English:

# 1. The Guardrail (if self.current_step:)

# Before the code tries to move forward, it asks: "Are we actually doing something right now?"

# Remember the current_step helper we looked at earlier? It returns None if the plan is already finished or empty.

# This line ensures that if the agent is already at the finish line, we don't keep pushing it into empty space (which would cause errors).

# 2. Moving the Pointer (self.plan_step_index += 1)

# This is the heart of the function.

# It takes the current "Task Number" (the index) and adds 1 to it.

# Example: If the agent just finished Step 0 ("Talk to the Guard"), the index becomes 1. Now, the current_step will automatically point to Step 1 ("Enter the Castle").

# 3. Updating the Global Counter (self.scene_counter += 1)

# While the plan_step_index tells us where we are in the current plan, the scene_counter tracks the entire game history.

# Even if the AI finishes one plan and starts a brand new one later, the scene_counter keeps going up (1, 2, 3, 4...).

# This is useful for things like "Day/Night" cycles or tracking how long the player has been playing overall.

# A Simple "Action" Example

# Imagine your agent is following this plan:

# [0] Open Door

# [1] Walk Inside

# [2] Close Door

# Current State: plan_step_index = 0 (The agent is at the door).

# The Agent completes the task.

# You call state.advance_plan().

# Internal Logic:

# Does a current step exist? Yes (Open Door).

# plan_step_index becomes 1.

# scene_counter goes from (let's say) 5 to 6.

# Result: The next time the AI asks "What should I do?", the system points to [1] Walk Inside. The agent has successfully moved to the next step in the plan!

    def add_message(self, message: BaseMessage):
        """Add a new message to the conversation history."""
        self.messages.append(message)

    def get_recent_messages(self, count: int = 5)-> List[BaseMessage]:
        """Return the most recent messages in the conversation history."""
        return self.messages[-count:] if self.messages else []
    
    def update_player_stat(self, stat: str, value: Any):
        """Update a player stat safely"""
        if stat in self.player_stats:
            # Apply bounds checking for numeric stats
            if stat == "power_level" and isinstance(value, (int, float)):
                self.player_stats[stat] = max(0, value)
            elif stat == "ki_mastery" and isinstance(value, (int, float)):
                self.player_stats[stat] = max(0, min(100, value))
            elif stat == "health" and isinstance(value, (int, float)):
                max_hp = self.player_stats.get("max_health", 100)
                self.player_stats[stat] = max(0, min(max_hp, value))
            else:
                self.player_stats[stat] = value
    
    def set_world_flag(self, flag: str, value: bool):
        """Easy way to update world flags without having to write complex code in the graph nodes."""
        self.world_flags[flag] = value

    def update_relationship(self, character: str, delta: float):
        """Update relationship with a character"""
        if character in self.relationships:
            current = self.relationships[character]
            self.relationships[character] = max(-1.0, min(1.0, current + delta))

    def add_item(self, item: str):
        """Add an item to inventory"""
        if "items" not in self.player_stats:
            self.player_stats["items"] = []
        if item not in self.player_stats["items"]:
            self.player_stats["items"].append(item)

    def remove_item(self, item: str):
        """Remove an item from inventory"""
        if "items" in self.player_stats and item in self.player_stats["items"]:
            self.player_stats["items"].remove(item)
    
    def add_technique(self, technique: str):
        """Add a new technique to player's arsenal"""
        if "techniques" not in self.player_stats:
            self.player_stats["techniques"] = []
        if technique not in self.player_stats["techniques"]:
            self.player_stats["techniques"].append(technique)
    
    def add_transformation(self, transformation: str):
        """Unlock a new transformation"""
        if "transformations" not in self.player_stats:
            self.player_stats["transformations"] = []
        if transformation not in self.player_stats["transformations"]:
            self.player_stats["transformations"].append(transformation)
    
    def add_title(self, title: str):
        """Add a title to player"""
        if "titles" not in self.player_stats:
            self.player_stats["titles"] = []
        if title not in self.player_stats["titles"]:
            self.player_stats["titles"].append(title)
    
    def add_plot_thread(self, thread: str):
        """Add an active plot thread"""
        if thread not in self.active_plot_threads:
            self.active_plot_threads.append(thread)
    
    def resolve_plot_thread(self, thread: str):
        """Remove a resolved plot thread"""
        if thread in self.active_plot_threads:
            self.active_plot_threads.remove(thread)
    
    def add_foreshadowing(self, hint: str):
        """Add a foreshadowing hint"""
        self.foreshadowing_hints.append(hint)
    
    def get_unresolved_hints(self) -> List[str]:
        """Get foreshadowing hints that haven't paid off yet"""
        return self.foreshadowing_hints
    
    def update_dramatic_tension(self, delta: float):
        """Update dramatic tension with bounds"""
        self.dramatic_tension = max(0.0, min(1.0, self.dramatic_tension + delta))
    
    def set_time_of_day(self, time: str):
        """Set current time of day"""
        valid_times = ["dawn", "day", "dusk", "night"]
        if time in valid_times:
            self.time_of_day = time
    
    def advance_time(self):
        """Advance time of day cyclically"""
        cycle = ["dawn", "day", "dusk", "night"]
        current_idx = cycle.index(self.time_of_day) if self.time_of_day in cycle else 1
        next_idx = (current_idx + 1) % len(cycle)
        self.time_of_day = cycle[next_idx]
    
     # =========================================================================
    # NPC MANAGEMENT
    # =========================================================================

    def update_npc(self, npc_key: str, updates: Dict[str, Any]):
        """Update an NPC's attributes"""
        if npc_key in self.npcs:
            self.npcs[npc_key].update(updates)
            self.npcs[npc_key]["last_interaction"] = datetime.now().isoformat()
    
    def get_npc(self, npc_key: str) -> Optional[Dict[str, Any]]:
        """Get NPC data by key"""
        return self.npcs.get(npc_key)
    
    def add_npc(self, npc_key: str, npc_data: Dict[str, Any]):
        """Add a new NPC to the world"""
        if npc_key not in self.npcs:
            npc_data["last_interaction"] = None
            self.npcs[npc_key] = npc_data
    
    def remove_npc(self, npc_key: str):
        """Remove an NPC (if they die or leave)"""
        if npc_key in self.npcs:
            del self.npcs[npc_key]

    # =========================================================================
    # BATTLE MANAGEMENT
    # =========================================================================
    
    def start_battle(self, opponent: str, opponent_power: int):
        """Initialize a battle state"""
        self.in_battle = True
        self.battle_state = {
            "opponent": opponent,
            "opponent_power": opponent_power,
            "player_hp": self.player_stats.get("health", 100),
            "opponent_hp": 100,
            "turn_count": 0,
            "battle_log": [],
            "special_used": False
        }
    
    def end_battle(self, player_victory: bool):
        """End the current battle"""
        self.in_battle = False
        if self.battle_state:
            self.battle_state["result"] = "victory" if player_victory else "defeat"
    
    def add_battle_log(self, entry: str):
        """Add an entry to battle log"""
        if self.battle_state:
            if "battle_log" not in self.battle_state:
                self.battle_state["battle_log"] = []
            self.battle_state["battle_log"].append(f"[Turn {self.battle_state.get('turn_count', 0)}] {entry}")

    # =========================================================================
    # METRICS TRACKING
    # =========================================================================
    
    def record_api_call(self, tokens: int, response_time: float):
        """Record metrics from an API call"""
        self.api_calls += 1
        self.tokens_used += tokens
        # Update running average
        self.average_response_time = (
            (self.average_response_time * (self.api_calls - 1) + response_time) / self.api_calls
        )
    
    def record_cache_hit(self):
        """Record a cache hit"""
        self.cache_hits += 1
    
    def record_error_recovery(self):
        """Record a recovered error"""
        self.errors_recovered += 1        
    
    # =========================================================================
    # PLAN MANAGEMENT
    # =========================================================================
    
    def get_next_step_preview(self) -> Optional[str]:
        """Get a preview of the next step (if any)"""
        next_index = self.plan_step_index + 1
        if self.current_plan and next_index < len(self.current_plan):
            return self.current_plan[next_index].description
        return None
    
    def get_remaining_steps(self) -> int:
        """Get number of steps remaining in current plan"""
        if not self.current_plan:
            return 0
        return len(self.current_plan) - self.plan_step_index
    
    def has_active_plot_threads(self) -> bool:
        """Check if there are unresolved plot threads"""
        return len(self.active_plot_threads) > 0
    
    def get_context_for_llm(self) -> Dict[str, Any]:
        """Get a condensed context dictionary for LLM prompts"""
        return {
            "player_name": self.player_name,
            "player_stats": self.player_stats,
            "relationships": self.relationships,
            "world_flags": self.world_flags,
            "active_plot_threads": self.active_plot_threads,
            "current_location": self.location,
            "time_of_day": self.time_of_day,
            "dramatic_tension": self.dramatic_tension,
            "scene_counter": self.scene_counter,
            "total_actions": self.total_actions
        }
    
    def to_serializable(self) -> Dict[str, Any]:
        """Convert to serializable dictionary"""
        data = self.model_dump()
        
        # Handle non-serializable fields
        data['messages'] = [
            {
                "type": type(message).__name__,
                "content": message.content,
                "additional_kwargs": getattr(message, "additional_kwargs", {}) if hasattr(message, "additional_kwargs") else {}
            }
            for message in self.messages
        ]
        
        data['current_plan'] = [step.to_dict() for step in self.current_plan]
        data['start_time'] = self.start_time.isoformat()
        
        return data


    @classmethod
    def from_serializable(cls, data: Dict[str, Any])-> "GameState":
        """Takes a dictionary (like the one created by to_serializable) and turns it back into a GameState object."""
#         This means:

# 👉 “Create a GameState object from saved data.”

# cls = the GameState class itself.

# So when you later call:
# GameState.from_serializable(saved_data)
# It creates a new GameState object using the data.
# Why Do We Need This?

# Because when you save your game to JSON, everything becomes plain text.

# Example:

# When saved, your messages might look like this:
# {
#   "messages": [
#     {
#       "type": "HumanMessage",
#       "content": "Start the saga"
#     }
#   ]
# }
# But your program expects:
# HumanMessage(content="Start the saga")
# Those are different!

# So this method:
# 	•	Takes plain text data
# 	•	Rebuilds real Python objects
# 	•	Returns a real GameState

# 2. What is from_serializable doing?
# When you save your game, it becomes a simple dictionary (strings and numbers). When you want to play again, you can't just give the AI that dictionary—the AI needs the "Smart" objects back.

# This function "rehydrates" the dry data.

# Step A: Rebuilding the Messages

# The dictionary just says: {"type": "HumanMessage", "content": "Hello"}. This code looks at the "type," finds the actual Python tool for HumanMessage, and creates a real, living message object again.

# Python
# message_map = {
#     "HumanMessage": HumanMessage,
#     "AIMessage": AIMessage,
#     "SystemMessage": SystemMessage
# }
# This map is like a phone book. If the data says "HumanMessage," the code looks up the "phone number" (the actual Python class) to build it.

# Step B: Rebuilding the Plan

# The dictionary just has text for the plan steps. This section loops through them and creates new PlanStep objects.

# Python
# step = PlanStep(
#     id=step_data.get("id"),
#     scene_type=SceneType(step_data.get("scene_type", "introduction")),
#     ...
# )
# It even converts the string "introduction" back into your Enum SceneType.INTRODUCTION.

# Step C: The Grand Finale

# Python
# return cls(**data)
# The **data is Python shorthand for: "Take all the variables in this dictionary and plug them into the GameState template." cls is GameState. So it’s basically saying: return GameState(player_name="Goku", health=100, ...)

# 3. Simple Example
# Imagine you saved your game to a file called save.json. Here is how you use this class method:

# Python
# # 1. Load the "dead" data (dictionary) from a file
# saved_dictionary = load_from_file("save.json")

# # 2. Use the CLASS method to bring it to life
# # Notice we call this on GameState (the class), not a specific variable!
# new_game_session = GameState.from_serializable(saved_dictionary)

# # 3. Now it's a "living" object again
# print(new_game_session.player_name) 
# new_game_session.advance_plan() # This works now because it's a real class instance!
# Summary: How to know when to use @classmethod
# Use a Regular Method (self): When the game is already running and you want to change something (e.g., take_damage).

# Use a @classmethod (cls): When you want to create a new game instance in a special way (e.g., from_file, from_database, create_default_game).

        # Reconstruct messages
        message_map = {
            "HumanMessage": HumanMessage,
            "AIMessage": AIMessage,
            "SystemMessage": SystemMessage
        }
        reconstructed_messages = []
        for msg_data in data.get("messages", []):
            msg_type = msg_data.get("type")
            if msg_type in message_map:
                msg_class = message_map[msg_type]
                reconstructed_messages.append(
                    msg_class(content = msg_data.get("content", ""),
                              additional_kwargs = msg_data.get("additional_kwargs", {}))
                )

        data['messages'] = reconstructed_messages
        
        # Reconstruct plan steps
        plan_data = data.get("current_plan", [])
        reconstructed_plan = []
        for step_data in plan_data:
            step = PlanStep(
                id=step_data.get("id", ""),
                scene_type=SceneType(step_data.get("scene_type", "introduction")),
                description=step_data.get("description", ""),
                expected_outcome=step_data.get("expected_outcome", ""),
                required_characters=step_data.get("required_characters", []),
                expected_duration=step_data.get("expected_duration", 1),
                emotional_intensity=step_data.get("emotional_intensity", 0.5),
                archetype=step_data.get("archetype"),
                branching_options=step_data.get("branching_options", []),
                rewards=step_data.get("rewards", {}),
                difficulty_modifier=step_data.get("difficulty_modifier", 1.0),
                narrative_weight=step_data.get("narrative_weight", 1.0),
                hidden_objectives=step_data.get("hidden_objectives"),
                completed=step_data.get("completed", False),
                completion_time=datetime.fromisoformat(step_data["completion_time"]) if step_data.get("completion_time") else None,
                actual_outcome=step_data.get("actual_outcome"),
                unexpected_events=step_data.get("unexpected_events", []),
                player_choice_made=step_data.get("player_choice_made"),
                performance_rating=step_data.get("performance_rating"),
                rewards_earned=step_data.get("rewards_earned", {})
            )
            reconstructed_plan.append(step)
        
        data['current_plan'] = reconstructed_plan
        # Reconstruct start_time if present
        if "start_time" in data and isinstance(data["start_time"], str):
            data["start_time"] = datetime.fromisoformat(data["start_time"])

        return cls(**data)