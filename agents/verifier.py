from typing import List, Any, Dict, Optional, Tuple
from langchain_core.messages import AIMessage, SystemMessage, BaseMessage, HumanMessage
import json
import re
from datetime import datetime

from schemas.state import GameState, PlanStep, SceneType
from utils.llm_wrapper import llm_wrapper
from utils.prompts import SystemPrompts


class VerifierConfig:
    """Configuration constants for VerifierAgent"""
    
    # Quality score penalties by severity
    PENALTIES = {
        "critical": 0.3,
        "high": 0.2,
        "medium": 0.1,
        "low": 0.05
    }
    
    # Length bonuses/penalties
    LENGTH_BONUS_THRESHOLD = 500
    LENGTH_PENALTY_THRESHOLD = 200
    LENGTH_BONUS = 0.1
    LENGTH_PENALTY = 0.1
    
    # Emotional keyword weights
    EMOTIONAL_WEIGHTS = {
        "high": 0.3,
        "medium": 0.15,
        "low": 0.05
    }


class VerifierAgent:
    """
    ✅ THE VERIFIER AGENT - NARRATIVE QUALITY GUARDIAN ✅
    
    Responsible for ensuring every scene meets quality standards:
    - Consistency with established lore and past events
    - Character voice accuracy
    - Plot hole prevention
    - Power level consistency
    - Emotional resonance
    - Logical coherence
    
    This agent acts as a quality gate before scenes are presented to the player!
    """
    def __init__(self, strictness: str = "medium"):
        """
        Initialize the verifier with configurable strictness
        
        Args:
            strictness: "low" (forgiving), "medium" (balanced), "high" (strict)
        """

        self.strictness = strictness

        # strictness thresholds
        self.thresholds = {
            "low": {
                "min_quality_score": 0.5,
                "max_unexpected_events": 5,
                "check_character_voice": False,
                "check_power_consistency": False,
                "check_foreshadowing": False,  # FIXED: spelling
                "check_emotional_arc": False    # FIXED: renamed
            },
            "medium": {
                "min_quality_score": 0.7,
                "max_unexpected_events": 5,
                "check_character_voice": True,
                "check_power_consistency": True,
                "check_foreshadowing": True,     # FIXED: spelling
                "check_emotional_arc": True       # FIXED: renamed
            },
            "high": {
                "min_quality_score": 0.84,
                "max_unexpected_events": 2,
                "check_character_voice": True,
                "check_power_consistency": True,
                "check_foreshadowing": True,      # FIXED: spelling
                "check_emotional_arc": True        # FIXED: renamed
            }
        }

        # common issues to look for
        self.issue_patterns = self._load_issue_patterns()

        print(f"✅ VERIFIER AGENT initialized (strictness: {strictness})")

    def invoke(self, state: GameState) -> Dict[str, Any]:
        """
        🔍 Verify the quality of the last scene and suggest corrections if needed
        
        Args:
            state: Current game state with the latest scene
            
        Returns:
            Dictionary with verification results and any needed corrections
        """
        print(f"\n{'🔍'*50}")
        print(f"🔍 VERIFIER: Analyzing narrative quality...")
        print(f"{'🔍'*50}")

        # get the last ai message, the scene which we need to verify
        last_ai_message = None
        for msg in reversed(state.messages):
            if hasattr(msg, 'type') and msg.type == "ai":
                last_ai_message = msg
                break
        
        if not last_ai_message:
            print("⚠️ No AI message found to verify")
            return {
                "needs_correction": False,
                "issues": [],
                "quality_score": 0.5,
                "verifier_notes": "No scene to verify.",
                "corrected_narrative": None,
                "tokens_used": llm_wrapper.total_tokens_used
            }
        
        # now get the current step to verify
        current_step = state.current_step
        if not current_step:
            print("⚠️ No current step found")
            return {
                "needs_correction": False,
                "issues": [],
                "quality_score": 0.6,
                "verifier_notes": "No active plan step",
                "corrected_narrative": None,
                "tokens_used": llm_wrapper.total_tokens_used
            }
        
        # Run all verification checks
        issues = []

        # 1. Basic quality checks
        quality_issues = self._check_basic_quality(last_ai_message, current_step)
        issues.extend(quality_issues)

        # 2. Character voice check (if enabled)
        if self.thresholds[self.strictness]["check_character_voice"]:
            voice_issues = self._check_character_voice(last_ai_message, state, current_step)
            issues.extend(voice_issues)

        # 3. power consistency check if enabled
        if self.thresholds[self.strictness]["check_power_consistency"]:
            power_issues = self._check_power_consistency(last_ai_message, state, current_step)
            issues.extend(power_issues)

        # 4. check for emotional resonance
        emotion_issues = self._check_emotional_resonance(last_ai_message, state, current_step)
        issues.extend(emotion_issues)

        # 5. check for plot holes
        plot_issues = self._check_plot_holes(last_ai_message, state)
        issues.extend(plot_issues)

        # 6. check unexpected event counts
        if hasattr(current_step, 'unexpected_events') and len(current_step.unexpected_events) > self.thresholds[self.strictness]["max_unexpected_events"]:
            issues.append({
                "type": "too_many_unexpected_events",
                "severity": "high",
                "description": f"Too many unexpected events ({len(current_step.unexpected_events)}) in this scene.",
                "suggestion": "Consider replanning or adjusting the narrative flow."
            })

        # calculate overall quality score
        quality_score = self._calculate_quality_score(issues, last_ai_message)

        # Determine if correction is needed
        needs_correction = quality_score < self.thresholds[self.strictness]["min_quality_score"]

        # generate verifier notes
        verifier_notes = self._generate_verifier_notes(issues, quality_score)

        print(f"\n📊 QUALITY SCORE: {quality_score:.1%}")
        print(f"📊 ISSUES FOUND: {len(issues)}")
        print(f"📊 NEEDS CORRECTION: {needs_correction}")

        if issues:
            print("\n📋 ISSUES DETECTED:")
            for i, issue in enumerate(issues):
                print(f"   {i+1}. [{issue['severity']}] {issue['description']}")

        # if correction is needed, generate corrected version
        corrected_narrative = None
        if needs_correction and self.strictness != "low":
            # FIXED: Pass issues list, not single issue
            corrected_narrative = self._generate_correction(
                last_ai_message,
                issues,  # FIXED: was 'issue'
                state,
                current_step
            )
            print("✅ Generated corrected narrative")

        return {
            "needs_correction": needs_correction,
            "issues": issues,
            "quality_score": quality_score,
            "verifier_notes": verifier_notes,
            "corrected_narrative": corrected_narrative,
            "tokens_used": llm_wrapper.total_tokens_used 
        }
    
    # =========================================================================
    # VERIFICATION CHECKS
    # =========================================================================

    def _check_basic_quality(self,
                             message: AIMessage,
                             step: PlanStep) -> List[Dict[str, Any]]:
        """
        📝 Check basic narrative quality
        - Minimum length
        - Proper formatting
        - Contains expected elements
        """

        issues = []
        content = message.content

        # check minimum length
        if len(content) < 100:
            issues.append({
                "type": "too_short",
                "severity": "medium",
                "description": f"Scene is too short ({len(content)} chars, minimum required is 100)",
                "suggestion": "Add more descriptive detail and character interaction"
            })

        # check if scene matches expected outcome
        if step.expected_outcome.lower() not in content.lower():
            issues.append({
                "type": "missed_outcome",
                "severity": "high",
                "description": f"Scene doesn't address expected outcome: {step.expected_outcome}",
                "suggestion": "Ensure the scene advances toward the planned outcome."
            })

        # check for proper punctuation, sentences should end properly
        sentences = re.split(r'[.!?]', content)
        incomplete_sentences = [s for s in sentences if len(s.strip()) > 0 and not s.strip()[-1] in '.!?']

        if incomplete_sentences:
            issues.append({
                "type": "poor_formatting",
                "severity": "low",
                "description": f"Found {len(incomplete_sentences)} sentences without proper ending punctuation.",
                "suggestion": "Use proper punctuation for better readability."
            })
        return issues
    

    def _check_character_voice(self,
                               message: AIMessage,
                               state: GameState,
                               step: PlanStep) -> List[Dict[str, Any]]:
        
        """
        🎭 Check if characters speak in character
        """
        issues = []
        content = message.content

        # Character voice patterns
        character_voices = {
            "mentor": {
                "patterns": [
                    r"listen", r"learn", r"wisdom", r"young", r"powerful", r"potential", r"train",
                    r"when I was your age", r"I have seen", r"trust in yourself"
                ],
                "avoid": [
                    r"I'll destroy you", r"you're weak", r"give up"
                ]
            },
            "rival": {
                "patterns": [
                    r"fight", r"battle", r"prove", r"stronger", r"defeat", r"challenge", r"rival",
                    r"I won't lose", r"you're not ready", r"show me what you've got"
                ],
                "avoid": [
                    r"I need your help", r"teach me", r"I'm scared"
                ]
            },
            "villain": {
                "patterns": [
                    r"destroy", r"power", r"fear", r"pathetic", r"worthless", r"submit", r"darkness",
                    r"you cannot stop me", r"witness my power", r"your suffering begins"
                ],
                "avoid": [
                    r"I believe in you", r"let's be friends", r"I was wrong"
                ]
            },
            "ally": {
                "patterns": [
                    r"help", r"together", r"trust", r"friend", r"believe", r"support",
                    r"I've got your back", r"we can do this", r"don't give up"
                ],
                "avoid": [
                    r"I will defeat you", r"you're my enemy", r"prepare to die"
                ]
            }
        }

        # check each character present in the scene
        for char_name in step.required_characters:
            char_key = char_name.lower()
            if char_key in character_voices:
                voice = character_voices[char_key]

                # check if character speaks at all
                char_mentioned = False
                for pattern in voice['patterns']:
                    if re.search(pattern, content, re.IGNORECASE):
                        char_mentioned = True
                        break
                
                if not char_mentioned and char_key in ["mentor", "rival", "villain", "ally"]:
                    issues.append({
                        "type": "missing_character_voice",
                        "severity": "medium",
                        "description": f"Character '{char_name}' doesn't speak or act in character",
                        "suggestion": f"Add dialogue or actions that reflect their {char_key} role."
                    })

                # check for out of character speech
                for avoid_pattern in voice["avoid"]:
                    if re.search(avoid_pattern, content, re.IGNORECASE):
                        issues.append({
                            "type": "out_of_character",
                            "severity": "high",
                            "description": f"{char_name} speaks out of character.",
                            "suggestion": "Ensure dialogue matches their personality"
                        })
            
        return issues
        
    
    def _check_power_consistency(
        self,
        message: AIMessage,
        state: GameState,
        step: PlanStep,
    ) -> List[Dict[str, Any]]:
        """
        ⚡ Check if power levels and abilities are consistent
        """

        issues = []
        content = message.content
        player_power = state.player_stats.get("power_level", 5000)

        # look for power claims
        power_mentions = re.findall(r'power\s*(?:level)?\s*(?:of)?\s*(\d+)', content, re.IGNORECASE)

        for power_str in power_mentions:
            try:
                mentioned_power = int(power_str)
                # check if mentioned power is validly different from actual
                ratio = mentioned_power / player_power if player_power > 0 else 1

                if ratio > 10:
                    issues.append({
                        "type": "power_inflation",
                        "severity": "high",
                        "description": f"Scene mentions power level {mentioned_power}, but player has {player_power}",
                        "suggestion": "Scale power mentions to be closer to actual player stats"
                    })
                
                elif ratio < 0.1 and mentioned_power > 0:
                    issues.append({
                        "type": "power_deflation",
                        "severity": "medium",
                        "description": f"Scene underestimates player power ({mentioned_power} vs {player_power})",
                        "suggestion": "Acknowledge the player's true power level"
                    })
            except ValueError:
                pass

        # Check for transformation references
        transformations = state.player_stats.get("transformations", [])

        # FIXED: Typo in "Super Saiyan"
        if "Super Saiyan" in content and "Super Saiyan" not in transformations:
            if player_power < 9000:
                issues.append({
                    "type": "premature_transformation",
                    "severity": "high",
                    "description": "Scene references Super Saiyan transformation before reaching 9000 power level",
                    "suggestion": "Remove transformation references or increase power level first"
                })
            
        return issues  # FIXED: Moved outside the loop
        
    def _check_plot_holes(self,
                          message: AIMessage,
                          state: GameState) -> List[Dict[str, Any]]:
        
        """
        🕳️ Check for plot holes and inconsistencies with past events
        """

        issues = []
        content = message.content

        # Check for character resurrection (if someone died, they shouldn't appear)
        for npc_key, npc_data in state.npcs.items():
            if not npc_data.get("alive", True):
                # if not alive, then npc is dead - check if they are mentioned as alive
                name = npc_data.get("name", npc_key)
                # FIXED: Logic error in condition
                if name in content and ("alive" in content.lower() or "appear" in content.lower()):
                    issues.append({
                        "type": "plot_hole",
                        "severity": "critical",
                        "description": f"Dead character {name} appears or is mentioned as alive in the scene",
                        "suggestion": "Remove references to dead character or explain resurrection."
                    })

        # check for resolved plot threads
        if hasattr(state, 'active_plot_threads'):
            for thread in state.active_plot_threads:
                if "resolved" in content.lower() and thread.lower() in content.lower():
                    # check if we actually resolved it properly
                    issues.append({
                        "type": "plot_thread_resolution",
                        "severity": "medium",
                        "description": f"Plot thread '{thread}' may have been resolved too quickly",
                        "suggestion": "Ensure proper buildup and payoff for major plot threads"
                    })
                
        return issues  # FIXED: Moved outside the loop
            
    
    def _check_emotional_resonance(self,
                                   message: AIMessage,
                                   state: GameState,
                                   step: PlanStep) -> List[Dict[str, Any]]:
        
        """
        💖 Check if the scene has appropriate emotional weight
        """

        issues = []
        content = message.content

        # Emotional keywords by intensity
        emotional_keywords = {
            "high": [
                "scream", "rage", "despair", "triumph", "glory", "sacrifice",
                "destroy", "annihilate", "transcend", "legendary", "epic"
            ],
            "medium": [
                "determined", "focus", "power", "challenge", "fight", "battle",
                "friend", "trust", "betray", "secret", "reveal"
            ],
            "low": [
                "think", "wonder", "maybe", "perhaps", "consider", "wait",
                "calm", "quiet", "peaceful", "rest"
            ]
        }

        # Calculate emotional intensity based on keywords
        emotional_score = 0
        for intensity, keywords in emotional_keywords.items():
            for keyword in keywords:
                if keyword in content.lower():
                    emotional_score += VerifierConfig.EMOTIONAL_WEIGHTS.get(intensity, 0.1)

        emotional_score = min(1.0, emotional_score)

        # Compare with expected emotional intensity from plan step
        expected_intensity = step.emotional_intensity if hasattr(step, "emotional_intensity") else 0.5

        if abs(emotional_score - expected_intensity) > 0.4:
            issues.append({
                "type": "emotional_mismatch",
                "severity": "medium",
                "description": f"Scene emotional intensity ({emotional_score:.1%}) doesn't match planned ({expected_intensity:.1%})",
                "suggestion": f"Adjust emotional tone to be more {'intense' if expected_intensity > emotional_score else 'subtle'}"
            })
        return issues
    

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def _calculate_quality_score(self, 
                                 issues: List[Dict[str, Any]], 
                                 message: AIMessage) -> float:
        
        """
        📊 Calculate overall quality score based on issues
        """

        if not issues:
            return 1.0
        
        # Base score
        score = 1.0

        # Deduct based on severity using config
        for issue in issues:
            severity = issue.get("severity", "medium")
            score -= VerifierConfig.PENALTIES.get(severity, 0.1)

        # Add bonus/penalty for length using config
        content_length = len(message.content)
        if content_length > VerifierConfig.LENGTH_BONUS_THRESHOLD:
            score += VerifierConfig.LENGTH_BONUS
        elif content_length < VerifierConfig.LENGTH_PENALTY_THRESHOLD:
            score -= VerifierConfig.LENGTH_PENALTY
        
        return max(0.0, min(1.0, score))
    

    def _generate_verifier_notes(self,
                                 issues: List[Dict[str, Any]],
                                 quality_score: float) -> str:
        
        """
        📝 Generate human-readable verifier notes
        """

        if not issues:
            return "✨ Narrative quality is excellent! No issues detected."
        
        if quality_score > 0.8:
            prefix = "🌟 High quality with minor issues:"
        elif quality_score > 0.6:
            prefix = "📝 Acceptable quality with some issues:"
        elif quality_score > 0.4:
            prefix = "⚠️ Needs improvement:"
        else:
            prefix = "❌ Significant issues detected:"
        
        notes = [prefix]

        for issue in issues[:4]:  # show top 4 issues
            notes.append(f"  • {issue['description']}")

        if len(issues) > 4:
            notes.append(f"  • ... and {len(issues) - 4} more issues")

        if issues:
            notes.append(f"\n💡 Suggestion: {issues[0]['suggestion']}")
        
        return "\n".join(notes)
    
    def _generate_correction(self,
                             original_message: AIMessage,
                             issues: List[Dict[str, Any]],
                             state: GameState,
                             step: PlanStep) -> AIMessage:
        """
        🔧 Generate a corrected version of the narrative using LLM
        """
         
        system_prompt = """You are a Narrative Correction Specialist. Your job is to fix issues in anime scenes 
while preserving the original intent and improving quality. Maintain the same basic plot points 
but address the specific issues identified by the verifier."""

        # build issue description
        # FIXED: Added space after dash and proper string formatting
        issue_desc = "\n".join(
            [f"- {issue['description']} (Severity: {issue['severity']})" for issue in issues]
        )

        user_prompt = f"""
Please correct the following anime scene based on these issues:

**ISSUES TO FIX:**
{issue_desc}

**SCENE CONTEXT:**
- Scene Type: {step.scene_type.value}
- Expected Outcome: {step.expected_outcome}
- Player Power Level: {state.player_stats.get('power_level', 5000)}

**ORIGINAL SCENE:**
{original_message.content}

**CORRECTION GUIDELINES:**
1. Address all identified issues
2. Keep the same basic plot progression
3. Improve emotional resonance if needed
4. Ensure character voices are consistent
5. Maintain power level consistency

Return ONLY the corrected scene text, no explanations or JSON.
"""
        try:
            corrected = llm_wrapper.generate_structured_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_format="text"
            )

            if isinstance(corrected, dict) and "response" in corrected:
                return AIMessage(content=corrected["response"])
            elif isinstance(corrected, str):
                return AIMessage(content=corrected)
            
        except Exception as e:
            print(f"⚠️ Correction generation failed: {e}")
        
        # if correction fails, return the original message
        return original_message
    

    def _load_issue_patterns(self) -> Dict[str, List[str]]:
        """
        📚 Load common issue patterns for quick detection
        """
        return {
            "plot_hole": [
                r"how did (.*) survive",
                r"but earlier (.*) happened",
                r"wait, (.*) was dead",
                r"contradicts",
                r"inconsistent"
            ],
            "character_voice": [
                r"sounds nothing like",
                r"would never say",
                r"out of character",
                r"doesn't fit"
            ],
            "power_level": [
                r"power level (.*) doesn't make sense",
                r"too weak to",
                r"too strong to",
                r"impossible for them to"
            ]
        }
    
    # =========================================================================
    # FACTORY FUNCTION
    # =========================================================================


def create_verifier(strictness: str = "medium") -> VerifierAgent:
    """
    🏭 Factory function to create a verifier agent
    
    Args:
        strictness: "low", "medium", or "high"
    
    Returns:
        Configured VerifierAgent
    """
    return VerifierAgent(strictness=strictness)


