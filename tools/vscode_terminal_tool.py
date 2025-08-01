"""
VS Code Terminal Integration Tool - Bridge MCP Server with Active Terminal

This tool provides direct integration with VS Code's terminal session,
allowing the MCP server to interact with your actual terminal state,
history, and current working context.
"""

import json
import logging
import os
import time
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable


class VSCodeTerminalTool:
    """Handles VS Code terminal integration and state management"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("VS Code Terminal Integration tool initialized")
        
        # VS Code terminal state tracking
        self._terminal_history = []
        self._current_directory = os.getcwd()
        self._environment_snapshot = dict(os.environ)
        
    def bb7_terminal_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get current VS Code terminal status and state"""
        try:
            status = {
                "current_directory": os.getcwd(),
                "shell": os.environ.get('SHELL', os.environ.get('COMSPEC', 'unknown')),
                "terminal_available": True,
                "environment_vars": {
                    "PATH": os.environ.get('PATH', ''),
                    "VIRTUAL_ENV": os.environ.get('VIRTUAL_ENV', ''),
                    "CONDA_DEFAULT_ENV": os.environ.get('CONDA_DEFAULT_ENV', ''),
                    "NODE_ENV": os.environ.get('NODE_ENV', ''),
                    "PYTHON_VERSION": os.environ.get('PYTHON_VERSION', '')
                },
                "integration_status": "Connected to VS Code terminal session"
            }
            
            # Check if we're in a virtual environment
            if 'VIRTUAL_ENV' in os.environ:
                status["python_env"] = {
                    "type": "virtualenv", 
                    "path": os.environ['VIRTUAL_ENV'],
                    "name": os.path.basename(os.environ['VIRTUAL_ENV']),
                    "active": True
                }
            elif 'CONDA_DEFAULT_ENV' in os.environ:
                status["python_env"] = {
                    "type": "conda",
                    "name": os.environ['CONDA_DEFAULT_ENV'],
                    "active": True
                }
            else:
                status["python_env"] = {
                    "type": "system",
                    "name": "system",
                    "active": False
                }
            
            self.logger.info("Retrieved VS Code terminal status")
            return {"success": True, "status": status}
            
        except Exception as e:
            self.logger.error(f"Error getting terminal status: {e}")
            return {"success": False, "error": str(e)}
    
    def bb7_terminal_run_command(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Run command in current terminal context with full state awareness"""
        try:
            command = arguments.get('command', '')
            if not command:
                return {"success": False, "error": "No command provided"}
            
            change_dir = arguments.get('change_directory', True)
            timeout = arguments.get('timeout', 30)
            
            # Capture current state
            original_cwd = os.getcwd()
            
            self.logger.info(f"Running terminal command: {command}")
            
            # Execute command with full terminal context with proper timeout handling
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=os.getcwd(),
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    env=os.environ.copy()
                )
            except subprocess.TimeoutExpired:
                return {
                    "success": False, 
                    "error": f"Command timed out after {timeout} seconds",
                    "command": command
                }
            
            # Update our understanding of terminal state
            if change_dir and command.strip().startswith('cd '):
                try:
                    new_dir = command.strip().split(' ', 1)[1].strip().strip('"\'')
                    if new_dir:
                        expanded_path = os.path.abspath(os.path.expanduser(new_dir))
                        if os.path.exists(expanded_path) and os.path.isdir(expanded_path):
                            os.chdir(expanded_path)
                            self._current_directory = expanded_path
                except:
                    pass  # If cd parsing fails, don't break the flow
            
            # Track command in history
            self._terminal_history.append({
                "command": command,
                "timestamp": time.time(),
                "exit_code": result.returncode,
                "working_directory": original_cwd
            })
            
            # Format response like a real terminal
            response = {
                "success": True,
                "command": command,
                "exit_code": result.returncode,
                "working_directory": original_cwd,
                "current_directory": os.getcwd(),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": 0.1,  # Approximate
                "terminal_formatted": self._format_terminal_output(command, result)
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error running terminal command: {e}")
            return {"success": False, "error": str(e)}
    
    def bb7_terminal_history(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get recent terminal command history"""
        try:
            limit = arguments.get('limit', 10)
            
            recent_history = self._terminal_history[-limit:] if self._terminal_history else []
            
            return {
                "success": True,
                "history": recent_history,
                "total_commands": len(self._terminal_history)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting terminal history: {e}")
            return {"success": False, "error": str(e)}
    
    def bb7_terminal_environment(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get current terminal environment with diff from startup"""
        try:
            current_env = dict(os.environ)
            
            # Find differences from initial environment
            added_vars = {}
            changed_vars = {}
            removed_vars = {}
            
            for key, value in current_env.items():
                if key not in self._environment_snapshot:
                    added_vars[key] = value
                elif self._environment_snapshot[key] != value:
                    changed_vars[key] = {
                        "old": self._environment_snapshot[key],
                        "new": value
                    }
            
            for key in self._environment_snapshot:
                if key not in current_env:
                    removed_vars[key] = self._environment_snapshot[key]
            
            return {
                "success": True,
                "current_environment": current_env,
                "changes_since_startup": {
                    "added": added_vars,
                    "changed": changed_vars,
                    "removed": removed_vars
                },
                "important_vars": {
                    "PATH": current_env.get('PATH', ''),
                    "VIRTUAL_ENV": current_env.get('VIRTUAL_ENV', ''),
                    "CONDA_DEFAULT_ENV": current_env.get('CONDA_DEFAULT_ENV', ''),
                    "PWD": current_env.get('PWD', os.getcwd()),
                    "HOME": current_env.get('HOME', current_env.get('USERPROFILE', ''))
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting terminal environment: {e}")
            return {"success": False, "error": str(e)}
    
    def bb7_terminal_cd(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Change directory with VS Code terminal context awareness"""
        try:
            path = arguments.get('path', '')
            if not path:
                # Return current directory
                return {
                    "success": True,
                    "current_directory": os.getcwd(),
                    "action": "show_current"
                }
            
            # Expand path
            expanded_path = os.path.abspath(os.path.expanduser(path))
            
            if not os.path.exists(expanded_path):
                return {"success": False, "error": f"Directory does not exist: {expanded_path}"}
            
            if not os.path.isdir(expanded_path):
                return {"success": False, "error": f"Path is not a directory: {expanded_path}"}
            
            old_dir = os.getcwd()
            os.chdir(expanded_path)
            self._current_directory = expanded_path
            
            return {
                "success": True,
                "old_directory": old_dir,
                "new_directory": expanded_path,
                "action": "changed"
            }
            
        except Exception as e:
            self.logger.error(f"Error changing directory: {e}")
            return {"success": False, "error": str(e)}
    
    def bb7_terminal_which(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Find executable in PATH like 'which' command"""
        try:
            command = arguments.get('command', '')
            if not command:
                return {"success": False, "error": "No command provided"}
            
            # Use 'where' on Windows, 'which' on Unix-like
            if os.name == 'nt':
                search_cmd = f"where {command}"
            else:
                search_cmd = f"which {command}"
            
            result = subprocess.run(
                search_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                paths = result.stdout.strip().split('\n')
                return {
                    "success": True,
                    "command": command,
                    "found": True,
                    "paths": paths,
                    "primary_path": paths[0] if paths else None
                }
            else:
                return {
                    "success": True,
                    "command": command,
                    "found": False,
                    "paths": [],
                    "primary_path": None
                }
                
        except Exception as e:
            self.logger.error(f"Error finding command: {e}")
            return {"success": False, "error": str(e)}
    
    def _format_terminal_output(self, command: str, result: subprocess.CompletedProcess) -> str:
        """Format output to look like real terminal session"""
        output = f"$ {command}\n"
        
        if result.stdout:
            output += result.stdout
        
        if result.stderr:
            output += result.stderr
        
        if result.returncode != 0:
            output += f"\n[Process exited with code {result.returncode}]"
        
        return output
    
    def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle VS Code terminal tool calls"""
        try:
            if name == "bb7_terminal_status":
                return self.bb7_terminal_status(arguments)
            elif name == "bb7_terminal_run_command":
                return self.bb7_terminal_run_command(arguments)
            elif name == "bb7_terminal_history":
                return self.bb7_terminal_history(arguments)
            elif name == "bb7_terminal_environment":
                return self.bb7_terminal_environment(arguments)
            elif name == "bb7_terminal_cd":
                return self.bb7_terminal_cd(arguments)
            elif name == "bb7_terminal_which":
                return self.bb7_terminal_which(arguments)
            else:
                return {"error": f"Unknown VS Code terminal tool: {name}"}
                
        except Exception as e:
            self.logger.error(f"Error in terminal tool '{name}': {e}")
            return {"error": f"Error in terminal tool '{name}': {str(e)}"}
    
    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        """Return all available VS Code terminal tools with their metadata."""
        return {
            'bb7_terminal_status': {
                "callable": lambda: self.bb7_terminal_status({}),
                "metadata": {
                    "name": "bb7_terminal_status",
                    "description": "🖥️ VS CODE INTEGRATION: Get current terminal status, environment, and integration state. Understand the active development context within VS Code.",
                    "category": "terminal",
                    "priority": "low",
                    "when_to_use": ["terminal_check", "environment_status", "integration_check", "context_awareness"],
                    "input_schema": { "type": "object", "properties": {}, "required": [] }
                }
            },
            'bb7_terminal_run_command': {
                "callable": lambda command, change_directory=True, timeout=30: self.bb7_terminal_run_command({"command": command, "change_directory": change_directory, "timeout": timeout}),
                "metadata": {
                    "name": "bb7_terminal_run_command",
                    "description": "⚡ VS CODE TERMINAL: Run commands in current VS Code terminal context with full state awareness. Maintains directory context and environment continuity.",
                    "category": "terminal",
                    "priority": "high",
                    "when_to_use": ["vscode_commands", "terminal_execution", "context_aware_commands", "development_tasks"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "command": { "type": "string", "description": "Command to execute" },
                            "change_directory": { "type": "boolean", "default": True },
                            "timeout": { "type": "integer", "default": 30 }
                        },
                        "required": ["command"]
                    }
                }
            },
            'bb7_terminal_history': {
                "callable": lambda limit=10: self.bb7_terminal_history({"limit": limit}),
                "metadata": {
                    "name": "bb7_terminal_history",
                    "description": "📜 VS CODE TERMINAL: Get recent command history from VS Code terminal. Use for understanding recent development activities or repeating commands.",
                    "category": "terminal",
                    "priority": "low",
                    "when_to_use": ["command_history", "recent_activities", "command_repeat", "development_context"],
                    "input_schema": {
                        "type": "object",
                        "properties": { "limit": { "type": "integer", "default": 10 } },
                        "required": []
                    }
                }
            },
            'bb7_terminal_environment': {
                "callable": lambda: self.bb7_terminal_environment({}),
                "metadata": {
                    "name": "bb7_terminal_environment",
                    "description": "🌍 VS CODE TERMINAL: Get environment variables and context from VS Code terminal. Use for understanding the development environment setup.",
                    "category": "terminal",
                    "priority": "low",
                    "when_to_use": ["environment_check", "variable_inspection", "setup_verification", "debugging"],
                    "input_schema": { "type": "object", "properties": {}, "required": [] }
                }
            },
            'bb7_terminal_cd': {
                "callable": lambda path=None: self.bb7_terminal_cd({"path": path} if path else {}),
                "metadata": {
                    "name": "bb7_terminal_cd",
                    "description": "📁 VS CODE TERMINAL: Change directory with context tracking. Navigate filesystem while maintaining awareness of location and context.",
                    "category": "terminal",
                    "priority": "medium",
                    "when_to_use": ["directory_navigation", "context_tracking", "filesystem_navigation", "project_navigation"],
                    "input_schema": {
                        "type": "object",
                        "properties": { "path": { "type": "string", "description": "Directory path to change to" } },
                        "required": ["path"]
                    }
                }
            },
            'bb7_terminal_which': {
                "callable": lambda command: self.bb7_terminal_which({"command": command}),
                "metadata": {
                    "name": "bb7_terminal_which",
                    "description": "🔍 VS CODE TERMINAL: Find executables in PATH from VS Code terminal context. Use for checking tool availability and executable locations.",
                    "category": "terminal",
                    "priority": "low",
                    "when_to_use": ["executable_location", "tool_availability", "path_check", "dependency_check"],
                    "input_schema": {
                        "type": "object",
                        "properties": { "command": { "type": "string", "description": "Command/executable to locate" } },
                        "required": ["command"]
                    }
                }
            }
        }


# For standalone testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    terminal = VSCodeTerminalTool()
    
    # Test terminal integration
    print("=== Terminal Status ===")
    status_result = terminal.bb7_terminal_status({})
    print(json.dumps(status_result, indent=2))
    
    print("\n=== Running Command ===")
    cmd_result = terminal.bb7_terminal_run_command({"command": "echo 'Hello from VS Code terminal!'"})
    print(json.dumps(cmd_result, indent=2))
    
    print("\n=== Environment Check ===")
    env_result = terminal.bb7_terminal_environment({})
    print("Environment variables count:", len(env_result.get("current_environment", {})))