#!/usr/bin/env python3
"""
MCP Server - Model Context Protocol Server Implementation
Complete implementation with 55+ tools for advanced AI-human collaboration

Features:
- Persistent memory across sessions
- File operations with comprehensive support
- Shell & system tools with secure execution
- Web tools for content fetching and search
- Session management with cognitive tracking
- Visual automation and screen interaction
- Enhanced code analysis with CFA, DFA, type inference
- Secure Python execution with sandboxing
- Real-time tool registration and management

Architecture:
- Modular tool system with dynamic loading
- Cross-platform compatibility (Windows, Linux, macOS)
- Resource monitoring and security controls
- Comprehensive audit logging
- MCP standard compliance
"""

import argparse
import json
import logging
import os
import re
import sys
import time
import traceback
import threading
import importlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union
import asyncio
from dataclasses import asdict


class MCPServer:
    """Model Context Protocol Server with comprehensive tool ecosystem"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Server state
        self.tools = {}
        self.tool_modules = {}
        self.server_info = {
            "name": "Advanced MCP Server",
            "version": "2.1.0",
            "description": "Comprehensive AI-Human Collaboration Platform",
            "capabilities": [
                "memory", "files", "shell", "web", "sessions", 
                "visual", "terminal", "auto", "code_analysis"
            ],
            "total_tools": 0,
            "startup_time": time.time()
        }
        
        # Initialize data directory
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)
        
        # Performance monitoring
        self.performance_metrics = {
            "tool_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "average_response_time": 0,
            "last_activity": time.time()
        }
        
        # Comprehensive Tool Registry for AI Guidance
        self.tool_registry = {            "auto_activation": [
                {
                    "name": "bb7_workspace_context_loader",
                    "description": "🚀 ALWAYS RUN FIRST: Automatically loads relevant project context, active sessions, recent memories, and current workspace state. Essential for understanding where we left off and maintaining seamless continuity across coding sessions.",
                    "category": "auto_activation",
                    "priority": "critical",
                    "when_to_use": ["session_start", "context_needed", "resuming_work", "conversation_start"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "include_recent_memories": {
                                "type": "boolean",
                                "default": True,
                                "description": "Load recent memory entries related to current workspace"
                            },
                            "include_active_sessions": {
                                "type": "boolean", 
                                "default": True,
                                "description": "Check for and resume active development sessions"
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "bb7_show_available_capabilities",
                    "description": "📋 Display comprehensive overview of all available MCP tools and current system capabilities. Use when user seems unaware of available functionality, when they ask 'what can you do?', or at the start of complex tasks to remind yourself of available tools.",
                    "category": "auto_activation",
                    "priority": "high",
                    "when_to_use": ["capability_inquiry", "tool_discovery", "complex_task_start", "user_confusion"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "category": {
                                "type": "string",
                                "enum": ["all", "memory", "files", "shell", "web", "sessions", "visual", "terminal"],
                                "description": "Filter capabilities by category"
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "bb7_auto_session_resume",
                    "description": "🔄 Intelligent session continuity manager. Automatically detects interrupted work, resumes the most relevant active session, or suggests starting a new session based on workspace context and user intent. Critical for eliminating 'cold start' problems.",
                    "category": "auto_activation",
                    "priority": "high",
                    "when_to_use": ["interrupted_work", "session_continuity", "context_recovery", "resuming_development"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "workspace_path": {
                                "type": "string",
                                "description": "Current workspace path for context"
                            },
                            "user_intent": {
                                "type": "string", 
                                "description": "Brief description of what user wants to accomplish"
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "bb7_intelligent_tool_guide",
                    "description": "🧠 AI-powered tool recommendation engine. Analyzes user intent and suggests optimal tool workflows. Use when user requests are complex or when you need guidance on tool selection.",
                    "category": "auto_activation",
                    "priority": "medium",
                    "when_to_use": ["complex_requests", "tool_selection", "workflow_planning", "optimization"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "user_query": {
                                "type": "string",
                                "description": "User's request or question"
                            },
                            "context": {
                                "type": "string",
                                "description": "Current context or situation"
                            }
                        },
                        "required": ["user_query"]
                    }
                },
                {
                    "name": "analyze_project_structure",
                    "description": "📊 Comprehensive project analysis including file structure, dependencies, and architecture insights. Use when starting work on new projects or when architectural understanding is needed.",
                    "category": "auto_activation",
                    "priority": "medium",
                    "when_to_use": ["new_project", "architecture_analysis", "codebase_understanding", "onboarding"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string",
                                "description": "Path to project root"
                            },
                            "analysis_depth": {
                                "type": "string",
                                "enum": ["shallow", "medium", "deep"],
                                "default": "medium"
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "get_project_dependencies",
                    "description": "📦 Analyze and list project dependencies, package.json, requirements.txt, etc. Use when understanding project setup or troubleshooting dependency issues.",
                    "category": "auto_activation",
                    "priority": "medium",
                    "when_to_use": ["dependency_analysis", "setup_issues", "environment_check", "build_problems"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "project_path": {
                                "type": "string",
                                "description": "Path to project root"
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "get_recent_changes",
                    "description": "🔄 Get recent git changes, modified files, and development activity. Use when understanding recent work or catching up on project changes.",
                    "category": "auto_activation",
                    "priority": "medium",
                    "when_to_use": ["recent_changes", "git_history", "catch_up", "change_analysis"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "days": {
                                "type": "integer",
                                "default": 7,
                                "description": "Number of days to look back"
                            }
                        },
                        "required": []
                    }
                }
            ],            "memory": [
                {
                    "name": "bb7_memory_store",
                    "description": "💾 Store critical information in persistent global memory that survives across ALL coding sessions. Use for: project context, important decisions, architectural insights, user preferences, recurring issues, learning patterns, and any context that should NEVER be lost. Essential for building long-term collaborative intelligence.",
                    "category": "memory",
                    "priority": "critical",
                    "when_to_use": ["important_decisions", "project_context", "user_preferences", "architectural_insights", "lessons_learned"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string", 
                                "description": "Unique identifier - use hierarchical naming like 'project:myapp:architecture' or 'user:preferences:coding_style'"
                            },
                            "value": {
                                "type": "string",
                                "description": "The information to store - can be text, JSON, insights, or any contextual data"
                            }
                        },
                        "required": ["key", "value"]
                    }
                },
                {
                    "name": "bb7_memory_retrieve",
                    "description": "🔍 Retrieve stored context from persistent memory. Use frequently to maintain continuity, recall previous decisions, understand project history, and avoid asking user to repeat information they've already provided.",
                    "category": "memory",
                    "priority": "high",
                    "when_to_use": ["context_recall", "decision_history", "project_continuity", "preference_lookup"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "The memory key to retrieve"
                            }
                        },
                        "required": ["key"]
                    }
                },
                {
                    "name": "bb7_memory_list",
                    "description": "📚 Browse available memory keys to discover stored context. Use when you need to understand what information is available, explore project history, or find relevant stored insights. Great for context discovery.",
                    "category": "memory",
                    "priority": "medium",
                    "when_to_use": ["context_discovery", "memory_exploration", "available_info", "knowledge_audit"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "prefix": {
                                "type": "string",
                                "description": "Filter keys by prefix (e.g., 'project:' or 'user:')"
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "bb7_memory_delete",
                    "description": "🗑️ Remove outdated or incorrect information from memory. Use when context has changed, decisions have been reversed, or information is no longer relevant.",
                    "category": "memory",
                    "priority": "low",
                    "when_to_use": ["outdated_info", "context_changed", "cleanup", "incorrect_data"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "key": {
                                "type": "string",
                                "description": "Memory key to delete"
                            }
                        },
                        "required": ["key"]
                    }
                },                {
                    "name": "bb7_memory_stats",
                    "description": "📊 Get overview of memory usage, storage patterns, and data insights. Useful for understanding the scope of stored context and managing memory efficiently.",
                    "category": "memory",
                    "priority": "low",
                    "when_to_use": ["memory_analysis", "storage_overview", "usage_stats", "cleanup_planning"],
                    "input_schema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            ],
            "sessions": [
                {
                    "name": "start_session",
                    "description": "🎯 Begin a new cognitive development session with goal tracking, episodic memory, and workflow recording. Use when starting significant work, tackling new problems, or beginning focused development sessions. Creates structured memory for complex tasks.",
                    "category": "sessions",
                    "priority": "high",
                    "when_to_use": ["new_project", "complex_task", "development_session", "focused_work"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "goal": {
                                "type": "string",
                                "description": "Clear objective for this session"
                            },
                            "context": {
                                "type": "string",
                                "description": "Background context or current situation"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Categorization tags for the session"
                            }
                        },
                        "required": ["goal"]
                    }
                },
                {
                    "name": "log_event",
                    "description": "📝 Record significant events, decisions, discoveries, or problems in the current session timeline. Use to build episodic memory of development process, track decision rationale, and create searchable development history.",
                    "category": "sessions",
                    "priority": "medium",
                    "when_to_use": ["important_events", "decisions", "discoveries", "problems", "milestones"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "event_type": {
                                "type": "string",
                                "description": "Type: 'decision', 'discovery', 'problem', 'solution', 'insight'"
                            },
                            "description": {
                                "type": "string",
                                "description": "What happened and why it's significant"
                            },
                            "details": {
                                "type": "object",
                                "description": "Additional structured information"
                            }
                        },
                        "required": ["event_type", "description"]
                    }
                },
                {
                    "name": "capture_insight",
                    "description": "💡 Record semantic insights, architectural understanding, or conceptual breakthroughs. Use when you or the user gain important understanding about the codebase, design patterns, or problem domain. Builds conceptual knowledge base.",
                    "category": "sessions",
                    "priority": "medium",
                    "when_to_use": ["insights", "understanding", "breakthroughs", "learning", "patterns"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "insight": {
                                "type": "string",
                                "description": "The key insight or understanding"
                            },
                            "concept": {
                                "type": "string", 
                                "description": "Main concept this relates to"
                            },
                            "relationships": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Related concepts or dependencies"
                            }
                        },
                        "required": ["insight", "concept"]
                    }
                },
                {
                    "name": "record_workflow",
                    "description": "⚙️ Document successful workflows, processes, or step-by-step procedures for future reuse. Use when you discover effective approaches, solve complex problems, or establish repeatable processes. Builds procedural knowledge.",
                    "category": "sessions",
                    "priority": "medium",
                    "when_to_use": ["successful_workflows", "processes", "procedures", "solutions", "patterns"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "workflow_name": {
                                "type": "string",
                                "description": "Descriptive name for the workflow"
                            },
                            "steps": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Ordered list of steps"
                            },
                            "context": {
                                "type": "string",
                                "description": "When and how to use this workflow"
                            }
                        },
                        "required": ["workflow_name", "steps"]
                    }
                },
                {
                    "name": "update_focus",
                    "description": "🎯 Update current attention focus and energy state. Use when switching contexts, changing priorities, or when user's focus shifts. Helps maintain awareness of current cognitive state and priorities.",
                    "category": "sessions",
                    "priority": "low",
                    "when_to_use": ["context_switch", "priority_change", "focus_shift", "energy_tracking"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "focus_areas": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Current areas of focus and attention"
                            },
                            "energy_level": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "default": "medium"
                            },
                            "momentum": {
                                "type": "string", 
                                "enum": ["starting", "building", "flowing", "slowing"],
                                "default": "steady"
                            }
                        },
                        "required": ["focus_areas"]
                    }
                },
                {
                    "name": "pause_session",
                    "description": "⏸️ Pause current session with state preservation. Use when taking breaks, switching tasks, or ending work sessions. Captures environment state for seamless resumption.",
                    "category": "sessions",
                    "priority": "medium",
                    "when_to_use": ["break_time", "task_switch", "session_end", "interruption"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "reason": {
                                "type": "string",
                                "description": "Why the session is being paused"
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "resume_session",
                    "description": "▶️ Resume a previously paused session with full context restoration. Use when continuing interrupted work or returning to previous tasks. Provides seamless continuity.",
                    "category": "sessions",
                    "priority": "medium",
                    "when_to_use": ["resume_work", "continue_task", "context_restoration", "session_continuation"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session ID to resume"
                            }
                        },
                        "required": ["session_id"]
                    }
                },
                {
                    "name": "list_sessions",
                    "description": "📋 View all development sessions with status and context. Use to understand work history, find interrupted tasks, or choose which session to resume.",
                    "category": "sessions",
                    "priority": "low",
                    "when_to_use": ["session_review", "work_history", "interrupted_tasks", "session_selection"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "enum": ["active", "paused", "completed"]
                            },
                            "limit": {
                                "type": "integer",
                                "default": 20
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "get_session_summary",
                    "description": "📊 Get detailed summary of specific session including events, insights, and outcomes. Use to understand context of previous work or communicate progress.",
                    "category": "sessions",
                    "priority": "low",
                    "when_to_use": ["session_analysis", "progress_review", "context_understanding", "reporting"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "session_id": {
                                "type": "string",
                                "description": "Session to summarize"
                            }
                        },
                        "required": ["session_id"]
                    }
                }
            ],
            "files": [
                {
                    "name": "read_file",
                    "description": "📖 Read complete contents of any file on the system. Use for understanding code, reviewing configurations, analyzing logs, or accessing any text-based content. Supports all text encodings.",
                    "category": "files",
                    "priority": "high",
                    "when_to_use": ["code_review", "file_analysis", "config_check", "log_reading", "documentation"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Full or relative path to file"
                            }
                        },
                        "required": ["path"]
                    }
                },
                {
                    "name": "write_file",
                    "description": "✍️ Create or overwrite files with new content. Use for generating code, creating documentation, saving configurations, or any file creation task. Creates directories as needed.",
                    "category": "files",
                    "priority": "high",
                    "when_to_use": ["file_creation", "code_generation", "documentation", "config_save", "script_creation"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Target file path"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to write"
                            }
                        },
                        "required": ["path", "content"]
                    }
                },
                {
                    "name": "append_file",
                    "description": "➕ Add content to end of existing file or create new file. Use for logging, adding to existing code, or incremental file building.",
                    "category": "files",
                    "priority": "medium",
                    "when_to_use": ["logging", "incremental_updates", "file_extension", "append_content"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Target file path"
                            },
                            "content": {
                                "type": "string",
                                "description": "Content to append"
                            }
                        },
                        "required": ["path", "content"]
                    }
                },
                {
                    "name": "list_directory",
                    "description": "📂 List directory contents with detailed file information. Use for exploring project structure, understanding codebases, or finding files. Shows sizes, timestamps, and file types.",
                    "category": "files",
                    "priority": "medium",
                    "when_to_use": ["directory_exploration", "project_structure", "file_discovery", "codebase_navigation"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Directory path to list"
                            }
                        },
                        "required": ["path"]
                    }
                },
                {
                    "name": "get_file_info",
                    "description": "ℹ️ Get detailed information about specific file or directory including size, timestamps, permissions, and type analysis. Use for understanding file characteristics.",
                    "category": "files",
                    "priority": "low",
                    "when_to_use": ["file_analysis", "metadata_check", "permissions", "file_properties"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Path to analyze"
                            }
                        },
                        "required": ["path"]
                    }
                },
                {
                    "name": "search_files",
                    "description": "🔍 Search for files matching patterns in directory trees. Use for finding specific files, locating code patterns, or exploring large codebases. Supports glob patterns.",
                    "category": "files",
                    "priority": "medium",
                    "when_to_use": ["file_discovery", "pattern_search", "codebase_exploration", "file_finding"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "directory": {
                                "type": "string",
                                "description": "Root directory to search"
                            },
                            "pattern": {
                                "type": "string",
                                "description": "Glob pattern (e.g., '*.py', '**/*.json')"
                            },
                            "max_results": {
                                "type": "integer",
                                "default": 50
                            }
                        },
                        "required": ["directory", "pattern"]
                    }
                }
            ],
            "shell": [
                {
                    "name": "run_command",
                    "description": "⚡ Execute shell commands with full output capture. Use for running builds, tests, git operations, system commands, or any command-line tasks. Provides detailed execution results.",
                    "category": "shell",
                    "priority": "high",
                    "when_to_use": ["builds", "tests", "git_ops", "system_commands", "installation"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Shell command to execute"
                            },
                            "working_dir": {
                                "type": "string",
                                "description": "Working directory for command"
                            },
                            "timeout": {
                                "type": "integer",
                                "default": 30,
                                "description": "Command timeout in seconds"
                            }
                        },
                        "required": ["command"]
                    }
                },
                {
                    "name": "run_script",
                    "description": "📜 Execute scripts from content strings. Supports bash, python, javascript, and powershell. Use for running complex multi-line scripts or generated code without creating temporary files.",
                    "category": "shell",
                    "priority": "medium",
                    "when_to_use": ["script_execution", "code_testing", "automation", "multi_line_commands"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "script_content": {
                                "type": "string",
                                "description": "Script content to execute"
                            },
                            "script_type": {
                                "type": "string",
                                "enum": ["bash", "python", "javascript", "powershell"],
                                "default": "bash"
                            },
                            "working_dir": {
                                "type": "string",
                                "description": "Working directory"
                            }
                        },
                        "required": ["script_content"]
                    }
                },
                {
                    "name": "get_environment",
                    "description": "🌍 Get comprehensive environment information including PATH, user context, installed tools, and development environment details. Use for troubleshooting, setup verification, or environment analysis.",
                    "category": "shell",
                    "priority": "low",
                    "when_to_use": ["environment_check", "troubleshooting", "setup_verification", "tool_discovery"],
                    "input_schema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "list_processes",
                    "description": "🔄 List running system processes with CPU and memory usage. Use for system monitoring, finding processes, or understanding system state.",
                    "category": "shell",
                    "priority": "low",
                    "when_to_use": ["system_monitoring", "process_discovery", "performance_analysis", "debugging"],
                    "input_schema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "kill_process",
                    "description": "🛑 Terminate processes by PID. Use carefully for stopping hung processes or cleaning up background tasks. Includes safety checks.",
                    "category": "shell",
                    "priority": "low",
                    "when_to_use": ["process_termination", "cleanup", "hung_processes", "system_management"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "process_id": {
                                "type": "integer",
                                "description": "Process ID to terminate"
                            }
                        },
                        "required": ["process_id"]
                    }
                },
                {
                    "name": "get_system_info",
                    "description": "💻 Get comprehensive system information including hardware, OS, CPU, memory, disk, and network details. Use for system analysis, troubleshooting, or environment documentation.",
                    "category": "shell",
                    "priority": "low",
                    "when_to_use": ["system_analysis", "hardware_info", "troubleshooting", "documentation"],
                    "input_schema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            ],
            "web": [
                {
                    "name": "fetch_url",
                    "description": "🌐 Fetch content from URLs via HTTP. Use for accessing documentation, APIs, downloading resources, or gathering web-based information. Supports headers and timeouts.",
                    "category": "web",
                    "priority": "medium",
                    "when_to_use": ["documentation", "api_access", "web_resources", "content_fetch", "research"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to fetch"
                            },
                            "headers": {
                                "type": "object",
                                "description": "Optional HTTP headers"
                            },
                            "timeout": {
                                "type": "integer",
                                "default": 30
                            }
                        },
                        "required": ["url"]
                    }
                },
                {
                    "name": "download_file",
                    "description": "⬇️ Download files from URLs to local filesystem. Use for fetching resources, documentation, or any web-based assets needed for development.",
                    "category": "web",
                    "priority": "medium",
                    "when_to_use": ["file_download", "resource_fetch", "asset_acquisition", "documentation"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to download from"
                            },
                            "filename": {
                                "type": "string",
                                "description": "Local path to save file"
                            },
                            "headers": {
                                "type": "object",
                                "description": "Optional HTTP headers"
                            }
                        },
                        "required": ["url", "filename"]
                    }
                },
                {
                    "name": "check_url_status",
                    "description": "🔍 Check URL accessibility and get response headers. Use for testing APIs, verifying links, or troubleshooting web connectivity.",
                    "category": "web",
                    "priority": "low",
                    "when_to_use": ["url_testing", "api_testing", "link_verification", "connectivity_check"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to check"
                            }
                        },
                        "required": ["url"]
                    }
                },
                {
                    "name": "search_web",
                    "description": "🔎 Search the web using DuckDuckGo for quick information lookup. Use when you need current information, documentation links, or research assistance.",
                    "category": "web",
                    "priority": "medium",
                    "when_to_use": ["information_search", "research", "documentation_lookup", "current_info"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "num_results": {
                                "type": "integer",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "extract_links",
                    "description": "🔗 Extract all links from webpages in structured format. Use for analyzing websites, finding documentation links, or building link repositories.",
                    "category": "web",
                    "priority": "low",
                    "when_to_use": ["link_extraction", "website_analysis", "documentation_discovery", "scraping"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to extract links from"
                            }
                        },
                        "required": ["url"]
                    }
                }
            ],
            "visual": [
                {
                    "name": "bb7_screen_capture",
                    "description": "📸 VISUAL PARTNERSHIP: Take screenshots for debugging, UI analysis, and visual understanding. Enables AI to see exactly what you see! Use for error screenshots, UI feedback, or visual documentation.",
                    "category": "visual",
                    "priority": "medium",
                    "when_to_use": ["debugging", "ui_analysis", "visual_feedback", "documentation", "error_capture"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "monitor": {
                                "type": "integer",
                                "default": 0,
                                "description": "Monitor to capture (0=primary, -1=all)"
                            },
                            "region": {
                                "type": "object",
                                "description": "Specific region {x, y, width, height}"
                            },
                            "save_path": {
                                "type": "string",
                                "description": "Optional file save path"
                            },
                            "format": {
                                "type": "string",
                                "enum": ["png", "jpg", "base64"],
                                "default": "base64"
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "bb7_keyboard_input",
                    "description": "⌨️ AUTOMATION: Send keystrokes and keyboard shortcuts for automation and UI interaction. Type alongside the user, trigger shortcuts, or automate repetitive input tasks.",
                    "category": "visual",
                    "priority": "medium",
                    "when_to_use": ["automation", "ui_interaction", "shortcuts", "text_input", "testing"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "Text to type"
                            },
                            "keys": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Special keys to press"
                            },
                            "hotkey": {
                                "type": "string",
                                "description": "Hotkey combination (e.g., 'ctrl+c')"
                            },
                            "delay": {
                                "type": "number",
                                "default": 0.1
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "bb7_mouse_control",
                    "description": "🖱️ AUTOMATION: Control mouse for clicking, dragging, and UI interaction. Click buttons, navigate interfaces, or automate mouse-based tasks.",
                    "category": "visual",
                    "priority": "medium",
                    "when_to_use": ["ui_automation", "clicking", "dragging", "interface_navigation", "testing"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["click", "double_click", "right_click", "drag", "scroll", "move"]
                            },
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                            "button": {
                                "type": "string",
                                "enum": ["left", "right", "middle"],
                                "default": "left"
                            }
                        },
                        "required": ["action"]
                    }
                },
                {
                    "name": "bb7_window_manager",
                    "description": "🪟 WORKSPACE AWARENESS: Manage windows and understand workspace layout. List windows, switch focus, resize, or organize the development environment.",
                    "category": "visual",
                    "priority": "low",
                    "when_to_use": ["window_management", "workspace_organization", "focus_control", "layout_management"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["list", "focus", "minimize", "maximize", "close", "move", "resize"]
                            },
                            "window_title": {
                                "type": "string",
                                "description": "Target window title"
                            }
                        },
                        "required": ["action"]
                    }
                },
                {
                    "name": "bb7_clipboard_manage",
                    "description": "📋 DATA EXCHANGE: Read/write clipboard for seamless data sharing between AI and human. Perfect for code snippets, URLs, or any text exchange.",
                    "category": "visual",
                    "priority": "medium",
                    "when_to_use": ["data_exchange", "clipboard_access", "text_sharing", "copy_paste", "data_transfer"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "action": {
                                "type": "string",
                                "enum": ["read", "write", "clear", "history"]
                            },
                            "text": {
                                "type": "string",
                                "description": "Text to write to clipboard"
                            }
                        },
                        "required": ["action"]
                    }
                }
            ],
            "terminal": [
                {
                    "name": "bb7_terminal_status",
                    "description": "🖥️ VS CODE INTEGRATION: Get current terminal status, environment, and integration state. Understand the active development context within VS Code.",
                    "category": "terminal",
                    "priority": "low",
                    "when_to_use": ["terminal_check", "environment_status", "integration_check", "context_awareness"],
                    "input_schema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "bb7_terminal_run_command",
                    "description": "⚡ VS CODE TERMINAL: Run commands in current VS Code terminal context with full state awareness. Maintains directory context and environment continuity.",
                    "category": "terminal",
                    "priority": "high",
                    "when_to_use": ["vscode_commands", "terminal_execution", "context_aware_commands", "development_tasks"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Command to execute"
                            },
                            "change_directory": {
                                "type": "boolean",
                                "default": True
                            },
                            "timeout": {
                                "type": "integer",
                                "default": 30
                            }
                        },
                        "required": ["command"]
                    }
                },
                {
                    "name": "bb7_terminal_history",
                    "description": "📜 VS CODE TERMINAL: Get recent command history from VS Code terminal. Use for understanding recent development activities or repeating commands.",
                    "category": "terminal",
                    "priority": "low",
                    "when_to_use": ["command_history", "recent_activities", "command_repeat", "development_context"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "limit": {
                                "type": "integer",
                                "default": 10
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "bb7_terminal_environment",
                    "description": "🌍 VS CODE TERMINAL: Get environment variables and context from VS Code terminal. Use for understanding the development environment setup.",
                    "category": "terminal",
                    "priority": "low",
                    "when_to_use": ["environment_check", "variable_inspection", "setup_verification", "debugging"],
                    "input_schema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "bb7_terminal_cd",
                    "description": "📁 VS CODE TERMINAL: Change directory with context tracking. Navigate filesystem while maintaining awareness of location and context.",
                    "category": "terminal",
                    "priority": "medium",
                    "when_to_use": ["directory_navigation", "context_tracking", "filesystem_navigation", "project_navigation"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Directory path to change to"
                            }
                        },
                        "required": ["path"]
                    }
                },
                {
                    "name": "bb7_terminal_which",
                    "description": "🔍 VS CODE TERMINAL: Find executables in PATH from VS Code terminal context. Use for checking tool availability and executable locations.",
                    "category": "terminal",
                    "priority": "low",
                    "when_to_use": ["executable_location", "tool_availability", "path_check", "dependency_check"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "Command/executable to locate"
                            }
                        },
                        "required": ["command"]
                    }
                }
            ],
            "code_analysis": [
                {
                    "name": "bb7_analyze_code_complete",
                    "description": "🔬 ENHANCED CODE ANALYSIS: Comprehensive code analysis with Control Flow Analysis (CFA), Data Flow Analysis (DFA), type inference, complexity metrics, and security auditing. Use for deep code understanding and quality assessment.",
                    "category": "code_analysis",
                    "priority": "high",
                    "when_to_use": ["code_review", "quality_assessment", "security_audit", "complexity_analysis", "refactoring"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "Path to code file to analyze"
                            },
                            "analysis_types": {
                                "type": "array",
                                "items": {"type": "string"},
                                "default": ["syntax", "complexity", "security", "type_inference"],
                                "description": "Types of analysis to perform"
                            }
                        },
                        "required": ["file_path"]
                    }
                },
                {
                    "name": "bb7_python_execute_secure",
                    "description": "🐍 SECURE EXECUTION: Execute Python code in a secure, sandboxed environment with resource limits and safety checks. Use for testing code snippets or running analysis safely.",
                    "category": "code_analysis",
                    "priority": "medium",
                    "when_to_use": ["code_testing", "snippet_execution", "safe_evaluation", "python_analysis"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "Python code to execute"
                            },
                            "timeout": {
                                "type": "integer",
                                "default": 10,
                                "description": "Execution timeout in seconds"
                            },
                            "capture_output": {
                                "type": "boolean",
                                "default": True
                            }
                        },
                        "required": ["code"]
                    }
                },
                {
                    "name": "bb7_security_audit",
                    "description": "🔒 SECURITY ANALYSIS: Comprehensive security audit for code including vulnerability detection, security best practices checking, and risk assessment. Use for security reviews and compliance.",
                    "category": "code_analysis",
                    "priority": "high",
                    "when_to_use": ["security_review", "vulnerability_scan", "compliance_check", "risk_assessment"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "target_path": {
                                "type": "string",
                                "description": "Path to file or directory to audit"                            },
                            "security_level": {
                                "type": "string",
                                "enum": ["basic", "standard", "strict"],
                                "default": "standard"
                            }
                        },
                        "required": ["target_path"]
                    }
                }
            ]
        }
          # Register all tools
        self.register_tools()
        
        self.logger.info(f"MCP Server initialized with {len(self.tools)} tools")
    
    def setup_logging(self):
        """Configure comprehensive logging"""
        log_file = self.data_dir / "mcp_server.log" if hasattr(self, 'data_dir') else Path("data/mcp_server.log")
        log_file.parent.mkdir(exist_ok=True)
        
        # Configure logging with file and stderr output (NOT stdout for MCP compliance)
        logging.basicConfig(
            level=logging.DEBUG if self.debug else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stderr)  # Use stderr instead of stdout for MCP compliance
            ]
        )
        
        # Suppress noisy loggers
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
    
    def get_tool_guidance(self, user_query: str = "", context: str = "") -> Dict[str, Any]:
        """Analyze user query and provide intelligent tool recommendations"""
        guidance = {
            "recommended_tools": [],
            "primary_categories": [],
            "workflow_suggestions": [],
            "context_tips": []
        }
        
        query_lower = user_query.lower()
        context_lower = context.lower()
        combined = f"{query_lower} {context_lower}"
        
        # Analyze intent and recommend tools
        intent_patterns = {
            "memory": ["remember", "store", "save", "recall", "context", "history", "previous"],
            "files": ["file", "read", "write", "create", "edit", "document", "code", "script"],
            "shell": ["run", "execute", "command", "build", "test", "install", "deploy"],
            "web": ["download", "fetch", "url", "api", "documentation", "search", "web"],
            "sessions": ["start", "begin", "track", "session", "goal", "workflow", "project"],
            "visual": ["screenshot", "capture", "see", "visual", "ui", "interface", "display"],
            "analysis": ["analyze", "debug", "inspect", "understand", "review", "audit"]
        }
        
        detected_intents = []
        for category, patterns in intent_patterns.items():
            if any(pattern in combined for pattern in patterns):
                detected_intents.append(category)
                guidance["primary_categories"].append(category)
        
        # Always recommend starting with context loading for new sessions
        if not context or "session_start" in combined:
            guidance["recommended_tools"].append({
                "name": "workspace_context_loader",
                "priority": "CRITICAL",
                "reason": "Load workspace context and active sessions"
            })
        
        # Add category-specific recommendations
        for category in detected_intents:
            if category in self.tool_registry:
                top_tools = sorted(
                    self.tool_registry[category], 
                    key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x.get("priority", "low"), 3)
                )[:2]  # Top 2 tools per category
                
                for tool in top_tools:
                    guidance["recommended_tools"].append({
                        "name": tool["name"],
                        "category": category,
                        "priority": tool.get("priority", "medium").upper(),
                        "reason": tool["description"][:100] + "..."
                    })
        
        # Add workflow suggestions
        if "memory" in detected_intents:
            guidance["workflow_suggestions"].append("Consider using memory_store to save important context")
        if "files" in detected_intents and "analysis" in detected_intents:
            guidance["workflow_suggestions"].append("Use read_file first, then analyze content")
        if "sessions" in detected_intents:
            guidance["workflow_suggestions"].append("Start with start_session to track your work")
        
        guidance["context_tips"] = [
            "Use memory tools to maintain context across conversations",
            "Start sessions for complex multi-step tasks",
            "Capture insights and decisions for future reference",
            "Use visual tools when UI debugging is needed"
        ]
        
        return guidance
    
    def get_tool_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all tools in a specific category with their full registry information"""
        return self.tool_registry.get(category, [])
    
    def find_tool_by_intent(self, intent: str) -> List[Dict[str, Any]]:
        """Find tools that match a specific usage intent"""
        matching_tools = []
        
        for category, tools in self.tool_registry.items():
            for tool in tools:
                when_to_use = tool.get("when_to_use", [])
                if any(intent.lower() in use_case.lower() for use_case in when_to_use):
                    matching_tools.append(tool)
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        matching_tools.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))
        
        return matching_tools
    
    def register_tools(self):
        """Register all available MCP tools from modules"""
        try:
            self.logger.info("Starting tool registration...")            # Import and register all tool modules
            tool_modules = [
                ('memory_tool', 'EnhancedMemoryTool'),
                ('memory_interconnect', 'MemoryInterconnectionEngine'),
                ('file_tool', 'FileTool'),
                ('shell_tool', 'ShellTool'),
                ('web_tool', 'WebTool'),
                ('session_manager_tool', 'EnhancedSessionTool'),
                ('visual_tool', 'VisualTool'),
                ('vscode_terminal_tool', 'VSCodeTerminalTool'),
                ('project_context_tool', 'ProjectContextTool'),
                ('auto_tool_module', 'AutoTool'),
                ('enhanced_code_analysis_tool', 'CodeAnalysisTool')
            ]
            
            for module_name, class_name in tool_modules:
                try:
                    self.logger.debug(f"Loading {module_name}...")
                    module = __import__(f'tools.{module_name}', fromlist=[class_name])
                    tool_class = getattr(module, class_name)
                    tool_instance = tool_class()
                    
                    # Get tools from the instance
                    if hasattr(tool_instance, 'get_tools'):
                        module_tools = tool_instance.get_tools()
                        self.tools.update(module_tools)
                        self.tool_modules[module_name] = tool_instance
                        self.logger.info(f"Loaded {len(module_tools)} tools from {module_name}")
                    else:
                        self.logger.warning(f"{module_name} does not have get_tools() method")
                        
                except ImportError as e:
                    self.logger.error(f"Failed to import {module_name}: {e}")
                except Exception as e:
                    self.logger.error(f"Failed to load {module_name}: {e}")
            
            # Update server info
            self.server_info["total_tools"] = len(self.tools)
            
            # Log successful registration
            self.logger.info(f"Tool registration complete! {len(self.tools)} tools available")
            self.log_tool_summary()
            
        except Exception as e:
            self.logger.error(f"Critical error during tool registration: {e}")
            self.logger.error(traceback.format_exc())
    
    def log_tool_summary(self):
        """Log detailed summary of registered tools"""
        self.logger.info("=" * 80)
        self.logger.info("MCP SERVER TOOL INVENTORY")
        self.logger.info("=" * 80)
        
        # Group tools by prefix/category
        categories = {}
        for tool_name in self.tools.keys():
            if tool_name.startswith('bb7_'):
                category = tool_name.split('_')[1] if '_' in tool_name else 'misc'
            else:
                category = 'legacy'
            
            if category not in categories:
                categories[category] = []
            categories[category].append(tool_name)
        
        for category, tools in categories.items():
            self.logger.info(f"{category.upper()}: {len(tools)} tools")
            for tool in sorted(tools):
                self.logger.info(f"   - {tool}")
        
        self.logger.info("=" * 80)
        self.logger.info(f"TOTAL TOOLS REGISTERED: {len(self.tools)}")
        self.logger.info("=" * 80)
    
    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Call a tool with comprehensive error handling and monitoring"""
        start_time = time.time()
        self.performance_metrics["tool_calls"] += 1
        self.performance_metrics["last_activity"] = start_time
        
        try:
            if tool_name not in self.tools:
                available_tools = list(self.tools.keys())
                # Try to find similar tool names
                similar = [t for t in available_tools if tool_name.lower() in t.lower()]
                error_msg = f"Tool '{tool_name}' not found."
                if similar:
                    error_msg += f" Did you mean: {', '.join(similar[:3])}?"
                else:
                    error_msg += f" Available tools: {len(available_tools)} total"
                
                return {
                    "success": False,
                    "error": "TOOL_NOT_FOUND",
                    "message": error_msg,
                    "available_tools": available_tools[:10]  # Return first 10 for reference
                }
            
            self.logger.debug(f"Calling tool: {tool_name} with args: {kwargs}")
            
            # Call the tool function
            tool_func = self.tools[tool_name]
            if callable(tool_func):
                result = tool_func(**kwargs)
                
                # Ensure result is JSON serializable
                if isinstance(result, str):
                    formatted_result = {"success": True, "result": result}
                elif isinstance(result, dict):
                    formatted_result = result
                else:
                    formatted_result = {"success": True, "result": str(result)}
                
                execution_time = time.time() - start_time
                formatted_result["execution_time"] = round(execution_time, 3)
                
                self.performance_metrics["successful_calls"] += 1
                self.update_average_response_time(execution_time)
                
                self.logger.debug(f"Tool {tool_name} completed in {execution_time:.3f}s")
                return formatted_result
                
            else:
                return {
                    "success": False,
                    "error": "TOOL_NOT_CALLABLE",
                    "message": f"Tool '{tool_name}' is not a callable function"
                }
                
        except TypeError as e:
            # Handle parameter mismatches
            self.performance_metrics["failed_calls"] += 1
            error_msg = f"Parameter error for tool '{tool_name}': {str(e)}"
            self.logger.error(error_msg)
            
            return {
                "success": False,
                "error": "PARAMETER_ERROR",
                "message": error_msg,
                "provided_args": list(kwargs.keys())
            }
            
        except Exception as e:
            # Handle all other exceptions
            self.performance_metrics["failed_calls"] += 1
            error_msg = f"Tool '{tool_name}' execution failed: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            
            return {
                "success": False,
                "error": "EXECUTION_ERROR",
                "message": error_msg,
                "exception_type": type(e).__name__
            }
    
    def update_average_response_time(self, execution_time: float):
        """Update rolling average response time"""
        current_avg = self.performance_metrics["average_response_time"]
        total_calls = self.performance_metrics["successful_calls"]
        
        if total_calls == 1:
            self.performance_metrics["average_response_time"] = execution_time
        else:
            # Rolling average calculation
            self.performance_metrics["average_response_time"] = (
                (current_avg * (total_calls - 1) + execution_time) / total_calls
            )
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get comprehensive server information"""
        uptime = time.time() - self.server_info["startup_time"]
        
        return {
            **self.server_info,
            "uptime_seconds": round(uptime, 1),
            "performance_metrics": self.performance_metrics.copy(),
            "tool_count": len(self.tools),
            "available_tools": list(self.tools.keys()),
            "module_count": len(self.tool_modules),
            "loaded_modules": list(self.tool_modules.keys()),
            "registry_categories": list(self.tool_registry.keys()),
            "status": "operational"
        }
    
    def get_tool_list(self, category: Optional[str] = None) -> List[str]:
        """Get list of available tools, optionally filtered by category"""
        if category:
            if category.startswith('bb7_'):
                category = category[4:]  # Remove bb7_ prefix
            
            filtered_tools = [
                name for name in self.tools.keys() 
                if category.lower() in name.lower()
            ]
            return sorted(filtered_tools)
        
        return sorted(list(self.tools.keys()))
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific tool including registry data"""
        if tool_name not in self.tools:
            return {"error": f"Tool '{tool_name}' not found"}
        
        tool_func = self.tools[tool_name]
        
        # Find registry information
        registry_info = None
        for category, tools in self.tool_registry.items():
            for tool_data in tools:
                if tool_data["name"] == tool_name:
                    registry_info = tool_data
                    break
            if registry_info:
                break
        
        # Extract function signature information
        import inspect
        try:
            sig = inspect.signature(tool_func)
            parameters = {}
            for param_name, param in sig.parameters.items():
                param_info = {
                    "name": param_name,
                    "required": param.default == inspect.Parameter.empty,
                    "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "Any"
                }
                if param.default != inspect.Parameter.empty:
                    param_info["default"] = param.default
                parameters[param_name] = param_info
            
            tool_info = {
                "name": tool_name,
                "parameters": parameters,
                "docstring": tool_func.__doc__ or "No documentation available",
                "module": getattr(tool_func, '__module__', 'unknown'),
                "callable": True
            }
            
            # Add registry information if available
            if registry_info:
                tool_info.update({
                    "registry_description": registry_info.get("description", ""),
                    "category": registry_info.get("category", "unknown"),
                    "priority": registry_info.get("priority", "medium"),
                    "when_to_use": registry_info.get("when_to_use", []),
                    "input_schema": registry_info.get("input_schema", {})
                })
            
            return tool_info
            
        except Exception as e:
            return {
                "name": tool_name,
                "error": f"Could not inspect tool: {str(e)}",
                "callable": callable(tool_func),
                "registry_info": registry_info
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        try:
            # Test core functionality
            memory_test = self.call_tool("bb7_memory_stats") if "bb7_memory_stats" in self.tools else None
            file_test = self.call_tool("bb7_get_file_info", path=".") if "bb7_get_file_info" in self.tools else None
            
            health_status = {
                "server_healthy": True,
                "total_tools": len(self.tools),
                "registry_categories": len(self.tool_registry),
                "performance_metrics": self.performance_metrics.copy(),
                "uptime": time.time() - self.server_info["startup_time"],
                "test_results": {
                    "memory_tool": memory_test is not None and memory_test.get("success", False),
                    "file_tool": file_test is not None and file_test.get("success", False)
                },
                "timestamp": time.time()
            }
            
            return health_status
            
        except Exception as e:
            return {
                "server_healthy": False,
                "error": str(e),
                "timestamp": time.time()
            }
    
    def shutdown(self):
        """Graceful server shutdown"""
        self.logger.info("Initiating MCP Server shutdown...")
        
        try:
            # Save shutdown status
            shutdown_info = {
                "shutdown_time": time.time(),
                "final_metrics": self.performance_metrics.copy(),
                "total_uptime": time.time() - self.server_info["startup_time"],
                "total_tools": len(self.tools),
                "registry_categories": len(self.tool_registry)
            }
            
            shutdown_file = self.data_dir / "shutdown_status.json"
            with open(shutdown_file, 'w', encoding='utf-8') as f:
                json.dump(shutdown_info, f, indent=2)
            
            self.logger.info("MCP Server shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def start_interactive_mode(self):
        """Start interactive mode for testing and debugging"""
        print("MCP Server Interactive Mode")
        print("=" * 50)
        print(f"Server: {self.server_info['name']} v{self.server_info['version']}")
        print(f"Tools available: {len(self.tools)}")
        print(f"Registry categories: {len(self.tool_registry)}")
        print("\nCommands:")
        print("  list                    - List all tools")
        print("  info <tool_name>        - Get tool information")
        print("  call <tool_name> [args] - Call a tool")
        print("  guidance <query>        - Get tool recommendations")
        print("  category <name>         - List tools in category")
        print("  health                  - Server health check")
        print("  stats                   - Performance statistics")
        print("  quit                    - Exit interactive mode")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\nmcp> ").strip()
                if not user_input:
                    continue
                
                parts = user_input.split()
                command = parts[0].lower()
                
                if command == "quit":
                    break
                elif command == "list":
                    tools = self.get_tool_list()
                    print(f"\nAvailable tools ({len(tools)}):")
                    for i, tool in enumerate(tools, 1):
                        print(f"  {i:2}. {tool}")
                
                elif command == "info" and len(parts) > 1:
                    tool_name = parts[1]
                    info = self.get_tool_info(tool_name)
                    print(f"\nTool Info: {tool_name}")
                    print(json.dumps(info, indent=2))
                
                elif command == "guidance" and len(parts) > 1:
                    query = ' '.join(parts[1:])
                    guidance = self.get_tool_guidance(query)
                    print(f"\nTool Guidance for: '{query}'")
                    print(json.dumps(guidance, indent=2))
                
                elif command == "category" and len(parts) > 1:
                    category = parts[1]
                    tools = self.get_tool_by_category(category)
                    print(f"\nTools in category '{category}' ({len(tools)}):")
                    for tool in tools:
                        print(f"  - {tool['name']}: {tool['description'][:80]}...")
                
                elif command == "call" and len(parts) > 1:
                    tool_name = parts[1]
                    # Simple argument parsing (could be improved)
                    kwargs = {}
                    if len(parts) > 2:
                        try:
                            # Try to parse as JSON
                            args_str = ' '.join(parts[2:])
                            kwargs = json.loads(args_str)
                        except json.JSONDecodeError:
                            # Fallback to simple key=value parsing
                            for arg in parts[2:]:
                                if '=' in arg:
                                    key, value = arg.split('=', 1)
                                    kwargs[key] = value
                    
                    result = self.call_tool(tool_name, **kwargs)
                    print(f"\nResult:")
                    print(json.dumps(result, indent=2))
                
                elif command == "health":
                    health = self.health_check()
                    print(f"\nHealth Check:")
                    print(json.dumps(health, indent=2))
                
                elif command == "stats":
                    stats = self.get_server_info()
                    print(f"\nServer Statistics:")
                    print(json.dumps(stats, indent=2))
                
                else:
                    print(f"Unknown command: {command}")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("Goodbye!")


def handle_mcp_protocol(server):
    """Handle MCP JSON-RPC protocol communication via stdin/stdout"""
    server.logger.info("Starting MCP JSON-RPC protocol handler")
    
    try:
        while True:
            # Read JSON-RPC request from stdin
            line = sys.stdin.readline()
            if not line:
                break
                
            try:
                request = json.loads(line.strip())
                server.logger.info(f"Received request: {request.get('method', 'unknown')}")
                
                # Handle the request
                response = handle_jsonrpc_request(server, request)
                
                # Send response to stdout
                json.dump(response, sys.stdout)
                sys.stdout.write('\n')
                sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                server.logger.error(f"Invalid JSON received: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    },
                    "id": None
                }
                json.dump(error_response, sys.stdout)
                sys.stdout.write('\n')
                sys.stdout.flush()
                
            except Exception as e:
                server.logger.error(f"Error handling request: {e}")
                server.logger.error(traceback.format_exc())
                
    except Exception as e:
        server.logger.error(f"Protocol handler error: {e}")
        server.logger.error(traceback.format_exc())


def handle_jsonrpc_request(server, request):
    """Handle a JSON-RPC request and return response"""
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")
    
    try:
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "logging": {}
                    },
                    "serverInfo": {
                        "name": server.server_info["name"],
                        "version": server.server_info["version"]
                    }
                },
                "id": request_id
            }
            
        elif method == "tools/list":
            tools = []
            for tool_name, tool_func in server.tools.items():
                # Get tool schema if available
                tool_schema = {
                    "name": tool_name,
                    "description": getattr(tool_func, '__doc__', f"Tool: {tool_name}"),
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
                tools.append(tool_schema)
            
            return {
                "jsonrpc": "2.0",
                "result": {
                    "tools": tools
                },
                "id": request_id
            }
            
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            if tool_name not in server.tools:
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32602,
                        "message": f"Tool '{tool_name}' not found"
                    },
                    "id": request_id
                }
            
            try:
                # Call the tool
                result = server.call_tool(tool_name, **tool_args)
                
                return {
                    "jsonrpc": "2.0",
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": str(result)
                            }
                        ]
                    },
                    "id": request_id
                }
                
            except Exception as e:
                server.logger.error(f"Tool execution error: {e}")
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": f"Tool execution failed: {str(e)}"
                    },
                    "id": request_id
                }
        
        else:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                },
                "id": request_id
            }
            
    except Exception as e:
        server.logger.error(f"Request handling error: {e}")
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Internal error: {str(e)}"
            },
            "id": request_id
        }


def main():
    """Main entry point for MCP Server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Server - Advanced AI Collaboration Platform")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--interactive", action="store_true", help="Start in interactive mode")
    parser.add_argument("--health-check", action="store_true", help="Run health check and exit")
    parser.add_argument("--list-tools", action="store_true", help="List all tools and exit")
    parser.add_argument("--tool-info", type=str, help="Get info about specific tool and exit")
    parser.add_argument("--guidance", type=str, help="Get tool guidance for query and exit")
    
    args = parser.parse_args()
    
    # Create and initialize server
    server = MCPServer(debug=args.debug)
    
    try:
        if args.health_check:
            health = server.health_check()
            print(json.dumps(health, indent=2), file=sys.stderr)
            
        elif args.list_tools:
            tools = server.get_tool_list()
            print(f"Available tools ({len(tools)}):", file=sys.stderr)
            for tool in tools:
                print(f"  - {tool}", file=sys.stderr)
                
        elif args.tool_info:
            info = server.get_tool_info(args.tool_info)
            print(json.dumps(info, indent=2), file=sys.stderr)
            
        elif args.guidance:
            guidance = server.get_tool_guidance(args.guidance)
            print(json.dumps(guidance, indent=2), file=sys.stderr)
            
        elif args.interactive:
            server.start_interactive_mode()
            
        else:
            # Default: MCP JSON-RPC protocol mode
            # All logging goes to stderr, JSON-RPC messages to stdout
            info = server.get_server_info()
            server.logger.info("MCP Server Started in JSON-RPC protocol mode")
            server.logger.info(f"Name: {info['name']}")
            server.logger.info(f"Version: {info['version']}")
            server.logger.info(f"Tools: {info['tool_count']}")
            server.logger.info(f"Modules: {info['module_count']}")
            server.logger.info(f"Registry Categories: {info['registry_categories']}")
            server.logger.info("Ready for MCP JSON-RPC protocol connections")
            
            # Handle MCP protocol on stdin/stdout
            handle_mcp_protocol(server)
                
    except Exception as e:
        server.logger.error(f"Server error: {e}")
        server.logger.error(traceback.format_exc())
        
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()