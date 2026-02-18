from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class CharacterType(str, Enum):
    """Types of Characters in the game"""
    HERO = "hero"
    VILLAIN = "villain"
    MENTOR = "mentor"
    RIVAL = "rival"
    ALLY = "ally"
    NEUTRAL = "neutral"


class Transformation(BaseModel):
    """Transformations that characters can undergo"""
    name: str
    power_multiplier: float = Field(default=1.0, ge=1.0)
    energy_cost: int = Field(default=20, ge=0)
    description: str = ""
    unlocked: bool = Field(default=False)


class Technique(BaseModel):
    """Techniques or Abilities that characters can have"""
    name: str
    power: int = Field(default=10, ge=1)
    energy_cost: int = Field(default=5, ge=0)
    description: str = ""
    unlocked: bool = Field(default=True)

class Character(BaseModel):
    """Character model representing players and NPCs"""
    name: str
    character_type: CharacterType
    base_power: int = Field(default=100, ge=1)
    current_power: Optional[int] = None
    health: int = Field(default=100, ge=0, le=100)
    max_health: int = Field(default=100, ge=1)
    energy: int = Field(default=100, ge=0, le=100)

    personality: Dict[str, float] = Field(
        default_factory=lambda: {
            "bravery": 0.5,
            "intelligence": 0.5,
            "kindness": 0.5,
            "aggressiveness": 0.5,
            "pride": 0.5,
            "determination": 0.5
        }
    )

    transformations: List[Transformation] = Field(default_factory=list)
    techniques: List[Technique] = Field(default_factory=list)
    current_transformation: Optional[str] = Field(default=None)

    # FIXED: Changed from Dict[str, str] to Dict[str, int] for numeric relationships
    relationships: Dict[str, int] = Field(
        default_factory=dict,
        description="Relationships with other characters (e.g., {'Goku': 50, 'Vegeta': -30})"
    )

    inventory: List[str] = Field(default_factory=list, description="Items the character possesses")
    backstory: str = Field(default="", description="A brief backstory of the character")
    goals: List[str] = Field(default_factory=list, description="Character's goals and motivations")

    def __init__(self, **data):
        super().__init__(**data)
        # IF current power is not provided, set it to base power
        if self.current_power is None:
            self.current_power = self.base_power
    
    def transform(self, transformation_name: str) -> bool:
        """Attempt to transform the character using a named transformation"""
        for transformation in self.transformations:
            if transformation_name == transformation.name and transformation.unlocked:
                if self.energy >= transformation.energy_cost:
                    self.current_power = int(self.base_power * transformation.power_multiplier)
                    self.current_transformation = transformation_name
                    self.energy -= transformation.energy_cost
                    return True
        return False

#     To understand this, you first need to know what __init__ does: it is the "Birth Function" of a class. Every time you create a new character or game state, Python runs __init__ to set everything up.

# Here is the breakdown of those three lines:

# 1. def __init__(self, **data):

# self: Refers to the specific object being born (e.g., "this specific Hero").

# **data: This is a "catch-all" bucket. It says: "Take any information given to me (like name, age, or power) and put it into a dictionary called data."

# 2. super().__init__(**data)

# The "Super" Parent: Because your class starts with class GameState(BaseModel):, it is a "child" of Pydantic’s BaseModel.

# The Logic: This line says: "Hey Pydantic (the parent), do your normal job first." It tells Pydantic to validate the data, check types, and set up all the fields you defined.

# Why it's necessary: If you forget this line, the "Bouncer" (Pydantic) never gets to do his job, and your class won't work properly.

# 3. The Custom Logic (The "Sync" Step)

# The Logic: This is a safety check that happens immediately after the object is created.

# The Purpose: It ensures that a character never starts with "None" (empty) power. If you didn't specifically say what the current_power is, the code automatically sets it to match the base_power.

# Simple English Example

# Imagine you are creating a "Warrior" class. Every warrior has a Max Health and a Current Health.

# When should you use this?

# Use this pattern whenever you have dependent variables.

# If you want current_mana to equal max_mana at the start.

# If you want the display_name to equal the username by default.

# It’s a way to make your class "smart" so it fills in the blanks for you.

    def take_damage(self, damage: int):
        """Apply damage to the character and reduce health"""
        self.health = max(0, self.health - damage)
        if self.health == 0:
            self.current_power = 0
            self.current_transformation = None
    
    def heal(self, amount: int):
        """Heal the character by a certain amount"""
        self.health = min(self.max_health, self.health + amount)
        if self.health > 0 and self.current_power == 0:
            self.current_power = self.base_power
    
    # FIXED: Changed parameter type from str to int
    def update_relationship(self, character_name: str, change: int):
        """Update relationship status with another character (positive = friendly, negative = hostile)"""
        current_relationship = self.relationships.get(character_name, 0)
        new_relationship = max(-100, min(100, current_relationship + change))
        self.relationships[character_name] = new_relationship





# This is a concept in Python called Inheritance.

# Think of it like DNA: the Player class is the "child" and the Character class is the "parent." Because of that little line class Player(Character):, the Player automatically "inherits" every single thing the Character has—all the variables, all the logic, and all the methods.

# 1. How is Player using Character?
# When you create a Player object, it isn't just a list of XP and levels. It is a full Character plus extra features.

# Imagine a Stack of Layers:

# The Bottom Layer (Character): Has name, health, power, and methods like take_damage() and transform().

# The Top Layer (Player): Sits right on top and adds experience, level, and gain_experience().

# Because they are stacked, a Player can do anything a Character can do, but a Character cannot do "Player things" (like leveling up).

# 2. A "Real-World" Example
# Let's see how this looks when you actually run the code in your project:

# 3. Why do we do it this way?
# You might ask: "Why not just put everything in one big class?"

# Reuse (The NPC Factor): You will likely have many NPCs (Villains, Mentors, Shopkeepers). They need health, power, and names, but they don't need XP or levels. By using inheritance, you create the Character once and use it for everyone.

# Organization: It keeps the "Universal Rules" (like taking damage) separate from the "Special Rules" (like leveling up).

# 4. Key Logic Points to Remember
# The __init__ Chain

# When you create a Player, it still runs the __init__ we talked about earlier.

# It runs super().__init__(**data) (Pydantic setup).

# It checks if current_power is None.

# It sets current_power = base_power.

# Even though that code is in the Character class, it runs perfectly for the Player.

# Method Interaction

# In your level_up method:

# The Player reaches down into the Character layer to update those stats.

# Summary for your Project
# In your LangGraph state, you might store the user as a Player object and the enemies as Character objects.

# If you call enemy.take_damage(10), it works.

# If you call player.take_damage(10), it also works because the Player is a Character.

class Player(Character):
    """Player character with additional features like experience and leveling"""
    experience: int = Field(default=0, ge=0)
    level: int = Field(default=1, ge=1)
    skill_points: int = Field(default=0, ge=0)
    quests_completed: List[str] = Field(default_factory=list)

    def gain_experience(self, xp: int):
        """Gain experience and handle leveling up"""
        self.experience += xp
        required_xp = self.level * 100

        while self.experience >= required_xp:
            self.level_up()
            self.experience = self.experience - required_xp
            required_xp = self.level * 100
    
    def level_up(self):
        """Level up the player and increase stats and grants bonus skill points"""
        self.level += 1
        self.skill_points += 5
        self.base_power += 20
        self.max_health += 20
        self.health = self.max_health
        self.current_power = self.base_power
    

class NPC(Character):
    """Non-Player Character with AI behavior and quest-giving capabilities"""
    # FIXED: Renamed from DIALOGUE_patterns to dialogue_patterns (Python convention)
    ai_personality: str = Field(default="neutral", description="AI personality type for the NPC")
    dialogue_patterns: List[str] = Field(default_factory=list, description="Common dialogue patterns for the NPC")
    quests_given: List[str] = Field(default_factory=list, description="Quests that the NPC can give to the player")
    location: str = Field(default="", description="Current location of the NPC in the game world")
    is_alive: bool = Field(default=True, description="Whether the NPC is alive or not")

    # return NPC(
    #     name=character.name,
    #     character_type=character.character_type,
    #     base_power=character.base_power,
    #     current_power=character.current_power,
    #     health=character.health,
    #     max_health=character.max_health,
    #     energy=character.energy,
    #     personality=character.personality,
    #     transformations=character.transformations,
    #     techniques=character.techniques,
    #     relationships=character.relationships,
    #     inventory=character.inventory,
    #     backstory=character.backstory,
    #     goals=character.goals,
    #     ai_personality=ai_personality,
    #     DIALOGUE_patterns=DIALOGUE_patterns,
    #     quests_given=quests_given,
    #     location=location,
    #     is_alive=is_alive
    # )