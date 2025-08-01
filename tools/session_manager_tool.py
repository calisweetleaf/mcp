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
import configparser
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
            hit_count = sum(1 for k in keywords if k in content_lower)
            if hit_count:
                importance += min(0.1 * hit_count, 0.3)
        
        # Length and complexity factors
        if len(content) > 100:
            importance += 0.1
        if len(content) > 500:
            importance += 0.2
        
        # Technical content indicators
        tech_indicators = ['code', 'function', 'class', 'method', 'api', 'database', 'server', 'client']
        tech_matches = sum(1 for indicator in tech_indicators if indicator in content_lower)
        if tech_matches > 0:
            importance += min(0.05 * tech_matches, 0.2)
        
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
            if any(k in content_lower for k in keywords):
                return True
        
        # Check for patterns we've learned are important
        for pattern in self.learned_patterns.get("learning_accelerators", []):
            if isinstance(pattern, str) and pattern.lower() in content_lower:
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
            
            # Update intelligence counters
            if self.current_session:
                intel = self.current_session.setdefault("intelligence", {})
                intel["auto_captured_memories"] = intel.get("auto_captured_memories", 0) + 1
            
            self.logger.info(f"Auto-captured memory: {memory_key} (importance: {importance:.2f})")
            
        except Exception as e:
            self.logger.error(f"Failed to auto-capture memory: {e}")
    
    def _analyze_session_patterns(self, session: Dict[str, Any]):
        """Analyze session for patterns and learning opportunities"""
        try:
            events = session.get("episodic", {}).get("events", [])
            if not events:
                return
            
            # Identify frequent problems
            problem_events = [e for e in events if e.get("type") in ["problem", "error", "obstacle", "blocker"]]
            if problem_events:
                common_terms = Counter()
                for e in problem_events:
                    for w in re.findall(r"[a-zA-Z_]{3,}", e.get("description", "").lower()):
                        if w not in {"the","and","for","with","from","this","that","have","has","had","into","onto","when","then","else"}:
                            common_terms[w] += 1
                common_top = [w for w,_ in common_terms.most_common(5)]
                if common_top:
                    self.learned_patterns.setdefault("common_obstacles", []).append({
                        "terms": common_top,
                        "session": session.get("id"),
                        "timestamp": time.time()
                    })
                    self._save_learned_patterns()
        
        except Exception as e:
            self.logger.error(f"Error analyzing session patterns: {e}")
    
    def _extract_energy_progression(self, events: List[Dict[str, Any]]) -> List[str]:
        """Extract energy level progression from events"""
        energy_levels = []
        for event in events:
            details = event.get("details", {})
            energy = details.get("energy_level") or details.get("energy")
            if isinstance(energy, str):
                energy_levels.append(energy)
        return energy_levels
    
    def bb7_start_session(self, goal: str, context: Optional[str] = None, 
                         tags: Optional[List[str]] = None) -> str:
        """Start a new enhanced cognitive session with intelligence"""
        with self._lock:
            session_id = str(uuid.uuid4())
            now = time.time()
            self.current_session_id = session_id
            self.current_session = {
                "id": session_id,
                "goal": goal,
                "context": context or "",
                "tags": tags or [],
                "created": now,
                "last_updated": now,
                "status": "active",
                "episodic": {
                    "events": [],
                    "timeline": [],
                    "breakthroughs": [],
                    "obstacles": [],
                    "achievements": []
                },
                "semantic": {
                    "concepts": {},
                    "key_insights": [],
                    "relationships": [],
                    "knowledge_connections": []
                },
                "procedural": {
                    "workflows": []
                },
                "metadata": {
                    "attention_focus": [],
                    "energy_level": "medium",
                    "momentum": "starting"
                },
                "intelligence": {
                    "auto_captured_memories": 0
                }
            }
            # Persist
            self._save_current_session()
            index = self._load_index()
            index[session_id] = {
                "goal": goal,
                "created": now,
                "status": "active",
                "tags": tags or []
            }
            self._save_index(index)
            
            # Recommend initial actions
            recs = self._generate_session_recommendations(goal)
            return f"🎯 Started session {session_id[:8]}: {goal}\nSuggested duration: {recs.get('optimal_duration',60)} min"
    
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
            index = self._load_index()
            # naive optimal duration based on recent successful sessions lengths
            durations = []
            for sid in list(index.keys())[-10:]:
                f = self.sessions_dir / f"{sid}.json"
                if f.exists():
                    with open(f, 'r', encoding='utf-8') as fh:
                        s = json.load(fh)
                        dur = max(0, s.get("last_updated", s.get("created", 0)) - s.get("created", 0))
                        if dur:
                            durations.append(dur)
            if durations:
                avg = sum(durations)/len(durations)
                recommendations["optimal_duration"] = max(30, int(avg/60))
        except Exception as e:
            self.logger.warning(f"Failed to compute recommendations: {e}")
        
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
            # Categorization
            if event_type in ["breakthrough", "major_insight", "critical_discovery"]:
                self.current_session["episodic"]["breakthroughs"].append(event)
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
                self._auto_capture_memory(
                    "achievement",
                    description,
                    {
                        "session_goal": self.current_session.get("goal"),
                        "energy_level": self.current_session.get("metadata", {}).get("energy_level"),
                        "timestamp": timestamp
                    }
                )
                event["auto_analyzed"] = True
            
            # Add to main logs
            self.current_session["episodic"]["events"].append(event)
            self.current_session["episodic"]["timeline"].append({
                "time": timestamp,
                "event": event_type,
                "summary": description[:100]
            })
            
            # Intelligent capture
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
            
            self.current_session["last_updated"] = timestamp
            self._save_current_session()
            
            response = f"📝 Event logged: {description}"
            if event["auto_analyzed"]:
                total = self.current_session.get('intelligence', {}).get('auto_captured_memories', 0)
                response += f"\n🧠 Auto-captured in memory (total: {total})"
            
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
                }
            }
            
            # Update semantic structures
            sem = self.current_session.setdefault("semantic", {})
            concepts = sem.setdefault("concepts", {})
            concept_data = concepts.setdefault(concept, {"insights": [], "importance_score": 0.5})
            concept_data["insights"].append(insight_entry)
            concept_data["importance_score"] = min(1.0, concept_data["importance_score"] + 0.1)
            concept_data.setdefault("evolution", []).append({
                "timestamp": timestamp,
                "type": "insight_added",
                "content": insight
            })
            
            # Relationships
            if relationships:
                for related_concept in relationships:
                    relationship = {
                        "from": concept,
                        "to": related_concept,
                        "timestamp": timestamp,
                        "context": insight,
                        "strength": self._calculate_relationship_strength(concept, related_concept, insight)
                    }
                    sem.setdefault("relationships", []).append(relationship)
                    sem.setdefault("knowledge_connections", []).append({
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
                self.current_session.setdefault("intelligence", {}).setdefault("auto_captured_memories", 0)
                self.current_session["intelligence"]["auto_captured_memories"] += 1
            
            self.current_session.setdefault("semantic", {}).setdefault("key_insights", []).append({
                "timestamp": timestamp,
                "insight": insight,
                "concept": concept
            })
            
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
            confidence += 0.2
        if len(insight) > 150:
            confidence += 0.2
        
        # Specificity indicators
        if any(tok in insight.lower() for tok in ["because", "therefore", "thus", "hence", "due to"]):
            confidence += 0.1
        
        return min(confidence, 1.0)

    def _calculate_relationship_strength(self, concept1: str, concept2: str, context: str) -> float:
        """Calculate strength of relationship between concepts"""
        base = 0.3
        if concept1 and concept2:
            base += 0.2
        overlap = len(set(concept1.lower().split()) & set(concept2.lower().split()))
        base += min(0.1 * overlap, 0.2)
        if len(context) > 80:
            base += 0.1
        return min(base, 1.0)

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
            if events:
                insights.append(f"\n📝 Events: {len(events)} recorded")
                types = Counter(e.get("type", "?") for e in events)
                top_types = ", ".join(f"{t}({c})" for t,c in types.most_common(5))
                insights.append(f"  • Types: {top_types}")
                
                # Energy progression
                energy_progression = self._extract_energy_progression(events)
                if energy_progression:
                    insights.append(f"  • Energy progression: {" -> ".join(energy_progression[:6])}{'...' if len(energy_progression)>6 else ''}")
            
            # Concepts and insights
            semantic = session.get("semantic", {})
            key_insights = semantic.get("key_insights", [])
            insights.append(f"\n💡 Key Insights: {len(key_insights)}")
            for ki in key_insights[:3]:
                insights.append(f"  • {ki.get('concept', '')}: {ki.get('insight', '')}")
            
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
        cutoff = time.time() - days_back*24*60*60
        try:
            index = self._load_index()
            recent_sessions = []
            for sid, meta in index.items():
                f = self.sessions_dir / f"{sid}.json"
                if f.exists() and meta.get('created', 0) >= cutoff:
                    with open(f, 'r', encoding='utf-8') as fh:
                        recent_sessions.append(json.load(fh))
            if not recent_sessions:
                return "No sessions found in the specified time window"
            
            analysis = []
            analysis.append("📈 Cross-Session Analysis")
            analysis.append("="*40)
            analysis.append(f"Analyzed sessions: {len(recent_sessions)} (last {days_back} days)")
            
            # Success metric
            successful_sessions = []
            for session in recent_sessions:
                duration = session.get("last_updated", session.get("created", 0)) - session.get("created", 0)
                insights = len(session.get("semantic", {}).get("key_insights", []))
                auto_memories = session.get("intelligence", {}).get("auto_captured_memories", 0)
                success_score = 0
                if duration > 1800:
                    success_score += 1
                if insights > 2:
                    success_score += 2
                if auto_memories > 3:
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
                success_factors = []
                for s in successful_sessions:
                    focus_areas = s["session"].get("metadata", {}).get("attention_focus", [])
                    success_factors.extend(focus_areas)
                if success_factors:
                    top = Counter(success_factors).most_common(5)
                    analysis.append("  • Frequent success focus areas: " + ", ".join(f"{k}({v})" for k,v in top))
            return "\n".join(analysis)
        except Exception as e:
            self.logger.error(f"Cross-session analysis failed: {e}")
            return f"Cross-session analysis failed: {e}"
    
    def bb7_pause_session(self, reason: Optional[str] = None) -> str:
        """Pause the current session"""
        if not self.current_session_id or not self.current_session:
            return "No active session to pause."
        with self._lock:
            self.current_session["status"] = "paused"
            self.current_session["last_updated"] = time.time()
            self.current_session.setdefault("metadata", {})["pause_reason"] = reason or "unspecified"
            self._save_current_session()
            index = self._load_index()
            if self.current_session_id in index:
                index[self.current_session_id]["status"] = "paused"
                self._save_index(index)
            return f"⏸️ Session {self.current_session_id[:8]} paused."

    def bb7_resume_session(self, session_id: str) -> str:
        """Resume a paused session"""
        f = self.sessions_dir / f"{session_id}.json"
        if not f.exists():
            return f"Session {session_id} not found"
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                self.current_session = json.load(fh)
            self.current_session_id = session_id
            self.current_session["status"] = "active"
            self.current_session["last_updated"] = time.time()
            self._save_current_session()
            index = self._load_index()
            if session_id in index:
                index[session_id]["status"] = "active"
                self._save_index(index)
            return f"▶️ Resumed session {session_id[:8]}"
        except Exception as e:
            self.logger.error(f"Failed to resume session {session_id}: {e}")
            return f"Failed to resume session: {e}"

    def bb7_list_sessions(self, status: Optional[str] = None, limit: int = 20) -> str:
        """List all sessions with optional status filter"""
        try:
            index = self._load_index()
            items = list(index.items())
            if status:
                items = [(k,v) for k,v in items if v.get('status') == status]
            items.sort(key=lambda kv: kv[1].get('created', 0), reverse=True)
            items = items[:max(1, limit)]
            lines = ["📋 Sessions:"]
            for sid, meta in items:
                created = datetime.fromtimestamp(meta.get('created', 0)).strftime('%Y-%m-%d %H:%M')
                lines.append(f"  • {sid[:8]} [{meta.get('status','?')}] {created} - {meta.get('goal','')}")
            return "\n".join(lines)
        except Exception as e:
            self.logger.error(f"Failed to list sessions: {e}")
            return f"Failed to list sessions: {e}"

    def bb7_get_session_summary(self, session_id: str) -> str:
        """Get a detailed summary of a specific session"""
        f = self.sessions_dir / f"{session_id}.json"
        if not f.exists():
            return f"Session {session_id} not found"
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                session = json.load(fh)
            summary = []
            summary.append(f"📄 Session Summary: {session_id[:8]}")
            created = datetime.fromtimestamp(session.get('created', 0))
            updated = datetime.fromtimestamp(session.get('last_updated', session.get('created', 0)))
            summary.append(f"🎯 Goal: {session.get('goal','')}")
            summary.append(f"📅 Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
            summary.append(f"🔄 Last Updated: {updated.strftime('%Y-%m-%d %H:%M:%S')}")
            summary.append(f"📊 Status: {session.get('status', 'Unknown')}")
            tags = session.get("tags", [])
            if tags:
                summary.append(f"🏷️ Tags: {', '.join(tags)}")
            # Episodic
            episodic = session.get("episodic", {})
            events = episodic.get("events", [])
            if events:
                summary.append(f"\n📝 Events ({len(events)} total):\n")
                for event in events[-10:]:
                    event_time = datetime.fromtimestamp(event["timestamp"]).strftime("%H:%M")
                    summary.append(f"  • {event_time}: {event['description']}")
            # Semantic
            semantic = session.get("semantic", {})
            concepts = semantic.get("concepts", {})
            insights = semantic.get("key_insights", [])
            if concepts:
                summary.append(f"\n🧠 Concepts ({len(concepts)}):\n")
                for concept, data in list(concepts.items())[:5]:
                    summary.append(f"  • {concept}: {len(data.get('insights', []))} insights")
            if insights:
                summary.append(f"\n💡 Key Insights ({len(insights)}):\n")
                for ins in insights[-5:]:
                    summary.append(f"  • {ins['insight']}")
            # Focus
            meta = session.get("metadata", {})
            energy = meta.get("energy_level", "medium")
            momentum = meta.get("momentum", "starting")
            summary.append(f"\n🎯 Focus: {', '.join(meta.get('attention_focus', [])) if meta.get('attention_focus') else 'n/a'}")
            summary.append(f"⚡ Energy: {energy}, Momentum: {momentum}")
            return "\n".join(summary)
        except Exception as e:
            self.logger.error(f"Failed to summarize session {session_id}: {e}")
            return f"Failed to summarize session: {e}"

    def bb7_link_memory_to_session(self, memory_key: str) -> str:
        """Link a memory key to the current session"""
        if not self.current_session_id or not self.current_session:
            return "No active session. Start a session first with bb7_start_session."

        with self._lock:
            memory_index = self._load_memory_index()
            session_id = self.current_session_id

            # Add memory to session's linked memories
            session_memories = memory_index.setdefault("session_memories", {}).setdefault(session_id, [])
            if memory_key not in session_memories:
                session_memories.append(memory_key)

            # Link memory to session
            memory_to_sessions = memory_index.setdefault("memory_to_sessions", {}).setdefault(memory_key, [])
            if session_id not in memory_to_sessions:
                memory_to_sessions.append(session_id)

            self._save_memory_index(memory_index)

            self.logger.info(f"Linked memory '{memory_key}' to session '{session_id[:8]}'")
            return f"✅ Memory '{memory_key}' linked to current session '{session_id[:8]}'"

    def bb7_auto_memory_stats(self) -> str:
        """Automatically compute and report memory usage statistics, trends, and optimization suggestions."""
        if not self.current_session:
            return "No active session to get auto-memory stats from."
        
        auto_captured_count = self.current_session.get('intelligence', {}).get('auto_captured_memories', 0)
        
        response = f"Auto-captured memories this session: {auto_captured_count}"
        
        if auto_captured_count > 0 and self.memory_tool:
            try:
                # Attempt to get more detailed stats from the memory tool itself
                memory_insights = self.memory_tool.get_memory_insights()
                response += f"\n\nOverall Memory Insights:\n{memory_insights}"
            except Exception as e:
                self.logger.warning(f"Could not retrieve overall memory insights: {e}")
                response += "\n\n(Could not retrieve overall memory insights)"
        
        return response

    def _load_index(self) -> Dict[str, Any]:
        """Load the session index"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load session index: {e}")
        return {}

    def _save_index(self, index: Dict[str, Any]) -> None:
        """Save the session index"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save session index: {e}")

    def _capture_environment_state(self) -> Dict[str, Any]:
        """Capture current development environment state"""
        env = {
            "cwd": os.getcwd(),
            "timestamp": time.time(),
        }
        return env

    def _load_current_session(self) -> None:
        """Load the current session from disk"""
        if not self.current_session_id:
            return
        f = self.sessions_dir / f"{self.current_session_id}.json"
        if f.exists():
            try:
                with open(f, 'r', encoding='utf-8') as fh:
                    self.current_session = json.load(fh)
            except Exception as e:
                self.logger.error(f"Failed to load session {self.current_session_id}: {e}")

    def _save_current_session(self) -> None:
        """Save the current session to disk"""
        if not self.current_session_id or not self.current_session:
            return
        f = self.sessions_dir / f"{self.current_session_id}.json"
        try:
            with open(f, 'w', encoding='utf-8') as fh:
                json.dump(self.current_session, fh, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Failed to save session {self.current_session_id}: {e}")

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
            wf = {
                "name": workflow_name,
                "steps": steps,
                "context": context or "",
                "created": time.time(),
                "frequency": 1
            }
            self.current_session.setdefault("procedural", {}).setdefault("workflows", []).append(wf)
            self.current_session["last_updated"] = time.time()
            self._save_current_session()
            return f"⚙️ Recorded workflow '{workflow_name}' with {len(steps)} steps."

    def bb7_update_focus(self, focus_areas: List[str], energy_level: str = "medium", momentum: str = "steady") -> str:
        """Update current attention focus and energy state"""
        if not self.current_session_id:
            return "No active session. Start a session first with bb7_start_session."
        if not self.current_session:
            self._load_current_session()
        with self._lock:
            meta = self.current_session.setdefault("metadata", {})
            meta["attention_focus"] = focus_areas
            meta["energy_level"] = energy_level
            meta["momentum"] = momentum
            self.current_session["last_updated"] = time.time()
            self._save_current_session()
            return "✅ Focus updated"

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
                    "priority": "high",
                    "when_to_use": ["insight_recording", "architecture", "design_patterns", "conceptual_breakthrough"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "insight": { "type": "string" },
                            "concept": { "type": "string" },
                            "relationships": { "type": "array", "items": {"type": "string"} }
                        },
                        "required": ["insight", "concept"]
                    }
                }
            },
            'bb7_get_session_insights': {
                "callable": lambda session_id=None: self.bb7_get_session_insights(session_id),
                "metadata": {
                    "name": "bb7_get_session_insights",
                    "description": "Generate a session intelligence report, highlighting key insights, breakthroughs, and cognitive metrics.",
                    "category": "sessions",
                    "priority": "medium",
                    "when_to_use": ["session_reporting", "cognitive_metrics", "insight_generation"],
                    "input_schema": {"type": "object", "properties": {"session_id": {"type": "string"}}, "required": []}
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
                    "input_schema": {"type": "object", "properties": {"goal": {"type": "string"}}, "required": ["goal"]}
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
                    "description": "Pause the current session",
                    "category": "sessions",
                    "priority": "low",
                    "when_to_use": ["pause_work", "interrupt_session"],
                    "input_schema": {
                        "type": "object",
                        "properties": { "reason": { "type": "string", "description": "Reason for pausing" } },
                        "required": []
                    }
                }
            },
            'bb7_resume_session': {
                "callable": self.bb7_resume_session,
                "metadata": {
                    "name": "bb7_resume_session",
                    "description": "Resume a paused session",
                    "category": "sessions",
                    "priority": "low",
                    "when_to_use": ["resume_work", "continue_session"],
                    "input_schema": {
                        "type": "object",
                        "properties": { "session_id": { "type": "string", "description": "ID of session to resume" } },
                        "required": ["session_id"]
                    }
                }
            },
            'bb7_list_sessions': {
                "callable": self.bb7_list_sessions,
                "metadata": {
                    "name": "bb7_list_sessions",
                    "description": "List all sessions with optional status filter",
                    "category": "sessions",
                    "priority": "low",
                    "when_to_use": ["session_overview", "find_session"],
                    "input_schema": {
                        "type": "object",
                        "properties": { "status": { "type": "string", "description": "Filter by status (e.g., 'active', 'paused', 'completed')" }, "limit": { "type": "integer", "description": "Maximum number of sessions to return" } },
                        "required": []
                    }
                }
            },
            'bb7_get_session_summary': {
                "callable": self.bb7_get_session_summary,
                "metadata": {
                    "name": "bb7_get_session_summary",
                    "description": "Get a detailed summary of a specific session",
                    "category": "sessions",
                    "priority": "low",
                    "when_to_use": ["session_details", "review_session"],
                    "input_schema": {
                        "type": "object",
                        "properties": { "session_id": { "type": "string", "description": "ID of session to summarize" } },
                        "required": ["session_id"]
                    }
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
                    "description": "Show raw intelligence metrics learned across sessions.",
                    "category": "sessions",
                    "priority": "low",
                    "when_to_use": ["metrics", "debug"],
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
                "callable": self.bb7_auto_memory_stats,
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
