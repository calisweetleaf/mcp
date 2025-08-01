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
- Secure Python execution with sandboxing (term noted for documentation)
- Real-time tool registration and management

Architecture:
- Modular tool system with dynamic loading
- Cross-platform compatibility (Windows, Linux, macOS)
- Resource monitoring and security controls
- Comprehensive audit logging
- MCP standard compliance
"""

import os
import sys
import json
import time
import logging
import traceback
import hashlib
import threading
import importlib
import pkgutil
import inspect
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional


class MCPServer:
    """
    Main MCP Server class. Handles initialization, tool registration, session and memory management.
    Ensures robust error handling and diagnostics during startup.
    """
    def __init__(self, config_path=None):
        self.config_path = config_path or os.path.join(os.path.dirname(__file__), '.vscode', 'mcp.json')
        self.tools: Dict[str, Any] = {}
        self.tool_registry: Dict[str, Dict[str, Any]] = {}
        self.tool_instances: Dict[str, Any] = {}
        self.sessions: Dict[str, Any] = {}
        self.memory = None
        self.logger = self._setup_logger()
        self._initialized = False
        self.debug = False
        self.data_dir = Path('data')
        self.data_dir.mkdir(exist_ok=True)
        # Initialize metrics and server info used later
        self.server_info: Dict[str, Any] = {"total_tools": 0}
        self.performance_metrics: Dict[str, Any] = {
            "tool_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "average_response_time": 0.0,
            "last_activity": None,
        }
        # L1/L2 KV cache structures
        self._cache_lock = threading.Lock()
        self._l1_cache: Dict[str, Tuple[Optional[float], Any]] = {}  # key -> (expiry_ts, value)
        self._default_ttl = 5.0  # seconds; conservative default
        # L2 uses EnhancedMemoryTool via self.memory once initialized
        try:
            self._init_server()
        except Exception as e:
            self.logger.error(f'Fatal error during initialization: {e}')
            self.logger.error(traceback.format_exc())
            self._initialized = False
            # Do not exit immediately; allow diagnostics and graceful failure

    def _setup_logger(self):
        logger = logging.getLogger('SovereignMCP')
        logger.setLevel(logging.INFO)
        log_path = os.path.join('data', 'mcp_server.log')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        handler = logging.FileHandler(log_path, encoding='utf-8')
        # Using standard logging format fields: asctime, levelname, message
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        if not logger.hasHandlers():
            logger.addHandler(handler)
        return logger

    def _init_server(self):
        self.logger.info('Initializing MCP Server...')
        self._check_dependencies()
        self._load_config()
        self._load_tools()
        self._init_memory()
        self._initialized = True
        self.logger.info('MCP Server initialized successfully.')

    def _check_dependencies(self):
        """
        Checks for required files, directories, and Python packages. Logs and raises errors if missing.
        """
        required_dirs = ['data', 'tools', 'tests', 'docs']
        for d in required_dirs:
            if not os.path.isdir(d):
                self.logger.error(f'Required directory missing: {d}')
                raise FileNotFoundError(f'Required directory missing: {d}')
        required_files = [self.config_path]
        for f in required_files:
            if not os.path.exists(f):
                self.logger.error(f'Required file missing: {f}')
        required_packages = [
            'RestrictedPython', 'Pillow', 'psutil', 'mss', 'pyautogui',
            'pynput', 'pytesseract', 'pyperclip', 'jsonrpcserver'
        ]
        missing = []
        for pkg in required_packages:
            try:
                importlib.import_module(pkg)
            except ImportError:
                missing.append(pkg)
        if missing:
            self.logger.warning(f'Missing optional Python packages (some tools may degrade): {missing}')

    def _load_config(self):
        """Loads server configuration from the config file and sets runtime flags."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                # JSONC tolerant: strip comments '//' simple heuristic
                raw = f.read()
                lines = []
                for line in raw.splitlines():
                    stripped = line.strip()
                    if stripped.startswith('//'):
                        continue
                    idx = stripped.find('//')
                    if idx != -1 and not stripped.lower().startswith('http'):
                        line = line[:line.index('//')]
                    lines.append(line)
                cfg = json.loads('\n'.join(lines))
            servers = cfg.get('servers', {})
            self.server_info['config_servers'] = list(servers.keys())
            # Enable debug if environment variable or config flag present
            self.debug = bool(os.environ.get('MCP_DEBUG', '').strip() or cfg.get('debug', False))
            if self.debug:
                self.logger.setLevel(logging.DEBUG)
                self.logger.debug('Debug mode enabled via configuration.')
            # Cache settings
            cache_cfg = cfg.get('cache', {})
            if isinstance(cache_cfg, dict):
                self._default_ttl = float(cache_cfg.get('default_ttl', self._default_ttl))
        except Exception as e:
            self.logger.error(f"Failed to load config '{self.config_path}': {e}")
            raise

    def _load_tools(self):
        """Dynamically loads and registers all tool modules using register_tools()."""
        try:
            self.register_tools()
        except Exception as e:
            self.logger.error(f"Tool registration failed: {e}")
            self.logger.error(traceback.format_exc())
            raise

    def _init_memory(self):
        """Initializes persistent memory subsystem if available."""
        try:
            from tools.memory_tool import EnhancedMemoryTool  # type: ignore
            self.memory = EnhancedMemoryTool()
            self.logger.info('EnhancedMemoryTool initialized.')
        except Exception as e:
            self.memory = None
            self.logger.warning(f'EnhancedMemoryTool not available or failed to init: {e}')

    def respond_to_initialize(self):
        """
        Responds to initialize requests. Returns error if server is not initialized.
        """
        if not self._initialized:
            self.logger.error('Server not initialized. Cannot respond to initialize request.')
            return {'error': 'Server not initialized'}
        return {'status': 'initialized', 'total_tools': len(self.tools)}

    # -------------------- Tool Registration --------------------
    def register_tools(self):
        """Register all available MCP tools from modules by dynamically importing them."""
        from pathlib import Path

        self.logger.info("Starting tool registration...")

        # Keep instances of tool classes alive
        if not hasattr(self, 'tool_instances'):
            self.tool_instances = {}

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
                
                # Find all tool classes in the module
                tool_classes = [obj for name, obj in inspect.getmembers(module, inspect.isclass) 
                                if name.endswith("Tool") and obj.__module__ == module.__name__]

                if not tool_classes:
                    self.logger.debug(f"No suitable *Tool class found in {mod_name}, skipping.")
                    continue

                for tool_class in tool_classes:
                    # Instantiate the tool class if not already done
                    if tool_class.__name__ not in self.tool_instances:
                        self.tool_instances[tool_class.__name__] = tool_class()
                    
                    tool_instance = self.tool_instances[tool_class.__name__]

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
                            self.tools[tool_name] = tool_info
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
        categories: Dict[str, List[str]] = {}
        for tool_name in self.tools:
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

    def _make_cache_key(self, tool_name: str, kwargs: Dict[str, Any]) -> str:
        try:
            payload = json.dumps({"tool": tool_name, "args": kwargs}, sort_keys=True, default=str)
        except Exception:
            payload = f"{tool_name}:{str(kwargs)}"
        return hashlib.md5(payload.encode('utf-8')).hexdigest()

    def _l1_get(self, key: str) -> Optional[Any]:
        now = time.time()
        with self._cache_lock:
            entry = self._l1_cache.get(key)
            if not entry:
                return None
            expiry, value = entry
            if expiry is not None and now > expiry:
                # expired
                del self._l1_cache[key]
                return None
            return value

    def _l1_set(self, key: str, value: Any, ttl: Optional[float]):
        expiry = (time.time() + ttl) if ttl and ttl > 0 else None
        with self._cache_lock:
            self._l1_cache[key] = (expiry, value)

    def _l2_get(self, key: str) -> Optional[Any]:
        # Use EnhancedMemoryTool if available
        if not self.memory:
            return None
        try:
            result = self.memory.retrieve(f"cache:{key}")
            if result and not result.startswith("Key 'cache:"):
                return result
        except Exception:
            return None
        return None

    def _l2_set(self, key: str, value: Any, ttl: Optional[float]):
        if not self.memory:
            return
        try:
            payload = json.dumps({"value": value, "ts": time.time(), "ttl": ttl}, ensure_ascii=False)
            self.memory.store(f"cache:{key}", payload, category="technical", importance=0.3, tags=["cache"])  # best-effort
        except Exception:
            self.logger.error(f"Failed to store in L2 cache: {key} - {value}")
            self.logger.error(traceback.format_exc())
    def call_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Call a tool with comprehensive error handling, monitoring, and caching"""
        start_time = time.time()
        self.performance_metrics["tool_calls"] += 1
        self.performance_metrics["last_activity"] = start_time
        
        # Determine cacheability from registry metadata
        meta = self.tool_registry.get(tool_name, {})
        cache_ttl = meta.get('cache_ttl', self._default_ttl) if isinstance(meta, dict) else self._default_ttl
        cache_enabled = bool(meta.get('cache', True)) if isinstance(meta, dict) else True
        cache_key = self._make_cache_key(tool_name, kwargs) if cache_enabled else None
        try:
            # Try cache first (L1 then L2)
            if cache_enabled and cache_key:
                cached = self._l1_get(cache_key)
                if cached is None:
                    l2 = self._l2_get(cache_key)
                    if l2 is not None:
                        cached = l2
                        self._l1_set(cache_key, cached, cache_ttl)
                if cached is not None:
                    execution_time = time.time() - start_time
                    self.performance_metrics["successful_calls"] += 1
                    self.update_average_response_time(execution_time)
                    return {"success": True, "cached": True, "result": cached}

            if tool_name not in self.tools:
                self.performance_metrics["failed_calls"] += 1
                msg = f"Tool '{tool_name}' not found"
                self.logger.error(msg)
                return {"success": False, "error": "NOT_FOUND", "message": msg}

            self.logger.debug(f"Calling tool: {tool_name} with args: {kwargs}")
            tool_func = self.tools[tool_name]
            if callable(tool_func):
                result = tool_func(**kwargs)
                execution_time = time.time() - start_time
                self.performance_metrics["successful_calls"] += 1
                self.update_average_response_time(execution_time)
                # Set cache after successful execution
                if cache_enabled and cache_key:
                    self._l1_set(cache_key, result, cache_ttl)
                    self._l2_set(cache_key, result, cache_ttl)
                return {"success": True, "cached": False, "result": result, "time_ms": int(execution_time * 1000)}
            else:
                self.performance_metrics["failed_calls"] += 1
                msg = f"Tool '{tool_name}' is not callable"
                self.logger.error(msg)
                return {"success": False, "error": "NOT_CALLABLE", "message": msg}
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

    def run(self, host: str = '127.0.0.1', port: int = 5000):
        """Starts the JSON-RPC2 server and listens for incoming requests.

        Args:
            host (str): The host address to bind the server to.
            port (int): The port number to listen on.
        """
        if not self._initialized:
            self.logger.error("Server not initialized. Cannot start.")
            return

        # Prefer fastmcp if available; fallback to jsonrpcserver
        try:
            from jsonrpcserver import serve
            from jsonrpcserver.methods import Methods
            from jsonrpcserver.exceptions import JsonRpcError

            methods = Methods()

            # Register all tools as JSON-RPC methods
            for tool_name in self.tools:
                def _tool_wrapper(tool_name=tool_name):
                    def handler(**kwargs):
                        try:
                            self.logger.info(f"Received RPC call for tool: {tool_name} with args: {kwargs}")
                            result = self.call_tool(tool_name, **kwargs)
                            if not result.get("success"):
                                error_message = result.get("message", "Tool execution failed")
                                error_code = -32000  # Application error
                                if result.get("error") == "NOT_FOUND":
                                    error_code = -32601  # Method not found
                                elif result.get("error") == "PARAMETER_ERROR":
                                    error_code = -32602  # Invalid params
                                raise JsonRpcError(error_message, code=error_code, data=result)
                            return result.get("result")
                        except JsonRpcError:
                            raise
                        except Exception as ex:
                            self.logger.error(f"Error in RPC tool wrapper for {tool_name}: {ex}")
                            self.logger.error(traceback.format_exc())
                            raise JsonRpcError(f"Internal server error during tool execution: {ex}", code=-32000)
                    return handler

                methods.register(_tool_wrapper(), name=tool_name)

            self.logger.info(f"Starting MCP Server on {host}:{port}...")
            self.logger.info("Press Ctrl+C to shut down.")
            serve(methods, host=host, port=port)
                
        except ImportError:
            self.logger.error("Neither fastmcp nor jsonrpcserver is available. Please install one:\n"
                              "pip install fastmcp\nor\npip install jsonrpcserver")

            # Flush session tracking
    def shutdown(self):
        """Gracefully shutdown the server and clean up resources."""
        self.logger.info("Shutting down MCP Server...")
        
        # Flush session tracking
        if hasattr(self, "sessions") and isinstance(self.sessions, dict):
            try:
                # Persist a minimal session snapshot
                snapshot = {
                    "active_sessions": list(self.sessions.keys()),
                    "last_activity": self.performance_metrics.get("last_activity"),
                    "timestamp": time.time(),
                }
                sessions_dir = self.data_dir / "sessions"
                sessions_dir.mkdir(parents=True, exist_ok=True)
                with open(sessions_dir / "last_shutdown.json", "w", encoding="utf-8") as f:
                    json.dump(snapshot, f, ensure_ascii=False, indent=2)
            except Exception as e:
                self.logger.warning(f"Failed to persist session snapshot: {e}")

        # Persist L1 cache to L2 (memory) best-effort
        try:
            if self._l1_cache:
                with self._cache_lock:
                    for key, (expiry, value) in list(self._l1_cache.items()):
                        ttl = None
                        if expiry is not None:
                            ttl = max(0.0, expiry - time.time())
                        self._l2_set(key, value, ttl)
        except Exception as e:
            self.logger.warning(f"Failed to persist L1 cache to memory: {e}")

        # Give tools a chance to cleanup if they expose a shutdown/close method
        try:
            for name, instance in getattr(self, "tool_instances", {}).items():
                try:
                    if hasattr(instance, "shutdown") and callable(getattr(instance, "shutdown")):
                        instance.shutdown()
                    elif hasattr(instance, "close") and callable(getattr(instance, "close")):
                        instance.close()
                except Exception as tool_err:
                    self.logger.debug(f"Tool '{name}' cleanup error: {tool_err}")
        except Exception as e:
            self.logger.warning(f"Tool cleanup sweep failed: {e}")

        # Attempt to flush memory tool if it supports it
        try:
            if self.memory and hasattr(self.memory, "flush") and callable(getattr(self.memory, "flush")):
                self.memory.flush()
        except Exception as e:
            self.logger.debug(f"Memory flush failed: {e}")


if __name__ == '__main__':
    # Configure logging for console output as well
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    root_logger = logging.getLogger('SovereignMCP')
    if not root_logger.hasHandlers():
        root_logger.addHandler(console_handler)
    else:
        root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)

    server = MCPServer()
    try:
        server.run()
    except KeyboardInterrupt:
        try:
            server.shutdown()
        except Exception as ex:
            server.logger.error(f"Shutdown encountered an error: {ex}")
            server.logger.error(traceback.format_exc())
    except Exception as main_e:
        server.logger.critical(f"Unhandled exception in main server loop: {main_e}")
        server.logger.critical(traceback.format_exc())
    finally:
        try:
            server.shutdown()
        except Exception as ex:
            server.logger.error(f"Shutdown encountered an error: {ex}")
            server.logger.error(traceback.format_exc())