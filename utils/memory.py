from __future__ import annotations
from langchain_core.messages import BaseMessage

from schemas.state import GameState

from typing import List, Dict, Any, Optional, Tuple
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from datetime import datetime
import json
import tiktoken
import re


class MemoryManager:
    """
    Memory compression and context management for the saga simulator.

    Responsibilities:
    - Compress long conversation histories
    - Maintain essential context for the AI
    - Track important plot points and character relationships
    - Optimize token usage for LLM calls
    - Generate summaries of past events
    """

    def __init__(
        self,
        enable_compression: bool = True,
        max_tokens: int = 100000,
        compression_threshold: int = 50000,
        summary_interval: int = 10,
        message_overhead_tokens: int = 4,
        max_important_events: int = 50,
        max_recent_messages: int = 20,
    ) -> None:
        self.enable_compression = enable_compression
        self.max_tokens = max_tokens
        self.compression_threshold = compression_threshold
        self.summary_interval = summary_interval
        self.message_overhead_tokens = message_overhead_tokens
        self.max_important_events = max_important_events
        self.max_recent_messages = max_recent_messages

        self.tokenizer = None
        if tiktoken is not None:
            try:
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
            except Exception:
                self.tokenizer = None

        self.important_events: List[Dict[str, Any]] = []
        self.relationship_memory: Dict[str, Dict[str, Any]] = {}
        self.plot_threads: Dict[str, Dict[str, Any]] = {}

    # ---------------------------------------------------------------------
    # Token management
    # ---------------------------------------------------------------------

    def count_tokens(self, text: Optional[str]) -> int:
        """Count tokens in text, handling None values"""
        if not text:
            return 0
        if self.tokenizer is not None:
            return len(self.tokenizer.encode(text))
        return max(1, len(text) // 3)  # Rough estimate: ~3 chars per token

    def count_messages_tokens(self, messages: List[BaseMessage]) -> int:
        """Count tokens in a list of messages including overhead"""
        total = 0
        for msg in messages:
            total += self.count_tokens(getattr(msg, "content", None))
            total += self.message_overhead_tokens  # FIXED: Use configured value
        return total

    def should_compress(self, state: GameState) -> bool:
        if not self.enable_compression:
            return False

        if state.tokens_used > self.compression_threshold:
            return True

        if len(state.messages) > 50:
            return True

        if state.scene_counter > 0 and state.scene_counter % self.summary_interval == 0:
            return True

        return False

    # ---------------------------------------------------------------------
    # Memory compression
    # ---------------------------------------------------------------------

    def compress_memory(self, state: GameState) -> str:
        key_events = self._extract_key_events(state)
        character_relationships = self._extract_relationships(state)
        plot_progress = self._extract_plot_progress(state)
        player_growth = self._extract_player_growth(state)

        summary_parts = []
        summary_parts.append(f"=== SAGA SUMMARY ===")
        summary_parts.append(f"Player: {state.player_name}")
        summary_parts.append(f"Saga: {state.saga_name}")
        summary_parts.append(f"Power Level: {state.player_stats.get('power_level', 'Unknown')}")
        summary_parts.append(f"Ki Mastery: {state.player_stats.get('ki_mastery', 0)}%")
        summary_parts.append(f"Scenes Completed: {state.scene_counter}")

        if key_events:
            summary_parts.append("\n📜 KEY EVENTS:")
            for event in key_events[-5:]:  # Last 5 events
                summary_parts.append(f"• {event}")

        # Relationships
        if character_relationships:
            summary_parts.append("\n🤝 RELATIONSHIPS:")
            for char, rel in list(character_relationships.items())[:3]:
                summary_parts.append(f"• {char}: {rel}")

        # Plot progress
        if plot_progress:
            summary_parts.append(f"\n🎯 CURRENT PLOT: {plot_progress}")

        # Player growth
        if player_growth:
            summary_parts.append(f"\n⚡ GROWTH: {player_growth}")

        # Current objective
        current_step = state.current_step
        if current_step:
            summary_parts.append(f"\n🎬 CURRENT OBJECTIVE: {current_step.description}")
            if hasattr(current_step, 'expected_outcome'):
                summary_parts.append(f"   Goal: {current_step.expected_outcome}")

        summary = "\n".join(summary_parts)
        self._store_important_events(state, summary)
        return summary

    def _extract_key_events(self, state: GameState) -> List[str]:
        events: List[str] = []
        significant_indicators = [
            "transformed",
            "defeated",
            "awakened",
            "discovered",
            "learned",
            "mastered",
            "achieved",
            "unlocked",
            "over 9000",
            "legendary",
            "epic",
            "final","sacrifice", "betrayal", "revealed", "secret"
        ]

        for msg in state.messages[-20:]:
            # FIXED: Safer type checking
            msg_type = getattr(msg, "type", None)
            if msg_type == "ai" or isinstance(msg, AIMessage):
                content = (msg.content or "").lower()
                for indicator in significant_indicators:
                    if indicator in content:
                        # Extract the sentence containing the indicator
                        sentences = re.split(r'[.!?]', msg.content or "")
                        for sentence in sentences:
                            if indicator in sentence.lower():
                                events.append(sentence.strip())
                                break
                        break

        seen = set()
        unique_events = []
        for event in events:
            if event not in seen and len(event) > 10:  # FIXED: Minimum length
                seen.add(event)
                unique_events.append(event)

        return unique_events

    def _extract_relationships(self, state: GameState) -> Dict[str, str]:
        relationships: Dict[str, str] = {}
        if hasattr(state, "relationships") and state.relationships:
            for char, value in state.relationships.items():
                if isinstance(value, (int, float)):
                    if value > 0.7:
                        relationships[char] = "Close Ally"
                    elif value > 0.3:
                        relationships[char] = "Friend"
                    elif value > -0.3:
                        relationships[char] = "Neutral"
                    elif value > -0.7:
                        relationships[char] = "Rival"
                    else:
                        relationships[char] = "Enemy"
                else:
                    relationships[char] = str(value)
        
        # Fallback to NPC data
        if not relationships and hasattr(state, "npcs"):
            for npc_key, npc_data in state.npcs.items():
                name = npc_data.get("name", npc_key)
                if "mentor" in npc_key:
                    relationships[name] = "Mentor"
                elif "rival" in npc_key:
                    relationships[name] = "Rival"
                elif "villain" in npc_key:
                    relationships[name] = "Threat"
                else:
                    mood = npc_data.get("mood", "neutral")
                    relationships[name] = mood.capitalize()

        return relationships

    def _extract_plot_progress(self, state: GameState) -> str:
        if state.current_plan and state.plan_step_index < len(state.current_plan):
            current_step = state.current_plan[state.plan_step_index]
            progress = (
                f"Act {state.plan_step_index + 1}/{len(state.current_plan)}: "
                f"{current_step.scene_type.value}"
            )
            if hasattr(current_step, "emotional_intensity"):
                intensity = current_step.emotional_intensity
                if intensity > 0.8:
                    progress += " (Climactic Moment)"
                elif intensity > 0.5:
                    progress += " (Rising Action)"
                else:
                    progress += " (Building)"
            return progress
        return "Beginning of saga"

    def _extract_player_growth(self, state: GameState) -> str:
        """Extract player growth milestones"""
        growth_points: List[str] = []
        stats = state.player_stats
        
        # Power level milestones
        power = stats.get("power_level", 0)
        if power >= 9000:
            growth_points.append("Transcended Super Saiyan")
        elif power >= 5000:
            growth_points.append("Awakened Super Saiyan")
        elif power >= 3000:
            growth_points.append("Unlocked hidden potential")
        elif power >= 1000:
            growth_points.append("Surpassed limits")

        # Transformations
        if stats.get("transformations"):
            growth_points.append(f"Mastered {stats['transformations'][-1]}")

        # Techniques
        techniques = stats.get("techniques", [])
        if len(techniques) > 5:
            growth_points.append("Learned multiple powerful techniques")
        elif len(techniques) > 3:
            growth_points.append("Expanded technique arsenal")

        # Level
        level = stats.get("level", 1)
        if level > 10:
            growth_points.append(f"Reached level {level}")
        elif level > 5:
            growth_points.append("Significant power growth")

        return ", ".join(growth_points) if growth_points else "Still growing"


    def _store_important_events(self, state: GameState, summary: str) -> None:
        event = {
            "timestamp": datetime.now().isoformat(),
            "scene": state.scene_counter,
            "summary": summary[:200],
            "power_level": state.player_stats.get("power_level", 0),
            "location": getattr(state, "location", "Unknown"),
        }
        self.important_events.append(event)
        
        # FIXED: Use configured max
        if len(self.important_events) > self.max_important_events:
            self.important_events = self.important_events[-self.max_important_events:]

    # ---------------------------------------------------------------------
    # Context building
    # ---------------------------------------------------------------------

    def build_context_for_llm(self, state: GameState, include_history: bool = True) -> str:
        context_parts: List[str] = []

        if state.memory_summary:
            context_parts.append(f"=== MEMORY SUMMARY ===\n{state.memory_summary}\n")

        if include_history and state.messages:
            recent = state.get_recent_messages(5)
            if recent:
                context_parts.append("=== RECENT EVENTS ===")
                for msg in recent[-3:]:
                    msg_type = getattr(msg, "type", "")
                    if msg_type == "human":
                        role = "Player"
                    elif msg_type == "system":
                        role = "System"
                    else:
                        role = "Narrator"
                    content = msg.content or ""
                    if len(content) > 150:
                        content = content[:150] + "..."
                    context_parts.append(f"{role}: {content}")
                context_parts.append("")

        if state.current_plan and state.plan_step_index < len(state.current_plan):
            step = state.current_plan[state.plan_step_index]
            context_parts.append("=== CURRENT OBJECTIVE ===")
            context_parts.append(f"Scene: {step.scene_type.value}")
            context_parts.append(f"Goal: {step.expected_outcome}")
            context_parts.append("")

        context_parts.append("=== PLAYER STATUS ===")
        stats = state.player_stats
        context_parts.append(f"Power Level: {stats.get('power_level', 'Unknown')}")
        context_parts.append(f"Ki Mastery: {stats.get('ki_mastery', 0)}%")
        if stats.get("transformations"):
            context_parts.append(
                f"Transformations: {', '.join(stats['transformations'])}"
            )
        if stats.get("techniques"):
            context_parts.append(f"Techniques: {', '.join(stats['techniques'][:3])}")
        context_parts.append("")

        if getattr(state, "active_plot_threads", None) and state.active_plot_threads:
            context_parts.append("[ACTIVE PLOT THREADS]")
            for thread in state.active_plot_threads[:3]:
                context_parts.append(f"• {thread}")
            context_parts.append("")

        # Relationships
        if hasattr(state, "relationships") and state.relationships:
            context_parts.append("[RELATIONSHIPS]")
            for char, value in list(state.relationships.items())[:3]:
                if isinstance(value, (int, float)):
                    rel_desc = self._relationship_value_to_string(value)
                    context_parts.append(f"• {char}: {rel_desc}")
            context_parts.append("")

        return "\n".join(context_parts)
    
    def _relationship_value_to_string(self, value: float) -> str:
        """Convert relationship value to descriptive string"""
        if value > 0.8:
            return "Close Ally"
        if value > 0.5:
            return "Friend"
        if value > 0.2:
            return "Friendly"
        if value > -0.2:
            return "Neutral"
        if value > -0.5:
            return "Distant"
        if value > -0.8:
            return "Hostile"
        return "Enemy"

    # ---------------------------------------------------------------------
    # Relationship tracking
    # ---------------------------------------------------------------------

    def update_relationship(self, character: str, change: float, context: str = "") -> None:
        """Update relationship with a character"""
        if character not in self.relationship_memory:
            self.relationship_memory[character] = {
                "value": 0.0,
                "history": [],
                "last_interaction": None,
            }

        rel = self.relationship_memory[character]
        old_value = rel["value"]
        rel["value"] = max(-1.0, min(1.0, old_value + change))

        # Record significant changes
        if abs(change) > 0.3:
            rel["history"].append({
                "timestamp": datetime.now().isoformat(),
                "change": change,
                "new_value": rel["value"],
                "context": context[:100],
            })

        rel["last_interaction"] = datetime.now().isoformat()

    def get_relationship(self, character: str) -> float:
        return self.relationship_memory.get(character, {}).get("value", 0.0)
    
    def get_relationship_description(self, character: str) -> str:
        """Get relationship description for a character"""
        value = self.get_relationship(character)
        return self._relationship_value_to_string(value)

    # ---------------------------------------------------------------------
    # Plot thread tracking
    # ---------------------------------------------------------------------

    def add_plot_thread(self, thread_id: str, description: str, importance: str = "medium") -> None:
        self.plot_threads[thread_id] = {
            "description": description,
            "importance": importance,
            "status": "active",
            "created": datetime.now().isoformat(),
            "last_mentioned": datetime.now().isoformat(),
            "mentions": 1,
        }

    def update_plot_thread(self, thread_id: str, status: str = "active", note: str = "") -> None:
        """Update status of a plot thread"""
        if thread_id in self.plot_threads:
            self.plot_threads[thread_id]["status"] = status
            self.plot_threads[thread_id]["last_mentioned"] = datetime.now().isoformat()
            self.plot_threads[thread_id]["mentions"] += 1

            if note:
                if "notes" not in self.plot_threads[thread_id]:
                    self.plot_threads[thread_id]["notes"] = []
                self.plot_threads[thread_id]["notes"].append({
                    "timestamp": datetime.now().isoformat(),
                    "note": note,
                })

    def get_active_plot_threads(self) -> List[Dict[str, Any]]:
        return [
            {"id": tid, **data}
            for tid, data in self.plot_threads.items()
            if data["status"] == "active"
        ]

    def get_unresolved_plot_threads(self) -> List[Dict[str, Any]]:
        return [
            {"id": tid, **data}
            for tid, data in self.plot_threads.items()
            if data["status"] == "active" and data.get("mentions", 0) > 2
        ]

    # ---------------------------------------------------------------------
    # Memory pruning
    # ---------------------------------------------------------------------

    def prune_old_messages(
        self, messages: List[BaseMessage], keep_count: int = 20
    ) -> List[BaseMessage]:
        if len(messages) <= keep_count:
            return messages

        important_indices = {0}
        important_keywords = [
            "transformation",
            "defeat",
            "victory",
            "discover",
            "learn",
            "secret",
            "reveal",
            "promise",
            "vow",
            "sacrifice",
        ]

        # Find important messages
        for i, msg in enumerate(messages):
            if i == 0 or i >= len(messages) - 5:
                continue

            msg_type = getattr(msg, "type", "")
            if msg_type == "system" or isinstance(msg, SystemMessage):
                important_indices.add(i)
                continue

            if msg_type == "ai" or isinstance(msg, AIMessage):
                content = (msg.content or "").lower()
                for keyword in important_keywords:
                    if keyword in content:
                        important_indices.add(i)
                        break

        pruned: List[BaseMessage] = []
        for i, msg in enumerate(messages):
            if i in important_indices or i >= len(messages) - keep_count:
                pruned.append(msg)

        return pruned

    # ---------------------------------------------------------------------
    # Serialization
    # ---------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        return {
            "important_events": self.important_events,
            "relationship_memory": self.relationship_memory,
            "plot_threads": self.plot_threads,
            "enable_compression": self.enable_compression,
            "max_tokens": self.max_tokens,
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        self.important_events = data.get("important_events", [])
        self.relationship_memory = data.get("relationship_memory", {})
        self.plot_threads = data.get("plot_threads", {})
        self.enable_compression = data.get("enable_compression", True)
        self.max_tokens = data.get("max_tokens", 100000)

    # ---------------------------------------------------------------------
    # Formatting helpers
    # ---------------------------------------------------------------------

    def format_memory_for_display(self, state: GameState) -> str:
        """Format memory for UI display"""
        lines: List[str] = []
        lines.append("=" * 60)
        lines.append("📚 MEMORY SNAPSHOT")
        lines.append("=" * 60)

        # Token usage
        token_percent = (state.tokens_used / self.max_tokens) * 100 if self.max_tokens else 0
        lines.append(f"\n📊 Token Usage: {state.tokens_used:,} / {self.max_tokens:,} ({token_percent:.1f}%)")

        # Summary
        if state.memory_summary:
            lines.append(f"\n📝 Summary:\n{state.memory_summary[:200]}...")

        # Important events
        if self.important_events:
            lines.append(f"\n📌 Important Events ({len(self.important_events)}):")
            for event in self.important_events[-3:]:
                lines.append(f"  • Scene {event['scene']}: {event['summary'][:50]}...")

        # Relationships
        if self.relationship_memory:
            lines.append("\n🤝 Relationships:")
            for char, data in list(self.relationship_memory.items())[:3]:
                desc = self._relationship_value_to_string(data['value'])
                lines.append(f"  • {char}: {desc} ({data['value']:.1f})")

        # Active plot threads
        active = self.get_active_plot_threads()
        if active:
            lines.append(f"\n🎯 Active Plot Threads ({len(active)}):")
            for thread in active[:3]:
                lines.append(f"  • {thread['description'][:50]}...")

        return "\n".join(lines)



class MemoryPrompts:
    """Collection of prompts for memory compression"""

    @staticmethod
    def get_compression_prompt() -> str:
        return (
            "You are a memory compression specialist for an anime saga. "
            "Summarize key events and important information from the conversation history.\n\n"
            "Focus on:\n"
            "- Major plot developments\n"
            "- Character introductions and changes\n"
            "- Important revelations\n"
            "- Power progression milestones\n"
            "- Current objectives\n\n"
            "Return a concise summary (2-3 paragraphs)."
        )

    @staticmethod
    def get_relationship_analysis_prompt() -> str:
        return (
            "Analyze relationships between the player and other characters based on interactions.\n"
            "Consider tone, actions, shared experiences, conflicts, and alliances. "
            "Describe each relationship in 1-2 sentences, including recent changes."
        )


def create_memory_manager(config: Optional[Dict[str, Any]] = None) -> MemoryManager:
    """Factory function to create a memory manager with configuration"""
    if config is None:
        config = {}
    return MemoryManager(
        enable_compression=config.get("enable_compression", True),
        max_tokens=config.get("max_tokens", 100000),
        compression_threshold=config.get("compression_threshold", 50000),
        summary_interval=config.get("summary_interval", 10),
        message_overhead_tokens=config.get("message_overhead_tokens", 4),
        max_important_events=config.get("max_important_events", 50),
        max_recent_messages=config.get("max_recent_messages", 20)
    )
