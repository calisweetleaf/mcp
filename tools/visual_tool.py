"""
Visual Awareness Tool for MCP Server - Fixed Version
Enables true AI-human partnership through screen awareness and visual interaction.
All tools are always available with graceful error handling for missing dependencies.
"""

import base64
import io
import json
import logging
import os
import platform
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Callable

# Import dependencies with graceful fallbacks
try:
    import mss
    import mss.tools  # <-- Add this import
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import pynput
    from pynput import keyboard, mouse
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

# Windows-specific imports
if platform.system() == "Windows":
    try:
        import win32gui
        import win32process
        import win32api
        import win32con
        import win32clipboard
        WIN32_AVAILABLE = True
    except ImportError:
        WIN32_AVAILABLE = False
else:
    WIN32_AVAILABLE = False


class VisualTool:
    """Visual awareness and interaction capabilities for true AI partnership"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.temp_dir = Path(tempfile.gettempdir()) / "mcp_visual"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Initialize available capabilities
        self.capabilities = self._check_capabilities()
        self.logger.info(f"Visual tool initialized with capabilities: {self.capabilities}")
    
    def _check_capabilities(self) -> Dict[str, bool]:
        """Check which visual capabilities are available"""        
        return {
            "screenshot": MSS_AVAILABLE or PYAUTOGUI_AVAILABLE,
            "image_processing": PIL_AVAILABLE,
            "automation": PYAUTOGUI_AVAILABLE,
            "input_control": PYNPUT_AVAILABLE,
            "windows_specific": WIN32_AVAILABLE,
            "ocr": PYTESSERACT_AVAILABLE and PIL_AVAILABLE
        }
    
    def get_tools(self) -> Dict[str, Dict[str, Any]]:
        """Return all visual tools with their metadata."""
        return {
            'bb7_screen_capture': {
                "callable": lambda monitor=0, region=None, save_path=None, format="base64": self._screen_capture({"monitor": monitor, "region": region, "save_path": save_path, "format": format}),
                "metadata": {
                    "name": "bb7_screen_capture",
                    "description": "📸 VISUAL PARTNERSHIP: Take screenshots for debugging, UI analysis, and visual understanding. Enables AI to see exactly what you see! Use for error screenshots, UI feedback, or visual documentation.",
                    "category": "visual",
                    "priority": "medium",
                    "when_to_use": ["debugging", "ui_analysis", "visual_feedback", "documentation", "error_capture"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "monitor": { "type": "integer", "default": 0, "description": "Monitor to capture (0=primary, -1=all)" },
                            "region": { "type": "object", "description": "Specific region {x, y, width, height}" },
                            "save_path": { "type": "string", "description": "Optional file save path" },
                            "format": { "type": "string", "enum": ["png", "jpg", "base64"], "default": "base64" }
                        },
                        "required": []
                    }
                }
            },
            'bb7_screen_monitor': {
                "callable": lambda duration=5, threshold=0.1, save_frames=False: self._screen_monitor({"duration": duration, "threshold": threshold, "save_frames": save_frames}),
                "metadata": {
                    "name": "bb7_screen_monitor",
                    "description": "Monitor the screen for visual changes over time, detecting UI updates or unexpected modifications.",
                    "category": "visual",
                    "priority": "medium",
                    "when_to_use": ["ui_monitoring", "visual_debugging", "change_detection"],
                    "input_schema": {"type": "object", "properties": {"duration": {"type": "integer", "default": 10}, "interval": {"type": "number", "default": 1.0}}, "required": []}
                }
            },
            'bb7_visual_diff': {
                "callable": lambda image1_path, image2_path, threshold=0.1, highlight_changes=True: self._visual_diff({"image1_path": image1_path, "image2_path": image2_path, "threshold": threshold, "highlight_changes": highlight_changes}),
                "metadata": {
                    "name": "bb7_visual_diff",
                    "description": "Compare two images or screenshots to detect and highlight visual differences.",
                    "category": "visual",
                    "priority": "medium",
                    "when_to_use": ["visual_testing", "ui_comparison", "regression_detection"],
                    "input_schema": {"type": "object", "properties": {"image1_path": {"type": "string"}, "image2_path": {"type": "string"}, "threshold": {"type": "number", "default": 0.1}}, "required": ["image1_path", "image2_path"]}
                }
            },
            'bb7_window_manager': {
                "callable": lambda action, window_title=None, position=None, size=None: self._window_manager({"action": action, "window_title": window_title, "position": position, "size": size}),
                "metadata": {
                    "name": "bb7_window_manager",
                    "description": "🪟 WORKSPACE AWARENESS: Manage windows and understand workspace layout. List windows, switch focus, resize, or organize the development environment.",
                    "category": "visual",
                    "priority": "low",
                    "when_to_use": ["window_management", "workspace_organization", "focus_control", "layout_management"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "action": { "type": "string", "enum": ["list", "focus", "minimize", "maximize", "close", "move", "resize"] },
                            "window_title": { "type": "string", "description": "Target window title" }
                        },
                        "required": ["action"]
                    }
                }
            },
            'bb7_active_window': {
                "callable": lambda include_geometry=True: self._active_window({"include_geometry": include_geometry}),
                "metadata": {
                    "name": "bb7_active_window",
                    "description": "Retrieve information about the currently active window, including title and geometry.",
                    "category": "visual",
                    "priority": "low",
                    "when_to_use": ["window_management", "context_awareness", "ui_information"],
                    "input_schema": {"type": "object", "properties": {"include_geometry": {"type": "boolean", "default": True}}, "required": []}
                }
            },
            'bb7_keyboard_input': {
                "callable": lambda text=None, keys=None, hotkey=None, delay=0.1: self._keyboard_input({"text": text, "keys": keys, "hotkey": hotkey, "delay": delay}),
                "metadata": {
                    "name": "bb7_keyboard_input",
                    "description": "⌨️ AUTOMATION: Send keystrokes and keyboard shortcuts for automation and UI interaction. Type alongside the user, trigger shortcuts, or automate repetitive input tasks.",
                    "category": "visual",
                    "priority": "medium",
                    "when_to_use": ["automation", "ui_interaction", "shortcuts", "text_input", "testing"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "text": { "type": "string", "description": "Text to type" },
                            "keys": { "type": "array", "items": {"type": "string"}, "description": "Special keys to press" },
                            "hotkey": { "type": "string", "description": "Hotkey combination (e.g., 'ctrl+c')" },
                            "delay": { "type": "number", "default": 0.1 }
                        },
                        "required": []
                    }
                }
            },
            'bb7_mouse_control': {
                "callable": lambda action, x=None, y=None, button="left", drag_to=None, scroll_direction=None, scroll_amount=3: self._mouse_control({"action": action, "x": x, "y": y, "button": button, "drag_to": drag_to, "scroll_direction": scroll_direction, "scroll_amount": scroll_amount}),
                "metadata": {
                    "name": "bb7_mouse_control",
                    "description": "🖱️ AUTOMATION: Control mouse for clicking, dragging, and UI interaction. Click buttons, navigate interfaces, or automate mouse-based tasks.",
                    "category": "visual",
                    "priority": "medium",
                    "when_to_use": ["ui_automation", "clicking", "dragging", "interface_navigation", "testing"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "action": { "type": "string", "enum": ["click", "double_click", "right_click", "drag", "scroll", "move"] },
                            "x": {"type": "integer"},
                            "y": {"type": "integer"},
                            "button": { "type": "string", "enum": ["left", "right", "middle"], "default": "left" }
                        },
                        "required": ["action"]
                    }
                }
            },
            'bb7_clipboard_manage': {
                "callable": lambda action, text=None, format="text": self._clipboard_manage({"action": action, "text": text, "format": format}),
                "metadata": {
                    "name": "bb7_clipboard_manage",
                    "description": "📋 DATA EXCHANGE: Read/write clipboard for seamless data sharing between AI and human. Perfect for code snippets, URLs, or any text exchange.",
                    "category": "visual",
                    "priority": "medium",
                    "when_to_use": ["data_exchange", "clipboard_access", "text_sharing", "copy_paste", "data_transfer"],
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "action": { "type": "string", "enum": ["read", "write", "clear", "history"] },
                            "text": { "type": "string", "description": "Text to write to clipboard" }
                        },
                        "required": ["action"]
                    }
                }
            }
        }
    
    def handle_tool_call(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle visual tool calls"""
        try:
            if name == "bb7_screen_capture":
                return self._screen_capture(arguments)
            elif name == "bb7_screen_monitor":
                return self._screen_monitor(arguments)
            elif name == "bb7_visual_diff":
                return self._visual_diff(arguments)
            elif name == "bb7_window_manager":
                return self._window_manager(arguments)
            elif name == "bb7_active_window":
                return self._active_window(arguments)
            elif name == "bb7_keyboard_input":
                return self._keyboard_input(arguments)
            elif name == "bb7_mouse_control":
                return self._mouse_control(arguments)
            elif name == "bb7_clipboard_manage":
                return self._clipboard_manage(arguments)
            else:
                return {"error": f"Unknown visual tool: {name}"}
                
        except Exception as e:
            self.logger.error(f"Error in visual tool {name}: {e}")
            return {"error": f"Visual tool error: {str(e)}"}
    
    def _screen_capture(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Take screenshot with proper dependency checking"""
        try:
            if not MSS_AVAILABLE and not PYAUTOGUI_AVAILABLE:
                return {"error": "Screenshot functionality requires 'mss' or 'pyautogui' library. Install with: pip install mss pyautogui"}
            
            monitor = args.get("monitor", 0)
            region = args.get("region")
            save_path = args.get("save_path")
            format_type = args.get("format", "base64")
            
            img = None
            
            # Try MSS first
            if MSS_AVAILABLE:
                with mss.mss() as sct:
                    if region:
                        capture_region = {
                            "left": region["x"],
                            "top": region["y"],
                            "width": region["width"],
                            "height": region["height"]
                        }
                        screenshot = sct.grab(capture_region)
                    else:
                        mon_num = monitor + 1 if monitor >= 0 else 1
                        if mon_num < len(sct.monitors):
                            screenshot = sct.grab(sct.monitors[mon_num])
                        else:
                            return {"error": f"Monitor {monitor} not found"}
                    
                    if PIL_AVAILABLE:
                        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                    else:
                        # Save without PIL
                        temp_path = self.temp_dir / f"screenshot_{int(time.time())}.png"
                        mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(temp_path))
                        return {
                            "success": True,
                            "message": f"Screenshot saved to {temp_path}",
                            "path": str(temp_path),
                            "size": {"width": screenshot.size[0], "height": screenshot.size[1]}
                        }
            
            # Fallback to pyautogui
            elif PYAUTOGUI_AVAILABLE:
                if region:
                    img = pyautogui.screenshot(region=(region["x"], region["y"], region["width"], region["height"]))
                else:
                    img = pyautogui.screenshot()
            
            if img is None:
                return {"error": "Failed to capture screenshot"}
            
            # Process result
            if save_path:
                img.save(save_path)
                return {
                    "success": True,
                    "message": f"Screenshot saved to {save_path}",
                    "path": save_path,
                    "size": {"width": img.width, "height": img.height}
                }
            elif format_type == "base64":
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                img_str = base64.b64encode(buffer.getvalue()).decode()
                return {
                    "success": True,
                    "image_base64": img_str,
                    "size": {"width": img.width, "height": img.height},
                    "message": "Screenshot captured successfully! 👀"
                }
            else:
                temp_path = self.temp_dir / f"screenshot_{int(time.time())}.{format_type}"
                img.save(temp_path, format=format_type.upper())
                return {
                    "success": True,
                    "path": str(temp_path),
                    "size": {"width": img.width, "height": img.height},
                    "message": f"Screenshot saved to {temp_path}"
                }
            
        except Exception as e:
            return {"error": f"Screenshot failed: {str(e)}"}
    
    def _screen_monitor(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor screen changes"""
        try:
            if not MSS_AVAILABLE and not PYAUTOGUI_AVAILABLE:
                return {"error": "Screen monitoring requires screenshot capability. Install: pip install mss pyautogui"}
            
            duration = args.get("duration", 10)
            interval = args.get("interval", 1.0)
            
            changes_detected = []
            last_screenshot = None
            
            start_time = time.time()
            while time.time() - start_time < duration:
                current_result = self._screen_capture({"format": "base64"})
                if "error" in current_result:
                    return current_result
                
                current_data = current_result["image_base64"]
                
                if last_screenshot and current_data != last_screenshot:
                    changes_detected.append({
                        "timestamp": time.time(),
                        "message": "Screen change detected"
                    })
                
                last_screenshot = current_data
                time.sleep(interval)
            
            return {
                "success": True,
                "monitoring_duration": duration,
                "changes_detected": len(changes_detected),
                "changes": changes_detected,
                "message": f"Screen monitoring complete. Detected {len(changes_detected)} changes."
            }
            
        except Exception as e:
            return {"error": f"Screen monitoring failed: {str(e)}"}
    
    def _visual_diff(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two images"""
        try:
            if not PIL_AVAILABLE:
                return {"error": "Visual diff requires PIL library. Install with: pip install Pillow"}
            
            image1_path = args["image1_path"]
            image2_path = args["image2_path"]
            threshold = args.get("threshold", 0.1)
            
            img1 = Image.open(image1_path)
            img1 = Image.open(image1_path)
            img2 = Image.open(image2_path)
            
            if img1.size != img2.size:
                img2 = img2.resize(img1.size)
            
            gray1 = img1.convert('L')
            gray2 = img2.convert('L')
            
            diff_pixels = 0
            total_pixels = img1.width * img1.height
            
            for x in range(img1.width):
                for y in range(img1.height):
                    pixel1 = gray1.getpixel((x, y))
                    pixel2 = gray2.getpixel((x, y))
                    
                    # Ensure pixel values are integers before subtraction
                    if isinstance(pixel1, (tuple, list)):
                        pixel1 = pixel1[0]  # Take first channel for RGB
                    if isinstance(pixel2, (tuple, list)):
                        pixel2 = pixel2[0]  # Take first channel for RGB
                    
                    # Handle None values
                    if pixel1 is None or pixel2 is None:
                        continue
                    
                    if abs(int(pixel1) - int(pixel2)) > threshold * 255:
                        diff_pixels += 1
            
            difference_ratio = diff_pixels / total_pixels
            
            return {
                "success": True,
                "difference_ratio": difference_ratio,
                "different_pixels": diff_pixels,
                "total_pixels": total_pixels,
                "significant_change": difference_ratio > threshold
            }
            
        except Exception as e:
            return {"error": f"Visual diff failed: {str(e)}"}
    
    def _window_manager(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Manage windows"""
        try:
            action = args["action"]
            
            if action == "list":
                return self._list_windows()
            elif action in ["focus", "minimize", "maximize", "close"]:
                window_title = args.get("window_title")
                if not window_title:
                    return {"error": f"window_title required for {action} action"}
                return self._window_action(action, window_title)
            else:
                return {"error": f"Unknown window action: {action}"}
                
        except Exception as e:
            return {"error": f"Window management failed: {str(e)}"}
    
    def _list_windows(self) -> Dict[str, Any]:
        """List all visible windows"""
        try:
            if not WIN32_AVAILABLE:
                return {"error": "Window listing requires Windows platform and pywin32 library. Install with: pip install pywin32"}
            
            windows = []
            
            def enum_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        rect = win32gui.GetWindowRect(hwnd)
                        windows.append({
                            "title": title,
                            "hwnd": hwnd,
                            "geometry": {
                                "x": rect[0], "y": rect[1],
                                "width": rect[2] - rect[0],
                                "height": rect[3] - rect[1]
                            }
                        })
                return True
            
            win32gui.EnumWindows(enum_callback, windows)
            
            return {
                "success": True,
                "windows": windows,
                "count": len(windows),
                "message": f"Found {len(windows)} visible windows"
            }
            
        except Exception as e:
            return {"error": f"Failed to list windows: {str(e)}"}
    
    def _window_action(self, action: str, window_title: str) -> Dict[str, Any]:
        """Perform action on specific window"""
        try:
            if not WIN32_AVAILABLE:
                return {"error": "Window actions require Windows platform and pywin32 library. Install with: pip install pywin32"}
            
            # Find window
            hwnd = win32gui.FindWindow(None, window_title)
            if not hwnd:
                # Try partial match
                def find_callback(hwnd, param):
                    title = win32gui.GetWindowText(hwnd)
                    if window_title.lower() in title.lower():
                        param["hwnd"] = hwnd
                        return False
                    return True
                
                param = {"hwnd": None}
                win32gui.EnumWindows(find_callback, param)
                hwnd = param["hwnd"]
            
            if not hwnd:
                return {"error": f"Window '{window_title}' not found"}
            
            # Perform action
            if action == "focus":
                win32gui.SetForegroundWindow(hwnd)
            elif action == "minimize":
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            elif action == "maximize":
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            elif action == "close":
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            
            return {
                "success": True,
                "message": f"Successfully performed {action} on '{window_title}'"
            }
            
        except Exception as e:
            return {"error": f"Window action failed: {str(e)}"}
    
    def _active_window(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get active window information"""
        try:
            if not WIN32_AVAILABLE:
                return {"error": "Active window detection requires Windows platform and pywin32 library. Install with: pip install pywin32"}
            
            include_geometry = args.get("include_geometry", True)
            
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            
            result = {
                "success": True,
                "title": title,
                "hwnd": hwnd
            }
            
            if include_geometry:
                rect = win32gui.GetWindowRect(hwnd)
                result["geometry"] = {
                    "x": rect[0], "y": rect[1],
                    "width": rect[2] - rect[0],
                    "height": rect[3] - rect[1]
                }
            
            return result
            
        except Exception as e:
            return {"error": f"Active window detection failed: {str(e)}"}
    
    def _keyboard_input(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Send keyboard input"""
        try:
            if not PYAUTOGUI_AVAILABLE and not PYNPUT_AVAILABLE:
                return {"error": "Keyboard input requires pyautogui or pynput library. Install with: pip install pyautogui pynput"}

            text = args.get("text")
            keys = args.get("keys")
            hotkey = args.get("hotkey")
            delay = args.get("delay", 0.1)

            if PYAUTOGUI_AVAILABLE:
                if text:
                    pyautogui.typewrite(text, interval=delay)
                    return {"success": True, "message": f"Typed text: '{text}' "}
                elif keys:
                    for key in keys:
                        pyautogui.press(key)
                        time.sleep(delay)
                    return {"success": True, "message": f"Pressed keys: {keys} "}
                elif hotkey:
                    pyautogui.hotkey(*hotkey.split('+'))
                    return {"success": True, "message": f"Pressed hotkey: {hotkey} "}
                else:
                    return {"error": "No text, keys, or hotkey specified"}
            
            else:  # PYNPUT_AVAILABLE must be True
                kbd = keyboard.Controller()

                if text:
                    for char in text:
                        kbd.press(char)
                        kbd.release(char)
                        time.sleep(delay)
                    return {"success": True, "message": f"Typed text: '{text}' 🎹"}
                elif keys:
                    for key_name in keys:
                        key = getattr(keyboard.Key, key_name, key_name)
                        kbd.press(key)
                        kbd.release(key)
                        time.sleep(delay)
                    return {"success": True, "message": f"Pressed keys: {keys} 🎹"}
                else:
                    return {"error": "Hotkey combinations not supported with pynput fallback"}

        except Exception as e:
            return {"error": f"Keyboard input failed: {str(e)}"}
    
    def _mouse_control(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Control mouse"""
        try:
            if not PYAUTOGUI_AVAILABLE and not PYNPUT_AVAILABLE:
                return {"error": "Mouse control requires pyautogui or pynput library. Install with: pip install pyautogui pynput"}
            
            action = args["action"]
            x = args.get("x")
            y = args.get("y")
            button = args.get("button", "left")

            # pyautogui branch
            if PYAUTOGUI_AVAILABLE:
                if action == "move":
                    if x is not None and y is not None:
                        pyautogui.moveTo(x, y)
                        return {"success": True, "message": f"Mouse moved to ({x}, {y}) 🖱️"}
                    else:
                        return {"error": "x and y coordinates required for move action"}
                elif action == "click":
                    if x is not None and y is not None:
                        pyautogui.click(x, y, button=button)
                    else:
                        pyautogui.click(button=button)
                    return {"success": True, "message": f"Clicked with {button} button 🖱️"}
                elif action == "double_click":
                    if x is not None and y is not None:
                        pyautogui.doubleClick(x, y)
                    else:
                        pyautogui.doubleClick()
                    return {"success": True, "message": "Double-clicked 🖱️"}
                else:
                    return {"error": f"Mouse action {action} not implemented"}
            # pynput branch
            elif PYNPUT_AVAILABLE:
                mouse_controller = mouse.Controller()
                if action == "move":
                    if x is None or y is None:
                        return {"error": "x and y coordinates required for move action"}
                    mouse_controller.position = (int(x), int(y))
                    return {"success": True, "message": f"Mouse moved to ({x}, {y}) 🖱️"}
                elif action == "click":
                    if x is not None and y is not None:
                        mouse_controller.position = (int(x), int(y))
                    mouse_btn = mouse.Button.left
                    if button == "right":
                        mouse_btn = mouse.Button.right
                    elif button == "middle":
                        mouse_btn = mouse.Button.middle
                    mouse_controller.click(mouse_btn)
                    return {"success": True, "message": f"Clicked with {button} button 🖱️"}
                elif action == "double_click":
                    if x is not None and y is not None:
                        mouse_controller.position = (int(x), int(y))
                    mouse_btn = mouse.Button.left
                    mouse_controller.click(mouse_btn, 2)
                    return {"success": True, "message": "Double-clicked 🖱️"}
                else:
                    return {"error": f"Mouse action {action} limited with pynput"}
            else:
                return {"error": "No mouse control backend available"}
        except Exception as e:
            return {"error": f"Mouse control failed: {str(e)}"}
    
    def _clipboard_manage(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Manage clipboard"""
        try:
            action = args["action"]
            if action == "read":
                if WIN32_AVAILABLE:
                    win32clipboard.OpenClipboard()
                    try:
                        data = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)
                        # decode bytes to string if needed
                        if isinstance(data, bytes):
                            data = data.decode(errors="replace")
                        return {
                            "success": True,
                            "clipboard_content": data,
                            "message": "Clipboard content retrieved 📋"
                        }
                    finally:
                        win32clipboard.CloseClipboard()
                else:
                    try:
                        import pyperclip
                        data = pyperclip.paste()
                        return {
                            "success": True,
                            "clipboard_content": data,
                            "message": "Clipboard content retrieved 📋"
                        }
                    except ImportError:
                        return {"error": "Clipboard access requires pywin32 or pyperclip. Install with: pip install pywin32 pyperclip"}
            elif action == "write":
                text = args.get("text")
                if not text:
                    return {"error": "text required for write action"}
                if WIN32_AVAILABLE:
                    win32clipboard.OpenClipboard()
                    try:
                        win32clipboard.EmptyClipboard()
                        # Ensure text is bytes for CF_TEXT
                        if isinstance(text, str):
                            text_bytes = text.encode("utf-8")
                        else:
                            text_bytes = text
                        win32clipboard.SetClipboardData(win32clipboard.CF_TEXT, text_bytes)
                        return {
                            "success": True,
                            "message": f"Text written to clipboard 📋"
                        }
                    finally:
                        win32clipboard.CloseClipboard()
                else:
                    try:
                        import pyperclip
                        pyperclip.copy(text)
                        return {
                            "success": True,
                            "message": f"Text written to clipboard 📋"
                        }
                    except ImportError:
                        return {"error": "Clipboard access requires pywin32 or pyperclip. Install with: pip install pywin32 pyperclip"}
            else:
                return {"error": f"Unknown clipboard action: {action}"}
        except Exception as e:
            return {"error": f"Clipboard operation failed: {str(e)}"}
# For standalone testingif __name__ == "__main__":    import logging    logging.basicConfig(level=logging.INFO)        visual = VisualTool()        print("=== Visual Tool Test ===")    tools = visual.get_tools()    print(f"Available tools: {list(tools.keys())}")        # Test screenshot    result = tools["bb7_screen_capture"]()    print(f"Screenshot test: {result.get('success', False)}")
