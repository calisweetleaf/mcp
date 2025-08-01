#!/usr/bin/env python3
"""
Auto-Activation Tool - Intelligent MCP Server Assistant

This tool provides meta-intelligence for the MCP server ecosystem,
helping Copilot understand available capabilities and automatically
activating relevant context for seamless collaboration continuity.
"""

import json
import logging
import os
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from tools.memory_tool import EnhancedMemoryTool
from tools.memory_interconnect import MemoryInterconnectionEngine


class AutoTool:
    """Intelligent auto-activation and tool guidance system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Initialize memory tools
        self.memory_tool = EnhancedMemoryTool()
        self.memory_interconnect = MemoryInterconnectionEngine()
        
        # Tool capability mapping for intelligent suggestions - Updated with complete standardized bb7_ inventory
        self.tool_categories = {
            "memory_core": ["bb7_memory_store", "bb7_memory_retrieve", "bb7_memory_list", "bb7_memory_delete", "bb7_memory_stats",
                           "bb7_memory_search", "bb7_memory_insights", "bb7_memory_consolidate", "bb7_memory_categories"],
            "memory_interconnect": ["bb7_memory_analyze_entry", "bb7_memory_intelligent_search", "bb7_memory_get_insights", 
                                   "bb7_memory_consolidate", "bb7_memory_concept_network", "bb7_memory_extract_concepts"],
            "files": ["bb7_read_file", "bb7_write_file", "bb7_append_file", "bb7_list_directory", "bb7_get_file_info", "bb7_search_files"],
            "shell": ["bb7_run_command", "bb7_run_script", "bb7_get_environment", "bb7_list_processes", "bb7_kill_process", "bb7_get_system_info"],
            "web": ["bb7_fetch_url", "bb7_download_file", "bb7_check_url_status", "bb7_search_web", "bb7_extract_links"],
            "sessions": ["bb7_start_session", "bb7_log_event", "bb7_capture_insight", "bb7_record_workflow", "bb7_update_focus", 
                        "bb7_pause_session", "bb7_resume_session", "bb7_list_sessions", "bb7_get_session_summary", 
                        "bb7_get_session_insights", "bb7_cross_session_analysis", "bb7_session_recommendations", 
                        "bb7_learned_patterns", "bb7_session_intelligence", "bb7_link_memory_to_session", "bb7_auto_memory_stats"],
            "visual": ["bb7_screen_capture", "bb7_screen_monitor", "bb7_visual_diff", "bb7_window_manager", 
                      "bb7_active_window", "bb7_keyboard_input", "bb7_mouse_control", "bb7_clipboard_manage"],
            "terminal": ["bb7_terminal_status", "bb7_terminal_run_command", "bb7_terminal_history", 
                        "bb7_terminal_environment", "bb7_terminal_cd", "bb7_terminal_which"],
            "project_context": ["bb7_analyze_project_structure", "bb7_get_project_dependencies", 
                               "bb7_get_recent_changes", "bb7_get_code_metrics"],
            "code_analysis": ["bb7_analyze_code_complete", "bb7_python_execute_secure", 
                             "bb7_security_audit", "bb7_get_execution_audit"],
            "auto_activation": ["bb7_workspace_context_loader", "bb7_show_available_capabilities", 
                               "bb7_auto_session_resume", "bb7_intelligent_tool_guide"]
        }
        
        self.logger.info("Auto-activation tool initialized - ready to guide AI collaboration")
    
    def workspace_context_loader(self, include_recent_memories: bool = True, 
                                include_active_sessions: bool = True) -> str:
        """🚀 FOUNDATIONAL: Load all relevant context for seamless session continuity"""
        try:
            context_report = []
            context_report.append("🚀 WORKSPACE CONTEXT LOADING - Establishing AI-Human Collaboration State")
            context_report.append("=" * 80)
            
            # Check current working directory and project structure
            cwd = os.getcwd()
            context_report.append(f"📂 Current Workspace: {cwd}")
            
            # Look for project indicators
            project_files = [".git", "package.json", "requirements.txt", "Cargo.toml", "go.mod", "pom.xml"]
            project_type = "generic"
            for file in project_files:
                if Path(file).exists():
                    if file == ".git":
                        project_type = "git repository"
                    elif file == "package.json":
                        project_type = "Node.js project"
                    elif file == "requirements.txt":
                        project_type = "Python project"
                    elif file == "Cargo.toml":
                        project_type = "Rust project"
                    elif file == "go.mod":
                        project_type = "Go project"
                    elif file == "pom.xml":
                        project_type = "Java/Maven project"
                    break
            
            context_report.append(f"🔍 Project Type: {project_type}")
            
            # Load recent memories if requested
            if include_recent_memories:
                memory_file = self.data_dir / "memory_store.json"
                if memory_file.exists():
                    try:
                        with open(memory_file, 'r', encoding='utf-8') as f:
                            memories = json.load(f)
                        
                        recent_keys = list(memories.keys())[-5:] if memories else []
                        context_report.append(f"\n💾 Recent Memory Keys ({len(recent_keys)}/total {len(memories)}):")
                        for key in recent_keys:
                            entry = memories[key]
                            if isinstance(entry, dict) and 'timestamp' in entry:
                                timestamp = time.strftime('%Y-%m-%d %H:%M', time.localtime(entry['timestamp']))
                                context_report.append(f"  • {key} (updated: {timestamp})")
                            else:
                                context_report.append(f"  • {key}")
                        
                        # Add memory interconnect insights
                        try:
                            memory_insights = self.memory_interconnect.get_memory_insights()
                            if memory_insights.get('top_concepts'):
                                context_report.append(f"\n🧠 Memory Intelligence:")
                                context_report.append(f"  • Top concepts: {', '.join(memory_insights['top_concepts'][:5])}")
                                if memory_insights.get('total_relationships', 0) > 0:
                                    context_report.append(f"  • Memory connections: {memory_insights['total_relationships']}")
                        except Exception as e:
                            self.logger.debug(f"Memory interconnect insights error: {e}")
                            
                    except Exception as e:
                        context_report.append(f"⚠️ Memory loading error: {e}")
                else:
                    context_report.append("\n💾 No persistent memory found - starting fresh")
            
            # Check for active sessions if requested
            if include_active_sessions:
                sessions_dir = self.data_dir / "sessions"
                if sessions_dir.exists():
                    try:
                        session_files = list(sessions_dir.glob("*.json"))
                        active_sessions = []
                        
                        for session_file in session_files:
                            try:
                                with open(session_file, 'r', encoding='utf-8') as f:
                                    session_data = json.load(f)
                                if session_data.get("status") == "active":
                                    active_sessions.append({
                                        "id": session_data.get("id", session_file.stem),
                                        "goal": session_data.get("goal", "No goal specified"),
                                        "created": session_data.get("created", 0)
                                    })
                            except:
                                continue
                        
                        if active_sessions:
                            context_report.append(f"\n🎯 Active Sessions ({len(active_sessions)}):")
                            for session in sorted(active_sessions, key=lambda x: x["created"], reverse=True):
                                created_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(session["created"]))
                                context_report.append(f"  • {session['goal']} (created: {created_time})")
                                context_report.append(f"    ID: {session['id']}")
                        else:
                            context_report.append("\n🎯 No active sessions found")
                    except Exception as e:
                        context_report.append(f"⚠️ Session loading error: {e}")
                else:
                    context_report.append("\n🎯 No sessions directory found")
            
            # MCP Server status
            context_report.append(f"\n🔧 MCP Server Status: ACTIVE")
            context_report.append(f"📊 Available Tool Categories: {len(self.tool_categories)}")
            total_tools = sum(len(tools) for tools in self.tool_categories.values()) + 3  # +3 for auto tools
            context_report.append(f"⚙️ Total Available Tools: {total_tools}")
            
            # Recommendations
            context_report.append(f"\n💡 COLLABORATION RECOMMENDATIONS:")
            context_report.append(f"  • Use 'show_available_capabilities' to see all available tools")
            context_report.append(f"  • Use 'auto_session_resume' to continue interrupted work")
            context_report.append(f"  • Use 'start_session' for new significant development tasks")
            context_report.append(f"  • Use 'memory_store' to save important insights and decisions")
            
            context_report.append(f"\n✨ CONTEXT LOADING COMPLETE - Ready for seamless AI-Human collaboration!")
            
            self.logger.info("Workspace context loaded successfully")
            return "\n".join(context_report)
            
        except Exception as e:
            self.logger.error(f"Error loading workspace context: {e}")
            return f"❌ Error loading workspace context: {str(e)}\n\nBasic MCP server is still available for collaboration."
    
    def show_available_capabilities(self, category: Optional[str] = None) -> str:
        """📋 Display comprehensive overview of all MCP tools and capabilities"""
        try:
            if category and category != "all":
                if category in self.tool_categories:
                    tools = self.tool_categories[category]
                    result = f"📋 {category.upper()} CAPABILITIES\n"
                    result += "=" * 50 + "\n\n"
                    result += f"Available {category} tools ({len(tools)}):\n"
                    for tool in tools:
                        result += f"  • {tool}\n"
                    return result
                else:
                    return f"❌ Unknown category '{category}'. Available: {list(self.tool_categories.keys())}"
            
            # Show all capabilities
            capability_overview = []
            capability_overview.append("🎯 COMPREHENSIVE MCP SERVER CAPABILITIES OVERVIEW")
            capability_overview.append("=" * 80)
            capability_overview.append("")
            capability_overview.append("🚀 AUTO-ACTIVATION & GUIDANCE TOOLS:")
            capability_overview.append("  • workspace_context_loader - Load project context and session state")
            capability_overview.append("  • show_available_capabilities - Display all available tools (this tool)")
            capability_overview.append("  • auto_session_resume - Intelligent session continuity management")
            capability_overview.append("")
            
            for cat_name, tools in self.tool_categories.items():
                icon_map = {
                    "memory": "🧠",
                    "files": "📁", 
                    "shell": "⚡",
                    "web": "🌐",
                    "sessions": "🎯",
                    "visual": "👁️",
                    "terminal": "🖥️"
                }
                icon = icon_map.get(cat_name, "🔧")
                
                capability_overview.append(f"{icon} {cat_name.upper()} TOOLS ({len(tools)}):")
                for tool in tools:
                    # Add brief descriptions for key tools
                    descriptions = {
                        "memory_store": "Store persistent context across sessions",
                        "start_session": "Begin tracked development sessions",
                        "bb7_screen_capture": "Take screenshots for visual debugging",
                        "run_command": "Execute shell commands",
                        "read_file": "Read any file on the system",
                        "fetch_url": "Download web content"
                    }
                    desc = descriptions.get(tool, "")
                    if desc:
                        capability_overview.append(f"  • {tool} - {desc}")
                    else:
                        capability_overview.append(f"  • {tool}")
                capability_overview.append("")
            
            capability_overview.append("💡 USAGE TIPS:")
            capability_overview.append("  • Tools can be invoked naturally: 'save this insight to memory'")
            capability_overview.append("  • Or explicitly: '#memory_store key=\"insight\" value=\"...\"'") 
            capability_overview.append("  • Use sessions for complex, multi-step development tasks")
            capability_overview.append("  • Visual tools enable true screen-aware collaboration")
            capability_overview.append("  • All data stays local - complete digital sovereignty")
            capability_overview.append("")
            capability_overview.append("🎉 READY FOR ADVANCED AI-HUMAN COLLABORATION!")
            
            self.logger.info("Displayed comprehensive capabilities overview")
            return "\n".join(capability_overview)
            
        except Exception as e:
            self.logger.error(f"Error showing capabilities: {e}")
            return f"❌ Error displaying capabilities: {str(e)}"
    
    def auto_session_resume(self, workspace_path: Optional[str] = None, 
                           user_intent: Optional[str] = None) -> str:
        """🔄 Intelligent session continuity and automatic resumption"""
        try:
            resume_report = []
            resume_report.append("🔄 AUTO-SESSION RESUME - Analyzing Continuity Options")
            resume_report.append("=" * 60)
            
            # Analyze current workspace
            current_path = workspace_path or os.getcwd()
            resume_report.append(f"📂 Workspace: {current_path}")
            if user_intent:
                resume_report.append(f"🎯 User Intent: {user_intent}")
            
            # Check for active sessions
            sessions_dir = self.data_dir / "sessions"
            active_sessions = []
            paused_sessions = []
            
            if sessions_dir.exists():
                try:
                    session_files = list(sessions_dir.glob("*.json"))
                    for session_file in session_files:
                        try:
                            with open(session_file, 'r', encoding='utf-8') as f:
                                session_data = json.load(f)
                            
                            status = session_data.get("status", "unknown")
                            if status == "active":
                                active_sessions.append(session_data)
                            elif status == "paused":
                                paused_sessions.append(session_data)
                        except:
                            continue
                except Exception as e:
                    resume_report.append(f"⚠️ Error reading sessions: {e}")
            
            # Decision logic for session resumption
            recommendations = []
            
            if active_sessions:
                resume_report.append(f"\n🟢 ACTIVE SESSIONS FOUND ({len(active_sessions)}):")
                for session in active_sessions:
                    goal = session.get("goal", "No goal")
                    last_updated = session.get("last_updated", session.get("created", 0))
                    time_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(last_updated))
                    resume_report.append(f"  • {goal} (last active: {time_str})")
                    resume_report.append(f"    ID: {session.get('id', 'unknown')}")
                
                recommendations.append("✅ RECOMMENDATION: Continue with most recent active session")
                recommendations.append("💡 Use: resume_session with the session ID above")
            
            elif paused_sessions:
                resume_report.append(f"\n⏸️ PAUSED SESSIONS FOUND ({len(paused_sessions)}):")
                most_recent = None
                most_recent_time = 0
                
                for session in paused_sessions:
                    goal = session.get("goal", "No goal")
                    paused_at = session.get("paused_at", session.get("last_updated", 0))
                    time_str = time.strftime('%Y-%m-%d %H:%M', time.localtime(paused_at))
                    resume_report.append(f"  • {goal} (paused: {time_str})")
                    resume_report.append(f"    ID: {session.get('id', 'unknown')}")
                    
                    if paused_at > most_recent_time:
                        most_recent_time = paused_at
                        most_recent = session
                
                if most_recent and user_intent:
                    # Try to match user intent with paused session
                    intent_keywords = user_intent.lower().split()
                    session_goal = most_recent.get("goal", "").lower()
                    
                    overlap = any(keyword in session_goal for keyword in intent_keywords)
                    if overlap:
                        recommendations.append("🎯 SMART MATCH: Your intent matches a paused session!")
                        recommendations.append(f"✅ RECOMMENDATION: Resume session '{most_recent.get('goal')}'")
                        recommendations.append(f"💡 Use: resume_session with ID: {most_recent.get('id')}")
                    else:
                        recommendations.append("🆕 NEW DIRECTION: Your intent seems different from paused sessions")
                        recommendations.append("✅ RECOMMENDATION: Start a new session")
                        recommendations.append(f"💡 Use: start_session with goal: '{user_intent}'")
                else:
                    recommendations.append("✅ RECOMMENDATION: Resume most recent paused session or start new")
                    recommendations.append("💡 Use: resume_session or start_session as appropriate")
            
            else:
                resume_report.append(f"\n🆕 NO EXISTING SESSIONS FOUND")
                if user_intent:
                    recommendations.append("🚀 FRESH START: Perfect time to begin a tracked session!")
                    recommendations.append(f"✅ RECOMMENDATION: Start new session with goal: '{user_intent}'")
                    recommendations.append("💡 Use: start_session to enable episodic memory tracking")
                else:
                    recommendations.append("💭 EXPLORATION MODE: Ready for any development task")
                    recommendations.append("✅ RECOMMENDATION: Start a session when you have a clear goal")
                    recommendations.append("💡 Use: start_session when ready to track progress")
            
            # Add recommendations to report
            if recommendations:
                resume_report.append(f"\n🎯 INTELLIGENT RECOMMENDATIONS:")
                for rec in recommendations:
                    resume_report.append(f"  {rec}")
            
            # Check for relevant memory
            memory_file = self.data_dir / "memory_store.json"
            if memory_file.exists() and user_intent:
                try:
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        memories = json.load(f)
                    
                    intent_keywords = user_intent.lower().split() if user_intent else []
                    relevant_memories = []
                    
                    for key, value in memories.items():
                        key_lower = key.lower()
                        value_str = str(value).lower() if not isinstance(value, dict) else str(value.get('value', '')).lower()
                        
                        if any(keyword in key_lower or keyword in value_str for keyword in intent_keywords):
                            relevant_memories.append(key)
                    
                    if relevant_memories:
                        resume_report.append(f"\n🧠 RELEVANT MEMORY FOUND:")
                        for key in relevant_memories[:3]:  # Show top 3
                            resume_report.append(f"  • {key}")
                        if len(relevant_memories) > 3:
                            resume_report.append(f"  ... and {len(relevant_memories) - 3} more")
                        resume_report.append("💡 Use: memory_retrieve to access these insights")
                
                except Exception as e:
                    resume_report.append(f"⚠️ Memory search error: {e}")
            
            resume_report.append(f"\n✨ SESSION CONTINUITY ANALYSIS COMPLETE")
            
            self.logger.info("Auto-session resume analysis completed")
            return "\n".join(resume_report)
            
        except Exception as e:
            self.logger.error(f"Error in auto session resume: {e}")
            return f"❌ Error analyzing session continuity: {str(e)}\n\nYou can still manually start a new session or resume existing ones."
    
    def intelligent_tool_guide(self, user_query: str, context: Optional[str] = None) -> str:
        """🧠 ADVANCED: Analyze user intent and suggest optimal tool combinations"""
        try:
            guide_report = []
            guide_report.append("🧠 INTELLIGENT TOOL GUIDANCE - Analyzing Your Request")
            guide_report.append("=" * 60)
            guide_report.append(f"📝 Query: {user_query}")
            if context:
                guide_report.append(f"📄 Context: {context}")
            
            query_lower = user_query.lower()
            suggested_tools = []
            workflow_suggestions = []
            
            # Intent analysis patterns
            intent_patterns = {
                "memory": ["remember", "save", "store", "recall", "memory", "persist", "context"],
                "files": ["file", "read", "write", "create", "edit", "directory", "folder", "code"],
                "shell": ["run", "execute", "command", "terminal", "bash", "script", "install"],
                "web": ["fetch", "download", "url", "website", "api", "search", "documentation"],
                "sessions": ["session", "track", "goal", "project", "workflow", "progress"],
                "visual": ["screenshot", "screen", "see", "visual", "ui", "interface", "click"],
                "analysis": ["analyze", "understand", "explain", "debug", "error", "problem"]
            }
            
            # Detect intent categories
            detected_intents = []
            for intent, keywords in intent_patterns.items():
                if any(keyword in query_lower for keyword in keywords):
                    detected_intents.append(intent)
            
            guide_report.append(f"\n🎯 DETECTED INTENTS: {', '.join(detected_intents) if detected_intents else 'general assistance'}")
            
            # Generate tool suggestions based on intents
            if "memory" in detected_intents:
                if any(word in query_lower for word in ["save", "store", "remember"]):
                    suggested_tools.append("memory_store - Save important information")
                elif any(word in query_lower for word in ["recall", "retrieve", "what", "find"]):
                    suggested_tools.append("memory_retrieve - Get stored information")
                    suggested_tools.append("memory_list - Browse available memories")
            
            if "files" in detected_intents:
                if any(word in query_lower for word in ["read", "show", "display", "content"]):
                    suggested_tools.append("read_file - Read file contents")
                    suggested_tools.append("list_directory - Explore directory structure")
                elif any(word in query_lower for word in ["create", "write", "generate"]):
                    suggested_tools.append("write_file - Create or modify files")
                elif any(word in query_lower for word in ["find", "search", "locate"]):
                    suggested_tools.append("search_files - Find files by pattern")
            
            if "shell" in detected_intents:
                suggested_tools.append("run_command - Execute shell commands")
                if "script" in query_lower:
                    suggested_tools.append("run_script - Execute custom scripts")
                if any(word in query_lower for word in ["environment", "system", "info"]):
                    suggested_tools.append("get_system_info - System analysis")
            
            if "web" in detected_intents:
                if any(word in query_lower for word in ["fetch", "get", "download"]):
                    suggested_tools.append("fetch_url - Get web content")
                elif "search" in query_lower:
                    suggested_tools.append("search_web - Web search")
            
            if "sessions" in detected_intents:
                if any(word in query_lower for word in ["start", "begin", "new"]):
                    suggested_tools.append("start_session - Begin tracked session")
                elif any(word in query_lower for word in ["resume", "continue", "ongoing"]):
                    suggested_tools.append("auto_session_resume - Continue previous work")
            
            if "visual" in detected_intents:
                suggested_tools.append("bb7_screen_capture - Take screenshots")
                if "click" in query_lower or "interact" in query_lower:
                    suggested_tools.append("bb7_mouse_control - Mouse automation")
                    suggested_tools.append("bb7_keyboard_input - Keyboard automation")
            
            if "analysis" in detected_intents:
                workflow_suggestions.extend([
                    "1. Use 'read_file' to examine relevant code/config files",
                    "2. Use 'memory_retrieve' to check for similar past issues",
                    "3. Use 'run_command' to reproduce or diagnose the problem",
                    "4. Use 'memory_store' to save the solution for future reference"
                ])
            
            # Display suggestions
            if suggested_tools:
                guide_report.append(f"\n🔧 SUGGESTED TOOLS:")
                for tool in suggested_tools:
                    guide_report.append(f"  • {tool}")
            
            if workflow_suggestions:
                guide_report.append(f"\n⚙️ SUGGESTED WORKFLOW:")
                for step in workflow_suggestions:
                    guide_report.append(f"  {step}")
            
            # General workflow suggestions based on query complexity
            if len(query_lower.split()) > 10 or any(word in query_lower for word in ["complex", "multiple", "several"]):
                guide_report.append(f"\n💡 COMPLEX TASK RECOMMENDATIONS:")
                guide_report.append(f"  • Start with: start_session to track this multi-step work")
                guide_report.append(f"  • Use: log_event to document key decisions and discoveries")
                guide_report.append(f"  • Use: capture_insight when you gain important understanding")
                guide_report.append(f"  • Use: memory_store to preserve important context")
            
            if not suggested_tools and not workflow_suggestions:
                guide_report.append(f"\n🤔 GENERAL GUIDANCE:")
                guide_report.append(f"  • Use 'show_available_capabilities' to see all available tools")
                guide_report.append(f"  • Use 'workspace_context_loader' to understand current state")
                guide_report.append(f"  • Consider starting a session if this is significant work")
            
            guide_report.append(f"\n✨ TOOL GUIDANCE COMPLETE - Ready to assist!")
            
            self.logger.info("Provided intelligent tool guidance")
            return "\n".join(guide_report)
            
        except Exception as e:
            self.logger.error(f"Error in intelligent tool guide: {e}")
            return f"❌ Error analyzing request: {str(e)}\n\nGeneral suggestion: Use 'show_available_capabilities' to see available tools."
    
    def analyze_project_structure(self, max_depth: int = 3, include_hidden: bool = False) -> str:
        """
        Analyze and summarize project structure in a format optimized for LLM understanding.
        Perfect for helping Copilot understand your codebase organization.
        
        Args:
            max_depth: Maximum directory depth to analyze (default: 3)
            include_hidden: Whether to include hidden files/directories (default: False)
        """
        try:
            cwd = Path.cwd()
            self.logger.info(f"Analyzing project structure from: {cwd}")
            
            analysis = {
                "project_root": str(cwd),
                "analysis_timestamp": time.ctime(),
                "structure": {},
                "key_files": [],
                "project_type": "unknown",
                "technologies": [],
                "summary": ""
            }
            
            # Detect project type and technologies
            analysis.update(self._detect_project_type(cwd))
            
            # Build directory tree
            analysis["structure"] = self._build_directory_tree(cwd, max_depth, include_hidden)
            
            # Find key configuration and documentation files
            analysis["key_files"] = self._find_key_files(cwd)
            
            # Generate LLM-friendly summary
            analysis["summary"] = self._generate_project_summary(analysis)
            
            # Format for LLM consumption
            return self._format_analysis_for_llm(analysis)
            
        except Exception as e:
            self.logger.error(f"Error analyzing project structure: {e}")
            return f"Error analyzing project structure: {str(e)}"
    
    def get_project_dependencies(self) -> str:
        """
        Extract and summarize project dependencies in LLM-friendly format.
        Helps Copilot understand what libraries and frameworks are available.
        """
        try:
            cwd = Path.cwd()
            dependencies = {
                "python": [],
                "node": [],
                "other": []
            }
            
            # Python dependencies
            req_files = ["requirements.txt", "pyproject.toml", "Pipfile", "environment.yml"]
            for req_file in req_files:
                req_path = cwd / req_file
                if req_path.exists():
                    deps = self._parse_python_dependencies(req_path)
                    dependencies["python"].extend(deps)
            
            # Node.js dependencies
            package_json = cwd / "package.json"
            if package_json.exists():
                dependencies["node"] = self._parse_node_dependencies(package_json)
            
            # Other dependency files
            other_files = ["Cargo.toml", "go.mod", "pom.xml", "build.gradle"]
            for dep_file in other_files:
                dep_path = cwd / dep_file
                if dep_path.exists():
                    dependencies["other"].append(f"{dep_file} found")
            
            return self._format_dependencies_for_llm(dependencies)
            
        except Exception as e:
            self.logger.error(f"Error getting project dependencies: {e}")
            return f"Error getting project dependencies: {str(e)}"
    
    def get_recent_changes(self, days: int = 7) -> str:
        """
        Get recent Git changes in LLM-friendly format.
        Helps Copilot understand recent development activity and context.
        
        Args:
            days: Number of days to look back for changes (default: 7)
        """
        try:
            # Check if we're in a git repository
            if not (Path.cwd() / ".git").exists():
                return "This project is not a Git repository"
            
            # Get recent commits with improved error handling
            cmd = ["git", "log", f"--since={days} days ago", "--oneline", "--no-merges"]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                
                if result.returncode != 0:
                    return f"Git command failed: {result.stderr}"
                
                commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
            except subprocess.TimeoutExpired:
                return "Git log command timed out - repository may be too large or hanging"
            except FileNotFoundError:
                return "Git not found - please ensure Git is installed and in PATH"
            except Exception as e:
                return f"Error running git log: {str(e)}"
            
            # Get changed files with improved error handling
            cmd_files = ["git", "diff", f"--since={days} days ago", "--name-only"]
            try:
                result_files = subprocess.run(cmd_files, capture_output=True, text=True, timeout=5)
                changed_files = result_files.stdout.strip().split('\n') if result_files.stdout.strip() else []
            except subprocess.TimeoutExpired:
                changed_files = []
                self.logger.warning("Git diff command timed out")
            except Exception as e:
                changed_files = []
                self.logger.warning(f"Error getting changed files: {e}")
            
            # Get current branch with improved error handling
            cmd_branch = ["git", "branch", "--show-current"]
            try:
                result_branch = subprocess.run(cmd_branch, capture_output=True, text=True, timeout=2)
                current_branch = result_branch.stdout.strip() if result_branch.returncode == 0 else "unknown"
            except subprocess.TimeoutExpired:
                current_branch = "unknown (timeout)"
            except Exception as e:
                current_branch = f"unknown (error: {str(e)[:30]})"
            
            # Format for LLM
            summary = f"📈 Recent Git Activity (last {days} days):\n\n"
            summary += f"Current Branch: {current_branch}\n\n"
            
            if commits:
                summary += f"Recent Commits ({len(commits)}):\n"
                for commit in commits[:10]:  # Limit to 10 most recent
                    summary += f"  • {commit}\n"
                if len(commits) > 10:
                    summary += f"  ... and {len(commits) - 10} more commits\n"
            else:
                summary += "No commits in the specified timeframe\n"
                
            if changed_files and changed_files != ['']:
                summary += f"\nFiles Modified Recently ({len(changed_files)}):\n"
                for file in changed_files[:15]:  # Limit to 15 files
                    summary += f"  • {file}\n"
                if len(changed_files) > 15:
                    summary += f"  ... and {len(changed_files) - 15} more files\n"
            else:
                summary += "\nNo files modified in the specified timeframe\n"
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting recent changes: {e}")
            return f"Error getting recent changes: {str(e)}"
    
    # Helper methods for project analysis
    def _detect_project_type(self, path: Path) -> Dict[str, Any]:
        """Detect project type and technologies"""
        project_indicators = {
            "package.json": {"type": "Node.js/JavaScript", "tech": ["JavaScript", "Node.js"]},
            "requirements.txt": {"type": "Python", "tech": ["Python"]},
            "pyproject.toml": {"type": "Python (Modern)", "tech": ["Python"]},
            "Cargo.toml": {"type": "Rust", "tech": ["Rust"]},
            "go.mod": {"type": "Go", "tech": ["Go"]},
            "pom.xml": {"type": "Java/Maven", "tech": ["Java", "Maven"]},
            "build.gradle": {"type": "Java/Gradle", "tech": ["Java", "Gradle"]},
            "Gemfile": {"type": "Ruby", "tech": ["Ruby"]},
            "composer.json": {"type": "PHP", "tech": ["PHP"]},
            ".csproj": {"type": ".NET", "tech": [".NET", "C#"]},
            "Dockerfile": {"type": "Containerized", "tech": ["Docker"]},
            ".git": {"type": "Git Repository", "tech": ["Git"]}
        }
        
        detected_type = "unknown"
        technologies = []
        
        for file_pattern, info in project_indicators.items():
            if file_pattern.startswith("."):
                # Directory check
                if (path / file_pattern).exists():
                    detected_type = info["type"]
                    technologies.extend(info["tech"])
            else:
                # File check
                matches = list(path.glob(f"**/{file_pattern}"))
                if matches:
                    detected_type = info["type"]
                    technologies.extend(info["tech"])
        
        return {"project_type": detected_type, "technologies": list(set(technologies))}
    
    def _build_directory_tree(self, path: Path, max_depth: int, include_hidden: bool, current_depth: int = 0) -> Dict:
        """Build a directory tree structure"""
        if current_depth >= max_depth:
            return {}
        
        tree = {}
        try:
            items = [item for item in path.iterdir() if include_hidden or not item.name.startswith('.')]
            items.sort(key=lambda x: (x.is_file(), x.name.lower()))
            
            for item in items:
                if item.is_dir():
                    tree[f"{item.name}/"] = self._build_directory_tree(item, max_depth, include_hidden, current_depth + 1)
                else:
                    tree[item.name] = "file"
        except PermissionError:
            tree["[Permission Denied]"] = "error"
        
        return tree
    
    def _find_key_files(self, path: Path) -> List[str]:
        """Find key configuration and documentation files"""
        key_patterns = [
            "README*", "*.md", "LICENSE*", "CHANGELOG*",
            "requirements.txt", "package.json", "pyproject.toml",
            "Dockerfile", "docker-compose.yml", ".env*",
            "tsconfig.json", "webpack.config.js", "vite.config.*",
            ".gitignore", ".gitattributes", "Makefile"
        ]
        
        found_files = []
        for pattern in key_patterns:
            matches = list(path.glob(pattern))
            found_files.extend([str(f.relative_to(path)) for f in matches])
        
        return sorted(found_files)
    
    def _generate_project_summary(self, analysis: Dict) -> str:
        """Generate a human-readable project summary"""
        summary = f"Project Type: {analysis['project_type']}\n"
        
        if analysis['technologies']:
            summary += f"Technologies: {', '.join(analysis['technologies'])}\n"
        
        summary += f"Key Files: {len(analysis['key_files'])} configuration/documentation files found\n"
        
        # Count directories and files
        def count_items(tree):
            dirs = files = 0
            for key, value in tree.items():
                if key.endswith('/'):
                    dirs += 1
                    sub_dirs, sub_files = count_items(value)
                    dirs += sub_dirs
                    files += sub_files
                else:
                    files += 1
            return dirs, files
        
        dirs, files = count_items(analysis['structure'])
        summary += f"Structure: {dirs} directories, {files} files (scanned)"
        
        return summary
    
    def _format_analysis_for_llm(self, analysis: Dict) -> str:
        """Format the analysis in an LLM-friendly way"""
        output = []
        output.append("🏗️ PROJECT STRUCTURE ANALYSIS")
        output.append("=" * 50)
        output.append(f"📂 Root: {analysis['project_root']}")
        output.append(f"⏰ Analyzed: {analysis['analysis_timestamp']}")
        output.append(f"🔍 {analysis['summary']}")
        
        if analysis['key_files']:
            output.append(f"\n📋 Key Configuration Files:")
            for file in analysis['key_files'][:10]:  # Limit display
                output.append(f"  • {file}")
            if len(analysis['key_files']) > 10:
                output.append(f"  ... and {len(analysis['key_files']) - 10} more files")
        
        output.append(f"\n📁 Directory Structure (depth limited):")
        output.append(self._format_tree(analysis['structure']))
        
        return "\n".join(output)
    
    def _format_tree(self, tree: Dict, prefix: str = "", is_last: bool = True) -> str:
        """Format directory tree for display"""
        if not tree:
            return ""
        
        output = []
        items = list(tree.items())
        
        for i, (name, subtree) in enumerate(items):
            is_last_item = (i == len(items) - 1)
            current_prefix = "└── " if is_last_item else "├── "
            output.append(f"{prefix}{current_prefix}{name}")
            
            if isinstance(subtree, dict) and subtree:
                next_prefix = prefix + ("    " if is_last_item else "│   ")
                output.append(self._format_tree(subtree, next_prefix, is_last_item))
        
        return "\n".join(filter(None, output))
    
    def _parse_python_dependencies(self, req_path: Path) -> List[str]:
        """Parse Python dependency files"""
        deps = []
        try:
            if req_path.name == "requirements.txt":
                content = req_path.read_text(encoding='utf-8')
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name before version specifier
                        package = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].strip()
                        if package:
                            deps.append(package)
            elif req_path.name == "pyproject.toml":
                # Basic TOML parsing for dependencies
                content = req_path.read_text(encoding='utf-8')
                if '[tool.poetry.dependencies]' in content:
                    deps.append("Poetry project detected")
                elif 'dependencies = [' in content:
                    deps.append("pyproject.toml dependencies found")
        except Exception as e:
            deps.append(f"Error parsing {req_path.name}: {str(e)}")
        
        return deps
    
    def _parse_node_dependencies(self, package_path: Path) -> List[str]:
        """Parse Node.js package.json dependencies"""
        deps = []
        try:
            with open(package_path, 'r', encoding='utf-8') as f:
                package_data = json.load(f)
            
            if 'dependencies' in package_data:
                deps.extend(list(package_data['dependencies'].keys()))
            if 'devDependencies' in package_data:
                dev_deps = list(package_data['devDependencies'].keys())
                deps.extend([f"{dep} (dev)" for dep in dev_deps])
                
        except Exception as e:
            deps.append(f"Error parsing package.json: {str(e)}")
        
        return deps
    
    def _format_dependencies_for_llm(self, dependencies: Dict) -> str:
        """Format dependencies in LLM-friendly format"""
        output = []
        output.append("📦 PROJECT DEPENDENCIES ANALYSIS")
        output.append("=" * 40)
        
        if dependencies["python"]:
            output.append(f"\n🐍 Python Dependencies ({len(dependencies['python'])}):")
            for dep in dependencies["python"][:15]:  # Limit display
                output.append(f"  • {dep}")
            if len(dependencies["python"]) > 15:
                output.append(f"  ... and {len(dependencies['python']) - 15} more packages")
        
        if dependencies["node"]:
            output.append(f"\n📦 Node.js Dependencies ({len(dependencies['node'])}):")
            for dep in dependencies["node"][:15]:  # Limit display
                output.append(f"  • {dep}")
            if len(dependencies["node"]) > 15:
                output.append(f"  ... and {len(dependencies['node']) - 15} more packages")
        
        if dependencies["other"]:
            output.append(f"\n🔧 Other Dependencies:")
            for dep in dependencies["other"]:
                output.append(f"  • {dep}")
        
        if not any(dependencies.values()):
            output.append("\n📋 No dependency files found in this project")
        
        return "\n".join(output)

    def get_tools(self) -> Dict[str, Callable]:
        """Return all available auto-activation tools with bb7_ prefix for MCP consistency"""
        return {
            # Core auto-activation tools
            'bb7_workspace_context_loader': lambda include_recent_memories=True, include_active_sessions=True: 
                self.workspace_context_loader(include_recent_memories, include_active_sessions),
                
            'bb7_show_available_capabilities': lambda category=None: 
                self.show_available_capabilities(category),
                
            'bb7_auto_session_resume': lambda workspace_path=None, user_intent=None: 
                self.auto_session_resume(workspace_path, user_intent),
                
            'bb7_intelligent_tool_guide': lambda user_query, context=None: 
                self.intelligent_tool_guide(user_query, context),
                
            # Project analysis tools
            'bb7_analyze_project_structure': lambda max_depth=3, include_hidden=False: 
                self.analyze_project_structure(max_depth, include_hidden),
                
            'bb7_get_project_dependencies': self.get_project_dependencies,
            
            'bb7_get_recent_changes': lambda days=7: 
                self.get_recent_changes(days)
        }


# For standalone testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    auto_tool = AutoTool()
    
    # Test auto-activation tools
    print("=== Workspace Context Loading ===")
    print(auto_tool.workspace_context_loader())
    
    print("\n=== Available Capabilities ===")
    print(auto_tool.show_available_capabilities())
    
    print("\n=== Auto Session Resume ===")
    print(auto_tool.auto_session_resume(user_intent="debugging authentication issues"))
    
    print("\n=== Intelligent Tool Guide ===")
    print(auto_tool.intelligent_tool_guide("I need to analyze error logs and save findings to memory"))
    
    print("\n=== Analyze Project Structure ===")
    print(auto_tool.analyze_project_structure())
    
    print("\n=== Get Project Dependencies ===")
    print(auto_tool.get_project_dependencies())
    
    print("\n=== Get Recent Changes ===")
    print(auto_tool.get_recent_changes())
