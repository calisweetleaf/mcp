#!/usr/bin/env python3
"""
Enhanced Session Manager Tool - Auto-memory formation and cross-system intelligence
Integrates with enhanced memory system for automatic insight capture
"""

import json
import logging
import time
import uuid
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable
import threading
import hashlib
import re
from collections import Counter, defaultdict

# Import enhanced memory tool
try:
    from tools.memory_tool import EnhancedMemoryTool
    ENHANCED_MEMORY_AVAILABLE = True
except ImportError:
    ENHANCED_MEMORY_AVAILABLE = False
    EnhancedMemoryTool = None

class EnhancedSessionTool:
    """Enhanced cognitive session management with automatic memory formation"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sessions_dir = Path("data/sessions")
        self.sessions_dir.mkdir(exist_ok=True)
        
        # Initialize enhanced memory integration
        if ENHANCED_MEMORY_AVAILABLE and EnhancedMemoryTool:
            self.memory_tool = EnhancedMemoryTool()
        else:
            self.memory_tool = None
            self.logger.warning("Enhanced memory tool not available")
        
        # Session files
        self.index_file = self.sessions_dir / "session_index.json"
        self.patterns_file = self.sessions_dir / "learned_patterns.json"
        self.intelligence_file = self.sessions_dir / "session_intelligence.json"
        
        # Current session state
        self.current_session_id = None
        self.current_session = None
        self._lock = threading.Lock()
        
        # Auto-memory formation settings
        self.auto_memory_thresholds = {
            "insight_keywords": ["discovered", "learned", "realized", "found", "solution", "breakthrough"],
            "decision_keywords": ["decided", "chosen", "selected", "committed", "determined"],
            "problem_keywords": ["error", "bug", "issue", "problem", "failed", "broken"],
            "success_keywords": ["working", "fixed", "resolved", "completed", "successful"],
            "pattern_keywords": ["pattern", "always", "typically", "usually", "consistently"]
        }
        
        # Load learned patterns
        self.learned_patterns = self._load_learned_patterns()
        self.session_intelligence = self._load_session_intelligence()
        
        self.logger.info("Enhanced session manager initialized with auto-memory formation")
    
    def _load_learned_patterns(self) -> Dict[str, Any]:
        """Load previously learned patterns from sessions"""
        try:
            if self.patterns_file.exists():
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load learned patterns: {e}")
        
        return {
            "successful_workflows": [],
            "common_obstacles": [],
            "productivity_patterns": [],
            "decision_patterns": [],
            "learning_accelerators": []
        }
    
    def _save_learned_patterns(self):
        """Save learned patterns to disk"""
        try:
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(self.learned_patterns, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save learned patterns: {e}")
    
    def _load_session_intelligence(self) -> Dict[str, Any]:
        """Load session intelligence data"""
        try:
            if self.intelligence_file.exists():
                with open(self.intelligence_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load session intelligence: {e}")
        
        return {
            "session_success_predictors": {},
            "optimal_session_lengths": {},
            "focus_transition_patterns": {},
            "energy_level_correlations": {},
            "goal_achievement_factors": {}
        }
    
    def _save_session_intelligence(self):
        """Save session intelligence data"""
        try:
            with open(self.intelligence_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_intelligence, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save session intelligence: {e}")
    
    def _calculate_content_importance(self, content: str, context_type: str) -> float:
        """Calculate importance score for content based on various factors"""
        importance = 0.5  # Base importance
        content_lower = content.lower()
        
        # Context type multipliers
        context_multipliers = {
            "insight": 0.8,
            "decision": 0.7,
            "breakthrough": 0.9,
            "obstacle": 0.6,
            "solution": 0.8,
            "pattern": 0.7,
            "goal": 0.6
        }
        
        importance *= context_multipliers.get(context_type, 1.0)
        
        # Keyword-based importance boosts
        for keyword_type, keywords in self.auto_memory_thresholds.items():
            matches = sum(1 for keyword in keywords if keyword in content_lower)
            if matches > 0:
                importance += min(matches * 0.1, 0.3)
        
        # Length and complexity factors
        if len(content) > 100:
            importance += 0.1
        if len(content) > 500:
            importance += 0.1
        
        # Technical content indicators
        tech_indicators = ['code', 'function', 'class', 'method', 'api', 'database', 'server', 'client']
        tech_matches = sum(1 for indicator in tech_indicators if indicator in content_lower)
        if tech_matches > 0:
            importance += min(tech_matches * 0.05, 0.2)
        
        return min(importance, 1.0)
    
    def _is_memory_worthy(self, event_type: str, content: str) -> bool:
        """Determine if an event should be automatically stored in memory"""
        if not content or len(content.strip()) < 10:
            return False
        
        content_lower = content.lower()
        
        # Always capture high-value event types
        high_value_types = ["breakthrough", "major_decision", "critical_insight", "solution_found"]
        if event_type in high_value_types:
            return True
        
        # Check for important keywords
        for keyword_type, keywords in self.auto_memory_thresholds.items():
            if any(keyword in content_lower for keyword in keywords):
                return True
        
        # Check for patterns we've learned are important
        for pattern in self.learned_patterns.get("learning_accelerators", []):
            if pattern.get("trigger_phrase", "").lower() in content_lower:
                return True
        
        # Length-based importance (longer descriptions often more important)
        if len(content) > 200:
            return True
        
        return False
    
    def _auto_capture_memory(self, event_type: str, content: str, additional_context: Optional[Dict[str, Any]] = None):
        """Automatically create memory entries for significant events"""
        if not self.memory_tool or not self._is_memory_worthy(event_type, content):
            return
        
        try:
            # Generate intelligent memory key
            session_prefix = f"session_{self.current_session_id[:8]}" if self.current_session_id else "global"
            timestamp = int(time.time())
            content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
            memory_key = f"{session_prefix}_{event_type}_{timestamp}_{content_hash}"
            
            # Calculate importance
            importance = self._calculate_content_importance(content, event_type)
            
            # Determine category
            category_mapping = {
                "insight": "insights",
                "decision": "decisions", 
                "breakthrough": "insights",
                "obstacle": "solutions",
                "solution": "solutions",
                "pattern": "patterns",
                "goal": "goals"
            }
            category = category_mapping.get(event_type, "sessions")
            
            # Generate smart tags
            tags = [event_type, "auto_generated"]
            if self.current_session_id:
                tags.append(f"session_{self.current_session_id[:8]}")
            
            # Add contextual tags
            if additional_context:
                if additional_context.get("focus_areas"):
                    tags.extend(additional_context["focus_areas"][:3])
                if additional_context.get("energy_level"):
                    tags.append(f"energy_{additional_context['energy_level']}")
            
            # Enhanced content with context
            enhanced_content = content
            if additional_context:
                context_info = []
                if additional_context.get("session_goal"):
                    context_info.append(f"Session Goal: {additional_context['session_goal']}")
                if additional_context.get("current_focus"):
                    context_info.append(f"Focus: {', '.join(additional_context['current_focus'])}")
                if additional_context.get("timestamp"):
                    dt = datetime.fromtimestamp(additional_context['timestamp'])
                    context_info.append(f"Time: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
                
                if context_info:
                    enhanced_content += f"\n\nContext: {' | '.join(context_info)}"
            
            # Store in enhanced memory
            result = self.memory_tool.store(
                memory_key,
                enhanced_content,
                category=category,
                importance=importance,
                tags=tags
            )
            
            self.logger.info(f"Auto-captured memory: {memory_key} (importance: {importance:.2f})")
            
        except Exception as e:
            self.logger.error(f"Failed to auto-capture memory: {e}")
    
    def _analyze_session_patterns(self, session: Dict[str, Any]):
        """Analyze session for patterns and learning opportunities"""
        try:
            # Extract session metrics
            session_duration = session.get("last_updated", session.get("created", 0)) - session.get("created", 0)
            events = session.get("episodic", {}).get("events", [])
            insights = session.get("semantic", {}).get("key_insights", [])
            workflows = session.get("procedural", {}).get("workflows", [])
            
            # Identify successful patterns
            if len(insights) > 3 and session_duration > 1800:  # 30 minutes with multiple insights
                success_pattern = {
                    "pattern_type": "high_insight_session",
                    "duration": session_duration,
                    "insight_count": len(insights),
                    "goal": session.get("goal", ""),
                    "focus_areas": session.get("metadata", {}).get("attention_focus", []),
                    "energy_levels": self._extract_energy_progression(events),
                    "identified_at": time.time()
                }
                
                self.learned_patterns["successful_workflows"].append(success_pattern)
                
                # Store pattern in memory
                self._auto_capture_memory(
                    "pattern",
                    f"Identified successful session pattern: {success_pattern['pattern_type']} - "
                    f"Duration {session_duration/60:.1f}min with {len(insights)} insights",
                    {"pattern_data": success_pattern}
                )
            
            # Identify obstacle patterns
            obstacle_events = [e for e in events if e.get("type") in ["problem", "error", "obstacle"]]
            if len(obstacle_events) > 2:
                obstacle_pattern = {
                    "pattern_type": "recurring_obstacles",
                    "obstacles": [e.get("description", "") for e in obstacle_events],
                    "session_context": session.get("goal", ""),
                    "identified_at": time.time()
                }
                
                self.learned_patterns["common_obstacles"].append(obstacle_pattern)
        
        except Exception as e:
            self.logger.error(f"Error analyzing session patterns: {e}")
    
    def _extract_energy_progression(self, events: List[Dict[str, Any]]) -> List[str]:
        """Extract energy level progression from events"""
        energy_levels = []
        for event in events:
            if event.get("type") == "focus_shift" and event.get("details", {}).get("energy"):
                energy_levels.append(event["details"]["energy"])
        return energy_levels
    
    def bb7_start_session(self, goal: str, context: Optional[str] = None, 
                         tags: Optional[List[str]] = None) -> str:
        """Start a new enhanced cognitive session with intelligence"""
        with self._lock:
            session_id = str(uuid.uuid4())
            timestamp = time.time()
            
            # Analyze previous sessions for recommendations
            recommendations = self._generate_session_recommendations(goal)
            
            # Create enhanced session structure
            session = {
                "id": session_id,
                "created": timestamp,
                "last_updated": timestamp,
                "status": "active",
                "goal": goal,
                "context": context or "",
                "tags": tags or [],
                
                # Enhanced cognitive architecture
                "episodic": {
                    "events": [],
                    "timeline": [],
                    "achievements": [],
                    "obstacles": [],
                    "breakthroughs": []
                },
                
                "semantic": {
                    "concepts": {},
                    "relationships": [],
                    "key_insights": [],
                    "decision_rationale": {},
                    "knowledge_connections": []
                },
                
                "procedural": {
                    "workflows": [],
                    "commands_used": [],
                    "patterns_discovered": [],
                    "automation_opportunities": [],
                    "learned_shortcuts": []
                },
                
                # Enhanced metadata
                "metadata": {
                    "environment_state": self._capture_environment_state(),
                    "attention_focus": [],
                    "energy_level": "high",
                    "momentum": "starting",
                    "predicted_success_factors": recommendations.get("success_factors", []),
                    "recommended_focus_duration": recommendations.get("optimal_duration", 60),
                    "similar_past_sessions": recommendations.get("similar_sessions", [])
                },
                
                # Intelligence tracking
                "intelligence": {
                    "auto_captured_memories": 0,
                    "pattern_matches": recommendations.get("pattern_matches", []),
                    "learning_opportunities": [],
                    "cross_session_connections": []
                }
            }
            
            # Save session
            session_file = self.sessions_dir / f"{session_id}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session, f, indent=2, ensure_ascii=False)
            
            # Update index
            index = self._load_index()
            index["sessions"][session_id] = {
                "goal": goal,
                "created": timestamp,
                "status": "active",
                "tags": tags or [],
                "file": str(session_file),
                "predicted_success": recommendations.get("success_probability", 0.5)
            }
            self._save_index(index)
            
            # Set as current session
            self.current_session_id = session_id
            self.current_session = session
            
            # Auto-capture session start
            self._auto_capture_memory(
                "session_start",
                f"Started new session: {goal}" + (f" - {context}" if context else ""),
                {
                    "session_goal": goal,
                    "session_id": session_id,
                    "timestamp": timestamp,
                    "recommendations": recommendations
                }
            )
            
            # Format response with intelligence
            response = f"🚀 Enhanced Session Started: {goal}\n"
            response += f"Session ID: {session_id}\n"
            
            if recommendations.get("success_factors"):
                response += f"\n💡 Success Factors (based on past sessions):\n"
                for factor in recommendations["success_factors"][:3]:
                    response += f"  • {factor}\n"
            
            if recommendations.get("optimal_duration"):
                response += f"\n⏱️ Recommended Focus Duration: {recommendations['optimal_duration']} minutes\n"
            
            if recommendations.get("similar_sessions"):
                response += f"\n🔍 Found {len(recommendations['similar_sessions'])} similar past sessions for reference\n"
            
            response += f"\n✨ Auto-memory formation enabled - insights will be captured automatically!"
            
            self.logger.info(f"Started enhanced session: {session_id}")
            return response
    
    def _generate_session_recommendations(self, goal: str) -> Dict[str, Any]:
        """Generate intelligent recommendations based on past sessions"""
        recommendations = {
            "success_factors": [],
            "optimal_duration": 60,
            "similar_sessions": [],
            "pattern_matches": [],
            "success_probability": 0.5
        }
        
        try:
            # Analyze goal for keywords and context
            goal_words = set(goal.lower().split())
            
            # Find similar past sessions
            index = self._load_index()
            similar_sessions = []
            
            for session_id, session_info in index.get("sessions", {}).items():
                past_goal = session_info.get("goal", "").lower()
                past_words = set(past_goal.split())
                
                # Calculate similarity
                intersection = goal_words & past_words
                if intersection and len(intersection) / len(goal_words | past_words) > 0.3:
                    similar_sessions.append({
                        "session_id": session_id,
                        "goal": session_info.get("goal", ""),
                        "similarity": len(intersection) / len(goal_words | past_words)
                    })
            
            recommendations["similar_sessions"] = sorted(similar_sessions, 
                                                       key=lambda x: x["similarity"], reverse=True)[:5]
            
            # Extract success factors from learned patterns
            for pattern in self.learned_patterns.get("successful_workflows", []):
                if any(word in pattern.get("goal", "").lower() for word in goal_words):
                    recommendations["success_factors"].extend(pattern.get("focus_areas", []))
                    if pattern.get("duration"):
                        recommendations["optimal_duration"] = max(recommendations["optimal_duration"], 
                                                                pattern["duration"] // 60)
            
            # Remove duplicates and limit
            recommendations["success_factors"] = list(set(recommendations["success_factors"]))[:5]
            
            # Calculate success probability based on similar sessions and patterns
            if similar_sessions:
                recommendations["success_probability"] = min(0.9, 0.5 + len(similar_sessions) * 0.1)
            
        except Exception as e:
            self.logger.error(f"Error generating session recommendations: {e}")
        
        return recommendations
    
    def bb7_log_event(self, event_type: str, description: str, 
                     details: Optional[Dict[str, Any]] = None) -> str:
        """Enhanced event logging with auto-memory formation"""
        if not self.current_session_id:
            return "No active session. Start a session first with bb7_start_session."
        
        # Ensure current session is loaded
        if not self.current_session:
            self._load_current_session()
            if not self.current_session:
                return "Failed to load current session. Please start a new session."
        
        with self._lock:
            timestamp = time.time()
            event = {
                "timestamp": timestamp,
                "type": event_type,
                "description": description,
                "details": details or {},
                "auto_analyzed": False
            }
            
            # Enhanced event categorization
            if event_type in ["breakthrough", "major_insight", "critical_discovery"]:
                self.current_session["episodic"]["breakthroughs"].append(event)
                # Auto-capture breakthrough
                self._auto_capture_memory(
                    "breakthrough",
                    description,
                    {
                        "session_goal": self.current_session.get("goal"),
                        "current_focus": self.current_session.get("metadata", {}).get("attention_focus", []),
                        "timestamp": timestamp
                    }
                )
                event["auto_analyzed"] = True
                
            elif event_type in ["obstacle", "problem", "error", "blocker"]:
                self.current_session["episodic"]["obstacles"].append(event)
                
            elif event_type in ["achievement", "milestone", "completion"]:
                self.current_session["episodic"]["achievements"].append(event)
                # Auto-capture achievement
                self._auto_capture_memory(
                    "achievement",
                    description,
                    {
                        "session_goal": self.current_session.get("goal"),
                        "timestamp": timestamp
                    }
                )
                event["auto_analyzed"] = True
            
            # Add to main event log
            self.current_session["episodic"]["events"].append(event)
            self.current_session["episodic"]["timeline"].append({
                "time": timestamp,
                "event": event_type,
                "summary": description[:100]
            })
            
            # Intelligent event analysis
            if self._should_auto_capture(event_type, description):
                self._auto_capture_memory(
                    event_type,
                    description,
                    {
                        "session_goal": self.current_session.get("goal"),
                        "current_focus": self.current_session.get("metadata", {}).get("attention_focus", []),
                        "energy_level": self.current_session.get("metadata", {}).get("energy_level"),
                        "timestamp": timestamp
                    }
                )
                event["auto_analyzed"] = True
                self.current_session["intelligence"]["auto_captured_memories"] += 1
            
            self.current_session["last_updated"] = timestamp
            self._save_current_session()
            
            response = f"📝 Event logged: {description}"
            if event["auto_analyzed"]:
                response += f"\n🧠 Auto-captured in memory (total: {self.current_session['intelligence']['auto_captured_memories']})"
            
            self.logger.info(f"Enhanced event logged: {event_type} - {description}")
            return response
    
    def _should_auto_capture(self, event_type: str, description: str) -> bool:
        """Enhanced logic for determining auto-capture worthiness"""
        # Always capture certain event types
        auto_capture_types = ["breakthrough", "major_insight", "critical_discovery", 
                             "achievement", "milestone", "decision", "solution"]
        if event_type in auto_capture_types:
            return True
        
        # Use existing memory worthiness logic
        return self._is_memory_worthy(event_type, description)
    
    def bb7_capture_insight(self, insight: str, concept: str, 
                           relationships: Optional[List[str]] = None) -> str:
        """Enhanced insight capture with auto-memory and relationship tracking"""
        if not self.current_session_id:
            return "No active session. Start a session first with bb7_start_session."
        
        if not self.current_session:
            self._load_current_session()
            if not self.current_session:
                return "Failed to load current session. Please start a new session."
        
        with self._lock:
            timestamp = time.time()
            
            # Enhanced semantic memory storage
            insight_entry = {
                "timestamp": timestamp,
                "insight": insight,
                "concept": concept,
                "relationships": relationships or [],
                "confidence": self._calculate_insight_confidence(insight, concept),
                "session_context": {
                    "goal": self.current_session.get("goal"),
                    "focus_areas": self.current_session.get("metadata", {}).get("attention_focus", []),
                    "energy_level": self.current_session.get("metadata", {}).get("energy_level")
                }
            }
            
            self.current_session["semantic"]["key_insights"].append(insight_entry)
            
            # Update concept network
            if concept not in self.current_session["semantic"]["concepts"]:
                self.current_session["semantic"]["concepts"][concept] = {
                    "defined": timestamp,
                    "insights": [],
                    "related_to": relationships or [],
                    "importance_score": 0.5,
                    "evolution": []
                }
            
            concept_data = self.current_session["semantic"]["concepts"][concept]
            concept_data["insights"].append(insight)
            concept_data["importance_score"] = min(1.0, concept_data["importance_score"] + 0.1)
            concept_data["evolution"].append({
                "timestamp": timestamp,
                "type": "insight_added",
                "content": insight
            })
            
            # Add enhanced relationships
            if relationships:
                for related_concept in relationships:
                    relationship = {
                        "from": concept,
                        "to": related_concept,
                        "timestamp": timestamp,
                        "context": insight,
                        "strength": self._calculate_relationship_strength(concept, related_concept, insight)
                    }
                    self.current_session["semantic"]["relationships"].append(relationship)
                    
                    # Cross-connect concepts
                    self.current_session["semantic"]["knowledge_connections"].append({
                        "concepts": [concept, related_concept],
                        "connection_type": "insight_based",
                        "evidence": insight,
                        "timestamp": timestamp
                    })
            
            # Auto-capture high-value insights
            importance = self._calculate_content_importance(insight, "insight")
            if importance > 0.6:
                self._auto_capture_memory(
                    "insight",
                    f"💡 {concept}: {insight}",
                    {
                        "concept": concept,
                        "relationships": relationships,
                        "session_goal": self.current_session.get("goal"),
                        "confidence": insight_entry["confidence"],
                        "timestamp": timestamp
                    }
                )
                self.current_session["intelligence"]["auto_captured_memories"] += 1
            
            self.current_session["last_updated"] = timestamp
            self._save_current_session()
            
            response = f"💡 Insight captured: {insight}"
            if importance > 0.6:
                response += f"\n🧠 Auto-stored in memory (importance: {importance:.2f})"
            if relationships:
                response += f"\n🔗 Connected to: {', '.join(relationships)}"
            
            self.logger.info(f"Enhanced insight captured: {concept} - {insight}")
            return response
    
    def _calculate_insight_confidence(self, insight: str, concept: str) -> float:
        """Calculate confidence score for an insight"""
        confidence = 0.5
        
        # Length and detail factors
        if len(insight) > 50:
            confidence += 0.1
        if len(insight) > 150:
            confidence += 0.1
        
        # Specificity indicators
        specific_words = ["because", "due to", "results in", "causes", "leads to", "enables"]
        if any(word in insight.lower() for word in specific_words):
            confidence += 0.2
        
        # Evidence indicators
        evidence_words = ["tested", "verified", "confirmed", "observed", "measured"]
        if any(word in insight.lower() for word in evidence_words):
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _calculate_relationship_strength(self, concept1: str, concept2: str, context: str) -> float:
        """Calculate strength of relationship between concepts"""
        strength = 0.5
        
        # Co-occurrence in context
        if concept1.lower() in context.lower() and concept2.lower() in context.lower():
            strength += 0.3
        
        # Strong relationship indicators
        strong_indicators = ["causes", "enables", "requires", "depends on", "results in"]
        if any(indicator in context.lower() for indicator in strong_indicators):
            strength += 0.3
        
        return min(strength, 1.0)
    
    def bb7_get_session_insights(self, session_id: Optional[str] = None) -> str:
        """Get comprehensive insights about a session"""
        target_session_id = session_id or self.current_session_id
        
        if not target_session_id:
            return "No session specified and no active session"
        
        session_file = self.sessions_dir / f"{target_session_id}.json"
        if not session_file.exists():
            return f"Session {target_session_id} not found"
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session = json.load(f)
            
            insights = []
            insights.append(f"🧠 Session Intelligence Report: {target_session_id[:8]}")
            insights.append("=" * 60)
            
            # Basic metrics
            goal = session.get("goal", "No goal specified")
            created = datetime.fromtimestamp(session.get("created", 0))
            duration = session.get("last_updated", session.get("created", 0)) - session.get("created", 0)
            
            insights.append(f"🎯 Goal: {goal}")
            insights.append(f"📅 Started: {created.strftime('%Y-%m-%d %H:%M:%S')}")
            insights.append(f"⏱️ Duration: {duration/60:.1f} minutes")
            
            # Intelligence metrics
            intelligence = session.get("intelligence", {})
            auto_memories = intelligence.get("auto_captured_memories", 0)
            insights.append(f"🧠 Auto-captured memories: {auto_memories}")
            
            # Event analysis
            events = session.get("episodic", {}).get("events", [])
            breakthroughs = session.get("episodic", {}).get("breakthroughs", [])
            obstacles = session.get("episodic", {}).get("obstacles", [])
            achievements = session.get("episodic", {}).get("achievements", [])
            
            insights.append(f"\n📊 Event Summary:")
            insights.append(f"  • Total events: {len(events)}")
            insights.append(f"  • Breakthroughs: {len(breakthroughs)}")
            insights.append(f"  • Obstacles: {len(obstacles)}")
            insights.append(f"  • Achievements: {len(achievements)}")
            
            # Concept network
            concepts = session.get("semantic", {}).get("concepts", {})
            key_insights = session.get("semantic", {}).get("key_insights", [])
            
            if concepts:
                insights.append(f"\n🧭 Concept Network ({len(concepts)} concepts):")
                # Sort concepts by importance
                sorted_concepts = sorted(
                    concepts.items(),
                    key=lambda x: x[1].get("importance_score", 0.5),
                    reverse=True
                )
                for concept, data in sorted_concepts[:5]:
                    importance = data.get("importance_score", 0.5)
                    insight_count = len(data.get("insights", []))
                    insights.append(f"  • {concept}: {insight_count} insights (importance: {importance:.2f})")
            
            # Workflow patterns
            workflows = session.get("procedural", {}).get("workflows", [])
            if workflows:
                insights.append(f"\n⚙️ Learned Workflows ({len(workflows)}):")
                for workflow in workflows[:3]:
                    name = workflow.get("name", "Unnamed")
                    steps = len(workflow.get("steps", []))
                    frequency = workflow.get("frequency", 1)
                    insights.append(f"  • {name}: {steps} steps (used {frequency}x)")
            
            # Success indicators
            if duration > 1800 and len(key_insights) > 2:  # 30 min with insights
                insights.append(f"\n✨ Success Indicators:")
                insights.append(f"  • Sustained focus ({duration/60:.1f} minutes)")
                insights.append(f"  • High insight generation ({len(key_insights)} insights)")
                if auto_memories > 3:
                    insights.append(f"  • Rich auto-memory formation ({auto_memories} entries)")
            
            return "\n".join(insights)
            
        except Exception as e:
            self.logger.error(f"Error generating session insights: {e}")
            return f"Error generating session insights: {str(e)}"
    
    def bb7_cross_session_analysis(self, days_back: int = 30) -> str:
        """Analyze patterns across multiple sessions"""
        try:
            cutoff_time = time.time() - (days_back * 24 * 60 * 60)
            index = self._load_index()
            
            recent_sessions = []
            for session_id, session_info in index.get("sessions", {}).items():
                if session_info.get("created", 0) > cutoff_time:
                    session_file = self.sessions_dir / f"{session_id}.json"
                    if session_file.exists():
                        with open(session_file, 'r', encoding='utf-8') as f:
                            session_data = json.load(f)
                        recent_sessions.append(session_data)
            
            if not recent_sessions:
                return f"No sessions found in the last {days_back} days"
            
            analysis = []
            analysis.append(f"🔍 Cross-Session Analysis ({days_back} days)")
            analysis.append("=" * 50)
            analysis.append(f"📊 Analyzed {len(recent_sessions)} sessions\n")
            
            # Goal pattern analysis
            goals = [s.get("goal", "") for s in recent_sessions]
            goal_words = []
            for goal in goals:
                goal_words.extend(goal.lower().split())
            
            common_goal_words = Counter(goal_words).most_common(5)
            analysis.append("🎯 Common Goal Themes:")
            for word, count in common_goal_words:
                if len(word) > 3:  # Skip short words
                    analysis.append(f"  • {word}: {count} sessions")
            
            # Success pattern analysis
            successful_sessions = []
            for session in recent_sessions:
                duration = session.get("last_updated", 0) - session.get("created", 0)
                insights = len(session.get("semantic", {}).get("key_insights", []))
                auto_memories = session.get("intelligence", {}).get("auto_captured_memories", 0)
                
                # Define success criteria
                success_score = 0
                if duration > 1800:  # > 30 minutes
                    success_score += 1
                if insights > 2:  # Multiple insights
                    success_score += 2
                if auto_memories > 3:  # Rich auto-capture
                    success_score += 1
                
                if success_score >= 3:
                    successful_sessions.append({
                        "session": session,
                        "score": success_score,
                        "duration": duration,
                        "insights": insights
                    })
            
            analysis.append(f"\n✨ Success Analysis:")
            analysis.append(f"  • Successful sessions: {len(successful_sessions)}/{len(recent_sessions)}")
            
            if successful_sessions:
                avg_duration = sum(s["duration"] for s in successful_sessions) / len(successful_sessions)
                avg_insights = sum(s["insights"] for s in successful_sessions) / len(successful_sessions)
                
                analysis.append(f"  • Average successful duration: {avg_duration/60:.1f} minutes")
                analysis.append(f"  • Average insights per success: {avg_insights:.1f}")
                
                # Extract success factors
                success_factors = []
                for s in successful_sessions:
                    focus_areas = s["session"].get("metadata", {}).get("attention_focus", [])
                    success_factors.extend(focus_areas)
                
                if success_factors:
                    common_factors = Counter(success_factors).most_common(3)
                    analysis.append(f"  • Top success factors:")
                    for factor, count in common_factors:
                        analysis.append(f"    - {factor} ({count} sessions)")
            
            # Concept evolution analysis
            all_concepts = {}
            for session in recent_sessions:
                concepts = session.get("semantic", {}).get("concepts", {})
                for concept, data in concepts.items():
                    if concept not in all_concepts:
                        all_concepts[concept] = []
                    all_concepts[concept].append({
                        "session_id": session.get("id"),
                        "importance": data.get("importance_score", 0.5),
                        "insights": len(data.get("insights", []))
                    })
            
            # Find evolving concepts (appearing in multiple sessions)
            evolving_concepts = {k: v for k, v in all_concepts.items() if len(v) > 1}
            
            if evolving_concepts:
                analysis.append(f"\n🧭 Evolving Concepts ({len(evolving_concepts)}):")
                for concept, occurrences in list(evolving_concepts.items())[:5]:
                    total_importance = sum(o["importance"] for o in occurrences)
                    analysis.append(f"  • {concept}: {len(occurrences)} sessions (importance: {total_importance:.2f})")
            
            return "\n".join(analysis)
            
        except Exception as e:
            self.logger.error(f"Error in cross-session analysis: {e}")
            return f"Error in cross-session analysis: {str(e)}"
    
    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        """Return all available enhanced session tools with their metadata."""
        return {
            'bb7_start_session': {
                "callable": self.bb7_start_session,
                "metadata": {
                    "name": "bb7_start_session",
                    "description": "🎯 Begin a new cognitive development session with goal tracking, episodic memory, and workflow recording. Use when starting significant work, tackling new problems, or beginning focused development sessions. Creates structured memory for complex tasks.",
                    "category": "sessions",
                    "priority": "high",
                    "when_to_use": ["new_project", "complex_task", "development_session", "focused_work"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "goal": { "type": "string", "description": "Clear objective for this session" },
                            "context": { "type": "string", "description": "Background context or current situation" },
                            "tags": { "type": "array", "items": {"type": "string"}, "description": "Categorization tags for the session" }
                        },
                        "required": ["goal"]
                    }
                }
            },
            'bb7_log_event': {
                "callable": self.bb7_log_event,
                "metadata": {
                    "name": "bb7_log_event",
                    "description": "📝 Record significant events, decisions, discoveries, or problems in the current session timeline. Use to build episodic memory of development process, track decision rationale, and create searchable development history.",
                    "category": "sessions",
                    "priority": "medium",
                    "when_to_use": ["important_events", "decisions", "discoveries", "problems", "milestones"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "event_type": { "type": "string", "description": "Type: 'decision', 'discovery', 'problem', 'solution', 'insight'" },
                            "description": { "type": "string", "description": "What happened and why it's significant" },
                            "details": { "type": "object", "description": "Additional structured information" }
                        },
                        "required": ["event_type", "description"]
                    }
                }
            },
            'bb7_capture_insight': {
                "callable": self.bb7_capture_insight,
                "metadata": {
                    "name": "bb7_capture_insight",
                    "description": "💡 Record semantic insights, architectural understanding, or conceptual breakthroughs. Use when you or the user gain important understanding about the codebase, design patterns, or problem domain. Builds conceptual knowledge base.",
                    "category": "sessions",
                    "priority": "medium",
                    "when_to_use": ["insights", "understanding", "breakthroughs", "learning", "patterns"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "insight": { "type": "string", "description": "The key insight or understanding" },
                            "concept": { "type": "string", "description": "Main concept this relates to" },
                            "relationships": { "type": "array", "items": {"type": "string"}, "description": "Related concepts or dependencies" }
                        },
                        "required": ["insight", "concept"]
                    }
                }
            },
            'bb7_record_workflow': {
                "callable": self.bb7_record_workflow,
                "metadata": {
                    "name": "bb7_record_workflow",
                    "description": "⚙️ Document successful workflows, processes, or step-by-step procedures for future reuse. Use when you discover effective approaches, solve complex problems, or establish repeatable processes. Builds procedural knowledge.",
                    "category": "sessions",
                    "priority": "medium",
                    "when_to_use": ["successful_workflows", "processes", "procedures", "solutions", "patterns"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "workflow_name": { "type": "string", "description": "Descriptive name for the workflow" },
                            "steps": { "type": "array", "items": {"type": "string"}, "description": "Ordered list of steps" },
                            "context": { "type": "string", "description": "When and how to use this workflow" }
                        },
                        "required": ["workflow_name", "steps"]
                    }
                }
            },
            'bb7_update_focus': {
                "callable": self.bb7_update_focus,
                "metadata": {
                    "name": "bb7_update_focus",
                    "description": "🎯 Update current attention focus and energy state. Use when switching contexts, changing priorities, or when user's focus shifts. Helps maintain awareness of current cognitive state and priorities.",
                    "category": "sessions",
                    "priority": "low",
                    "when_to_use": ["context_switch", "priority_change", "focus_shift", "energy_tracking"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "focus_areas": { "type": "array", "items": {"type": "string"}, "description": "Current areas of focus and attention" },
                            "energy_level": { "type": "string", "enum": ["low", "medium", "high"], "default": "medium" },
                            "momentum": { "type": "string", "enum": ["starting", "building", "flowing", "slowing"], "default": "steady" }
                        },
                        "required": ["focus_areas"]
                    }
                }
            },
            'bb7_pause_session': {
                "callable": self.bb7_pause_session,
                "metadata": {
                    "name": "bb7_pause_session",
                    "description": "⏸️ Pause current session with state preservation. Use when taking breaks, switching tasks, or ending work sessions. Captures environment state for seamless resumption.",
                    "category": "sessions",
                    "priority": "medium",
                    "when_to_use": ["break_time", "task_switch", "session_end", "interruption"],
                    "input_schema": {
                        "type": "object",
                        "properties": { "reason": { "type": "string", "description": "Why the session is being paused" } },
                        "required": []
                    }
                }
            },
            'bb7_resume_session': {
                "callable": self.bb7_resume_session,
                "metadata": {
                    "name": "bb7_resume_session",
                    "description": "▶️ Resume a previously paused session with full context restoration. Use when continuing interrupted work or returning to previous tasks. Provides seamless continuity.",
                    "category": "sessions",
                    "priority": "medium",
                    "when_to_use": ["resume_work", "continue_task", "context_restoration", "session_continuation"],
                    "input_schema": {
                        "type": "object",
                        "properties": { "session_id": { "type": "string", "description": "Session ID to resume" } },
                        "required": ["session_id"]
                    }
                }
            },
            'bb7_list_sessions': {
                "callable": self.bb7_list_sessions,
                "metadata": {
                    "name": "bb7_list_sessions",
                    "description": "📋 View all development sessions with status and context. Use to understand work history, find interrupted tasks, or choose which session to resume.",
                    "category": "sessions",
                    "priority": "low",
                    "when_to_use": ["session_review", "work_history", "interrupted_tasks", "session_selection"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "status": { "type": "string", "enum": ["active", "paused", "completed"] },
                            "limit": { "type": "integer", "default": 20 }
                        },
                        "required": []
                    }
                }
            },
            'bb7_get_session_summary': {
                "callable": self.bb7_get_session_summary,
                "metadata": {
                    "name": "bb7_get_session_summary",
                    "description": "📊 Get detailed summary of specific session including events, insights, and outcomes. Use to understand context of previous work or communicate progress.",
                    "category": "sessions",
                    "priority": "low",
                    "when_to_use": ["session_analysis", "progress_review", "context_understanding", "reporting"],
                    "input_schema": {
                        "type": "object",
                        "properties": { "session_id": { "type": "string", "description": "Session to summarize" } },
                        "required": ["session_id"]
                    }
                }
            },
            "bb7_get_session_insights": {
                "callable": self.bb7_get_session_insights,
                 "metadata": {
                    "name": "bb7_get_session_insights",
                    "description": "Get comprehensive insights about a session",
                    "category": "sessions",
                    "priority": "low",
                    "when_to_use": ["session_analysis", "progress_review", "context_understanding", "reporting"],
                    "input_schema": {
                        "type": "object",
                        "properties": { "session_id": { "type": "string", "description": "Session to get insights from" } },
                        "required": ["session_id"]
                    }
                }
            },
            "bb7_cross_session_analysis": {
                "callable": lambda days_back=30: self.bb7_cross_session_analysis(days_back),
                "metadata": {
                    "name": "bb7_cross_session_analysis",
                    "description": "Analyze patterns, goals, and outcomes across multiple sessions. Use for longitudinal insights and workflow optimization.",
                    "category": "sessions",
                    "priority": "medium",
                    "when_to_use": ["longitudinal_analysis", "workflow_optimization", "session_patterns"],
                    "input_schema": {"type": "object", "properties": {"days_back": {"type": "integer", "default": 30}}, "required": []}
                }
            },
            "bb7_session_recommendations": {
                "callable": lambda goal: json.dumps(self._generate_session_recommendations(goal), indent=2),
                "metadata": {
                    "name": "bb7_session_recommendations",
                    "description": "Provide recommendations for next actions or improvements based on session history and patterns.",
                    "category": "sessions",
                    "priority": "medium",
                    "when_to_use": ["action_recommendations", "workflow_improvement", "session_guidance"],
                    "input_schema": {"type": "object", "properties": {}, "required": []}
                }
            },
            "bb7_learned_patterns": {
                "callable": lambda: json.dumps(self.learned_patterns, indent=2),
                "metadata": {
                    "name": "bb7_learned_patterns",
                    "description": "Summarize recurring patterns, solutions, and best practices learned from past sessions and memories.",
                    "category": "sessions",
                    "priority": "medium",
                    "when_to_use": ["pattern_recognition", "best_practices", "solution_summarization"],
                    "input_schema": {"type": "object", "properties": {}, "required": []}
                }
            },
            "bb7_session_intelligence": {
                "callable": lambda: json.dumps(self.session_intelligence, indent=2),
                "metadata": {
                    "name": "bb7_session_intelligence",
                    "description": "Generate a session intelligence report, highlighting key insights, breakthroughs, and cognitive metrics.",
                    "category": "sessions",
                    "priority": "medium",
                    "when_to_use": ["session_reporting", "cognitive_metrics", "insight_generation"],
                    "input_schema": {"type": "object", "properties": {}, "required": []}
                }
            },
            "bb7_link_memory_to_session": {
                "callable": self.bb7_link_memory_to_session,
                "metadata": {
                    "name": "bb7_link_memory_to_session",
                    "description": "Link a memory key to the current session",
                    "category": "sessions",
                    "priority": "low",
                    "when_to_use": ["memory_linking"],
                    "input_schema": {
                        "type": "object",
                        "properties": { "memory_key": { "type": "string", "description": "Memory key to link" } },
                        "required": ["memory_key"]
                    }
                }
            },
            "bb7_auto_memory_stats": {
                "callable": lambda: f"Auto-captured memories this session: {self.current_session.get('intelligence', {}).get('auto_captured_memories', 0) if self.current_session else 0}",
                "metadata": {
                    "name": "bb7_auto_memory_stats",
                    "description": "Automatically compute and report memory usage statistics, trends, and optimization suggestions.",
                    "category": "memory",
                    "priority": "low",
                    "when_to_use": ["memory_management", "resource_optimization", "usage_analysis"],
                    "input_schema": {"type": "object", "properties": {}, "required": []}
                }
            }
        }

    def _load_index(self) -> Dict[str, Any]:
        """Load the session index"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load session index: {e}")
        return {"sessions": {}, "active_threads": {}, "patterns": {}}

    def _save_index(self, index: Dict[str, Any]) -> None:
        """Save the session index"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save session index: {e}")

    def _capture_environment_state(self) -> Dict[str, Any]:
        """Capture current development environment state"""
        import os, subprocess
        state = {
            "timestamp": time.time(),
            "working_directory": os.getcwd(),
        }
        # Git state with proper error handling to prevent hanging
        try:
            git_branch = subprocess.run(['git', 'branch', '--show-current'], 
                                      capture_output=True, text=True, timeout=2, 
                                      shell=False, check=False)
            if git_branch.returncode == 0 and git_branch.stdout.strip():
                state["git"] = {"branch": git_branch.stdout.strip()}
            else:
                state["git"] = {"status": "not_in_git_repo"}
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            state["git"] = {"status": "git_unavailable", "reason": str(e)}
        except Exception as e:
            state["git"] = {"status": "error", "reason": str(e)}
        return state

    def _load_current_session(self) -> None:
        """Load the current session from disk"""
        if not self.current_session_id:
            return
        
        session_file = self.sessions_dir / f"{self.current_session_id}.json"
        if session_file.exists():
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    self.current_session = json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load current session: {e}")
                self.current_session = None

    def _save_current_session(self) -> None:
        """Save the current session to disk"""
        if not self.current_session_id or not self.current_session:
            return
        
        session_file = self.sessions_dir / f"{self.current_session_id}.json"
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_session, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save current session: {e}")
    
    def _load_memory_index(self) -> Dict[str, Any]:
        """Load the memory-session mapping"""
        memory_index_file = self.sessions_dir / "memory_index.json"
        if memory_index_file.exists():
            try:
                with open(memory_index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load memory index: {e}")
        return {"memory_to_sessions": {}, "session_memories": {}}

    def _save_memory_index(self, memory_index: Dict[str, Any]) -> None:
        """Save the memory-session mapping"""
        memory_index_file = self.sessions_dir / "memory_index.json"
        try:
            with open(memory_index_file, 'w', encoding='utf-8') as f:
                json.dump(memory_index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save memory index: {e}")

    def bb7_record_workflow(self, workflow_name: str, steps: List[str], 
                           context: Optional[str] = None) -> str:
        """Record a procedural workflow or pattern"""
        if not self.current_session_id:
            return "No active session. Start a session first with bb7_start_session."
        
        if not self.current_session:
            self._load_current_session()
            if not self.current_session:
                return "Failed to load current session. Please start a new session."
        
        with self._lock:
            timestamp = time.time()
            workflow = {
                "timestamp": timestamp,
                "name": workflow_name,
                "steps": steps,
                "context": context or "",
                "frequency": 1
            }
            
            # Check if similar workflow exists
            existing = None
            for i, existing_workflow in enumerate(self.current_session["procedural"]["workflows"]):
                if existing_workflow["name"] == workflow_name:
                    existing = i
                    break
            
            if existing is not None:
                # Update existing workflow
                self.current_session["procedural"]["workflows"][existing]["frequency"] += 1
                self.current_session["procedural"]["workflows"][existing]["last_used"] = timestamp
                self.current_session["procedural"]["workflows"][existing]["steps"] = steps
            else:
                # Add new workflow
                self.current_session["procedural"]["workflows"].append(workflow)
            
            self.current_session["last_updated"] = timestamp
            self._save_current_session()
            
            self.logger.info(f"Recorded workflow: {workflow_name}")
            return f"⚙️ Workflow recorded: {workflow_name} ({len(steps)} steps)"

    def bb7_update_focus(self, focus_areas: List[str], energy_level: str = "medium", momentum: str = "steady") -> str:
        """Update current attention focus and energy state"""
        if not self.current_session_id:
            return "No active session. Start a session first with bb7_start_session."
        if not self.current_session:
            self._load_current_session()
            if not self.current_session:
                return "Failed to load current session. Please start a new session."
        
        with self._lock:
            timestamp = time.time()
            self.current_session["metadata"]["attention_focus"] = focus_areas
            self.current_session["metadata"]["energy_level"] = energy_level
            self.current_session["metadata"]["momentum"] = momentum
            self.current_session["metadata"]["focus_updated"] = timestamp
            self.current_session["last_updated"] = timestamp
            
            # Log as event
            self.current_session["episodic"]["events"].append({
                "timestamp": timestamp,
                "type": "focus_shift",
                "description": f"Focus shifted to: {', '.join(focus_areas)}",
                "details": {
                    "energy": energy_level,
                    "momentum": momentum
                }
            })
            
            self._save_current_session()
            return f"🎯 Focus updated: {', '.join(focus_areas)} (Energy: {energy_level}, Momentum: {momentum})"

    def bb7_pause_session(self, reason: Optional[str] = None) -> str:
        """Pause the current session"""
        if not self.current_session_id:
            return "No active session to pause."
        if not self.current_session:
            self._load_current_session()
            if not self.current_session:
                return "Failed to load current session. Please start a new session."
        
        with self._lock:
            timestamp = time.time()
            self.current_session["status"] = "paused"
            self.current_session["paused_at"] = timestamp
            self.current_session["pause_reason"] = reason or "Manual pause"
            self.current_session["last_updated"] = timestamp
            
            # Capture final environment state
            self.current_session["metadata"]["pause_environment"] = self._capture_environment_state()
            
            # Log pause event
            self.current_session["episodic"]["events"].append({
                "timestamp": timestamp,
                "type": "session_paused",
                "description": f"Session paused: {reason or 'Manual pause'}",
                "details": {"environment_captured": True}
            })
            
            self._save_current_session()
            
            # Update index
            index = self._load_index()
            if self.current_session_id in index["sessions"]:
                index["sessions"][self.current_session_id]["status"] = "paused"
            self._save_index(index)
            
            paused_session_id = self.current_session_id
            self.current_session_id = None
            self.current_session = None
            
            self.logger.info(f"Paused session: {paused_session_id}")
            return f"⏸️ Session paused: {reason or 'Manual pause'}"

    def bb7_resume_session(self, session_id: str) -> str:
        """Resume a paused session"""
        with self._lock:
            session_file = self.sessions_dir / f"{session_id}.json"
            if not session_file.exists():
                return f"Session {session_id} not found."
            
            # Load session
            with open(session_file, 'r', encoding='utf-8') as f:
                session = json.load(f)
            
            if session["status"] != "paused":
                return f"Session {session_id} is not paused (status: {session['status']})."
            
            # Resume session
            timestamp = time.time()
            session["status"] = "active"
            session["resumed_at"] = timestamp
            session["last_updated"] = timestamp
            
            # Set as current session
            self.current_session_id = session_id
            self.current_session = session
            
            self._save_current_session()
            
            # Update index
            index = self._load_index()
            if session_id in index["sessions"]:
                index["sessions"][session_id]["status"] = "active"
            self._save_index(index)
            
            self.logger.info(f"Resumed session: {session_id}")
            return f"▶️ Session resumed: {session['goal']}"

    def bb7_list_sessions(self, status: Optional[str] = None, limit: int = 20) -> str:
        """List all sessions with optional status filter"""
        index = self._load_index()
        sessions = index.get("sessions", {})
        
        if not sessions:
            return "No sessions found."
        
        # Filter by status if specified
        if status:
            filtered_sessions = {k: v for k, v in sessions.items() 
                               if v.get("status") == status}
        else:
            filtered_sessions = sessions
        
        if not filtered_sessions:
            return f"No sessions found with status '{status}'."
        
        # Sort by creation time (newest first)
        sorted_sessions = sorted(filtered_sessions.items(), 
                               key=lambda x: x[1].get("created", 0), reverse=True)
        
        result = []
        result.append(f"📊 Sessions ({len(sorted_sessions)} total):\n")
        
        for session_id, session_info in sorted_sessions[:limit]:
            created = datetime.fromtimestamp(session_info.get("created", 0))
            status_emoji = {"active": "🟢", "paused": "⏸️", "completed": "✅"}.get(
                session_info.get("status", "unknown"), "❓"
            )
            
            result.append(f"{status_emoji} {session_id[:8]}... - {session_info.get('goal', 'No goal')}")
            result.append(f"    Created: {created.strftime('%Y-%m-%d %H:%M')}")
            
            tags = session_info.get("tags", [])
            if tags:
                result.append(f"    Tags: {', '.join(tags)}")
        
        if len(sorted_sessions) > limit:
            result.append(f"\n... and {len(sorted_sessions) - limit} more sessions")
        
        return "\n".join(result)

    def bb7_get_session_summary(self, session_id: str) -> str:
        """Get a detailed summary of a specific session"""
        session_file = self.sessions_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return f"Session {session_id} not found."
        
        with open(session_file, 'r', encoding='utf-8') as f:
            session = json.load(f)
        
        # Build comprehensive summary
        summary = []
        
        # Header
        created = datetime.fromtimestamp(session.get("created", 0))
        updated = datetime.fromtimestamp(session.get("last_updated", 0))
        
        summary.append(f"📋 Session Summary: {session_id}")
        summary.append(f"🎯 Goal: {session.get('goal', 'Not specified')}")
        summary.append(f"📅 Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append(f"🔄 Last Updated: {updated.strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append(f"📊 Status: {session.get('status', 'Unknown')}")
        
        tags = session.get("tags", [])
        if tags:
            summary.append(f"🏷️ Tags: {', '.join(tags)}")
        
        # Episodic Memory
        episodic = session.get("episodic", {})
        events = episodic.get("events", [])
        if events:
            summary.append(f"\n📝 Events ({len(events)} total):")
            for event in events[-10:]:  # Last 10 events
                event_time = datetime.fromtimestamp(event["timestamp"]).strftime("%H:%M")
                summary.append(f"  • {event_time}: {event['description']}")
        
        # Semantic Memory
        semantic = session.get("semantic", {})
        concepts = semantic.get("concepts", {})
        insights = semantic.get("key_insights", [])
        
        if concepts:
            summary.append(f"\n🧠 Concepts ({len(concepts)}):")
            for concept, data in list(concepts.items())[:5]:
                summary.append(f"  • {concept}: {len(data.get('insights', []))} insights")
        
        if insights:
            summary.append(f"\n💡 Key Insights ({len(insights)}):")
            for insight in insights[-5:]:
                summary.append(f"  • {insight['insight']}")
        
        # Procedural Memory
        procedural = session.get("procedural", {})
        workflows = procedural.get("workflows", [])
        
        if workflows:
            summary.append(f"\n⚙️ Workflows ({len(workflows)}):")
            for workflow in workflows:
                freq = workflow.get("frequency", 1)
                summary.append(f"  • {workflow['name']}: {len(workflow['steps'])} steps (used {freq}x)")
        
        # Current Focus
        metadata = session.get("metadata", {})
        focus = metadata.get("attention_focus", [])
        if focus:
            energy = metadata.get("energy_level", "unknown")
            momentum = metadata.get("momentum", "unknown")
            summary.append(f"\n🎯 Current Focus: {', '.join(focus)}")
            summary.append(f"⚡ Energy: {energy}, Momentum: {momentum}")
        
        return "\n".join(summary)
    
    def bb7_link_memory_to_session(self, memory_key: str) -> str:
        """Link a memory key to the current session"""
        if not self.current_session_id:
            return "No active session to link memory to."
        
        # Update memory index
        memory_index = self._load_memory_index()
        
        if memory_key not in memory_index["memory_to_sessions"]:
            memory_index["memory_to_sessions"][memory_key] = []
        
        if self.current_session_id not in memory_index["memory_to_sessions"][memory_key]:
            memory_index["memory_to_sessions"][memory_key].append(self.current_session_id)
        
        if self.current_session_id not in memory_index["session_memories"]:
            memory_index["session_memories"][self.current_session_id] = []
        
        if memory_key not in memory_index["session_memories"][self.current_session_id]:
            memory_index["session_memories"][self.current_session_id].append(memory_key)
        
        self._save_memory_index(memory_index)
        
        return f"🔗 Linked memory key '{memory_key}' to current session {self.current_session_id[:8]}"