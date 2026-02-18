from typing import Dict, Any, List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
import json
import random
from schemas.state import GameState, SceneType, PlanStep
from utils.llm_wrapper import llm_wrapper
from utils.prompts import SystemPrompts
import traceback
from datetime import datetime

class ExecutorConfig:
    """Configuration constants for ExecutorAgent"""
    
    # Power thresholds for transformations
    TRANSFORMATION_THRESHOLDS = [9000, 18000, 50000, 100000, 500000]
    TRANSFORMATION_NAMES = ["Super Saiyan", "Super Saiyan 2", "Super Saiyan 3", "Super Saiyan God", "Ultra Instinct"]
    
    # Power gain multipliers
    POWER_GAIN = {
        SceneType.TRAINING: (20, 100),
        SceneType.BATTLE: (50, 200),
        SceneType.CLIMAX: (200, 500),
        "default": (10, 50)
    }
    
    # Ki gain amounts
    KI_GAIN = {
        SceneType.TRAINING: (5, 10),
        "default": (1, 5)
    }

class ExecutorAgent:
    """
    The ExecutorAgent is responsible for executing a single scene step based on the current game state and player action.
    It uses the LLM to generate the next scene and updates the game state accordingly.
    """

    def __init__(self):
        # Iniitialize templates for fallback or stylistic guidance
        self.scene_templates = self._load_scene_templates()

    # def invoke(self,
    #            state: GameState,
    #            player_action: Optional[str] = None) -> Dict[str, Any]:
    #     """🎭 EXECUTE A SINGLE SCENE 🎭
        
    #     Takes the current game state and optional player action, then:
    #     1. Validates the current plan step
    #     2. Prepares rich narrative context
    #     3. Generates a dynamic scene using LLM or templates
    #     4. Updates game state based on outcomes
    #     5. Creates an immersive message for the player
        
    #     Args:
    #         state: Current game state with plan, stats, world flags
    #         player_action: Optional text of what the player wants to do
            
    #     Returns:
    #         Dictionary of state updates to apply
    #     """

    #     print(f"🎬 EXECUTOR: Bringing Act {state.plan_step_index + 1} to life...")

    #     # 1. Validation: Ensure we have a valid plan step to execute
    #     current_step = state.current_step

    #     if not current_step:
    #         print("No current plan step found. Executor cannot proceed.")
    #         return {
    #             "error_message": "The story has reached an unexpected state where there is no current step to execute",
    #             "should_continue": False
    #         }
    
    #     try:
    #         # 2. Context preperation: Gather stats, NPCs, history, and plot threads

    #         context = self._prepare_context(state, current_step, player_action)

    #         # 3. Character Interaction: Determine which NPCs are present and their moods
    #         characters = self._prepare_characters(state, current_step)

    #         # 4. Scene Generation: Use LLM or fallback templates to create the scene
    #         if self._should_use_llm(state):
    #             scene_data = self._generate_scene_with_llm(state, current_step, context, characters, player_action)
    #         else:
    #             scene_data = self._generate_scene_with_template(state, current_step, context, characters, player_action)
            
    #         # 5. Battle Resolution: If this was a battle scene handle combat outcomes
    #         if current_step.scene_type == SceneType.BATTLE or state.in_battle:
    #             scene_data = self._resolve_battle_outcome(state, scene_data, current_step)

    #         # 6. STate Evolution: Update stats based on scene outcomes
    #         state_updates = self._apply_current_state_updates(state, scene_data.get("state_updates", {}))

    #         # 7. Check for Transformations: Power threshold crossings
    #         if self._check_transformation_threshold(state, state_updates):
    #             scene_data['narrative'] += self._trigger_transformation_sequence(state, state_updates)
    #             state_updates['world_flags']['transformation_updates'] = True
            
    #         # 8. Mark Progress: Update the PlanStep with actual outcome
    #         current_step.mark_completed(
    #             outcome=scene_data.get("narration", "A decisive moment passed"),
    #             unexpected=scene_data.get("unexpected_events", [])
    #         )

    #         # 9 Generate Branching Options: If appropriate, create choices for next step
    #         branching_options = self._generate_next_choices(scene_data, current_step, state)

    #         # 10. Message Creation: The final immersive text shown to the player
    #         ai_message = self._create_cinematic_message(
    #             scene_data,
    #             current_step,
    #             characters,
    #             branching_options,
    #             state_updates
    #         )

    #         # 11. Determine if we should advance to next steps
    #         advance_plan = self._should_advance_plan(scene_data, current_step)

    #         print(f"✅ EXECUTOR: Scene complete! Power: {state_updates.get('player_stats', {}).get('power_level', '?')}")

    #         return{
    #             "message": ai_message,
    #             "current_plan": state.current_plan,
    #             "plan_step_index": state.plan_step_index + 1 if advance_plan else state.plan_step_index,
    #             "scene_counter": state.scene_counter +1,
    #             "player_stats": state_updates.get("player_stats", state.player_stats),
    #             "world_flags": state_updates.get("world_flags", state.world_flags),
    #             "npcs":state_updates.get("npcs", state.npcs),
    #             "in_battle":scene_data.get("in_battle", False),
    #             "battle_state":scene_data.get("battle_state"),
    #             "total_actions":state.total_actions + 1,
    #             "tokens_used": state.tokens_used + scene_data.get("tokens_used", 0),
    #             "should_continue": True
    #         }
        
    #     except Exception as e:
    #         print(f"❌ EXECUTOR CRASH: {str(e)}")
    #         traceback.print_exc()
    #         return self._create_error_scene(state, current_step, str(e), player_action)

    def invoke(self, state: GameState, player_action: Optional[str] = None) -> Dict[str, Any]:
        """🎭 EXECUTE A SINGLE SCENE 🎭"""
        
        print(f"\n{'🔥'*50}")
        print(f"🔥 EXECUTOR INVOKED - STEP {state.plan_step_index + 1}")
        print(f"{'🔥'*50}")
        print(f"Current plan length: {len(state.current_plan)}")
        print(f"Current step: {state.plan_step_index}")
        print(f"Player action: {player_action}")
        
        # 1. Validation: Ensure we have a valid plan step to execute
        current_step = state.current_step
        print(f"Current step object: {current_step}")

        if not current_step:
            print("❌ No current plan step found!")
            return {
                "error_message": "The story has reached an unexpected state where there is no current step to execute",
                "should_continue": False
            }
        
        print(f"✅ Valid step found: {current_step.description[:50]}...")
        
        try:
            # 2. Context preparation
            print("📝 Preparing context...")
            context = self._prepare_context(state, current_step, player_action)
            print(f"✅ Context prepared: {len(context)} keys")

            # 3. Character Interaction
            print("👥 Preparing characters...")
            characters = self._prepare_characters(state, current_step)
            print(f"✅ Characters prepared: {len(characters)} found")

            # 4. Scene Generation
            print("🎨 Generating scene...")
            if self._should_use_llm(state):
                print("🤖 Using LLM for scene generation")
                scene_data = self._generate_scene_with_llm(state, current_step, context, characters, player_action)
            else:
                print("📜 Using template for scene generation")
                scene_data = self._generate_scene_with_template(state, current_step, context, characters, player_action)
            
            print(f"✅ Scene generated: {scene_data.get('narration', 'No narration')[:100]}...")

            # 5. Battle Resolution
            if current_step.scene_type == SceneType.BATTLE or state.in_battle:
                print("⚔️ Resolving battle...")
                scene_data = self._resolve_battle_outcome(state, scene_data, current_step)
                print("✅ Battle resolved")

            # 6. State Evolution
            print("📊 Applying state updates...")
            state_updates = self._apply_current_state_updates(state, scene_data.get("state_updates", {}))
            print("✅ State updates applied")

            # 7. Check for Transformations
            if self._check_transformation_threshold(state, state_updates):
                print("✨ Transformation triggered!")
                scene_data['narrative'] += self._trigger_transformation_sequence(state, state_updates)
                state_updates['world_flags']['transformation_updates'] = True

            # 8. Mark Progress
            print("✅ Marking step as completed...")
            current_step.mark_completed(
                outcome=scene_data.get("narration", "A decisive moment passed"),
                unexpected=scene_data.get("unexpected_events", [])
            )

            # 9. Generate Branching Options
            print("🔀 Generating next choices...")
            branching_options = self._generate_next_choices(scene_data, current_step, state)

            # 10. Message Creation
            print("📝 Creating cinematic message...")
            ai_message = self._create_cinematic_message(
                scene_data,
                current_step,
                characters,
                branching_options,
                state_updates
            )

            # 11. Determine if we should advance
            advance_plan = self._should_advance_plan(scene_data, current_step)
            print(f"🔄 Advance plan: {advance_plan}")

            print(f"✅ EXECUTOR COMPLETE! Power: {state_updates.get('player_stats', {}).get('power_level', '?')}")

            return {
                "messages": ai_message,
                "current_plan": state.current_plan,
                "plan_step_index": state.plan_step_index + 1 if advance_plan else state.plan_step_index,
                "scene_counter": state.scene_counter + 1,
                "player_stats": state_updates.get("player_stats", state.player_stats),
                "world_flags": state_updates.get("world_flags", state.world_flags),
                "npcs": state_updates.get("npcs", state.npcs),
                "in_battle": scene_data.get("in_battle", False),
                "battle_state": scene_data.get("battle_state"),
                "total_actions": state.total_actions + 1,
                "tokens_used": state.tokens_used + scene_data.get("tokens_used", 0),
                "should_continue": True
            }
            
        except Exception as e:
            print(f"❌ EXECUTOR CRASH: {str(e)}")
            import traceback
            traceback.print_exc()
            return self._create_error_scene(state, current_step, str(e), player_action)
        
    # =========================================================================
    #  CONTEXT PREPARATION METHODS
    # =========================================================================

    def _prepare_context(self,
                         state: GameState,
                         step: PlanStep,
                         player_action: Optional[str] = None) -> Dict[str, Any]:
        """
         Gather all relevant context for scene generation
        
        Compiles:
        - Player stats and recent history
        - World flags and important events
        - Recent messages for continuity
        - Current plan context
        """

        context = state.get_context_for_llm()
        recent_messages = state.get_recent_messages()
        context.update({
        "recent_history": [msg.content for msg in recent_messages if hasattr(msg, 'content')],
        "plan_context": {
            "current_step_description": step.description,
            "expected_outcome": step.expected_outcome,
            "step_number": state.plan_step_index + 1,
            "total_steps": len(state.current_plan)
        },
        "scene_type": step.scene_type.value,
        "time_of_day": self._determine_time_of_day(state),
        "dramatic_tension": self._calculate_dramatic_tension(state, step)
    })
        if player_action:
            context["player_action"] = player_action
        
        return context
    
    def _prepare_characters(self, 
                            state: GameState, 
                            step: PlanStep) -> List[Dict[str, Any]]:
        """
        👥 Prepare character data for the scene
        
        Determines:
        - Which NPCs are present
        - Their current mood and relationship with player
        - Their power levels relative to player
        """
        characters = []

        # add required characters from plan step
        for char_name in step.required_characters:
            char_data = self._get_character_data(state, char_name)
            if char_data:
                characters.append(char_data)
        
        # add any characters from world state that makes sense
        if step.scene_type == SceneType.BATTLE and "rival" not in [c['name'] for c in characters]:
            rival_data = self._get_character_data(state, "rival")
            if rival_data:
                characters.append(rival_data)
        
        # add mentor for training
        if step.scene_type == SceneType.TRAINING and "mentor" not in [c['name'] for c in characters]:
            mentor_data = self._get_character_data(state, 'mentor')
            if mentor_data:
                characters.append(mentor_data)
        
        return characters
    
    def _get_character_data(self,
                            state: GameState,
                            character_key: str) -> Optional[Dict[str, Any]]:
        """🔍 Retrieve and enrich character data from state"""

        if character_key in state.npcs:
            npc = state.npcs[character_key]

            # calculate relationship based on past interactions
            relationship = self._calculate_relationship(state, character_key)

            # Determine mood based on scene type aand history
            mood = self._determine_character_mood(state, character_key)

            return{
                "key": character_key,
                "name": npc.get("name",character_key.title()),
                "power_level": npc.get("power_level", 1000),
                "alive": npc.get("alive", True),
                "relationship": relationship,
                "mood": mood,
                "description": npc.get("description", f"A mysterios {character_key}"),
                "last_interaction": self._get_last_interaction(state, character_key)
            }
        
        return None
    
    def _calculate_relationship(self,
                                state: GameState,
                                character: str) -> str:
        """💞 Calculate relationship status based on past interactions"""
        # This would ideally be tracked in state, but for now use heuristics
        if character == "mentor":
            if state.player_stats.get("power_level", 0) > 8000:
                return "proud"
            return "patient"
        elif character == "rival":
            if state.player_stats.get("power_level", 0) > 5000:
                return "respectful rivalry"
            return "competitive"
        elif character == "villian":
            return "antagonistic"
        return "neutral"
    
    def _determine_character_mood(self,
                                  state: GameState,
                                  character: str) -> str:
        """😠😊 Determine character's current emotional state"""
        moods = {
            "mentor": ["wise", "stern", "encouraging", "mysterious"],
            "rival": ["confident", "cocky", "respectful", "intense"],
            "villain": ["menacing", "arrogant", "calculating", "enraged"],
            "ally": ["supportive", "worried", "determined", "cheerful"]
        }

        char_type = "ally" # default
        for key in moods:
            if key in character.lower():
                char_type = key
                break
        
        return random.choice(moods.get(char_type, ["neutral"]))
    

    def _get_last_interaction(self,
                              state: GameState,
                              character: str)-> Optional[str]:
        """📝 Get summary of last interaction with this character"""
        # In a real implementation, you'd search through messages
        # For now, return None or a generic response
        return None
    
    def _determine_time_of_day(self, state: GameState) -> str:
        """☀️🌙 Determine dramatic time of day based on scene type"""
        if state.scene_counter % 5 == 0:
            return "dawn"
        elif state.scene_counter % 7 == 0:
            return "dusk"
        elif state.scene_counter % 3 == 0:
            return "night"
        return "day"
    
    def _calculate_dramatic_tension(self, state: GameState, step: PlanStep) -> float:
        """📈 Calculate dramatic tension for the scene (0-1)"""
        
        base_tension = step.emotional_intensity if hasattr(step, 'emotional_intensity') else 0.5
        
        # Increase tension near climax
        if step.scene_type == SceneType.CLIMAX:
            base_tension += 0.3
        
        # Increase tension if power levels are high
        power_factor = min(1.0, state.player_stats.get("power_level", 0) / 10000)
        
        # Decrease tension after battle
        if state.in_battle:
            base_tension += 0.2
        
        new_tension = min(1.0, base_tension + power_factor * 0.2)
        
        # Update state's dramatic tension
        state.update_dramatic_tension(new_tension - state.dramatic_tension)
        
        return new_tension
    
    # =========================================================================
    # 🤖 LLM SCENE GENERATION
    # =========================================================================

    def _generate_scene_with_llm_with_retry(self, max_retries=3):
        for attempt in range(max_retries):
            try:
                return self._generate_scene_with_llm(...)
            except Exception:
                if attempt == max_retries - 1:
                    raise
                continue

    def _should_use_llm(self, state: GameState)-> bool:
        """🤔 Determine whether to use LLM or template for this scene"""
        # use templates for simple scenes to use tokens
        if state.scene_counter % 5 == 0: # every 5th scene we will use template
            return False
        return True
    
    def _generate_scene_with_llm(self,
                                 state: GameState,
                                 step: PlanStep,
                                 context: Dict[str, Any],
                                 characters: List[Dict[str, Any]],
                                 player_action: Optional[str] = None) -> Dict[str, Any]:
        """
        🧠 Generate scene using LLM for maximum creativity
        """
        system_prompt = SystemPrompts.get_executor_prompt()

        # Build Character descriptions
        character_description = "\n".join([
            f"-{c['name']}: {c['description']} (Mood : {c['mood']}, Relationship: {c['relationship']})"
            for c in characters
        ])

        user_prompt = f"""
        You are writing Scene {state.plan_step_index + 1} of the {state.saga_name} saga.

        📖 **SCENE CONTEXT:**
        - Scene Type: {step.scene_type.value}
        - Description: {step.description}
        - Expected Outcome: {step.expected_outcome}

        👤 **PLAYER:**
        - Name: {state.player_name}
        - Power Level: {state.player_stats.get('power_level', 0)}
        - Ki Mastery: {state.player_stats.get('ki_mastery', 0)}%

        👥 **CHARACTERS PRESENT:**
        {character_description if character_description else "No other characters present"}

        🌍 **WORLD STATE:**
        - Time of Day: {context['time_of_day']}
        - Dramatic Tension: {context['dramatic_tension']:.1%}
        - Key Flags: {', '.join([k for k, v in state.world_flags.items() if v]) or 'None'}

        """
        
        if player_action:
            user_prompt += f"""
        ⚡ **PLAYER ACTION:**
        "{player_action}"

        Respond to this action in your narration.
        """
        user_prompt += """
        Generate a compelling scene that:
        1. Opens with vivid sensory details
        2. Shows character reactions and dialogue
        3. Advances the plot toward the expected outcome
        4. Includes dynamic descriptions of power/techniques if appropriate
        5. Ends with a hook for player response

        Also suggest state updates based on what happens:
        - Power level changes
        - Ki mastery improvements
        - New items or abilities
        - Character relationship shifts

        Return your response as a JSON with:
        - "narration": The full scene text
        - "dialogue": Any character dialogue (as a list)
        - "state_updates": Object with player_stats, world_flags, and npcs changes
        - "unexpected_events": List of any surprising developments
        - "tokens_used": Estimated token count
        """

        try:
            response = llm_wrapper.generate_structured_response(system_prompt=system_prompt,
                                                                user_prompt=user_prompt,
                                                                response_format='json')
            
            # parse and validate the response
            if isinstance(response, dict):
                # ensure required fields
                tokens_used = response.get("tokens_used", 500)
                # Record the API call in state
                state.record_api_call(tokens_used, response_time=0.5)  # You'd need actual response time
                scene_data = {
                    "narration": response.get("narration", "The scene unfolds..."),
                    "dialogue": response.get("dialogue", []),
                    "state_updates": response.get("state_updates", {}),
                    "unexpected_events": response.get("unexpected_events", []),
                    "tokens_used": response.get("tokens_used", 500)
                }
                return scene_data
        except Exception as e:
            print(f"⚠️ LLM scene generation failed: {e}")
            # Fall back to template
            return self._generate_scene_with_template(state, step, context, characters, player_action)
        

    def _generate_scene_with_template(self,
                                  state: GameState,
                                  step: PlanStep,
                                  context: Dict[str, Any],
                                  characters: List[Dict[str, Any]],
                                  player_action: Optional[str]=None) -> Dict[str, Any]:
    
        """
        📜 Generate scene using templates (fallback or for simple scenes)
        """

        scene_type = step.scene_type
        template = self.scene_templates.get(scene_type, self.scene_templates[SceneType.DIALOGUE])

        # FIX: Remove the duplicate parameters - they're already in context!
        # Also, make a copy of context to avoid modifying the original
        format_dict = context.copy()
        
        # Add player-specific info if not already in context
        if 'player_name' not in format_dict:
            format_dict['player_name'] = state.player_name
        if 'power_level' not in format_dict:
            format_dict['power_level'] = state.player_stats.get("power_level", 0)
        
        # personalize template
        try:
            narration = template['narration'].format(**format_dict)
        except KeyError as e:
            # If a key is missing, fall back to a simpler version
            print(f"⚠️ Missing template key: {e}, using fallback")
            narration = template['narration'].replace('{', '').replace('}', '')
        except Exception as e:
            print(f"⚠️ Template formatting error: {e}")
            narration = template['narration']

        # Add character interactions if available
        if characters:
            char = random.choice(characters)
            dialogue = [
                f'**{char["name"]}** (looking {char["mood"]}): "{self._generate_character_line(char, scene_type)}"'
            ]
        else:
            dialogue = []
        
        # Add player action response if provided
        if player_action:
            narration += f"\n\n{player_action}!"
            narration += self._generate_action_response(player_action, context)
        
        # Calculate basic state updates
        state_updates = self._calculate_template_state_updates(step, context, player_action)

        return {
            "narration": narration,
            "dialogue": dialogue,
            "state_updates": state_updates,
            "unexpected_events": [],
            "tokens_used": 0
        }
    
    def _generate_character_line(self,
                                 character: Dict[str, Any],
                                 scene_type: SceneType)-> str:
        """💬 Generate appropriate dialogue for a character"""

        lines = {
            SceneType.TRAINING: [
                f"Focus your ki, {character['name']}! Feel it flowing through every cell!",
                "Again! Push past your limits!",
                "Your form is improving, but you're still holding back!"
            ],
            SceneType.BATTLE: [
                "Is that all you've got?",
                "You'll have to try harder than that!",
                "Our battle will be legendary!"
            ],
            SceneType.DIALOGUE: [
                "There's something I need to tell you...",
                "The truth is more complicated than you think.",
                "Trust your instincts."
            ],
            SceneType.EXPLORATION: [
                "I've heard rumors about this place...",
                "Be careful. The energy here is unstable.",
                "Look! Over there!"
            ]
        }

        scene_lines = lines.get(scene_type, ["----"])
        return random.choice(scene_lines)
    
    def _generate_action_response(self,
                                  action: str,
                                  context: Dict[str, Any]) -> str:
        """⚡ Generate response to player action"""

        responses = [
            f" The energy of your action ripples through the {context['time_of_day']} air.",
            " Your determination is palpable.",
            " The world responds to your will.",
            " Fate holds its breath, waiting for what comes next."
        ]
        return random.choice(responses)

    def _calculate_template_state_updates(self,
                                      step: PlanStep,
                                      context: Dict[str, Any],
                                      player_action: Optional[str] = None) -> Dict[str, Any]:
    
        """📊 Calculate basic state updates for template scenes"""
        updates = {
            "player_stats": {},
            "world_flags": {},
            "npcs": {}
        }

        # Base power gain (as DELTA, not absolute value)
        power_gain = random.randint(10, 50)
        if step.scene_type == SceneType.TRAINING:
            power_gain *= 2
        elif step.scene_type == SceneType.BATTLE:
            power_gain = random.randint(50, 200)
        elif step.scene_type == SceneType.CLIMAX:
            power_gain = random.randint(200, 500)
        
        updates["player_stats"]["power_level"] = power_gain  # This is a delta
        
        # Ki mastery improvement (as DELTA)
        ki_gain = random.randint(1, 5)
        if step.scene_type == SceneType.TRAINING:
            ki_gain += 3
        updates["player_stats"]["ki_mastery"] = ki_gain  # This is a delta
        
        return updates
    
     # =========================================================================
    # ⚔️ BATTLE RESOLUTION
    # =========================================================================

    
    def _resolve_battle_outcome(self, state: GameState, scene_data: Dict[str, Any], step: PlanStep) -> Dict[str, Any]:
        """⚔️ Calculate battle results and update state accordingly"""
        
        player_power = state.player_stats.get("power_level", 1000)
        
        # Find opponent
        opponent = None
        opponent_power = 1000
        
        for char_key, char_data in state.npcs.items():
            if char_data.get("alive", False) and ("rival" in char_key or "villain" in char_key):
                opponent = char_data
                opponent_power = char_data.get("power_level", 2000)
                break
        
        if not opponent:
            opponent_power = player_power * 1.1
        
        # FIXED: Use calculated victory chance
        victory_chance = self._calculate_victory_chance(player_power, opponent_power)
        player_victory = random.random() < victory_chance
        
        # Start battle in state if not already started
        if not state.in_battle:
            opponent_name = opponent.get("name", "Unknown Enemy") if opponent else "Mysterious Foe"
            state.start_battle(opponent_name, opponent_power)
        
        # Add to battle log
        state.add_battle_log(f"Player Power: {player_power} vs Opponent Power: {opponent_power}")
        state.add_battle_log(f"Victory Chance: {victory_chance:.1%}")
        
        if player_victory:
            # FIXED: More sophisticated power gain
            power_gain = int(opponent_power * 0.1 * (1 + random.random() * 0.5))
            scene_data["narration"] += f"\n\n💥 **VICTORY!** Your power surges as you overcome the challenge!"
            scene_data["state_updates"]["player_stats"]["power_level"] = player_power + power_gain
            scene_data["state_updates"]["world_flags"]["training_completed"] = True
            state.end_battle(True)
            
            # Add relationship improvement
            if opponent:
                opponent_name = opponent.get("name", "rival").lower()
                scene_data["state_updates"]["relationships_delta"] = {
                    opponent_name: 0.2  # Gain respect
                }
        else:
            # FIXED: Loss still gives some gains
            power_gain = int(opponent_power * 0.02 * (1 + random.random()))
            scene_data["narration"] += f"\n\n😤 **DEFEAT...** But you learn valuable lessons from the loss."
            scene_data["state_updates"]["player_stats"]["power_level"] = player_power + power_gain
            scene_data["state_updates"]["player_stats"]["determination"] = True
            state.end_battle(False)
            
            # Relationship might worsen
            if opponent:
                opponent_name = opponent.get("name", "rival").lower()
                scene_data["state_updates"]["relationships_delta"] = {
                    opponent_name: -0.1  # Frustration
                }
        
        # Add battle flavor
        scene_data["narration"] += f"\n\nPower Level: {player_power} → {player_power + power_gain}"
        
        # Update opponent using state method
        if opponent:
            opponent_name = opponent.get("name", "rival").lower()
            # Opponent also grows
            opponent_growth = random.randint(10, 50)
            state.update_npc(opponent_name, {
                "power_level": opponent_power + opponent_growth,
                "alive": True,
                "last_interaction": datetime.now().isoformat()
            })
        
        return scene_data
    
    def _calculate_victory_chance(self, player_power: int, opponent_power: int) -> float:
        """📊 Calculate victory chance based on power levels"""
        
        # Power ratio with diminishing returns
        ratio = player_power / max(opponent_power, 1)
        
        # Logistic function for smooth probability curve
        # At ratio 1.0 -> ~50% chance, at ratio 2.0 -> ~88% chance
        victory_chance = 1 / (1 + (opponent_power / max(player_power, 1)))
        
        # Add randomness factor
        victory_chance += random.uniform(-0.1, 0.1)
        
        return max(0.1, min(0.95, victory_chance))
    
    def _check_transformation_threshold(self, state: GameState, state_updates: Dict[str, Any]) -> bool:
        """✨ Check if player has crossed a transformation threshold"""
        
        old_power = state.player_stats.get("power_level", 1000)
        new_power = state_updates.get("player_stats", {}).get("power_level", old_power)
        
        for i, threshold in enumerate(ExecutorConfig.TRANSFORMATION_THRESHOLDS):
            if old_power < threshold <= new_power:
                if i < len(ExecutorConfig.TRANSFORMATION_NAMES):
                    state.add_transformation(ExecutorConfig.TRANSFORMATION_NAMES[i])
                return True
        
        return False
    
    def _trigger_transformation_sequence(self, state: GameState, state_updates: Dict[str, Any]) -> str:
        """🔥 Generate epic transformation sequence and update player stats"""
        
        new_power = state_updates.get("player_stats", {}).get("power_level", 0)
        
        if new_power >= 9000:
            state.add_title("Super Saiyan")
            return f"""
    ⚡⚡⚡ **IT'S OVER 9000!!!** ⚡⚡⚡

    Golden light erupts around you! Your hair stands on end, turning brilliant gold!
    Your eyes flash green as the power of the **LEGENDARY SUPER SAIYAN** awakens!

    The ground cracks beneath your feet. The sky itself trembles!
    """
        elif new_power >= 18000:
            state.add_title("Super Saiyan 2")
            return """
    💥 **SUPER SAIYAN 2!** Lightning crackles around your golden aura!
    Your power has doubled, and your fighting spirit reaches new heights!
    """
        elif new_power >= 50000:
            state.add_title("Super Saiyan 3")
            return """
    🌟 **SUPER SAIYAN 3!** Your hair grows longer, your eyebrows vanish,
    and your power transcends mortal comprehension! The very fabric of reality bends!
    """
        else:
            return "\n✨ You feel your power reaching a new plateau! ✨"

    
    # =========================================================================
    # 🎯 STATE MANAGEMENT
    # =========================================================================
    

    # def _apply_current_state_updates(self,
    #                                  state: GameState,
    #                                  updates: Dict[str, Any]) -> Dict[str, Any]:
        
    #     """📝 Apply updates to game state, ensuring consistency"""

    #     result = {
    #         "player_stats": state.player_stats.copy(),
    #         "world_flags": state.world_flags.copy(),
    #         "npcs": state.npcs.copy()
    #     }

    #     # apply player stat updates
    #     if "player_stats" in updates:
    #         for key, value in updates["player_stats"].items():
    #             if key == "power_level":
    #                 result["player_stats"][key] = max(0, value)
    #             elif key == "ki_mastery":
    #                 # cap at 100%
    #                 result["player_stats"][key] = min(100, max(0, value))
    #             else:
    #                 result["player_stats"][key] = value

    #     # apply world flag updates
    #     if "world_flags" in updates:
    #         result["world_flags"].update(updates["world_flags"])

    #     # apply npc updates
    #     if "npcs" in updates:
    #         for npc_key, npc_data in updates["npcs"].items():
    #             if npc_key in result["npcs"]:
    #                 result["npcs"][npc_key].update(npc_data)

    #     return result
    
    def _apply_current_state_updates(self, 
                                 state: GameState, 
                                 updates: Dict[str, Any]) -> Dict[str, Any]:
        """📝 Apply updates to game state, ensuring consistency"""
        
        # Start with current state values
        result = {
            "player_stats": state.player_stats.copy(),
            "world_flags": state.world_flags.copy(),
            "npcs": state.npcs.copy()
        }
        
        # Apply player stat updates using the state's helper methods
        if "player_stats" in updates:
            for key, value in updates["player_stats"].items():
                # FIX: Safely handle both existing and new keys
                if key in result["player_stats"]:
                    # Existing key - update with bounds checking
                    if key == "power_level":
                        new_val = max(0, result["player_stats"][key] + value)
                        result["player_stats"][key] = new_val
                        state.update_player_stat(key, new_val)
                    elif key == "ki_mastery":
                        new_val = max(0, min(100, result["player_stats"][key] + value))
                        result["player_stats"][key] = new_val
                        state.update_player_stat(key, new_val)
                    elif key == "health":
                        max_hp = result["player_stats"].get("max_health", 100)
                        new_val = max(0, min(max_hp, result["player_stats"][key] + value))
                        result["player_stats"][key] = new_val
                        state.update_player_stat(key, new_val)
                    else:
                        # For other stats, just add the value
                        result["player_stats"][key] = result["player_stats"][key] + value
                        if hasattr(state, 'update_player_stat'):
                            state.update_player_stat(key, result["player_stats"][key])
                else:
                    # New key - add it directly
                    result["player_stats"][key] = value
                    # Also update the actual state if it has the key
                    if hasattr(state, 'player_stats') and key not in state.player_stats:
                        # Add new key to state's player_stats
                        state.player_stats[key] = value
        
        # Apply world flag updates using state's method
        if "world_flags" in updates:
            for flag, value in updates["world_flags"].items():
                state.set_world_flag(flag, value)
                result["world_flags"][flag] = value
        
        # Apply NPC updates using state's method
        if "npcs" in updates:
            for npc_key, npc_data in updates["npcs"].items():
                state.update_npc(npc_key, npc_data)
                if npc_key in result["npcs"]:
                    result["npcs"][npc_key].update(npc_data)
        
        return result
    
    def _should_advance_plan(self,
                             scene_data: Dict[str, Any],
                             step: PlanStep) -> bool:
        """🔄 Determine if we should move to the next plan step"""

        # Always advance if scene is completed
        if step.completed:
            return True
        
        # dont advance if battle is still pending
        if scene_data.get("in_battle", False):
            return False
        
        # advance if we have unexpected events (means something interesting happened)
        if scene_data.get("unexpected_events"):
            return True
        
        # Default: advance
        return True
    

    def _generate_next_choices(self,
                            scene_data: Dict[str, Any],
                            step: PlanStep,
                            state: GameState) -> List[Dict[str, str]]:
        """🔀 Generate meaningful choices for the player's next action"""

        # FIXED: Use if-elif-else instead of double assignment
        if step.scene_type == SceneType.TRAINING:
            choices = [
                {"text": "Push harder! Increase the gravity!", "type": "aggressive", "risk": "medium"},
                {"text": "Focus on perfecting your form.", "type": "precise", "risk": "low"},
                {"text": "Ask your mentor for advanced techniques.", "type": "strategic", "risk": "low"}
            ]
        
        elif step.scene_type == SceneType.BATTLE:
            choices = [
                {"text": "Go all out! Use your ultimate attack!", "type": "aggressive", "risk": "high"},
                {"text": "Look for an opening in their defense.", "type": "strategic", "risk": "medium"},
                {"text": "Try to talk them down.", "type": "diplomatic", "risk": "low"}
            ]

        elif step.scene_type == SceneType.DIALOGUE:
            choices = [
                {"text": "Ask for more details about the past.", "type": "curious", "risk": "low"},
                {"text": "Share your own story and experiences.", "type": "open", "risk": "low"},
                {"text": "Challenge their perspective.", "type": "confrontational", "risk": "medium"}
            ]

        elif step.scene_type == SceneType.EXPLORATION:
            choices = [
                {"text": "Investigate the mysterious energy source.", "type": "curious", "risk": "high"},
                {"text": "Proceed with extreme caution.", "type": "cautious", "risk": "low"},
                {"text": "Set up camp and observe first.", "type": "patient", "risk": "low"}
            ]
        
        else:
            # Default choices for other scene types
            choices = [
                {"text": "Continue forward with determination.", "type": "bold", "risk": "medium"},
                {"text": "Take a moment to assess the situation.", "type": "cautious", "risk": "low"},
                {"text": "Call out to see if anyone responds.", "type": "social", "risk": "low"}
            ]
        
        return choices
    
    # =========================================================================
    # 📝 MESSAGE CREATION
    # =========================================================================

    def _create_cinematic_message(self,
                                  scene_data: Dict[str, Any],
                                  step: PlanStep,
                                  characters: List[Dict[str, Any]],
                                  choices: List[Dict[str, str]],
                                  state_updates: Dict[str, Any]) -> AIMessage:
        """🎬 Create an immersive, visually rich scene message"""


        # Build header with scene info
        header = self._build_scene_header(step, characters)

        # add narration
        body = scene_data.get("narration", "")

        # add dialouge if present
        if scene_data.get("dialogue"):
            dialogue_section = "\n\n" + "\n".join(scene_data["dialogue"])
            body += dialogue_section

        # Add state changes notification
        state_changes = self._format_state_changes(state_updates)
        if state_changes:
            body += f"\n\n{state_changes}"

        # add choices for next action
        choices_section = self._format_choices(choices)

        # combine everything
        full_message = f"{header} \n\n {body} \n\n {choices_section}"

        return AIMessage(content=full_message)
    

    def _build_scene_header(self,
                            step:PlanStep,
                            characters: List[Dict[str,Any]]) -> str:
        """🎭 Build the dramatic scene header"""
        scene_emojis = {
            SceneType.INTRODUCTION: "🌅",
            SceneType.EXPLORATION: "🗺️",
            SceneType.DIALOGUE: "💬",
            SceneType.BATTLE: "⚔️",
            SceneType.TRAINING: "💪",
            SceneType.CLIMAX: "💥",
            SceneType.RESOLUTION: "✨"
        }

        emoji = scene_emojis.get(step.scene_type, "📖")

        # build character presence string
        if characters:
            char_names = [c["name"] for c in characters]
            presence = f" with {', '.join(char_names)}"

        else:
            presence = ""
        
        return f"""
{'═'*60}
{emoji} **{step.scene_type.value.upper()}** {emoji}{presence}
{'═'*60}
"""
    
    def _format_state_changes(self,
                              state_updates: Dict[str, Any])-> str:
        """📊 Format state changes for display"""
        changes = []

        if "player_stats" in state_updates:
            stats = state_updates["player_stats"]
            if "power_level" in stats:
                changes.append(f"⚡ Power Level: {stats['power_level']}")
            if "ki_mastery" in stats:
                changes.append(f"🌀 Ki Mastery: {stats['ki_mastery']}%")

        if changes:
            return "**✨ STAT UPDATES:** " + " | ".join(changes)
        return ""
    
    def _format_choices(self,
                        choices: List[Dict[str, str]]) -> str:
        
        """🔀 Format choices for player"""
        if not choices:
            return ""
        
        choice_text = "\n".join([
            f"{i+1}. {c['text']}" for i, c in enumerate(choices)
        ])

        return f"""
{'─'*60}
**⚡ WHAT IS YOUR MOVE? ⚡**

{choice_text}

_Type your choice or describe your own action!_
{'─'*60}
"""
    
    # =========================================================================
    # 🚨 ERROR HANDLING
    # =========================================================================

    def _create_error_scene(self,
                            state: GameState,
                            step: Optional[PlanStep],
                            error: str,
                            player_action: Optional[str] = None)-> Dict[str, Any]:
        """🆘 Create a graceful error recovery scene"""
        print(f"🆘 Creating error recovery scene...")


        error_message = f"""
        {'⚠️'*50}
**SYSTEM RESONANCE DISTURBANCE DETECTED**

The fabric of reality momentarily wavered, but your spirit remains strong!

{'─'*40}

**The scene continues...**

"""
        
        # create a simple recovery scene
        recovery_scene = {
            "narration": error_message + "\nThe world steadies itself around you.",
            "dialogue": [],
            "state_updates": {
                "player_stats": state.player_stats.copy(),
                "world_flags": state.world_flags.copy()
            },
            "unexpected_events": [f"System resonance: {error[:50]}..."]
        }

        # Generate simple choices
        choices = [
            {"text": "Continue forward with renewed determination.", "type": "bold"},
            {"text": "Take a moment to gather your thoughts.", "type": "cautious"}
        ]

        ai_message = self._create_cinematic_message(
            scene_data=recovery_scene,
            step = step if step else PlanStep(
                scene_type=SceneType.DIALOGUE,
                description="Recovery scene",
                expected_outcome="System stabilizes"
            ),
            characters=[],
            choices=choices,
            state_updates=recovery_scene["state_updates"]
        )

        return {
            "messages": ai_message,
            "current_plan": state.current_plan,
            "plan_step_index": state.plan_step_index,
            "scene_counter": state.scene_counter + 1,
            "player_stats": state.player_stats,
            "world_flags": state.world_flags,
            "npcs": state.npcs,
            "total_actions": state.total_actions + 1,
            "error_message": error,
            "should_continue": True
        }
    
    # =========================================================================
    # 📚 TEMPLATE LOADING
    # =========================================================================

    def _load_scene_templates(self) -> Dict[SceneType, Dict[str, str]]:
        """📚 Load narrative templates for each scene type"""
        return {
            SceneType.INTRODUCTION: {
                "narration": "The journey begins in {time_of_day} light. {player_name} stands at the threshold of destiny."
            },
            SceneType.TRAINING: {
                "narration": "Sweat and determination. {player_name} pushes beyond their limits, power level rising to {power_level}!"
            },
            SceneType.BATTLE: {
                "narration": "The clash of energies illuminates the battlefield! {player_name} faces their greatest test with power level {power_level}!"
            },
            SceneType.DIALOGUE: {
                "narration": "Words carry weight in this moment. Secrets are shared and bonds are tested."
            },
            SceneType.EXPLORATION: {
                "narration": "The unknown beckons. {player_name} ventures into uncharted territory."
            },
            SceneType.CLIMAX: {
                "narration": "Everything converges to this single moment! The fate of worlds hangs in the balance! Power level {power_level}!"
            },
            SceneType.RESOLUTION: {
                "narration": "The dust settles. {player_name} reflects on the journey and what lies ahead."
            }
        }
    
    def _load_dramatic_phrases(self) -> List[str]:
        """🔥 Load dramatic phrases for scene enhancement"""
        return [
            "The air crackles with energy!",
            "Time seems to slow down...",
            "A chill runs down your spine!",
            "Your heart pounds like a drum!",
            "The ground shakes beneath your feet!",
            "A blinding light erupts before you!",
            "You feel a strange presence watching...",
            "The wind carries whispers of ancient power!"
        ]
    
    def _load_transformation_triggers(self) -> List[str]:
        """✨ Load transformation trigger phrases"""
        return [
            "PUSH PAST YOUR LIMITS!",
            "UNLEASH YOUR HIDDEN POWER!",
            "TRANSCEND YOUR MORTAL FORM!",
            "AWAKEN THE LEGEND WITHIN!",
            "BREAK THE BONDS OF FATE!"
        ]


