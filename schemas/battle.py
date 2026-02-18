
"""
⚔️ BATTLE SCHEMA - The Heart of Combat! ⚔️

This module defines all the data structures needed for epic DBZ-style battles:
- Turn-based combat
- Special moves and transformations
- Power level calculations
- Battle logs and history
- Victory/defeat conditions
"""

from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from enum import Enum


class BattleStatus(str, Enum):
    """Current state of the battle"""
    ACTIVE = "active"
    PAUSED = "paused"
    PLAYER_VICTORY = "player_victory"
    PLAYER_DEFEAT = "player_defeat"
    ESCAPED = "escaped"
    INTERRUPTED = "interrupted"


class BattleActionType(str, Enum):
    """Types of actions a player can take in battle"""
    ATTACK = "attack"
    DEFEND = "defend"
    SPECIAL_MOVE = "special_move"
    TRANSFORM = "transform"
    CHARGE = "charge"
    ITEM = "item"
    ESCAPE = "escape"
    FUSE = "fuse"  # DBZ-style fusion!
    SURRENDER = "surrender"


class AttackType(str, Enum):
    """Different types of attacks"""
    PHYSICAL = "physical"
    KI_BLAST = "ki_blast"
    ENERGY_BEAM = "energy_beam"
    EXPLOSIVE = "explosive"
    PRECISION = "precision"
    AREA_EFFECT = "area_effect"


class SpecialMove(BaseModel):
    """A special technique usable in battle"""
    name: str = Field(..., description="Name of the move (e.g., 'Kamehameha')")
    attack_type: AttackType
    base_power: int = Field(default=50, ge=10, le=1000)
    ki_cost: int = Field(default=20, ge=0, le=100)
    description: str = Field(default="")
    charge_time: int = Field(default=0, ge=0, le=3, description="Turns needed to charge")
    is_unlocked: bool = Field(default=True)
    cooldown: int = Field(default=0, ge=0, le=5, description="Turns before reuse")
    current_cooldown: int = Field(default=0, ge=0)
    
    # ✨ DBZ Special: Multiplier effects
    power_multiplier: float = Field(default=1.0, ge=0.5, le=10.0)
    accuracy: float = Field(default=0.9, ge=0.0, le=1.0)
    critical_chance: float = Field(default=0.05, ge=0.0, le=0.5)
    
    def can_use(self) -> bool:
        """Check if move is available"""
        return self.is_unlocked and self.current_cooldown == 0
    
    def use_move(self) -> int:
        """Use the move and start cooldown"""
        if self.can_use():
            self.current_cooldown = self.cooldown
            return int(self.base_power * self.power_multiplier)
        return 0
    
    def reduce_cooldown(self):
        """Reduce cooldown by 1 (called each turn)"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1


class Transformation(BaseModel):
    """Battle transformation state"""
    name: str = Field(..., description="Transformation name (e.g., 'Super Saiyan')")
    power_multiplier: float = Field(default=50.0, ge=1.0, le=1000.0)
    ki_cost: int = Field(default=50, ge=0)
    duration: int = Field(default=5, ge=1, description="Turns transformation lasts")
    turns_remaining: int = Field(default=0)
    is_active: bool = Field(default=False)
    requirements: Dict[str, Any] = Field(default_factory=dict)
    
    def activate(self):
        """Activate the transformation"""
        self.is_active = True
        self.turns_remaining = self.duration
    
    def deactivate(self):
        """Deactivate the transformation"""
        self.is_active = False
        self.turns_remaining = 0
    
    def tick(self) -> bool:
        """Process one turn, return True if still active"""
        if self.is_active and self.turns_remaining > 0:
            self.turns_remaining -= 1
            if self.turns_remaining == 0:
                self.deactivate()
                return False
            return True
        return False


class BattleParticipant(BaseModel):
    """Represents a single combatant in the battle"""
    name: str = Field(..., description="Character name")
    power_level: int = Field(default=1000, ge=1)
    max_health: int = Field(default=100, ge=1)
    current_health: int = Field(default=100, ge=0)
    max_ki: int = Field(default=100, ge=1)
    current_ki: int = Field(default=100, ge=0)
    
    # Combat stats
    attack: int = Field(default=50, ge=1)
    defense: int = Field(default=50, ge=1)
    speed: int = Field(default=50, ge=1)
    accuracy: float = Field(default=0.9, ge=0.0, le=1.0)
    evasion: float = Field(default=0.1, ge=0.0, le=0.5)
    
    # Battle state
    is_defending: bool = Field(default=False)
    defense_multiplier: float = Field(default=1.0, ge=0.5, le=2.0)
    attack_multiplier: float = Field(default=1.0, ge=0.5, le=2.0)
    
    # Special moves and transformations
    special_moves: List[SpecialMove] = Field(default_factory=list)
    active_transformation: Optional[Transformation] = Field(default=None)
    
    # Status effects
    status_effects: Dict[str, int] = Field(
        default_factory=dict,
        description="Status effects and their remaining turns"
    )
    
    # Battle history
    actions_taken: List[str] = Field(default_factory=list)
    damage_dealt: int = Field(default=0)
    damage_taken: int = Field(default=0)
    
    @field_validator('current_health')
    @classmethod
    def validate_health(cls, v: int, info: Any) -> int:
        """Ensure health doesn't go negative"""
        return max(0, v)
    
    @field_validator('current_ki')
    @classmethod
    def validate_ki(cls, v: int, info: Any) -> int:
        """Ensure ki doesn't go negative"""
        return max(0, v)
    
    def take_damage(self, damage: int) -> int:
        """Apply damage considering defense, return actual damage taken"""
        if self.is_defending:
            damage = int(damage * 0.5)  # 50% reduction when defending
        
        # Apply defense stat
        damage = max(1, int(damage * (100 / (100 + self.defense))))
        
        actual_damage = min(self.current_health, damage)
        self.current_health -= actual_damage
        self.damage_taken += actual_damage
        
        return actual_damage
    
    def use_ki(self, amount: int) -> bool:
        """Use ki, return True if successful"""
        if self.current_ki >= amount:
            self.current_ki -= amount
            return True
        return False
    
    def regenerate_ki(self, amount: int = 5):
        """Regenerate ki each turn"""
        self.current_ki = min(self.max_ki, self.current_ki + amount)
    
    def has_special_move(self, move_name: str) -> bool:
        """Check if character has a specific special move"""
        return any(move.name == move_name for move in self.special_moves)
    
    def get_special_move(self, move_name: str) -> Optional[SpecialMove]:
        """Get a special move by name"""
        for move in self.special_moves:
            if move.name == move_name:
                return move
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "power_level": self.power_level,
            "current_health": self.current_health,
            "max_health": self.max_health,
            "current_ki": self.current_ki,
            "max_ki": self.max_ki,
            "is_defending": self.is_defending,
            "active_transformation": self.active_transformation.name if self.active_transformation else None,
            "health_percentage": self.current_health / self.max_health if self.max_health > 0 else 0
        }


class BattleTurn(BaseModel):
    """Records a single turn in the battle"""
    turn_number: int
    participant_name: str
    action_type: BattleActionType
    action_description: str
    damage_dealt: int = 0
    damage_taken: int = 0
    ki_used: int = 0
    special_move_used: Optional[str] = None
    transformation_used: Optional[str] = None
    critical_hit: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)


class BattleRewards(BaseModel):
    """Rewards for winning a battle"""
    experience_points: int = Field(default=100, ge=0)
    zeni: int = Field(default=1000, ge=0)  # DBZ currency
    items: List[str] = Field(default_factory=list)
    techniques_unlocked: List[str] = Field(default_factory=list)
    transformations_unlocked: List[str] = Field(default_factory=list)
    relationship_changes: Dict[str, int] = Field(default_factory=dict)
    story_flags_unlocked: List[str] = Field(default_factory=list)


class BattleState(BaseModel):
    """
    ⚔️ THE BATTLE STATE - Complete battle management ⚔️
    
    Tracks everything about an ongoing battle:
    - Participants (player and opponents)
    - Turn order and current turn
    - Battle history and logs
    - Special conditions
    - Victory/defeat status
    """
    
    # Battle identification
    battle_id: str = Field(default_factory=lambda: f"battle_{datetime.now().timestamp()}")
    battle_name: str = Field(default="Epic Showdown")
    
    # Participants
    player: BattleParticipant
    opponents: List[BattleParticipant] = Field(default_factory=list)
    allies: List[BattleParticipant] = Field(default_factory=list)
    
    # Battle status
    status: BattleStatus = Field(default=BattleStatus.ACTIVE)
    current_turn: int = Field(default=0, ge=0)
    current_participant_index: int = Field(default=0, ge=0)
    
    # Turn order (list of participant names in order)
    turn_order: List[str] = Field(default_factory=list)
    
    # Battle history
    turn_history: List[BattleTurn] = Field(default_factory=list)
    battle_log: List[str] = Field(default_factory=list)
    
    # Battle modifiers
    terrain: str = Field(default="plains", description="Battle location (plains, wasteland, space, etc.)")
    terrain_effect: float = Field(default=1.0, ge=0.5, le=2.0)
    time_limit: Optional[int] = Field(default=None, description="Max turns before special outcome")
    
    # Special battle conditions
    is_tag_team: bool = Field(default=False, description="Whether allies/opponents can switch")
    can_escape: bool = Field(default=True)
    can_fuse: bool = Field(default=False, description="Whether fusion is possible")
    dramatic_finish_required: bool = Field(default=False, description="Need special move to win")
    
    # Rewards
    rewards: BattleRewards = Field(default_factory=BattleRewards)
    
    # Battle results
    winner: Optional[str] = Field(default=None)
    loser: Optional[str] = Field(default=None)
    battle_duration_seconds: Optional[float] = Field(default=None)
    end_time: Optional[datetime] = Field(default=None)
    
    class Config:
        arbitrary_types_allowed = True
    
    @property
    def all_participants(self) -> List[BattleParticipant]:
        """Get all participants in the battle"""
        participants = [self.player] + self.allies + self.opponents
        return participants
    
    @property
    def active_opponents(self) -> List[BattleParticipant]:
        """Get opponents that are still alive"""
        return [opp for opp in self.opponents if opp.current_health > 0]
    
    @property
    def active_allies(self) -> List[BattleParticipant]:
        """Get allies that are still alive"""
        return [ally for ally in self.allies if ally.current_health > 0]
    
    @property
    def player_alive(self) -> bool:
        """Check if player is alive"""
        return self.player.current_health > 0
    
    @property
    def battle_over(self) -> bool:
        """Check if battle has ended"""
        if self.status != BattleStatus.ACTIVE:
            return True
        
        # Check win conditions
        if not self.active_opponents:
            self.status = BattleStatus.PLAYER_VICTORY
            return True
        
        # Check lose conditions
        if not self.player_alive and not self.active_allies:
            self.status = BattleStatus.PLAYER_DEFEAT
            return True
        
        return False
    
    @property
    def current_participant(self) -> Optional[BattleParticipant]:
        """Get the participant whose turn it is"""
        if not self.turn_order or self.current_participant_index >= len(self.turn_order):
            return None
        
        current_name = self.turn_order[self.current_participant_index]
        
        # Find participant by name
        for participant in self.all_participants:
            if participant.name == current_name:
                return participant
        return None
    
    def calculate_turn_order(self):
        """Calculate turn order based on speed"""
        # Sort by speed (highest first)
        sorted_participants = sorted(
            self.all_participants,
            key=lambda p: p.speed,
            reverse=True
        )
        self.turn_order = [p.name for p in sorted_participants]
        self.current_participant_index = 0
    
    def next_turn(self) -> bool:
        """Advance to next turn, return True if battle continues"""
        if self.battle_over:
            return False
        
        self.current_participant_index += 1
        
        # If we've gone through all participants, start new round
        if self.current_participant_index >= len(self.turn_order):
            self.current_participant_index = 0
            self.current_turn += 1
            self._process_end_of_round()
        
        return not self.battle_over
    
    def _process_end_of_round(self):
        """Process end-of-round effects"""
        # Regenerate ki for all participants
        for participant in self.all_participants:
            participant.regenerate_ki()
            
            # Reduce cooldowns
            for move in participant.special_moves:
                move.reduce_cooldown()
            
            # Process transformation duration
            if participant.active_transformation:
                still_active = participant.active_transformation.tick()
                if not still_active:
                    participant.active_transformation = None
        
        self.add_to_log(f"--- Round {self.current_turn} End ---")
    
    def add_turn_record(self, turn: BattleTurn):
        """Add a turn to history"""
        self.turn_history.append(turn)
        self.add_to_log(f"Turn {turn.turn_number}: {turn.action_description}")
    
    def add_to_log(self, message: str):
        """Add a message to battle log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.battle_log.append(f"[{timestamp}] {message}")
    
    def calculate_damage(self, 
                        attacker: BattleParticipant, 
                        defender: BattleParticipant,
                        move: Optional[SpecialMove] = None) -> int:
        """Calculate damage for an attack"""
        base_power = move.base_power if move else attacker.attack
        
        # Apply multipliers
        attack_power = base_power * attacker.attack_multiplier
        defense_power = defender.defense * defender.defense_multiplier
        
        # Power level difference matters in DBZ!
        power_ratio = attacker.power_level / max(defender.power_level, 1)
        power_bonus = max(0.5, min(2.0, power_ratio))
        
        # Random factor (80-120%)
        import random
        random_factor = random.uniform(0.8, 1.2)
        
        # Check for critical hit
        is_critical = random.random() < (move.critical_chance if move else 0.05)
        critical_multiplier = 2.0 if is_critical else 1.0
        
        damage = int(attack_power * power_bonus * random_factor * critical_multiplier / defense_power)
        
        return max(1, damage)  # Minimum 1 damage
    
    def process_action(self, 
                      action_type: BattleActionType,
                      target_name: Optional[str] = None,
                      move_name: Optional[str] = None,
                      item_name: Optional[str] = None) -> Dict[str, Any]:
        """Process a battle action and return result"""
        
        current = self.current_participant
        if not current:
            return {"error": "No current participant"}
        
        # Find target
        target = None
        if target_name:
            for participant in self.all_participants:
                if participant.name == target_name:
                    target = participant
                    break
        
        result = {
            "action_type": action_type,
            "participant": current.name,
            "target": target.name if target else None,
            "damage_dealt": 0,
            "damage_taken": 0,
            "special_message": "",
            "success": True
        }
        
        # Process based on action type
        if action_type == BattleActionType.ATTACK:
            if not target:
                result["success"] = False
                result["special_message"] = "No target selected"
            else:
                # Regular attack
                damage = self.calculate_damage(current, target)
                actual_damage = target.take_damage(damage)
                
                result["damage_dealt"] = actual_damage
                result["special_message"] = f"{current.name} attacks {target.name} for {actual_damage} damage!"
                
                # Add to turn history
                turn = BattleTurn(
                    turn_number=self.current_turn,
                    participant_name=current.name,
                    action_type=action_type,
                    action_description=f"Attacked {target.name} for {actual_damage} damage",
                    damage_dealt=actual_damage
                )
                self.add_turn_record(turn)
        
        elif action_type == BattleActionType.DEFEND:
            current.is_defending = True
            result["special_message"] = f"{current.name} takes a defensive stance!"
            
            turn = BattleTurn(
                turn_number=self.current_turn,
                participant_name=current.name,
                action_type=action_type,
                action_description="Takes defensive stance"
            )
            self.add_turn_record(turn)
        
        elif action_type == BattleActionType.SPECIAL_MOVE:
            if not move_name or not target:
                result["success"] = False
                result["special_message"] = "Invalid special move or target"
            else:
                move = current.get_special_move(move_name)
                if move and move.can_use() and current.use_ki(move.ki_cost):
                    damage = self.calculate_damage(current, target, move)
                    actual_damage = target.take_damage(damage)
                    
                    move.use_move()  # Start cooldown
                    
                    result["damage_dealt"] = actual_damage
                    result["special_message"] = f"{current.name} uses {move_name}! {actual_damage} damage!"
                    
                    turn = BattleTurn(
                        turn_number=self.current_turn,
                        participant_name=current.name,
                        action_type=action_type,
                        action_description=f"Used {move_name} on {target.name} for {actual_damage} damage",
                        damage_dealt=actual_damage,
                        ki_used=move.ki_cost,
                        special_move_used=move_name
                    )
                    self.add_turn_record(turn)
                else:
                    result["success"] = False
                    result["special_message"] = f"Cannot use {move_name} (no ki or on cooldown)"
        
        elif action_type == BattleActionType.CHARGE:
            ki_gained = 20
            current.regenerate_ki(ki_gained)
            result["special_message"] = f"{current.name} charges ki! +{ki_gained} ki"
            
            turn = BattleTurn(
                turn_number=self.current_turn,
                participant_name=current.name,
                action_type=action_type,
                action_description=f"Charged ki, gained {ki_gained} ki"
            )
            self.add_turn_record(turn)
        
        elif action_type == BattleActionType.ESCAPE:
            if self.can_escape:
                # 50% chance to escape
                import random
                if random.random() > 0.5:
                    self.status = BattleStatus.ESCAPED
                    result["special_message"] = f"{current.name} escaped from battle!"
                    result["battle_ended"] = True
                else:
                    result["special_message"] = f"{current.name} failed to escape!"
                
                turn = BattleTurn(
                    turn_number=self.current_turn,
                    participant_name=current.name,
                    action_type=action_type,
                    action_description=result["special_message"]
                )
                self.add_turn_record(turn)
            else:
                result["success"] = False
                result["special_message"] = "Cannot escape from this battle!"
        
        return result
    
    def end_battle(self, winner: str):
        """End the battle and record results"""
        self.winner = winner
        self.loser = self.player.name if winner != self.player.name else self.opponents[0].name if self.opponents else "Unknown"
        self.end_time = datetime.now()
        self.battle_duration_seconds = (self.end_time - datetime.now()).total_seconds() * -1  # Fix negative
        
        if winner == self.player.name:
            self.status = BattleStatus.PLAYER_VICTORY
        else:
            self.status = BattleStatus.PLAYER_DEFEAT
        
        self.add_to_log(f"🏆 BATTLE ENDED! Winner: {winner}")
    
    def get_battle_summary(self) -> Dict[str, Any]:
        """Get a summary of the battle for UI display"""
        return {
            "battle_name": self.battle_name,
            "status": self.status.value,
            "current_turn": self.current_turn,
            "player": self.player.to_dict(),
            "opponents": [opp.to_dict() for opp in self.opponents],
            "allies": [ally.to_dict() for ally in self.allies],
            "active_opponents": len(self.active_opponents),
            "active_allies": len(self.active_allies),
            "player_alive": self.player_alive,
            "battle_over": self.battle_over,
            "turn_order": self.turn_order,
            "current_participant": self.current_participant.name if self.current_participant else None,
            "recent_log": self.battle_log[-5:] if self.battle_log else []
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "battle_id": self.battle_id,
            "battle_name": self.battle_name,
            "status": self.status.value,
            "current_turn": self.current_turn,
            "player": self.player.dict(),
            "opponents": [opp.dict() for opp in self.opponents],
            "allies": [ally.dict() for ally in self.allies],
            "turn_history": [turn.dict() for turn in self.turn_history],
            "battle_log": self.battle_log,
            "terrain": self.terrain,
            "winner": self.winner,
            "loser": self.loser,
            "rewards": self.rewards.dict() if self.rewards else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BattleState":
        """Create BattleState from dictionary"""
        # Reconstruct participants
        player_data = data.get("player", {})
        player = BattleParticipant(**player_data)
        
        opponents = [BattleParticipant(**opp) for opp in data.get("opponents", [])]
        allies = [BattleParticipant(**ally) for ally in data.get("allies", [])]
        
        # Reconstruct turns
        turn_history = [BattleTurn(**turn) for turn in data.get("turn_history", [])]
        
        # Create instance
        battle = cls(
            battle_id=data.get("battle_id", f"battle_{datetime.now().timestamp()}"),
            battle_name=data.get("battle_name", "Epic Showdown"),
            player=player,
            opponents=opponents,
            allies=allies,
            status=BattleStatus(data.get("status", "active")),
            current_turn=data.get("current_turn", 0),
            turn_history=turn_history,
            battle_log=data.get("battle_log", []),
            terrain=data.get("terrain", "plains"),
            winner=data.get("winner"),
            loser=data.get("loser")
        )
        
        return battle


class BattleAction(BaseModel):
    """
    🎮 PLAYER BATTLE ACTION - What the player chooses to do
    
    This is what gets passed from the UI to the battle system
    """
    action_type: BattleActionType
    target_name: Optional[str] = None
    move_name: Optional[str] = None
    item_name: Optional[str] = None
    transformation_name: Optional[str] = None
    
    @classmethod
    def attack(cls, target: str) -> "BattleAction":
        """Create an attack action"""
        return cls(action_type=BattleActionType.ATTACK, target_name=target)
    
    @classmethod
    def defend(cls) -> "BattleAction":
        """Create a defend action"""
        return cls(action_type=BattleActionType.DEFEND)
    
    @classmethod
    def special_move(cls, move: str, target: str) -> "BattleAction":
        """Create a special move action"""
        return cls(
            action_type=BattleActionType.SPECIAL_MOVE,
            move_name=move,
            target_name=target
        )
    
    @classmethod
    def charge(cls) -> "BattleAction":
        """Create a charge action"""
        return cls(action_type=BattleActionType.CHARGE)
    
    @classmethod
    def escape(cls) -> "BattleAction":
        """Create an escape action"""
        return cls(action_type=BattleActionType.ESCAPE)
    
    @classmethod
    def transform(cls, transformation: str) -> "BattleAction":
        """Create a transform action"""
        return cls(
            action_type=BattleActionType.TRANSFORM,
            transformation_name=transformation
        )


# =========================================================================
# FACTORY FUNCTIONS
# =========================================================================

def create_test_battle(player_name: str = "Goku", opponent_name: str = "Vegeta") -> BattleState:
    """Create a test battle for development"""
    
    # Create player
    player = BattleParticipant(
        name=player_name,
        power_level=9000,
        max_health=100,
        current_health=100,
        max_ki=100,
        current_ki=100,
        attack=80,
        defense=70,
        speed=75,
        special_moves=[
            SpecialMove(
                name="Kamehameha",
                attack_type=AttackType.KI_BLAST,
                base_power=200,
                ki_cost=30,
                description="The legendary Kamehameha wave!",
                power_multiplier=2.0,
                critical_chance=0.1
            ),
            SpecialMove(
                name="Dragon Fist",
                attack_type=AttackType.PHYSICAL,
                base_power=150,
                ki_cost=20,
                description="A devastating punch!",
                accuracy=0.95
            )
        ]
    )
    
    # Create opponent
    opponent = BattleParticipant(
        name=opponent_name,
        power_level=8500,
        max_health=100,
        current_health=100,
        max_ki=100,
        current_ki=100,
        attack=75,
        defense=75,
        speed=80,
        special_moves=[
            SpecialMove(
                name="Galick Gun",
                attack_type=AttackType.ENERGY_BEAM,
                base_power=190,
                ki_cost=30,
                description="Vegeta's signature attack!",
                power_multiplier=1.9
            ),
            SpecialMove(
                name="Final Flash",
                attack_type=AttackType.EXPLOSIVE,
                base_power=250,
                ki_cost=40,
                description="Vegeta's ultimate technique!",
                cooldown=3
            )
        ]
    )
    
    # Create battle
    battle = BattleState(
        battle_name=f"{player_name} vs {opponent_name}",
        player=player,
        opponents=[opponent]
    )
    
    # Calculate initial turn order
    battle.calculate_turn_order()
    
    return battle


# =========================================================================
# EXAMPLE USAGE
# =========================================================================

if __name__ == "__main__":
    """Example of how to use the battle system"""
    
    # Create a test battle
    battle = create_test_battle("Goku", "Vegeta")
    
    print(f"⚔️ BATTLE START: {battle.battle_name}")
    print(f"Turn order: {battle.turn_order}")
    
    # Simulate a few turns
    while not battle.battle_over and battle.current_turn < 5:
        current = battle.current_participant
        if not current:
            break
        
        print(f"\n--- Turn {battle.current_turn}, {current.name}'s turn ---")
        
        # Simple AI: if player's turn, use special move; if opponent, attack
        if current.name == "Goku":
            result = battle.process_action(
                action_type=BattleActionType.SPECIAL_MOVE,
                target_name="Vegeta",
                move_name="Kamehameha"
            )
        else:
            result = battle.process_action(
                action_type=BattleActionType.ATTACK,
                target_name="Goku"
            )
        
        print(result["special_message"])
        
        # Next turn
        battle.next_turn()
    
    print("\n" + "="*50)
    print("BATTLE SUMMARY:")
    summary = battle.get_battle_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")