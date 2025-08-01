"""
Shell Tool - Command execution for MCP Server

This tool provides full shell command execution capabilities,
allowing Copilot to run any system command, script, or utility.
No restrictions - designed for a dedicated coding environment.
"""
import subprocess
import os
import time
import platform
import logging
import threading
import psutil
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Callable


class ShellTool:
    """Handles shell command execution with full system access"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("Shell tool initialized with full command access")
        
        # Track running processes for potential cleanup
        self._active_processes = {}
        self._process_counter = 0
        self._lock = threading.Lock()
    
    def run_command(self, command: str, working_dir: Optional[str] = None, 
                   timeout: int = 30, capture_output: bool = True) -> str:
        """Execute a shell command and return results"""
        try:
            # Resolve working directory
            if working_dir:
                work_path = Path(working_dir).expanduser().resolve()
                if not work_path.exists():
                    return f"Error: Working directory '{working_dir}' does not exist"
                if not work_path.is_dir():
                    return f"Error: '{working_dir}' is not a directory"
                cwd = str(work_path)
            else:
                cwd = os.getcwd()
            
            self.logger.info(f"Executing command: {command} (cwd: {cwd})")
            
            start_time = time.time()
            
            # Execute the command with proper timeout handling
            if capture_output:
                try:
                    # Additional protection: limit environment size to prevent hanging
                    env = os.environ.copy()
                    
                    result = subprocess.run(
                        command,
                        shell=True,
                        cwd=cwd,
                        capture_output=True,
                        text=True,
                        timeout=timeout,
                        env=env
                    )
                    
                    execution_time = time.time() - start_time
                    
                    # Format the response
                    response = f"Command: {command}\n"
                    response += f"Working directory: {cwd}\n"
                    response += f"Exit code: {result.returncode}\n"
                    response += f"Execution time: {execution_time:.2f} seconds\n\n"
                    
                    if result.stdout:
                        # Limit output size to prevent memory issues
                        stdout = result.stdout
                        if len(stdout) > 10000:
                            stdout = stdout[:10000] + "\n... (output truncated, too long)"
                        response += f"STDOUT:\n{stdout}\n"
                    
                    if result.stderr:
                        stderr = result.stderr
                        if len(stderr) > 5000:
                            stderr = stderr[:5000] + "\n... (error output truncated)"
                        response += f"STDERR:\n{stderr}\n"
                    
                    if result.returncode == 0:
                        self.logger.info(f"Command completed successfully: {command}")
                    else:
                        self.logger.warning(f"Command failed with exit code {result.returncode}: {command}")
                    
                    return response
                    
                except subprocess.TimeoutExpired as e:
                    execution_time = time.time() - start_time
                    self.logger.error(f"Command timed out after {timeout} seconds: {command}")
                    error_msg = f"Error: Command timed out after {timeout} seconds\n"
                    error_msg += f"Command: {command}\n"
                    error_msg += f"Execution time: {execution_time:.2f} seconds\n"
                    if hasattr(e, 'stdout') and e.stdout:
                        error_msg += f"Partial STDOUT: {e.stdout[:1000]}\n"
                    if hasattr(e, 'stderr') and e.stderr:
                        error_msg += f"Partial STDERR: {e.stderr[:1000]}\n"
                    return error_msg
                
            else:
                # For commands that don't need output capture (like launching GUI apps)
                process = subprocess.Popen(
                    command,
                    shell=True,
                    cwd=cwd,
                    env=os.environ.copy()
                )
                
                # Give it a moment to start
                time.sleep(0.1)
                
                if process.poll() is None:
                    # Still running
                    with self._lock:
                        self._process_counter += 1
                        process_id = self._process_counter
                        self._active_processes[process_id] = process
                    
                    return f"Command started in background: {command}\nProcess ID: {process_id}"
                else:
                    # Completed quickly
                    return f"Command completed: {command}\nExit code: {process.returncode}"
            
        except Exception as e:
            self.logger.error(f"Error executing command '{command}': {e}")
            return f"Error executing command '{command}': {str(e)}"
    
    def run_script(self, script_content: str, script_type: str = "bash", 
                  working_dir: Optional[str] = None) -> str:
        """Execute a script from content"""
        try:
            # Determine script extension and shebang
            if script_type.lower() in ['bash', 'sh']:
                extension = '.sh'
                shebang = '#!/bin/bash\n'
            elif script_type.lower() in ['python', 'py']:
                extension = '.py'
                shebang = '#!/usr/bin/env python3\n'
            elif script_type.lower() in ['node', 'js', 'javascript']:
                extension = '.js'
                shebang = '#!/usr/bin/env node\n'
            elif script_type.lower() in ['powershell', 'ps1']:
                extension = '.ps1'
                shebang = ''
            else:
                extension = '.sh'
                shebang = '#!/bin/bash\n'
            
            # Create temporary script file
            temp_dir = Path("data/temp_scripts")
            temp_dir.mkdir(exist_ok=True)
            
            script_file = temp_dir / f"script_{int(time.time())}{extension}"
            
            # Write script content
            with open(script_file, 'w', encoding='utf-8') as f:
                if shebang:
                    f.write(shebang)
                f.write(script_content)
            
            # Make executable (Unix-like systems)
            try:
                os.chmod(script_file, 0o755)
            except:
                pass  # Windows or permission issues
            
            # Execute the script
            if script_type.lower() in ['powershell', 'ps1']:
                command = f"powershell -ExecutionPolicy Bypass -File {script_file}"
            else:
                command = str(script_file)
            
            result = self.run_command(command, working_dir)
            
            # Cleanup
            try:
                script_file.unlink()
            except:
                pass
            
            return f"Script execution result:\n{result}"
            
        except Exception as e:
            self.logger.error(f"Error executing script: {e}")
            return f"Error executing script: {str(e)}"
    
    def get_environment(self) -> str:
        """Get current environment information"""
        try:
            info = []
            
            # Basic system info
            info.append(f"Current working directory: {os.getcwd()}")
            info.append(f"User: {os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))}")
            info.append(f"Home directory: {os.environ.get('HOME', os.environ.get('USERPROFILE', 'unknown'))}")
            info.append(f"Shell: {os.environ.get('SHELL', os.environ.get('COMSPEC', 'unknown'))}")
            
            # PATH info
            path_dirs = os.environ.get('PATH', '').split(os.pathsep)
            info.append(f"PATH directories ({len(path_dirs)}):")
            for i, path_dir in enumerate(path_dirs[:10]):  # Show first 10
                info.append(f"  {i+1}. {path_dir}")
            if len(path_dirs) > 10:
                info.append(f"  ... and {len(path_dirs) - 10} more")
            
            # Python info - with shorter timeout and better error handling
            try:
                python_version = subprocess.run(['python', '--version'], 
                                              capture_output=True, text=True, timeout=2)
                if python_version.returncode == 0:
                    info.append(f"Python: {python_version.stdout.strip()}")
                else:
                    info.append("Python: (not available)")
            except subprocess.TimeoutExpired:
                info.append("Python: (timeout - may be hanging)")
            except FileNotFoundError:
                info.append("Python: (not found)")
            except Exception as e:
                info.append(f"Python: (error - {str(e)[:50]})")
            
            # Git info - with shorter timeout and better error handling
            try:
                git_version = subprocess.run(['git', '--version'], 
                                           capture_output=True, text=True, timeout=2)
                if git_version.returncode == 0:
                    info.append(f"Git: {git_version.stdout.strip()}")
                else:
                    info.append("Git: (not available)")
            except subprocess.TimeoutExpired:
                info.append("Git: (timeout - may be hanging)")
            except FileNotFoundError:
                info.append("Git: (not found)")
            except Exception as e:
                info.append(f"Git: (error - {str(e)[:50]})")
            
            # Node info - with shorter timeout and better error handling
            try:
                node_version = subprocess.run(['node', '--version'], 
                                            capture_output=True, text=True, timeout=2)
                if node_version.returncode == 0:
                    info.append(f"Node.js: {node_version.stdout.strip()}")
                else:
                    info.append("Node.js: (not available)")
            except subprocess.TimeoutExpired:
                info.append("Node.js: (timeout - may be hanging)")
            except FileNotFoundError:
                info.append("Node.js: (not found)")
            except Exception as e:
                info.append(f"Node.js: (error - {str(e)[:50]})")
            
            return "Environment Information:\n" + "\n".join(info)
            
        except Exception as e:
            self.logger.error(f"Error getting environment info: {e}")
            return f"Error getting environment info: {str(e)}"
    
    def list_processes(self) -> str:
        """List currently running processes on the system"""
        try:
            info = []
            info.append("Currently running processes:\n")
            
            # Get all processes with timeout protection
            processes = []
            start_time = time.time()
            max_collection_time = 5.0  # Maximum 5 seconds to collect processes
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    # Check timeout
                    if time.time() - start_time > max_collection_time:
                        info.append("(Process collection timeout - showing partial list)")
                        break
                        
                    proc_info = proc.info
                    # Get CPU percent without blocking (use cached value)
                    proc_info['cpu_percent'] = proc.cpu_percent() or 0
                    processes.append(proc_info)
                    
                    # Limit total processes to prevent hanging
                    if len(processes) >= 100:
                        info.append("(Showing first 100 processes)")
                        break
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                except Exception:
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            
            # Show top 20 processes
            info.append(f"{'PID':<8} {'Name':<30} {'CPU%':<8} {'Memory%':<8}")
            info.append("-" * 60)
            
            for proc in processes[:20]:
                pid = proc.get('pid', 'N/A')
                name = proc.get('name', 'N/A')[:28]
                cpu = proc.get('cpu_percent', 0)
                mem = proc.get('memory_percent', 0)
                info.append(f"{pid:<8} {name:<30} {cpu:<8.1f} {mem:<8.1f}")
            
            if len(processes) > 20:
                info.append(f"\n... and {len(processes) - 20} more processes")
            
            # Show our tracked background processes
            with self._lock:
                if self._active_processes:
                    info.append("\nBackground processes started by this tool:")
                    finished = []
                    for proc_id, process in self._active_processes.items():
                        if process.poll() is not None:
                            finished.append(proc_id)
                            info.append(f"  Process {proc_id}: Finished (exit code: {process.returncode})")
                        else:
                            info.append(f"  Process {proc_id}: Running (PID: {process.pid})")
                    
                    # Remove finished processes
                    for proc_id in finished:
                        del self._active_processes[proc_id]
            
            return "\n".join(info)
            
        except Exception as e:
            self.logger.error(f"Error listing processes: {e}")
            return f"Error listing processes: {str(e)}"
    
    def kill_process(self, process_id: int) -> str:
        """Kill a process by PID or background process ID"""
        try:
            # First check if it's one of our tracked background processes
            with self._lock:
                if process_id in self._active_processes:
                    process = self._active_processes[process_id]
                    
                    try:
                        if process.poll() is None:
                            process.terminate()
                            time.sleep(0.1)
                            
                            if process.poll() is None:
                                process.kill()
                                time.sleep(0.1)
                        
                        exit_code = process.poll()
                        del self._active_processes[process_id]
                        
                        return f"Background process {process_id} terminated (exit code: {exit_code})"
                    except Exception as e:
                        return f"Error killing background process {process_id}: {str(e)}"
            
            # If not a background process, try to kill by system PID
            proc = None
            proc_name = "unknown"
            
            try:
                proc = psutil.Process(process_id)
                proc_name = proc.name()
                proc.terminate()
                
                # Wait for termination
                proc.wait(timeout=3)
                return f"Process {process_id} ({proc_name}) terminated successfully"
                
            except psutil.TimeoutExpired:
                # Force kill if termination didn't work
                if proc is not None:
                    proc.kill()
                    return f"Process {process_id} ({proc_name}) force killed"
                else:
                    return f"Process {process_id} termination timeout but process reference lost"
                
        except psutil.NoSuchProcess:
            return f"Process {process_id} not found"
        except psutil.AccessDenied:
            return f"Access denied: Cannot kill process {process_id} (insufficient permissions)"
        except Exception as e:
            self.logger.error(f"Error killing process {process_id}: {e}")
            return f"Error killing process {process_id}: {str(e)}"
    
    def get_system_info(self) -> str:
        """Get comprehensive system information"""
        try:
            info = []
            
            # System basics
            info.append("System Information:")
            info.append(f"  Platform: {platform.platform()}")
            info.append(f"  System: {platform.system()}")
            info.append(f"  Release: {platform.release()}")
            info.append(f"  Version: {platform.version()}")
            info.append(f"  Machine: {platform.machine()}")
            info.append(f"  Processor: {platform.processor()}")
            
            # CPU information
            cpu_count = psutil.cpu_count()
            # Use non-blocking CPU percent check
            cpu_percent = psutil.cpu_percent() or 0
            info.append(f"\nCPU Information:")
            info.append(f"  Physical cores: {psutil.cpu_count(logical=False)}")
            info.append(f"  Total cores: {cpu_count}")
            info.append(f"  Current usage: {cpu_percent}% (cached)")
            
            # Memory information
            memory = psutil.virtual_memory()
            info.append(f"\nMemory Information:")
            info.append(f"  Total: {memory.total / (1024**3):.1f} GB")
            info.append(f"  Available: {memory.available / (1024**3):.1f} GB")
            info.append(f"  Used: {memory.used / (1024**3):.1f} GB ({memory.percent}%)")
            
            # Disk information
            disk = psutil.disk_usage('/')
            info.append(f"\nDisk Information (root):")
            info.append(f"  Total: {disk.total / (1024**3):.1f} GB")
            info.append(f"  Used: {disk.used / (1024**3):.1f} GB ({disk.used/disk.total*100:.1f}%)")
            info.append(f"  Free: {disk.free / (1024**3):.1f} GB")
            
            # Network information
            try:
                network = psutil.net_if_addrs()
                info.append(f"\nNetwork Interfaces:")
                for interface, addresses in network.items():
                    info.append(f"  {interface}:")
                    for addr in addresses:
                        if addr.family.name == 'AF_INET':
                            info.append(f"    IPv4: {addr.address}")
                        elif addr.family.name == 'AF_INET6':
                            info.append(f"    IPv6: {addr.address}")
            except:
                info.append(f"\nNetwork: Information unavailable")
            
            # Boot time
            boot_time = psutil.boot_time()
            boot_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(boot_time))
            info.append(f"\nSystem Boot Time: {boot_time_str}")
            
            return "\n".join(info)
            
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return f"Error getting system info: {str(e)}"
    
    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        """Return all available shell tools with their metadata."""
        return {
            'bb7_run_command': {
                "callable": lambda command, working_dir=None, timeout=30: self.run_command(command, working_dir, timeout),
                "metadata": {
                    "name": "bb7_run_command",
                    "description": "⚡ Execute shell commands with full output capture. Use for running builds, tests, git operations, system commands, or any command-line tasks. Provides detailed execution results.",
                    "category": "shell",
                    "priority": "high",
                    "when_to_use": ["builds", "tests", "git_ops", "system_commands", "installation"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "command": { "type": "string", "description": "Shell command to execute" },
                            "working_dir": { "type": "string", "description": "Working directory for command" },
                            "timeout": { "type": "integer", "default": 30, "description": "Command timeout in seconds" }
                        },
                        "required": ["command"]
                    }
                }
            },
            'bb7_run_script': {
                "callable": lambda script_content, script_type="bash", working_dir=None: self.run_script(script_content, script_type, working_dir),
                "metadata": {
                    "name": "bb7_run_script",
                    "description": "📜 Execute scripts from content strings. Supports bash, python, javascript, and powershell. Use for running complex multi-line scripts or generated code without creating temporary files.",
                    "category": "shell",
                    "priority": "medium",
                    "when_to_use": ["script_execution", "code_testing", "automation", "multi_line_commands"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "script_content": { "type": "string", "description": "Script content to execute" },
                            "script_type": { "type": "string", "enum": ["bash", "python", "javascript", "powershell"], "default": "bash" },
                            "working_dir": { "type": "string", "description": "Working directory" }
                        },
                        "required": ["script_content"]
                    }
                }
            },
            'bb7_get_environment': {
                "callable": self.get_environment,
                "metadata": {
                    "name": "bb7_get_environment",
                    "description": "🌍 Get comprehensive environment information including PATH, user context, installed tools, and development environment details. Use for troubleshooting, setup verification, or environment analysis.",
                    "category": "shell",
                    "priority": "low",
                    "when_to_use": ["environment_check", "troubleshooting", "setup_verification", "tool_discovery"],
                    "input_schema": { "type": "object", "properties": {}, "required": [] }
                }
            },
            'bb7_list_processes': {
                "callable": self.list_processes,
                "metadata": {
                    "name": "bb7_list_processes",
                    "description": "🔄 List running system processes with CPU and memory usage. Use for system monitoring, finding processes, or understanding system state.",
                    "category": "shell",
                    "priority": "low",
                    "when_to_use": ["system_monitoring", "process_discovery", "performance_analysis", "debugging"],
                    "input_schema": { "type": "object", "properties": {}, "required": [] }
                }
            },
            'bb7_kill_process': {
                "callable": self.kill_process,
                "metadata": {
                    "name": "bb7_kill_process",
                    "description": "🛑 Terminate processes by PID. Use carefully for stopping hung processes or cleaning up background tasks. Includes safety checks.",
                    "category": "shell",
                    "priority": "low",
                    "when_to_use": ["process_termination", "cleanup", "hung_processes", "system_management"],
                    "input_schema": {
                        "type": "object",
                        "properties": { "process_id": { "type": "integer", "description": "Process ID to terminate" } },
                        "required": ["process_id"]
                    }
                }
            },
            'bb7_get_system_info': {
                "callable": self.get_system_info,
                "metadata": {
                    "name": "bb7_get_system_info",
                    "description": "💻 Get comprehensive system information including hardware, OS, CPU, memory, disk, and network details. Use for system analysis, troubleshooting, or environment documentation.",
                    "category": "shell",
                    "priority": "low",
                    "when_to_use": ["system_analysis", "hardware_info", "troubleshooting", "documentation"],
                    "input_schema": { "type": "object", "properties": {}, "required": [] }
                }
            }
        }


# For standalone testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    shell = ShellTool()
    
    # Test basic operations
    print(shell.get_environment())
    print("\n" + "="*50 + "\n")
    print(shell.run_command("echo 'Hello from shell!'"))
    print("\n" + "="*50 + "\n")
    print(shell.get_system_info())
