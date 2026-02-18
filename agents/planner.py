from typing import Dict, Any, List, Optional, Tuple
from langchain_core.messages import BaseMessage, AIMessage, SystemMessage, HumanMessage
import json
import random
from datetime import datetime
import re
import math
from schemas.state import GameState, PlanStep, SceneType
from utils.llm_wrapper import llm_wrapper
from utils.prompts import SystemPrompts

class PlannerConfig:
    """Configuration constants for PlannerAgent"""
    
    # Power thresholds for archetype detection
    POWER_THRESHOLDS = {
        "GOD-TIER": 8000,
        "KI_SAGE": (70, "ki_mastery"),
        "SPIRIT_COLLECTOR": (5, "spirit_bombs"),
        "ZENKAI_EVOLUTIONIST": (3, "zenkai_boosts")
    }
    
    # Emotional intensity scaling
    EMOTIONAL_PEAK_MULTIPLIER = 2.0
    RANDOM_VARIATION = 0.1
    
    # Reward multipliers
    REWARD_MULTIPLIERS = {
        "BATTLE": 2.0,
        "CLIMAX": 5.0,
        "TRAINING": 1.2
    }

class PlannerAgent:
    """
    ⚡ DIVINE PLANNER ENTITY ⚡
    Creates legendary, multi-dimensional story plans with dynamic branching,
    emotional depth, and cinematic pacing worthy of anime greatness!
    """

    def __init__(self,
                 max_plan_length: int = 7,
                 difficulty: str = "medium",
                 narrative_complexity: int = 5):
        
        self.max_plan_length = max_plan_length
        self.difficulty = difficulty
        self.narrative_complexity = narrative_complexity

        # ✨ Epic narrative templates
        self.arc_templates = {
            "Power Progression": {
                "vibes": ["Explosive", "Determined", "Transcendent"],
                "themes": ["Overcoming limits", "Legacy", "Protection"],
                "emotional_peaks": [0.3, 0.6, 0.9],
                "power_curve": "exponential"
            },
            "Mystical Quest": {
                "vibes": ["Mysterious", "Wonderous", "Revelatory"],
                "themes": ["Self-discovery", "Ancient wisdom", "Sacrifice"],
                "emotional_peaks": [0.2, 0.5, 0.8, 1.0],
                "power_curve": "growth"
            },
            "School Rivalry": {
                "vibes": ["Competitive", "Dramatic", "Redemptive"],
                "themes": ["Friendship", "Rivalry", "Excellence"],
                "emotional_peaks": [0.4, 0.7, 0.95],
                "power_curve": "steady"
            },
            "Mecha Warfare": {
                "vibes": ["Intense", "Strategic", "Cataclysmic"],
                "themes": ["War and peace", "Humanity", "Sacrifice"],
                "emotional_peaks": [0.1, 0.4, 0.8, 1.0],
                "power_curve": "exponential"
                },
                "Romantic Drama": {
                "vibes": ["Heartfelt", "Tense", "Euphoric"],
                "themes": ["Love", "Loss", "Connection"],
                "emotional_peaks": [0.3, 0.5, 0.7, 0.9],
                "power_curve": "emotional"
            },
            "Supernatural Horror": {
            "vibes": ["Eerie", "Terrifying", "Hopeful"],
            "themes": ["Fear", "Survival", "Humanity"],
            "emotional_peaks": [0.2, 0.4, 0.6, 0.8, 1.0],
            "power_curve": "desperate"
        }}
        
        self.scene_archetypes = {
            SceneType.INTRODUCTION: [
                "Awakening", "Discovery", "Arrival", "Reunion", "Prophecy"
            ],
            SceneType.TRAINING: [
                "Trial by Fire", "Master's Wisdom", "Breaking Limits", 
                "Secret Technique", "Unorthodox Method"
            ],
            SceneType.BATTLE: [
                "Clash of Ideals", "Desperate Stand", "Unexpected Alliance",
                "Betrayal", "Redemption Fight", "Final Flash"
            ],
            SceneType.DIALOGUE: [
                "Revelation", "Confession", "Confrontation", "Heart-to-Heart",
                "Ancient Secrets", "Warning from Beyond"
            ],
            SceneType.EXPLORATION: [
                "Forgotten Ruins", "Mystical Forest", "Spiritual Realm",
                "Underworld", "Parallel Dimension"
            ],
            SceneType.CLIMAX: [
                "Cosmic Convergence", "Emotional Awakening", "Ultimate Sacrifice",
                "Power of Friendship", "Transcendence", "Genesis"
            ]
        
        }
    
    def invoke(self, state: GameState)-> Dict[str, Any]:
        """
        🌟 GENERATE LEGENDARY PLAN 🌟
        Creates a multi-layered narrative architecture with:
        - Emotional pacing curves
        - Dynamic difficulty scaling
        - Character arc trajectories
        - Branching narrative paths
        - Epic cinematic moments
        """

        print(f"""
        ╔══════════════════════════════════════════════════════════════╗
        ║     🌀 DIVINE PLANNER MANIFESTING SAGA: {state.saga_name.upper():<25} 🌀
        ╠══════════════════════════════════════════════════════════════╣
        ║  Warrior: {state.player_name:<30} Rank: {state.player_stats.get('combat_tier', 'E Rank'):<15} ║
        ║  Power: {state.player_stats.get('power_level', 0):<10} Ki: {state.player_stats.get('ki_mastery', 0):<10}%      ║
        ║  Difficulty: {self.difficulty.upper():<20} Complexity: {self.narrative_complexity}★         ║
        ╚══════════════════════════════════════════════════════════════╝
        """)

        try:
            # analyze player profile for personalized planning
            player_analysis = self._analyze_player_profile(state)

            #calculate optimal pacing based on saga type and player
            pacing_profile = self._calculate_pacing_profile(state.saga_name, player_analysis)

            # generate a multi-layered plan with emotional beats, branching paths, and character arcs
            plan = self._generate_epic_plan(state, pacing_profile, player_analysis)

            # add emotional beats and narrative twists to the plan
            plan = self._infuse_emotional_architecture(plan, pacing_profile)

            # create hidden branching opportunities for player agency
            plan = self._seed_branching_narratives(plan, state.saga_name)

            # scale difficulty based on player stats
            plan = self._dynamic_difficulty_scaling(plan, state.player_stats)

            print(f"""
            ╔══════════════════════════════════════════════════════════════╗
            ║     ✅ LEGENDARY PLAN MANIFESTED! {len(plan)} ACTS UNFOLD...     ║
            ╠══════════════════════════════════════════════════════════════╣
            """)
            
            for i, step in enumerate(plan, 1):
                print(f"    Act {i}: {step.description[:60]}...")
            
            print("╚══════════════════════════════════════════════════════════════╝")

            # generate a epic intro scene to kick off the saga
            intro_message = self._create_cinematic_introduction(plan, state.player_name, state.saga_name)
            print(f"🔍 PLANNER RETURNING: {len(plan)} steps")
            for i, step in enumerate(plan[:3]):  # Show first 3 steps
                print(f"   Step {i+1}: {step.description[:50]}...")

            return {
                "current_plan": plan,
                "plan_step_index": 0,
                "plan_revisions": 0,
                "messages": [intro_message],
                "total_actions": state.total_actions + 1,
                "tokens_used": state.tokens_used + llm_wrapper.total_tokens_used,
                "narrative_metadata": {
                    "pacing_profile": pacing_profile,
                    "player_analysis": player_analysis,
                    "plan_generation_time": datetime.now().isoformat(),
                    "branching_points":len([step for step in plan if step.branching_options]),
                    "emotional_arc": pacing_profile.get("emotional_curve", []),
                    "difficulty_scaling": self.difficulty

                }
            }
        except Exception as e:
            print(f"❌ Error in PlannerAgent: {str(e)}")
            return {
                "current_plan": [],
                "plan_step_index": 0,
                "plan_revisions": 0,
                "messages": [SystemMessage(content="An error occurred while generating the plan. Please try again.")],
                "total_actions": state.total_actions + 1,
                "tokens_used": state.tokens_used + llm_wrapper.total_tokens_used,
                "narrative_metadata": {}
            }
        
    # ----------------------------
    def _analyze_player_profile(self, state: GameState) -> Dict[str, Any]:
        """🧠 Deep player psychology and preference analysis"""
        stats = state.player_stats
        
        #calculate play style archetype based on stats
        power_level = stats.get('power_level', 1000)
        ki_mastery = stats.get('ki_mastery', 50)
        spirit_bombs = stats.get('spirit_bombs', 0)
        zenkai_boosts = stats.get('zenkai_boosts', 0)

        # Determine play style archetype
        if power_level > 8000:
            archetype = "GOD-TIER WARRIOR"
            play_style = "Aggressive Transcendent"
            preferred_scenes = ["battle", "climax"]
        elif ki_mastery > 70:
            archetype = "KI SAGE"
            play_style = "Strategic Master"
            preferred_scenes = ["training", "dialogue"]
        elif spirit_bombs > 5:
            archetype = "SPIRIT COLLECTOR"
            play_style = "Patient Powerhouse"
            preferred_scenes = ["exploration", "training"]
        elif zenkai_boosts > 3:
            archetype = "ZENKAI EVOLUTIONIST"
            play_style = "Adaptive Fighter"
            preferred_scenes = ["battle", "training"]
        
        else:
            archetype = "RAISING WARRIOR"
            play_style = "Balanced Adventurer"
            preferred_scenes = ["introduction", "exploration", "dialogue"]

        # calculate challenge preferences based on difficulty
        if stats.get('level', 1) > 10 or power_level > 5000:
            challenge_threshold = 0.8
        elif stats.get('level', 1) > 5:
            challenge_threshold = 0.5
        else:
            challenge_threshold = 0.3
        
        return {
            "archetype": archetype,
            "play_style": play_style,
            "preferred_scenes": preferred_scenes,
            "challenge_threshold": challenge_threshold,
            "power_velocity": power_level / max(1, stats.get('level', 1)),
            "experience_level": stats.get('level', 1),
            "adapatability": zenkai_boosts * 10 + ki_mastery * 0.3,
            "momentum": stats.get('momentum', 0)
        }
    
    def _calculate_pacing_profile(self,
                                  saga_name: str,
                                  player_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """📈 Calculate optimal emotional and narrative pacing based on saga type and player profile"""

        template = self.arc_templates.get(saga_name, self.arc_templates["Power Progression"])

        # adjust pacing based on player experience
        exp_factor = min(1.0, player_analysis["experience_level"] / 10)

        # generate emotional intensity curve
        emotional_curve = []

        for i in range(self.max_plan_length):
            progress = i / (self.max_plan_length - 1) if self.max_plan_length > 1 else 0

            # base intensity from template peaks
            intensity = 0.5
            for peak in template["emotional_peaks"]:
                distance = abs(progress - peak)
                intensity += max(0, (1 - distance * 2))  # sharper peaks

                # add player specific adjustments
                intensity += exp_factor * 0.2  # more experienced players get higher intensity

                # add random emotional variation
                intensity += random.uniform(-0.1, 0.1)
                emotional_curve.append(round(min(max(intensity, 0), 1), 2))

        # determine scene type distribution based on player preferences
        scene_distribution = self._calculate_optimal_scene_mix(saga_name, player_analysis['preferred_scenes'])

        return {
            "emotional_curve": emotional_curve,
            "scene_distribution": scene_distribution,
            "pacing_intensity": exp_factor + 0.5,
            "narrative_tension_points": [ i for i, intensity in enumerate(emotional_curve) if intensity > 0.7 ],
            "power_curve_type": template["power_curve"],
            "vibe": random.choice(template["vibes"]),
            "theme": random.choice(template["themes"])

        }
        
    
    def _calculate_optimal_scene_mix(self, saga_name: str, preferences: List[str]) -> Dict[SceneType, float]:
        """🎲 Calculate optimal scene type distribution"""
        
        # Base distributions per saga type
        base_distributions = {
            "Power Progression": {
                SceneType.INTRODUCTION: 0.1,
                SceneType.TRAINING: 0.3,
                SceneType.BATTLE: 0.3,
                SceneType.DIALOGUE: 0.1,
                SceneType.EXPLORATION: 0.1,
                SceneType.CLIMAX: 0.1
            },
            "Mystical Quest": {
                SceneType.INTRODUCTION: 0.1,
                SceneType.EXPLORATION: 0.4,
                SceneType.DIALOGUE: 0.2,
                SceneType.BATTLE: 0.15,
                SceneType.TRAINING: 0.05,
                SceneType.CLIMAX: 0.1
            },
            "School Rivalry": {
                SceneType.INTRODUCTION: 0.1,
                SceneType.TRAINING: 0.2,
                SceneType.BATTLE: 0.2,
                SceneType.DIALOGUE: 0.3,
                SceneType.EXPLORATION: 0.1,
                SceneType.CLIMAX: 0.1
            }
        }

        distribution = base_distributions.get(saga_name, base_distributions["Power Progression"]).copy()

        # adjust based on player preferences
        for pref in preferences:
            try:
                scene_type = SceneType(pref.upper())
                distribution[scene_type] = distribution.get(scene_type, 0) + 0.1  # boost preferred scenes
            except ValueError:
                continue
        
        # normalize distribution
        total = sum(distribution.values())
        for key in distribution:
            distribution[key] /= total
        
        return distribution
    
    def _generate_epic_plan(self, 
                            state: GameState, 
                            pacing_profile: Dict[str, Any], 
                            player_analysis: Dict[str, Any]
                            ) -> List[PlanStep]:
        """🎬 Generate multi-dimensional plan with legendary structure"""

        plan = []
        scene_types = list(pacing_profile["scene_distribution"].keys())
        scene_weights = list(pacing_profile["scene_distribution"].values())

        ## Opening scene - always impactful
        opening = self._create_legendary_scene(
            scene_type=SceneType.INTRODUCTION,
            index=0,
            total_steps=self.max_plan_length,
            pacing_profile=pacing_profile,
            player_analysis=player_analysis,
            saga_name=state.saga_name,
            is_opening=True
        )
        plan.append(opening)
        
        # Middle scenes with dynamic variety
        for i in range(1, self.max_plan_length - 1):
            # Weighted random scene selection
            scene_type = random.choices(scene_types, weights=scene_weights, k=1)[0]
            
            scene = self._create_legendary_scene(
                scene_type=scene_type,
                index=i,
                total_steps=self.max_plan_length,
                pacing_profile=pacing_profile,
                player_analysis=player_analysis,
                saga_name=state.saga_name,
                is_opening=False
            )
            plan.append(scene)
        
        # Climax scene - always EPIC
        climax = self._create_legendary_scene(
            scene_type=SceneType.CLIMAX,
            index=self.max_plan_length - 1,
            total_steps=self.max_plan_length,
            pacing_profile=pacing_profile,
            player_analysis=player_analysis,
            saga_name=state.saga_name,
            is_climax=True
        )
        plan.append(climax)
        
        return plan
    
    def _create_legendary_scene(self,
                            scene_type: SceneType,
                            index: int,
                            total_steps: int,
                            pacing_profile: Dict[str, Any],
                            player_analysis: Dict[str, Any],
                            saga_name: str,
                            is_opening: bool = False,
                            is_climax: bool = False) -> PlanStep:
        """Craft a single scene with cinematic flair, emotional depth, and narrative significance"""

        # Select epic archetype
        archetypes = self.scene_archetypes.get(scene_type, ["Legendary Moment"])
        archetype = random.choice(archetypes)
        
        # Calculate emotional intensity
        emotional_intensity = pacing_profile["emotional_curve"][index]
        
        # Generate scene description
        if is_opening:
            description = self._generate_opening_description(saga_name, archetype, player_analysis)
            expected_outcome = self._generate_opening_outcome(player_analysis)
            duration = random.randint(1, 2)
        elif is_climax:
            description = self._generate_climax_description(saga_name, archetype, emotional_intensity)
            expected_outcome = self._generate_climax_outcome(saga_name, emotional_intensity)
            duration = random.randint(3, 4)
        else:
            description = self._generate_scene_description(scene_type, saga_name, archetype, emotional_intensity)
            expected_outcome = self._generate_outcome(scene_type, emotional_intensity)
            duration = random.randint(1, 3)
        
        # Generate branching options
        branching_options = self._generate_branching_options(scene_type, emotional_intensity, index)
        
        # Calculate rewards
        rewards = self._calculate_scene_rewards(scene_type, emotional_intensity, player_analysis)
        
        # Determine required characters
        required_characters = self._determine_required_characters(scene_type, saga_name, emotional_intensity)
        
        # FIX: Ensure difficulty_modifier is between 0.5 and 3.0
        raw_modifier = emotional_intensity * player_analysis["challenge_threshold"]
        difficulty_modifier = max(0.5, min(3.0, raw_modifier))
        
        return PlanStep(
            scene_type=scene_type,
            description=description,
            expected_outcome=expected_outcome,
            required_characters=required_characters,
            expected_duration=duration,
            emotional_intensity=emotional_intensity,
            archetype=archetype,
            branching_options=branching_options,
            rewards=rewards,
            difficulty_modifier=difficulty_modifier,  # FIXED: Now between 0.5 and 3.0
            narrative_weight=emotional_intensity,
            hidden_objectives=self._generate_hidden_objectives(scene_type, emotional_intensity) if index % 2 == 0 else None
        )
    


    def _generate_opening_description(self, saga_name: str, archetype: str, player_analysis: Dict) -> str:
        """✨ Generate immersive, high-stakes cinematic opening scene descriptions"""
        
        # We pull a specific trait from the analysis to make it feel personalized
        trait = player_analysis.get('dominant_trait', 'unyielding')
        
        openings = {
            "Power Progression": [
                f"The sky bleeds crimson as the village of your youth lies in smoldering ruins. Among the ashes, "
                f"the weight of your {archetype} heritage finally takes root. Your fists tremble, not with fear, "
                f"but with a raw, {trait} power that threatens to shatter the very ground beneath you. Your journey begins in the embers.",
                
                f"The Great Tournament stadium holds its breath. You stand at the center of the ring, battered and breathless. "
                f"Suddenly, the air begins to hum. Your {player_analysis['archetype']} potential erupts in a pillar of light, "
                f"blinding the spectators. You aren't just a fighter anymore; you are a force of nature.",
                
                f"A thunderclap echoes across a cloudless sky. A silhouette descends from the heavens, wreathed in lightning. "
                f"The mysterious warrior points a trembling finger at you, 'The prophecy spoke of a {archetype} soul "
                f"with a {trait} spirit. At last, I have found you. The fate of the twelve realms now rests on your shoulders.'"
            ],
            "Mystical Quest": [
                f"Deep within the Forbidden Caverns, an ancient artifact encased in jagged crystal pulses with a rhythmic, "
                f"{archetype} glow. As your hand nears, the crystal shatters. The energy surges into your veins, "
                f"binding your soul to a weapon of the gods. You feel the {trait} memories of a thousand ancestors flood your mind.",
                
                f"For seven nights, the same vision has haunted your sleep: a {player_analysis['archetype']} spirit "
                f"standing atop the World Tree, beckoning you. You wake with a strange mark etched into your palm. "
                f"The call to adventure is no longer a dream—it is a command written in your very blood.",
                
                f"The Sacred Texts have remained silent for three centuries, but today, the ink began to glow. "
                f"The high priests fall to their knees as you enter the temple. The prophecy of the {archetype} hero "
                f"is manifesting, and your {trait} aura is the sign they have prayed for. The quest for the shards begins."
            ],
            "School Rivalry": [
                f"The iron gates of the Academy creak open as the transfer student steps through a shroud of mist. "
                f"The air grows heavy—they possess a {player_analysis['archetype']} presence that humbles even the masters. "
                f"Your eyes meet across the courtyard, and in that instant, a {trait} destiny is forged. You have found your wall.",
                
                f"The bells of the Final Pavilion chime. You stand across from your lifelong rival, the one who has always "
                f"been a step ahead. But today is different. You feel the {archetype} fire burning in your gut. "
                f"This isn't just a match; it's the culmination of your {trait} resolve. The world is watching.",
                
                f"Under the cherry blossom tree where you once played as children, your oldest friend draws a blade "
                f"etched with dark runes. 'I have ascended to the rank of {archetype} warrior,' they whisper. "
                f"The innocence of the past dies here. To save them, you must embrace your own {trait} path."
            ]
        }
        
        # Fallback to Power Progression if the saga_name isn't found
        saga_openings = openings.get(saga_name, openings["Power Progression"])
        return random.choice(saga_openings)


    def _generate_climax_description(self, saga_name: str, archetype: str, intensity: float) -> str:
        """💥 Generate LEGENDARY, multi-stage climax scene descriptions"""
        
        # Calculate Spirit Percentage for display
        spirit_pct = int(intensity * 100)
        
        # We categorize climaxes by "Vibe" to match the saga's weight
        climaxes = [
            # THE COSMIC CLASH
            f"THE FINAL SHOWDOWN! Your {archetype} power reaches a critical frequency, "
            f"warping the laws of physics. As you clash with destiny, every strike sends "
            f"shockwaves through the dimensions. The sky has turned into a kaleidoscope of "
            f"shattering glass, reflecting every version of you that failed—but this time, you stand firm.",

            # THE EMOTIONAL PEAK
            f"Everything you've learned, every scarred battlefield, and every tear shed for "
            f"fallen allies culminates in this heartbeat. Your {archetype} aura isn't just "
            f"energy anymore; it's a living memory. You realize that to win, you must become "
            f"more than a warrior—you must become the legend the world needs.",

            # THE REVELATION
            f"As the ancient {archetype} prophecy reaches its final verse, the truth hits you like "
            f"a physical blow: this was never about winning or losing. It was about the "
            f"transcendence of your spirit. Your enemies look on in terror as your eyes begin to "
            f"glow with the cold, absolute light of a true God of Battle.",

            # THE ULTIMATE TECHNIQUE (Uses the intensity variable)
            f"With {spirit_pct}% of your spirit burning like a dying star, you bypass your mortal "
            f"limits. You begin to weave your ultimate technique, drawing energy from the "
            f"very core of the planet. Reality begins to fray at the edges, unable to contain "
            f"the sheer {archetype} pressure of your existence!",

            # THE FATE CONVERGENCE
            f"The universe holds its breath. Time itself seems to grind to a halt as you and your "
            f"fate converge in a blinding display of {archetype} glory. There is no more past, "
            f"no more future—only the blinding white heat of the present moment and the "
            f"terrifying power of your resolve."
        ]

        # If intensity is extremely high (e.g., > 0.9), add an "Overdrive" modifier
        selected = random.choice(climaxes)
        if intensity > 0.95:
            selected = f"⚠️ CRITICAL OVERDRIVE: {selected} Your power is so immense that " \
                    f"the Scouter systems are melting in your presence!"

        return selected
    
    def _generate_scene_description(self, 
                                scene_type: SceneType, 
                                saga_name: str, 
                                archetype: str, 
                                intensity: float) -> str:
        """📜 Generate immersive, sensory-rich scene descriptions"""
    
        spirit_pct = int(intensity * 100)
        
        # We use a dictionary where each key has a list of multi-sentence, 
        # highly descriptive options.
        descriptions = {
            SceneType.TRAINING: [
                f"The air grows heavy with the scent of ozone and effort. Your mentor's voice cuts through the "
                f"exhaustion as you undergo brutal {archetype} conditioning, forcing your muscles to adapt "
                f"to a power that should be impossible for a mortal to contain.",
                
                f"Deep within the gravity chamber, hours blur into days. You are perfecting the {archetype} technique, "
                f"your movements becoming a blur of peak efficiency. Every drop of sweat that hits the floor "
                f"echoes like a drumbeat of your rising potential.",
                
                f"Beneath a crashing waterfall of pure energy, you meditate on the {archetype} path. Blood and "
                f"determination stain your gi, but as your breathing slows, you feel the spirit of the "
                f"ancients acknowledging your {spirit_pct}% sync rate with their power."
            ],
            SceneType.BATTLE: [
                f"Impact! The first {archetype} clash sends a seismic shockwave tearing through the landscape, "
                f"splitting the earth for miles. Dust chokes the sky, but your eyes remain locked on your foe, "
                f"sensing the terrifying symmetry of your fighting styles.",
                
                f"Your opponent is a mirror image of your own lethal intent. This is the {archetype} struggle "
                f"you have hungered for—a dance of destruction where every counter-punch shatters the sound barrier "
                f"and every ki-blast illuminates the horizon like a second sun.",
                
                f"With {spirit_pct}% fighting spirit surging like a tidal wave, you throw yourself into the fray. "
                f"The battlefield is no longer just dirt and rock; it is a canvas of {archetype} energy where "
                f"the victor will be the one whose will outlasts their strength."
            ],
            SceneType.DIALOGUE: [
                f"The tension in the room is thick enough to choke on. A single {archetype} revelation hangs in the air, "
                f"stripping away your certainties. Behind your companion's eyes lies {spirit_pct} years of hidden "
                f"burdens, and suddenly, the mission feels much heavier.",
                
                f"In the quiet of the temple, words are spoken that carry the weight of entire civilizations. "
                f"This {archetype} exchange isn't just about information—it's about the soul. Enemies share "
                f"their grief, and for a moment, the war outside feels a universe away.",
                
                f"A whisper, cold and precise, reveals a secret that shifts the axis of your world. This "
                f"conversation is the final piece of the {archetype} puzzle; the mask has slipped, and "
                f"friends and foes have traded places in the blink of an eye."
            ],
            SceneType.EXPLORATION: [
                f"You step into the {archetype} unknown, where the very atmosphere feels charged with ancient "
                f"malice. Your heart beats in your ears, a rhythmic reminder that in this untouched wilderness, "
                f"you are the intruder.",
                
                f"The ruins before you pulse with a rhythmic, {spirit_pct}% mystical resonance. Moss-covered statues "
                f"of forgotten {archetype} kings stare down at you, their stone eyes seemingly following "
                f"your every move as you descend into the dark.",
                
                f"The path of the {archetype} has brought you to a place where the stars look different. "
                f"Gravity pulls sideways, and the flora glows with a haunting, bioluminescent light—a "
                f"landscape of pure wonder and hidden lethality."
            ]
        }
        
        # Fallback logic
        scene_descs = descriptions.get(scene_type, [
            f"A moment of pure {archetype} significance unfolds, vibrating with {spirit_pct}% intensity.",
            f"The chronicle of your {archetype} journey continues, leading you toward a destiny written in fire."
        ])
        
        return random.choice(scene_descs)
    
    def _generate_branching_options(self, scene_type: SceneType, intensity: float, index: int) -> List[Dict[str, str]]:
        """🔄 Generate high-stakes, cinematic branching narrative options"""
        
        branches = []
        
        # --- INTENSITY-BASED BRANCHES (The "Vibe" of the moment) ---
        if intensity > 0.7:
            branches.append({
                "type": "dramatic",
                "option": "🔥 LIMIT BREAKER: Take a Daring Risk!",
                "description": "Abandon all defense and pour your soul into a single, devastating gambit. Success brings legend; failure brings ruin."
            })
            branches.append({
                "type": "strategic",
                "option": "👁️ SCOUTER LOGIC: Analyze Coldly.",
                "description": "Ignore the chaos and find the structural weakness in your situation. Survival is guaranteed, but glory may be lost."
            })
        elif intensity > 0.4:
            branches.append({
                "type": "balanced",
                "option": "🧘‍♂️ ZEN STATE: Trust Your Instincts.",
                "description": "Stop overthinking. Let your body move on its own, relying on years of blood and sweat to guide your path."
            })
            branches.append({
                "type": "supportive",
                "option": "🤝 UNITED FRONT: Call for Backup.",
                "description": "Lend your energy to your allies. By standing together, you create a combined power level the enemy cannot calculate."
            })
        else:
            branches.append({
                "type": "cautious",
                "option": "🛡️ PATIENT OBSERVER: Bide Your Time.",
                "description": "Let the opponent tire themselves out. Watch for the micro-second of vulnerability that only the patient can see."
            })
            branches.append({
                "type": "aggressive",
                "option": "⚡ BLITZKRIEG: Strike Without Warning!",
                "description": "The best defense is total annihilation. Explode into action before the enemy can even process your intent."
            })

        # --- SCENE-SPECIFIC BRANCHES (The "Mechanics" of the scene) ---
        if scene_type == SceneType.TRAINING:
            branches.append({
                "type": "innovation",
                "option": "🌀 FORGE: Create an Original Technique!",
                "description": "Synthesize everything you've learned into a signature move. This is the birth of your personal legacy."
            })
        elif scene_type == SceneType.DIALOGUE:
            branches.append({
                "type": "emotional",
                "option": "❤️ HEART-CRY: Speak Your Raw Truth.",
                "description": "Shatter the social masks. Be vulnerable. It’s the only way to turn a bitter rival into a lifelong brother-in-arms."
            })
        elif scene_type == SceneType.BATTLE:
            branches.append({
                "type": "mercy",
                "option": "🕊️ REDEMPTION: Extend a Hand of Mercy.",
                "description": "Stop the final blow. If you can break the cycle of vengeance now, you gain an ally that knows your true strength."
            })
        elif scene_type == SceneType.EXPLORATION:
            branches.append({
                "type": "mystery",
                "option": "⛩️ FORBIDDEN PATH: Enter the Sealed Zone.",
                "description": "Ignore the warning signs. What lies behind the seal is ancient, dangerous, and holds the key to your next power-up."
            })

        # Shuffle to keep the player on their toes, and return the top 3
        random.shuffle(branches)
        return branches[:3]
    
    def _calculate_scene_rewards(self,
                                 scene_type: SceneType,
                                 intensity: float,
                                 player_analysis: Dict[str, Any]) -> Dict[str, Any]:
        
        """💎 Calculate legendary rewards with Archetype Scaling and Multiplier Stacking"""
        # 1. Base Scaling Logic (Exponential growth feels more 'Anime' than linear)
        # Using intensity^2 ensures that a 90% intensity scene is significantly 
        # more rewarding than a 50% one

        power_mul = intensity ** 2

        rewards = {
        "power_level": int(power_mul * 1000),
        "ki_mastery": int(intensity * 25),
        "spirit_points": int(intensity * 5),
        "prestige": 0
        }

        # 2. Archetype Affinity (Personalized Gains)
        # Different archetypes should naturally excel in different areas

        archetype = player_analysis.get("archetype", "RAISING WARRIOR")

        if archetype == "Brawler":
            rewards["power_level"] = int(rewards["power_level"] * 1.2)
        elif archetype == "Tactician":
            rewards["ki_mastery"] = int(rewards["ki_mastery"] * 1.4)
        elif archetype == "Hero":
            rewards["spirit_points"] = int(rewards["spirit_points"] * 1.5)

    # 3. Scene Multipliers
    # Preferred scenes give a 'Hype Bonus'
        if scene_type.value in player_analysis.get("preferred_scenes", []):
            rewards["power_level"] = int(rewards["power_level"] * 1.5)
            rewards["prestige"] += 10 

        # 4. The Legendary Climax / Zenkai Factor
        if scene_type == SceneType.BATTLE and intensity > 0.8:
            # High intensity battles grant a "Zenkai Boost" (Recovering from the brink)
            rewards["zenkai_boost"] = 1
            rewards["power_level"] = int(rewards["power_level"] * 2.0)
            
        if scene_type == SceneType.CLIMAX:
            rewards["power_level"] *= 5
            rewards["ki_mastery"] *= 3
            rewards["ascension_points"] = 1 # Special currency for transformation unlocks

        return rewards

    def _determine_required_characters(self, scene_type: SceneType, saga_name: str, intensity: float) -> List[str]:
        """👥 Determine a narratively consistent cast for the current scene"""
        
        # Define roles within each saga for better narrative 'casting'
        # Format: "Role": [Characters]
        saga_cast_profiles = {
            "Power Progression": {
                "mentors": ["Master Roshi", "King Kai", "Whis"],
                "rivals": ["Vegeta", "Piccolo"],
                "allies": ["Krillin", "Bulma", "Gohan"],
                "villains": ["Frieza", "Cell", "Majin Buu"]
            },
            "Mystical Quest": {
                "mentors": ["Ancient Sage", "Guardian of Earth"],
                "rivals": ["Corrupted Monk", "Dark Mirror Image"],
                "allies": ["Spirit Fox", "Oracle"],
                "villains": ["Dimensional Eater", "Chaos Lord"]
            },
            "School Rivalry": {
                "mentors": ["The Headmaster", "Sensei Sato"],
                "rivals": ["Elite Rank #1", "The Delinquent King"],
                "allies": ["Childhood Friend", "Tech Club Prez"],
                "villains": ["Student Council President", "Shadow Proctor"]
            }
        }

        # Get the cast for the current saga, fallback to a generic pool
        cast = saga_cast_profiles.get(saga_name, {
            "mentors": ["Mentor"], "rivals": ["Rival"], 
            "allies": ["Ally"], "villains": ["Villain"]
        })

        required_characters = []

        # --- SCENE-BASED CASTING ---
        if scene_type == SceneType.TRAINING:
            # Training usually requires a Mentor or an Ally to spar with
            required_characters.append(random.choice(cast["mentors"] + cast["allies"]))
            
        elif scene_type == SceneType.BATTLE:
            # Battles always need a Rival or a Villain
            required_characters.append(random.choice(cast["rivals"] + cast["villains"]))
            
        elif scene_type == SceneType.DIALOGUE:
            # Dialogue can be with anyone, but usually starts with one key figure
            all_available = [c for sublist in cast.values() for c in sublist]
            required_characters.append(random.choice(all_available))
            
        elif scene_type == SceneType.CLIMAX:
            # Climaxes are crowded: Big Bad + A key Rival/Ally
            required_characters.append(random.choice(cast["villains"]))
            required_characters.append(random.choice(cast["rivals"] + cast["allies"]))

        # --- INTENSITY MODIFIERS ---
        # High intensity (above 80%) suggests a "Team Up" or an "Interruption"
        if intensity > 0.8:
            # Add a random ally to watch your back or provide commentary (like the DBZ sidelines)
            potential_backup = random.choice(cast["allies"])
            if potential_backup not in required_characters:
                required_characters.append(potential_backup)

        # Low intensity (below 30%) Dialogue scenes might just be a solo reflection/monologue
        if intensity < 0.3 and scene_type == SceneType.DIALOGUE:
            # Maybe it's just you and your inner thoughts or a voice-over
            return ["Inner Spirit"]

        return list(set(required_characters))

    def _generate_hidden_objectives(self, scene_type: SceneType, intensity: float) -> Optional[Dict[str, str]]:
        """🎯 Generate high-stakes secret objectives with unique reward hooks"""
        
        # 40% chance to trigger a Hidden Objective (the 'S-Rank' challenge)
        if random.random() > 0.4:
            return None

        # We structure these as Dicts so the UI can show the Challenge AND the Reward
        objectives = {
            SceneType.TRAINING: [
                {"goal": "Master the flow without a single stumble", "reward": "Permanent +5% Agility boost"},
                {"goal": "Push the gravity to 100x during the final set", "reward": "Unlock 'Heavyweight' Title"},
                {"goal": "Counter your mentor's surprise strike", "reward": "Hidden Technique: 'Ghost Counter'"}
            ],
            SceneType.BATTLE: [
                {"goal": "Win with less than 10% Health remaining", "reward": "Zenkai Master: +500 Max HP"},
                {"goal": "Defeat the opponent using only basic strikes", "reward": "Trait: 'Pure Martial Artist'"},
                {"goal": "End the fight in under 3 turns", "reward": "Unlock 'God of Speed' aura FX"}
            ],
            SceneType.DIALOGUE: [
                {"goal": "Make them reveal the 'Project X' codename", "reward": "Unlock Secret Story Node"},
                {"goal": "Outmaneuver the villain's logic", "reward": "Trait: 'Master Manipulator'"},
                {"goal": "Mention the fallen hero's name at the right moment", "reward": "Gain a powerful ghost-ally"}
            ],
            SceneType.EXPLORATION: [
                {"goal": "Locate the 'Cursed Jade' fragment", "reward": "Special Item: 'Jade Amulet'"},
                {"goal": "Find the developer's hidden signature", "reward": "Unlock 'Meta-Awareness' dialogue"},
                {"goal": "Repair the ancient mechanism on the first try", "reward": "Gain +2000 Ki permanently"}
            ],
            SceneType.CLIMAX: [
                {"goal": "Save the 'Tragic Rival' from their fate", "reward": "Unlock 'True Ending' path"},
                {"goal": "Finish with a 100-hit combo", "reward": "Unlock 'Super Saiyan 2' early"},
                {"goal": "Refuse to use your power-up", "reward": "Unlock 'Base-Form Legend' achievement"}
            ]
        }

        # Get the list for the current scene type, fallback to generic
        scene_pool = objectives.get(scene_type, [{"goal": "Complete perfectly", "reward": "Glory"}])
        
        # Select one and return it
        return random.choice(scene_pool)

    def _infuse_emotional_architecture(self, plan: List[PlanStep], pacing_profile: Dict) -> List[PlanStep]:
        """💖 Transform a sequence of events into a resonant emotional journey"""
        
        # Emotional Archetypes for flavor
        themes = ["Justice", "Loss", "Pride", "Redemption", "Sacrifice", "Legacy"]
        selected_theme = random.choice(themes)

        for i, step in enumerate(plan):
            # 1. Map intensity to the "Heartbeat" of the saga
            step.emotional_intensity = pacing_profile["emotional_curve"][i]
            
            # 2. High-Tension "Pivot" Points
            if i in pacing_profile.get("narrative_tension_points", []):
                step.description = f"🏮 [PIVOT] {step.description}"
                step.expected_outcome += f" The theme of **{selected_theme}** weighs heavily on your soul here."
                # High tension points offer "Spirit" rewards instead of just power
                step.rewards["spirit_points"] = step.rewards.get("spirit_points", 0) + 15

            # 3. The "Memory Echo" (Callbacks & Foreshadowing)
            if i > 0:
                # Foreshadowing: Sensing the 'weight' of the future
                if random.random() > 0.7 and i < len(plan) - 1:
                    step.description += " \n\n*A cold shiver runs down your spine—the future is casting a long shadow...*"
                
                # Callback: Remembering the past
                if random.random() > 0.8:
                    step.description += f" \n\n*The echoes of your earlier choices regarding {selected_theme} resonate in this moment.*"

            # 4. Character Development Logic
            # Dialogue + High Intensity = A "Breakthrough" moment
            if step.scene_type == SceneType.DIALOGUE and step.emotional_intensity > 0.6:
                step.description = f"🌟 **BREAKTHROUGH:** {step.description}"
                step.expected_outcome = "You aren't just talking; you're evolving. " + step.expected_outcome
                # Breakthroughs provide unique "Archetype XP"
                step.rewards["archetype_xp"] = step.rewards.get("archetype_xp", 0) + 20
                
            # 5. The "Quiet Before the Storm"
            # If intensity is very low before a climax, emphasize the silence
            if step.emotional_intensity < 0.3 and i < len(plan) - 1:
                if plan[i+1].scene_type in [SceneType.BATTLE, SceneType.CLIMAX]:
                    step.description += " \n\n*The silence is deafening. The world seems to be holding its breath for what comes next.*"

        return plan
    
    def _seed_branching_narratives(self, plan: List[PlanStep], saga_name: str) -> List[PlanStep]:
        """🌳 Seed choice points that ripple through time and alter the saga's fabric"""
        
        for i, step in enumerate(plan):
            # 1. Strategic Placement of Choice Points
            # We seed branches on every other step, OR whenever the heart is racing (>0.7 intensity)
            if i % 2 == 0 or step.emotional_intensity > 0.7:
                step.branching_options = self._generate_branching_options(
                    step.scene_type, 
                    step.emotional_intensity,
                    i
                )

                # 2. Assign a "Consequence Vector"
                # This tells the LangGraph which part of the future is affected
                impact_areas = ["Alliance", "Power Evolution", "World State", "Character Fate"]
                area = random.choice(impact_areas)
                
                # 3. Dynamic Consequence Descriptions
                if i < len(plan) - 2:
                    # Early choices are about 'Sowing Seeds'
                    step.expected_outcome += (
                        f"\n\n⚠️ **CONSEQUENCE:** This decision will ripple into your "
                        f"future **{area}**. The path you choose now cannot be untread."
                    )
                elif i == len(plan) - 2:
                    # Final choices are about 'Harvesting the Storm'
                    step.expected_outcome += (
                        f"\n\n🔥 **FINAL WEIGHT:** Your actions here will directly "
                        f"dictate the nature of your final confrontation!"
                    )

                # 4. Inject "Choice Tension" for the AI
                # We add a hidden instruction for the LLM to emphasize the difficulty
                step.description += (
                    " [Narrative Note: Present this choice as a moral or tactical crossroads.]"
                )

        return plan


    def _dynamic_difficulty_scaling(self, plan: List[PlanStep], player_stats: Dict) -> List[PlanStep]:
        """⚔️ Scale world-threat and rewards using the 'Scaling Horizon' logic"""
        
        current_power = player_stats.get('power_level', 1000)
        
        # 1. Define the Threat Tier
        # This changes the vocabulary the AI uses to describe the world
        if current_power < 5000:
            tier = "Mortal"
            multiplier = 1.0
        elif current_power < 25000:
            tier = "Superhuman"
            multiplier = 1.5
        elif current_power < 100000:
            tier = "Planetary"
            multiplier = 2.2
        else:
            tier = "Cosmic"
            multiplier = 4.0

        for i, step in enumerate(plan):
            # 2. Scaling Rewards (The "Rich get Richer" vs "Underdog" logic)
            # We use a logarithmic scale so power gains don't explode infinitely
            reward_growth = math.log10(current_power) / 3.0
            step.rewards['power_level'] = int(step.rewards.get('power_level', 100) * reward_growth * multiplier)

            # 3. Narrative Reframing
            # We don't just replace words; we inject the current 'Threat Tier' 
            # into the AI's instruction set.
            if tier == "Cosmic":
                step.description = f"🌌 [COSMIC THREAT] {step.description}"
                step.description = step.description.replace("battle", "UNIVERSAL COLLISION")
                step.difficulty_modifier *= 2.0
            elif tier == "Planetary":
                step.description = f"🌍 [PLANETARY] {step.description}"
                step.description = step.description.replace("challenge", "CATASTROPHIC EVENT")
                step.difficulty_modifier *= 1.5

            # 4. The "Underdog" Safety Net
            # If the player is in a high-difficulty scene with low power, 
            # add a 'Willpower' bonus.
            if current_power < 2000 and step.difficulty_modifier > 1.2:
                step.rewards['spirit_points'] = step.rewards.get('spirit_points', 0) + 20
                step.description += " \n\n*(Your underdog spirit burns bright against these impossible odds!)*"

        return plan
    
    def _create_cinematic_introduction(self, plan: List[PlanStep], player_name: str, saga_name: str) -> AIMessage:
        """🎬 Generate an EPIC, high-fidelity cinematic roadmap for the player"""
        
        total_duration = sum(step.expected_duration for step in plan)
        high_stakes_count = len([s for s in plan if s.emotional_intensity > 0.8])
        choice_points = len([s for s in plan if s.branching_options])
        
        # Header with a "Wide-Screen" feel
        header = f"""
        {'═'*60}
        ║  🎬  SAGA OVERVIEW: {saga_name.upper()}  🎬  ║
        {'═'*60}
        
        ✨ **DESTINY HAS CALLED, {player_name.upper()}!**
        
        The chronicles of the **{saga_name}** are being written in real-time. 
        Prepare yourself for a journey spanning **{len(plan)} Acts**.
        
        📊 **SAGA SPECS:**
        🔥 {high_stakes_count} Critical Crisis Points | 🌪️ {choice_points} Divergent Realities
        ⏳ Estimated Arc Duration: {total_duration} Narrative Cycles
        
        {'━'*60}
        📜 **THE SCROLL OF FATE:**
        """

        body = ""
        for i, step in enumerate(plan, 1):
            # Create a visual intensity gauge
            level = int(step.emotional_intensity * 10)
            gauge = "🔥" * level + "❄️" * (10 - level)
            
            # Highlight "Crisis" acts
            is_crisis = step.emotional_intensity > 0.8
            act_header = f"◈ ACT {i}: {step.scene_type.name} " + ("⚠️ [CRISIS]" if is_crisis else "")
            
            body += f"""
        {act_header}
        ╭──────────────────────────────────────────────────────────
        │ 📖 **Premise:** {step.description[:120]}...
        │ 🎯 **Outcome:** {step.expected_outcome}
        │ ⚡ **Vibration:** [{gauge}] {int(step.emotional_intensity * 100)}%
        """
            if step.branching_options:
                body += f"│ 🧬 **Butterfly Effect:** A choice here ripples into eternity.\n"
            
            body += "╰──────────────────────────────────────────────────────────\n"

        footer = f"""
        {'━'*60}
        ⚡ **PROTAGONIST INITIALIZED.**
        The stars are aligning. The first chapter of your legend is already unfolding.
        
        **DO YOU ACCEPT THIS DESTINY?**
        🔥 *Type 'START' or your first action to begin the opening scene!*
        """

        return AIMessage(content=header + body + footer)
    
    def _get_scene_emoji(self, scene_type: SceneType) -> str:
        """🎭 Get cinematic emoji sets and status colors for scene types"""
        
        # We use a dictionary of dictionaries to store more than just a single icon
        # This allows you to style your UI borders or headers dynamically
        scene_assets = {
            SceneType.INTRODUCTION: {
                "main": "🌅", 
                "accent": "📜", 
                "style": "The Horizon Beckons"
            },
            SceneType.TRAINING: {
                "main": "🥋", 
                "accent": "🔥", 
                "style": "Limit Breaking"
            },
            SceneType.BATTLE: {
                "main": "⚔️", 
                "accent": "💥", 
                "style": "Total Conflict"
            },
            SceneType.DIALOGUE: {
                "main": "🗣️", 
                "accent": "🎐", 
                "style": "Fate's Whisper"
            },
            SceneType.EXPLORATION: {
                "main": "🧭", 
                "accent": "🌲", 
                "style": "Into the Unknown"
            },
            SceneType.CLIMAX: {
                "main": "🌟", 
                "accent": "☄️", 
                "style": "Final Transcendence"
            }
        }
        
        # Return the main emoji, or a sparkle if not found
        return scene_assets.get(scene_type, {"main": "✨"})["main"]

    def _create_emergency_plan(self, state: GameState) -> Dict[str, Any]:
        """🆘 EMERGENCY PLAN - When the logic breaks, the Spirit takes over!"""
        
        print("⚠️ EMERGENCY PLAN ACTIVATED - SHONEN REBOOT ENGAGED!")
        
        # We build a tighter, more punchy arc that mirrors the 
        # 'Hero's Journey' in its purest anime form.
        emergency_plan = [
            PlanStep(
                scene_type=SceneType.INTRODUCTION,
                description="The mundane world shatters! A sudden, terrifying energy signature "
                            "erupts within you, revealing a lineage you never knew existed.",
                expected_outcome="Awaken your dormant Aura and survive the initial surge.",
                expected_duration=1,
                emotional_intensity=0.8,
                archetype="Chosen One",
                branching_options=self._generate_branching_options(SceneType.INTRODUCTION, 0.8, 0)
            ),
            PlanStep(
                scene_type=SceneType.TRAINING,
                description="Under the guidance of a cryptic master, you enter the 'Gravity Chamber' "
                            "of your soul to harness the raw chaos of your new power.",
                expected_outcome="Establish your first signature technique.",
                expected_duration=2,
                emotional_intensity=0.6,
                archetype="Disciple",
                branching_options=self._generate_branching_options(SceneType.TRAINING, 0.6, 1)
            ),
            PlanStep(
                scene_type=SceneType.BATTLE,
                description="The destined Rival appears! They represent everything you are not, "
                            "and they intend to prove your awakening was a fluke.",
                expected_outcome="Taste a bitter defeat that fuels a legendary resolve.",
                expected_duration=2,
                emotional_intensity=0.9,
                archetype="Rivalry",
                branching_options=self._generate_branching_options(SceneType.BATTLE, 0.9, 2)
            ),
            PlanStep(
                scene_type=SceneType.CLIMAX,
                description="The Grand Arena! Thousands roar as you face your rival once more. "
                            "The air screams with the friction of your clashing spirits!",
                expected_outcome="Surpass your limits and achieve a transcendent victory.",
                expected_duration=3,
                emotional_intensity=1.0,
                archetype="Legendary",
                branching_options=self._generate_branching_options(SceneType.CLIMAX, 1.0, 3)
            )
        ]

        # Create the Hype Message
        message_content = f"""
    ╔══════════════════════════════════════════════════════════════════╗
    ║             🔥 EMERGENCY PROTOCOL: SHONEN REBOOT 🔥              ║
    ╚══════════════════════════════════════════════════════════════════╝

    **DATA CORRUPTION DETECTED... SPIRIT CORE STABILIZED!**

    {state.player_name}, the complex threads of fate have tangled, but your 
    **WILLPOWER** is absolute! We are stripping away the noise and returning 
    to the **CLASSIC PATH**.

    📜 **THE REBOOT ARC: "THE TOURNAMENT OF SOULS"**
    • **AWAKEN:** Unleash the power that was hidden in plain sight.
    • **SPAR:** Suffer the defeat that creates a true warrior.
    • **ASCEND:** Shatter your limits in the Grand Arena finale!

    **[SYSTEM NOTE]:** Emergency Mode is active. All Power Gains are DOUBLED 
    until the Climax is reached. 

    🔥 **THE FIRST ACT BEGINS NOW! WHAT IS YOUR MOVE?**
        """
        
        message = AIMessage(content=message_content)

        return {
            "current_plan": emergency_plan,
            "plan_step_index": 0,
            "plan_revisions": state.plan_revisions + 1,
            "messages": [message],
            "total_actions": state.total_actions + 1,
            "narrative_metadata": {
                "emergency_mode": True, 
                "classic_anime": True,
                "power_multiplier": 2.0  # Hidden bonus for the player to 'catch up'
            }
        }
    
    def _generate_opening_outcome(self, player_analysis: Dict) -> str:
        """🌟 Generate high-impact opening outcomes with narrative hooks"""
        
        # Extracting the archetype for a personalized touch
        arch = player_analysis.get('archetype', 'Warrior')
        
        outcomes = [
            # The Destiny Hook
            f"You fully embrace your destiny as a {arch}. The seal on your power is "
            f"permanently broken, and the world—and those who hunt your kind—now "
            f"know exactly where to find you.",
            
            # The Milestone Hook
            f"The first step on a legendary path is carved in blood and stone. "
            f"You have secured a temporary sanctuary, but the call of the {arch} "
            f"spirit demands you find the source of the recent disturbance.",
            
            # The Transformation Hook
            f"Your ordinary life is reduced to ash. From the ruins, your saga BEGINS! "
            f"You possess the raw {arch} potential, but you must now find a mentor "
            f"before this unrefined energy consumes you.",
            
            # The Rivalry/Antagonist Hook
            f"The shadows retreat for now, but they have left a mark on your soul. "
            f"You have survived your first encounter, proving you are a worthy {arch}, "
            f"but the enemy's true face remains hidden in the clouds.",
            
            # The Mystery Hook
            f"An ancient resonance is triggered within you. As a {arch}, you now "
            f"hear the 'Hum of the World.' Your objective is clear: follow the "
            f"vibration to the Forbidden Peaks."
        ]
        
        return random.choice(outcomes)
    
    def _generate_climax_outcome(self, saga_name: str, intensity: float) -> str:
        """🌟 Generate world-shaping climax outcomes with finality"""
        
        # We use intensity to determine how "loud" the victory is
        spirit_level = "Cosmic" if intensity > 0.8 else "Heroic"
        
        outcomes = [
            # The Limit Break
            f"You achieve the impossible and transcend your mortal limits! The "
            f"shards of your previous self lie scattered, replaced by a being of "
            f"pure {spirit_level} energy. The {saga_name} saga ends in blinding light.",
            
            # The Earth-Shatterer
            f"The {saga_name} saga reaches its EARTH-SHATTERING conclusion! Your "
            f"final strike was so powerful it rewritten the local geography, "
            f"leaving a permanent monument to your {spirit_level} resolve.",
            
            # The Growth Payoff
            f"Your growth culminates in an ultimate victory that echoes across the "
            f"realms. You didn't just win the battle; you proved that your {spirit_level} "
            f"spirit is the new standard by which all future legends will be measured.",
            
            # The Subversion
            f"The prophecy is fulfilled in ways no one expected! By merging your "
            f"{spirit_level} power with mercy, you have ended the {saga_name} cycle "
            f"of violence forever, ushering in a new age of peace.",
            
            # The Sacrifice/Burden
            f"Victory is yours, but at a {spirit_level} cost. You stand as the lone "
            f"sentinel of the {saga_name}, your name now a prayer whispered by "
            f"those you saved and a curse feared by those you defeated."
        ]
        
        # Using .format for saga_name and returning a random high-impact outcome
        return random.choice(outcomes).format(saga_name=saga_name)
    
    def _generate_outcome(self, scene_type: SceneType, intensity: float) -> str:
        """🌟 Generate high-stakes, narrative-shifting expected outcomes"""
        
        # We can use intensity to add a prefix for extra 'flavor'
        prefix = "🔥 CRITICAL SUCCESS: " if intensity > 0.8 else "✨ ACHIEVEMENT: "
        
        outcomes = {
            SceneType.TRAINING: [
                f"{prefix}Your neural pathways rewiring under the pressure, unlocking a technique once thought impossible.",
                f"{prefix}The barrier of your previous limitations shatters, permanently elevating your base power floor.",
                f"{prefix}You earn the 'Nod of the Master,' a rare sign that you are no longer a student, but a peer."
            ],
            SceneType.BATTLE: [
                f"{prefix}You've etched your name into the memory of the battlefield, earning the fearful respect of foes.",
                f"{prefix}The heat of combat has tempered your spirit like high-grade steel; you are now harder to break.",
                f"{prefix}You survived the impossible. Both your scars and your victory serve as a warning to those who follow."
            ],
            SceneType.DIALOGUE: [
                f"{prefix}The veil of secrecy is lifted. You now hold a piece of the truth that changes the rules of the game.",
                f"{prefix}A bridge is built where there was once a canyon. An ally’s loyalty is now a weapon at your disposal.",
                f"{prefix}You have successfully planted a seed of doubt in your enemy's mind—it will bloom when you least expect it."
            ],
            SceneType.EXPLORATION: [
                f"{prefix}The map grows smaller as you uncover a sanctuary that hasn't seen the sun in a thousand years.",
                f"{prefix}You have reclaimed a relic of the Old World, a tool that resonates with your specific energy.",
                f"{prefix}The 'Geography of Fate' is revealed. You now understand not just where you are, but *why* you are here."
            ]
        }
        
        scene_outcomes = outcomes.get(scene_type, ["The chronicle of your legend grows by another decisive chapter!"])
        return random.choice(scene_outcomes)
    
    def _validate_plan(self, plan: List[PlanStep]) -> bool:
        """✅ Validate that the generated plan meets quality standards"""
        
        if len(plan) < 3:
            print("⚠️ Plan too short, adding emergency steps")
            return False
        
        # Check for climax at the end
        if plan[-1].scene_type != SceneType.CLIMAX:
            print("⚠️ Plan missing climax, adjusting")
            plan[-1].scene_type = SceneType.CLIMAX
        
        # Check emotional arc progression
        intensities = [step.emotional_intensity for step in plan]
        if max(intensities) < 0.7:
            print("⚠️ Emotional arc too flat, boosting peaks")
            plan[-1].emotional_intensity = 0.9
        
        return True