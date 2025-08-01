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
        
        # Comprehensive Tool Registry for AI Guidance (flat dict, all tools by name)
        self.tool_registry = {
            "bb7_memory_analyze_entry": {
                "name": "bb7_memory_analyze_entry",
                "description": "Analyze a memory entry for key concepts, importance, and semantic connections. Use to extract insights and relationships from stored knowledge.",
                "category": "memory",
                "priority": "medium",
                "when_to_use": ["knowledge_extraction", "semantic_analysis", "insight_generation"],
                "input_schema": {"type": "object", "properties": {"key": {"type": "string"}, "value": {"type": "string"}, "source": {"type": "string", "default": "memory"}}, "required": ["key", "value"]}
            },
            "bb7_memory_intelligent_search": {
                "name": "bb7_memory_intelligent_search",
                "description": "Search memories using semantic similarity and concept matching. Use for advanced context recall and finding related information.",
                "category": "memory",
                "priority": "high",
                "when_to_use": ["semantic_search", "context_recall", "information_retrieval"],
                "input_schema": {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer", "default": 10}}, "required": ["query"]}
            },
            "bb7_memory_get_insights": {
                "name": "bb7_memory_get_insights",
                "description": "Generate high-level insights and statistics about the memory system, including categories, importance, and usage patterns.",
                "category": "memory",
                "priority": "low",
                "when_to_use": ["memory_analysis", "system_overview", "performance_metrics"],
                "input_schema": {"type": "object", "properties": {}, "required": []}
            },
            "bb7_memory_concept_network": {
                "name": "bb7_memory_concept_network",
                "description": "Build and visualize the network of concepts and relationships across all memories. Use for knowledge graph analysis and discovery.",
                "category": "memory",
                "priority": "medium",
                "when_to_use": ["knowledge_graph", "concept_mapping", "relationship_discovery"],
                "input_schema": {"type": "object", "properties": {"concept": {"type": "string"}}, "required": ["concept"]}
            },
            "bb7_memory_extract_concepts": {
                "name": "bb7_memory_extract_concepts",
                "description": "Extract key concepts, technical terms, and important phrases from memory entries or text. Use for tagging, indexing, and semantic enrichment.",
                "category": "memory",
                "priority": "medium",
                "when_to_use": ["tagging", "indexing", "semantic_enrichment"],
                "input_schema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}
            },
            "bb7_cross_session_analysis": {
                "name": "bb7_cross_session_analysis",
                "description": "Analyze patterns, goals, and outcomes across multiple sessions. Use for longitudinal insights and workflow optimization.",
                "category": "sessions",
                "priority": "medium",
                "when_to_use": ["longitudinal_analysis", "workflow_optimization", "session_patterns"],
                "input_schema": {"type": "object", "properties": {"days_back": {"type": "integer", "default": 30}}, "required": []}
            },
            "bb7_session_recommendations": {
                "name": "bb7_session_recommendations",
                "description": "Provide recommendations for next actions or improvements based on session history and patterns.",
                "category": "sessions",
                "priority": "medium",
                "when_to_use": ["action_recommendations", "workflow_improvement", "session_guidance"],
                "input_schema": {"type": "object", "properties": {}, "required": []}
            },
            "bb7_learned_patterns": {
                "name": "bb7_learned_patterns",
                "description": "Summarize recurring patterns, solutions, and best practices learned from past sessions and memories.",
                "category": "sessions",
                "priority": "medium",
                "when_to_use": ["pattern_recognition", "best_practices", "solution_summarization"],
                "input_schema": {"type": "object", "properties": {}, "required": []}
            },
            "bb7_session_intelligence": {
                "name": "bb7_session_intelligence",
                "description": "Generate a session intelligence report, highlighting key insights, breakthroughs, and cognitive metrics.",
                "category": "sessions",
                "priority": "medium",
                "when_to_use": ["session_reporting", "cognitive_metrics", "insight_generation"],
                "input_schema": {"type": "object", "properties": {}, "required": []}
            },
            "bb7_auto_memory_stats": {
                "name": "bb7_auto_memory_stats",
                "description": "Automatically compute and report memory usage statistics, trends, and optimization suggestions.",
                "category": "memory",
                "priority": "low",
                "when_to_use": ["memory_management", "resource_optimization", "usage_analysis"],
                "input_schema": {"type": "object", "properties": {}, "required": []}
            },
            "bb7_screen_monitor": {
                "name": "bb7_screen_monitor",
                "description": "Monitor the screen for visual changes over time, detecting UI updates or unexpected modifications.",
                "category": "visual",
                "priority": "medium",
                "when_to_use": ["ui_monitoring", "visual_debugging", "change_detection"],
                "input_schema": {"type": "object", "properties": {"duration": {"type": "integer", "default": 10}, "interval": {"type": "number", "default": 1.0}}, "required": []}
            },
            "bb7_visual_diff": {
                "name": "bb7_visual_diff",
                "description": "Compare two images or screenshots to detect and highlight visual differences.",
                "category": "visual",
                "priority": "medium",
                "when_to_use": ["visual_testing", "ui_comparison", "regression_detection"],
                "input_schema": {"type": "object", "properties": {"image1_path": {"type": "string"}, "image2_path": {"type": "string"}, "threshold": {"type": "number", "default": 0.1}}, "required": ["image1_path", "image2_path"]}
            },
            "bb7_active_window": {
                "name": "bb7_active_window",
                "description": "Retrieve information about the currently active window, including title and geometry.",
                "category": "visual",
                "priority": "low",
                "when_to_use": ["window_management", "context_awareness", "ui_information"],
                "input_schema": {"type": "object", "properties": {"include_geometry": {"type": "boolean", "default": True}}, "required": []}
            },
            "bb7_get_execution_audit": {
                "name": "bb7_get_execution_audit",
                "description": "Retrieve the audit log of recent secure Python code executions, including code, input, output, errors, and security scan results.",
                "category": "code_analysis",
                "priority": "low",
                "when_to_use": ["audit_log_review", "execution_history", "security_analysis_review"],
                "input_schema": {"type": "object", "properties": {"limit": {"type": "integer", "default": 20}}, "required": []}
            },
            "memory": [
                {
                    "name": "bb7_memory_store",
                    "description": "💾 Store a key-value pair in persistent memory with category, importance, and tags. Use for project context, insights, decisions, or any information that should persist across sessions.",
                    "category": "memory",
                    "priority": "critical",
                    "when_to_use": ["project_context", "insights", "decisions", "persistent_data", "knowledge_base"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Unique memory key (e.g. 'project:status')"},
                            "value": {"type": "string", "description": "Value to store (text, JSON, etc.)"},
                            "category": {"type": "string", "description": "Category for organization (optional)"},
                            "importance": {"type": "number", "default": 0.5, "description": "Importance score 0-1 (optional)"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for search/filtering (optional)"}
                        },
                        "required": ["key", "value"]
                    }
                },
                {
                    "name": "bb7_memory_retrieve",
                    "description": "🔍 Retrieve a value from persistent memory by key, with optional related memories. Use for context recall, project history, or knowledge lookup.",
                    "category": "memory",
                    "priority": "high",
                    "when_to_use": ["context_recall", "history", "lookup", "knowledge_retrieval"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Memory key to retrieve"},
                            "include_related": {"type": "boolean", "default": False, "description": "Include related memories (optional)"}
                        },
                        "required": ["key"]
                    }
                },
                {
                    "name": "bb7_memory_delete",
                    "description": "🗑️ Delete a key from persistent memory. Use for cleanup, removing outdated or incorrect information.",
                    "category": "memory",
                    "priority": "medium",
                    "when_to_use": ["cleanup", "remove_outdated", "delete_incorrect"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Memory key to delete"}
                        },
                        "required": ["key"]
                    }
                },
                {
                    "name": "bb7_memory_list",
                    "description": "📚 List memory keys with optional filtering by prefix, category, importance, or sort order. Use to discover available context and knowledge.",
                    "category": "memory",
                    "priority": "medium",
                    "when_to_use": ["explore_memory", "context_discovery", "knowledge_audit"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "prefix": {"type": "string", "description": "Filter keys by prefix (optional)"},
                            "category": {"type": "string", "description": "Filter by category (optional)"},
                            "min_importance": {"type": "number", "default": 0.0, "description": "Minimum importance (optional)"},
                            "sort_by": {"type": "string", "enum": ["timestamp", "importance", "access", "alphabetical"], "default": "timestamp", "description": "Sort order (optional)"}
                        },
                        "required": []
                    }
                },
                {
                    "name": "bb7_memory_search",
                    "description": "🔎 Search memory using semantic or text matching. Use for finding relevant knowledge, context, or related information.",
                    "category": "memory",
                    "priority": "medium",
                    "when_to_use": ["search", "semantic_lookup", "find_related"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "max_results": {"type": "integer", "default": 5, "description": "Max results (optional)"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "bb7_memory_stats",
                    "description": "📊 Get statistics about memory usage, entry counts, and storage patterns. Use for memory management and analysis.",
                    "category": "memory",
                    "priority": "low",
                    "when_to_use": ["memory_management", "usage_stats", "analysis"],
                    "input_schema": {"type": "object", "properties": {}, "required": []}
                },
                {
                    "name": "bb7_memory_insights",
                    "description": "🧠 Get high-level insights about memory system, including categories, importance, and usage patterns. Use for knowledge management and optimization.",
                    "category": "memory",
                    "priority": "low",
                    "when_to_use": ["insights", "knowledge_management", "optimization"],
                    "input_schema": {"type": "object", "properties": {}, "required": []}
                },
                {
                    "name": "bb7_memory_consolidate",
                    "description": "🗃️ Consolidate and archive old or low-importance memories. Use for memory optimization and long-term storage.",
                    "category": "memory",
                    "priority": "low",
                    "when_to_use": ["archive", "optimize", "cleanup"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "days_old": {"type": "integer", "default": 30, "description": "Archive memories older than this (optional)"}
                        },
                        "required": []
                    }
                },
                {
                    "name": "bb7_memory_categories",
                    "description": "🏷️ List all available memory categories and their descriptions. Use for organizing and tagging knowledge.",
                    "category": "memory",
                    "priority": "low",
                    "when_to_use": ["organization", "tagging", "category_discovery"],
                    "input_schema": {"type": "object", "properties": {}, "required": []}
                }
            ],
            "auto_activation": [
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
                    "name": "bb7_analyze_project_structure",
                    "description": "📊 Comprehensive project analysis including file structure, dependencies, and architecture insights. Use when starting work on new projects or when architectural understanding is needed.",
                    "category": "auto_activation",
                    "priority": "medium",
                    "when_to_use": ["new_project", "architecture_analysis", "codebase_understanding", "onboarding"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "max_depth": {
                                "type": "integer",
                                "default": 3,
                                "description": "Maximum directory depth to analyze"
                            },
                            "include_hidden": {
                                "type": "boolean",
                                "default": False,
                                "description": "Include hidden files and directories"
                            }
                        },
                        "required": []
                    }
                },
                {
                    "name": "bb7_get_project_dependencies",
                    "description": "📦 Analyze and list project dependencies, package.json, requirements.txt, etc. Use when understanding project setup or troubleshooting dependency issues.",
                    "category": "auto_activation",
                    "priority": "medium",
                    "when_to_use": ["dependency_analysis", "setup_issues", "environment_check", "build_problems"],
                    "input_schema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                },
                {
                    "name": "bb7_get_recent_changes",
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
                    "description": "💾 Store a key-value pair in persistent memory with category, importance, and tags. Use for project context, insights, decisions, or any information that should persist across sessions.",
                    "category": "memory",
                    "priority": "critical",
                    "when_to_use": ["project_context", "insights", "decisions", "persistent_data", "knowledge_base"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Unique memory key (e.g. 'project:status')"},
                            "value": {"type": "string", "description": "Value to store (text, JSON, etc.)"},
                            "category": {"type": "string", "description": "Category for organization (optional)"},
                            "importance": {"type": "number", "default": 0.5, "description": "Importance score 0-1 (optional)"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags for search/filtering (optional)"}
                        },
                        "required": ["key", "value"]
                    }
                },
                {
                    "name": "bb7_memory_retrieve",
                    "description": "🔍 Retrieve a value from persistent memory by key, with optional related memories. Use for context recall, project history, or knowledge lookup.",
                    "category": "memory",
                    "priority": "high",
                    "when_to_use": ["context_recall", "history", "lookup", "knowledge_retrieval"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Memory key to retrieve"},
                            "include_related": {"type": "boolean", "default": False, "description": "Include related memories (optional)"}
                        },
                        "required": ["key"]
                    }
                },
                {
                    "name": "bb7_memory_delete",
                    "description": "🗑️ Delete a key from persistent memory. Use for cleanup, removing outdated or incorrect information.",
                    "category": "memory",
                    "priority": "medium",
                    "when_to_use": ["cleanup", "remove_outdated", "delete_incorrect"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Memory key to delete"}
                        },
                        "required": ["key"]
                    }
                },
                {
                    "name": "bb7_memory_list",
                    "description": "📚 List memory keys with optional filtering by prefix, category, importance, or sort order. Use to discover available context and knowledge.",
                    "category": "memory",
                    "priority": "medium",
                    "when_to_use": ["explore_memory", "context_discovery", "knowledge_audit"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "prefix": {"type": "string", "description": "Filter keys by prefix (optional)"},
                            "category": {"type": "string", "description": "Filter by category (optional)"},
                            "min_importance": {"type": "number", "default": 0.0, "description": "Minimum importance (optional)"},
                            "sort_by": {"type": "string", "enum": ["timestamp", "importance", "access", "alphabetical"], "default": "timestamp", "description": "Sort order (optional)"}
                        },
                        "required": []
                    }
                },
                {
                    "name": "bb7_memory_search",
                    "description": "🔎 Search memory using semantic or text matching. Use for finding relevant knowledge, context, or related information.",
                    "category": "memory",
                    "priority": "medium",
                    "when_to_use": ["search", "semantic_lookup", "find_related"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "max_results": {"type": "integer", "default": 5, "description": "Max results (optional)"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "bb7_memory_stats",
                    "description": "📊 Get statistics about memory usage, entry counts, and storage patterns. Use for memory management and analysis.",
                    "category": "memory",
                    "priority": "low",
                    "when_to_use": ["memory_management", "usage_stats", "analysis"],
                    "input_schema": {"type": "object", "properties": {}, "required": []}
                },
                {
                    "name": "bb7_memory_insights",
                    "description": "🧠 Get high-level insights about memory system, including categories, importance, and usage patterns. Use for knowledge management and optimization.",
                    "category": "memory",
                    "priority": "low",
                    "when_to_use": ["insights", "knowledge_management", "optimization"],
                    "input_schema": {"type": "object", "properties": {}, "required": []}
                },
                {
                    "name": "bb7_memory_consolidate",
                    "description": "🗃️ Consolidate and archive old or low-importance memories. Use for memory optimization and long-term storage.",
                    "category": "memory",
                    "priority": "low",
                    "when_to_use": ["archive", "optimize", "cleanup"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "days_old": {"type": "integer", "default": 30, "description": "Archive memories older than this (optional)"}
                        },
                        "required": []
                    }
                },
                {
                    "name": "bb7_memory_categories",
                    "description": "🏷️ List all available memory categories and their descriptions. Use for organizing and tagging knowledge.",
                    "category": "memory",
                    "priority": "low",
                    "when_to_use": ["organization", "tagging", "category_discovery"],
                    "input_schema": {"type": "object", "properties": {}, "required": []}
                }
            ],
            "sessions": [
                {
                    "name": "bb7_start_session",
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
                    "name": "bb7_log_event",
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
                    "name": "bb7_capture_insight",
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
                    "name": "bb7_record_workflow",
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
                    "name": "bb7_update_focus",
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
                    "name": "bb7_pause_session",
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
                    "name": "bb7_resume_session",
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
                    "name": "bb7_list_sessions",
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
                    "name": "bb7_get_session_summary",
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
                    "name": "bb7_read_file",
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
                    "name": "bb7_write_file",
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
                    "name": "bb7_append_file",
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
                    "name": "bb7_list_directory",
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
                    "name": "bb7_get_file_info",
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
                    "name": "bb7_search_files",
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
                    "name": "bb7_run_command",
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
                    "name": "bb7_run_script",
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
                    "name": "bb7_get_environment",
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
                    "name": "bb7_list_processes",
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
                    "name": "bb7_kill_process",
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
                    "name": "bb7_get_system_info",
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
                    "name": "bb7_fetch_url",
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
                    "name": "bb7_download_file",
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
                    "name": "bb7_check_url_status",
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
                    "name": "bb7_search_web",
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
                    "name": "bb7_extract_links",
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
                    "input_schema": {"type": "object", "properties": {"file_path": {"type": "string", "description": "Path to code file to analyze"}, "analysis_types": {"type": "array", "items": {"type": "string"}, "default": ["syntax", "complexity", "security", "type_inference"], "description": "Types of analysis to perform"}}, "required": ["file_path"]}
                },
                {
                    "name": "bb7_python_execute_secure",
                    "description": "🐍 SECURE EXECUTION: Execute Python code in a secure, sandboxed environment with resource limits and safety checks. Use for testing code snippets or running analysis safely.",
                    "category": "code_analysis",
                    "priority": "medium",
                    "when_to_use": ["code_testing", "snippet_execution", "safe_evaluation", "python_analysis"],
                    "input_schema": {"type": "object", "properties": {"code": {"type": "string", "description": "Python code to execute"}, "timeout": {"type": "integer", "default": 10, "description": "Execution timeout in seconds"}, "capture_output": {"type": "boolean", "default": True}}, "required": ["code"]}
                },
                {
                    "name": "bb7_security_audit",
                    "description": "🔒 SECURITY ANALYSIS: Comprehensive security audit for code including vulnerability detection, security best practices checking, and risk assessment. Use for security reviews and compliance.",
                    "category": "code_analysis",
                    "priority": "high",
                    "when_to_use": ["security_review", "vulnerability_scan", "compliance_check", "risk_assessment"],
                    "input_schema": {"type": "object", "properties": {"target_path": {"type": "string", "description": "Path to file or directory to audit"}, "security_level": {"type": "string", "enum": ["basic", "standard", "strict"], "default": "standard"}}, "required": ["target_path"]}
                },
                {
                    "name": "bb7_get_execution_audit",
                    "description": "Retrieve the audit log of recent secure Python code executions, including code, input, output, errors, and security scan results.",
                    "category": "code_analysis",
                    "priority": "low",
                    "when_to_use": ["audit_log_review", "execution_history", "security_analysis_review"],
                    "input_schema": {"type": "object", "properties": {"limit": {"type": "integer", "default": 20}}, "required": []}
                }
            ],
            "files": [
                {
                    "name": "bb7_read_file",
                    "description": "📖 Read complete contents of any file on the system. Use for understanding code, reviewing configurations, analyzing logs, or accessing any text-based content. Supports all text encodings.",
                    "category": "files",
                    "priority": "high",
                    "when_to_use": ["code_review", "file_analysis", "config_check", "log_reading", "documentation"],
                    "input_schema": {"type": "object", "properties": {"path": {"type": "string", "description": "Full or relative path to file"}}, "required": ["path"]}
                },
                {
                    "name": "bb7_write_file",
                    "description": "✍️ Create or overwrite files with new content. Use for generating code, creating documentation, saving configurations, or any file creation task. Creates directories as needed.",
                    "category": "files",
                    "priority": "high",
                    "when_to_use": ["file_creation", "code_generation", "documentation", "config_save", "script_creation"],
                    "input_schema": {"type": "object", "properties": {"path": {"type": "string", "description": "Target file path"}, "content": {"type": "string", "description": "Content to write"}}, "required": ["path", "content"]}
                },
                {
                    "name": "bb7_append_file",
                    "description": "➕ Add content to end of existing file or create new file. Use for logging, adding to existing code, or incremental file building.",
                    "category": "files",
                    "priority": "medium",
                    "when_to_use": ["logging", "incremental_updates", "file_extension", "append_content"],
                    "input_schema": {"type": "object", "properties": {"path": {"type": "string", "description": "Target file path"}, "content": {"type": "string", "description": "Content to append"}}, "required": ["path", "content"]}
                },
                {
                    "name": "bb7_list_directory",
                    "description": "📂 List directory contents with detailed file information. Use for exploring project structure, understanding codebases, or finding files. Shows sizes, timestamps, and file types.",
                    "category": "files",
                    "priority": "medium",
                    "when_to_use": ["directory_exploration", "project_structure", "file_discovery", "codebase_navigation"],
                    "input_schema": {"type": "object", "properties": {"path": {"type": "string", "description": "Directory path to list", "default": "."}}, "required": []}
                },
                {
                    "name": "bb7_get_file_info",
                    "description": "ℹ️ Get detailed information about specific file or directory including size, timestamps, permissions, and type analysis. Use for understanding file characteristics.",
                    "category": "files",
                    "priority": "low",
                    "when_to_use": ["file_analysis", "metadata_check", "permissions", "file_properties"],
                    "input_schema": {"type": "object", "properties": {"path": {"type": "string", "description": "Path to analyze"}}, "required": ["path"]}
                },
                {
                    "name": "bb7_search_files",
                    "description": "🔍 Search for files matching patterns in directory trees. Use for finding specific files, locating code patterns, or exploring large codebases. Supports glob patterns.",
                    "category": "files",
                    "priority": "medium",
                    "when_to_use": ["file_discovery", "pattern_search", "codebase_exploration", "file_finding"],
                    "input_schema": {"type": "object", "properties": {"directory": {"type": "string", "description": "Root directory to search"}, "pattern": {"type": "string", "description": "Glob pattern (e.g., '*.py', '**/*.json')"}, "max_results": {"type": "integer", "default": 50}}, "required": ["directory", "pattern"]}
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
        
        # Add category-specific recommendations (flat registry)
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        for category in detected_intents:
            # Only process dict values (ignore lists/invalids)
            tools_in_category = [tool for tool in self.tool_registry.values() if isinstance(tool, dict) and tool.get("category", "unknown") == category]
            top_tools = sorted(
                tools_in_category,
                key=lambda x: priority_order.get(x.get("priority", "low"), 3)
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
        """Get all tools in a specific category with their full registry information (flat registry)"""
        return [
            tool for tool in self.tool_registry.values()
            if isinstance(tool, dict) and tool.get("category", "unknown") == category
        ]

    def find_tool_by_intent(self, intent: str) -> List[Dict[str, Any]]:
        """Find tools that match a specific usage intent"""
        matching_tools = []
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        for tool in self.tool_registry.values():
            if not isinstance(tool, dict):
                continue
            when_to_use = tool.get("when_to_use", [])
            if any(intent.lower() in (w or '').lower() for w in when_to_use):
                matching_tools.append(tool)
        matching_tools.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))
        return matching_tools

    def register_tools(self):
        """Register all available MCP tools from modules by dynamically importing them."""
        import importlib
        import pkgutil
        import sys
        import inspect
        from pathlib import Path

        self.logger.info("Starting tool registration...")

        # Keep instances of tool classes alive
        if not hasattr(self, 'tool_instances'):
            self.tool_instances = []

        tools_dir = Path(__file__).parent / "tools"
        if str(tools_dir.parent) not in sys.path:
            sys.path.insert(0, str(tools_dir.parent))

        self.tools = {}
        self.tool_registry = {}

        for module_info in pkgutil.iter_modules([str(tools_dir)]):
            mod_name = module_info.name
            if mod_name.startswith("__"):
                continue

            try:
                module = importlib.import_module(f"tools.{mod_name}")

                # Find the primary tool class in the module (heuristic: ends with 'Tool')
                tool_class = None
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if name.endswith("Tool") and obj.__module__ == module.__name__:
                        tool_class = obj
                        break

                if not tool_class:
                    self.logger.debug(f"No suitable *Tool class found in {mod_name}, skipping.")
                    continue

                # Instantiate the tool class and get the tools
                tool_instance = tool_class()
                self.tool_instances.append(tool_instance) # Keep instance alive

                if not hasattr(tool_instance, 'get_tools') or not callable(getattr(tool_instance, 'get_tools')):
                    self.logger.warning(f"No callable get_tools method found in {tool_class.__name__}, skipping.")
                    continue

                tool_map = tool_instance.get_tools()

                for tool_name, tool_info in tool_map.items():
                    if isinstance(tool_info, dict) and 'callable' in tool_info and 'metadata' in tool_info:
                        self.tools[tool_name] = tool_info['callable']
                        self.tool_registry[tool_name] = tool_info['metadata']
                        self.logger.debug(f"Registered tool '{tool_name}' from {mod_name}")
                    elif callable(tool_info):
                        # This path is for modules that haven't been updated to the new metadata format.
                        self.tools[tool_name] = tool_info
                        # This is the source of the "No description" problem. We will fix this by updating the modules.
                        self.tool_registry[tool_name] = {"name": tool_name, "description": "No description provided.", "category": "uncategorized"}
                        self.logger.warning(f"Tool '{tool_name}' from {mod_name} is missing embedded metadata. Please update its get_tools() method.")
                    else:
                        self.logger.warning(f"Invalid tool info format for '{tool_name}' in {mod_name}")

            except Exception as e:
                self.logger.error(f"Failed to load or register tools from module {mod_name}: {e}")
                self.logger.error(traceback.format_exc())

        self.server_info["total_tools"] = len(self.tools)
        self.logger.info(f"Tool registration complete. Total tools: {self.server_info['total_tools']}")
        self.log_tool_summary()

    def log_tool_summary(self):
        """Log detailed summary of registered tools"""
        self.logger.info("=" * 80)
        self.logger.info("MCP SERVER TOOL INVENTORY")
        self.logger.info("=" * 80)
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
                    "available_tools": available_tools[:10]
                }
            self.logger.debug(f"Calling tool: {tool_name} with args: {kwargs}")
            tool_func = self.tools[tool_name]
            if callable(tool_func):
                result = tool_func(**kwargs)
                execution_time = time.time() - start_time
                self.performance_metrics["successful_calls"] += 1
                self.update_average_response_time(execution_time)
                # Ensure result is JSON serializable
                if isinstance(result, str):
                    formatted_result = {"success": True, "result": result}
                elif isinstance(result, dict):
                    formatted_result = result
                else:
                    formatted_result = {"success": True, "result": str(result)}
                formatted_result["execution_time"] = round(execution_time, 3)
                self.logger.debug(f"Tool {tool_name} completed in {execution_time:.3f}s")
                return formatted_result
            else:
                return {
                    "success": False,
                    "error": "TOOL_NOT_CALLABLE",
                    "message": f"Tool '{tool_name}' is not a callable function"
                }
        except TypeError as e:
            self.performance_metrics["failed_calls"] += 1
            error_msg = f"Parameter error for tool '{tool_name}': {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": "PARAMETER_ERROR",
                "message": error_msg,
                "provided_args": list(kwargs.keys()),
                "exception_type": type(e).__name__
            }
        except Exception as e:
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
# ...existing code...