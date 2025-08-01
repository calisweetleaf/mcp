"""
File Tool - System-wide file operations for MCP Server

This tool provides full file system access for reading, writing, and
managing files anywhere on the system. No restrictions - designed for
a dedicated coding environment where full access is desired.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Callable
import time


class FileTool:
    """Handles file system operations with full system access"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("File tool initialized with system-wide access")
    
    def read_file(self, path: str) -> str:
        """Read the complete contents of a file"""
        try:
            file_path = Path(path).expanduser().resolve()
            
            if not file_path.exists():
                return f"Error: File '{path}' does not exist"
            
            if not file_path.is_file():
                return f"Error: '{path}' is not a file"
            
            # Try to read as text with common encodings
            encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    
                    file_size = file_path.stat().st_size
                    self.logger.info(f"Read file '{path}' ({file_size} bytes, {encoding})")
                    
                    return content
                    
                except UnicodeDecodeError:
                    continue
            
            # If all text encodings fail, try binary and return info
            try:
                with open(file_path, 'rb') as f:
                    binary_content = f.read(1024)  # First 1KB
                
                return (f"File '{path}' appears to be binary. "
                       f"Size: {file_path.stat().st_size} bytes. "
                       f"First 1KB as hex: {binary_content.hex()}")
                       
            except Exception as e:
                return f"Error reading file '{path}': {str(e)}"
                
        except Exception as e:
            self.logger.error(f"Error reading file '{path}': {e}")
            return f"Error reading file '{path}': {str(e)}"
    
    def write_file(self, path: str, content: str) -> str:
        """Write content to a file, creating directories as needed"""
        try:
            file_path = Path(path).expanduser().resolve()
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            file_size = file_path.stat().st_size
            self.logger.info(f"Wrote file '{path}' ({file_size} bytes)")
            
            return f"Successfully wrote {len(content)} characters to '{path}'"
            
        except Exception as e:
            self.logger.error(f"Error writing file '{path}': {e}")
            return f"Error writing file '{path}': {str(e)}"
    
    def append_file(self, path: str, content: str) -> str:
        """Append content to a file"""
        try:
            file_path = Path(path).expanduser().resolve()
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Append to the file
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(content)
            
            file_size = file_path.stat().st_size
            self.logger.info(f"Appended to file '{path}' (now {file_size} bytes)")
            
            return f"Successfully appended {len(content)} characters to '{path}'"
            
        except Exception as e:
            self.logger.error(f"Error appending to file '{path}': {e}")
            return f"Error appending to file '{path}': {str(e)}"
    
    def list_directory(self, path: str = ".") -> str:
        """List contents of a directory with detailed information"""
        try:
            dir_path = Path(path).expanduser().resolve()
            
            if not dir_path.exists():
                return f"Error: Directory '{path}' does not exist"
            
            if not dir_path.is_dir():
                return f"Error: '{path}' is not a directory"
            
            items = []
            total_files = 0
            total_dirs = 0
            total_size = 0
            
            try:
                for item in sorted(dir_path.iterdir()):
                    try:
                        stat = item.stat()
                        size = stat.st_size
                        modified = time.strftime('%Y-%m-%d %H:%M:%S', 
                                               time.localtime(stat.st_mtime))
                        
                        if item.is_file():
                            items.append(f"  📄 {item.name} ({size} bytes, {modified})")
                            total_files += 1
                            total_size += size
                        elif item.is_dir():
                            # Try to count items in subdirectory
                            try:
                                subitem_count = len(list(item.iterdir()))
                                items.append(f"  📁 {item.name}/ ({subitem_count} items, {modified})")
                            except PermissionError:
                                items.append(f"  📁 {item.name}/ (access denied, {modified})")
                            total_dirs += 1
                        else:
                            items.append(f"  🔗 {item.name} (symlink, {modified})")
                            
                    except (PermissionError, OSError) as e:
                        items.append(f"  ❌ {item.name} (error: {e})")
                        
            except PermissionError:
                return f"Error: Permission denied accessing directory '{path}'"
            
            result = f"Directory listing for '{path}':\n"
            result += f"Total: {total_dirs} directories, {total_files} files ({total_size} bytes)\n\n"
            result += "\n".join(items) if items else "  (empty directory)"
            
            self.logger.info(f"Listed directory '{path}' ({total_dirs} dirs, {total_files} files)")
            return result
            
        except Exception as e:
            self.logger.error(f"Error listing directory '{path}': {e}")
            return f"Error listing directory '{path}': {str(e)}"
    
    def get_file_info(self, path: str) -> str:
        """Get detailed information about a file or directory"""
        try:
            file_path = Path(path).expanduser().resolve()
            
            if not file_path.exists():
                return f"Error: '{path}' does not exist"
            
            stat = file_path.stat()
            
            info = f"File information for '{path}':\n"
            info += f"  Absolute path: {file_path}\n"
            info += f"  Type: {'File' if file_path.is_file() else 'Directory' if file_path.is_dir() else 'Other'}\n"
            info += f"  Size: {stat.st_size} bytes\n"
            info += f"  Created: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_ctime))}\n"
            info += f"  Modified: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_mtime))}\n"
            info += f"  Accessed: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat.st_atime))}\n"
            info += f"  Permissions: {oct(stat.st_mode)[-3:]}\n"
            
            if file_path.is_file():
                # Try to determine file type
                suffix = file_path.suffix.lower()
                if suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs']:
                    info += f"  File type: Source code ({suffix})\n"
                elif suffix in ['.txt', '.md', '.rst', '.log']:
                    info += f"  File type: Text document ({suffix})\n"
                elif suffix in ['.json', '.xml', '.yaml', '.yml', '.toml']:
                    info += f"  File type: Data format ({suffix})\n"
                else:
                    info += f"  File type: {suffix if suffix else 'No extension'}\n"
            
            self.logger.info(f"Got file info for '{path}'")
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting file info for '{path}': {e}")
            return f"Error getting file info for '{path}': {str(e)}"
    
    def search_files(self, directory: str, pattern: str, max_results: int = 50) -> str:
        """Search for files matching a pattern in a directory tree"""
        try:
            search_path = Path(directory).expanduser().resolve()
            
            if not search_path.exists():
                return f"Error: Directory '{directory}' does not exist"
            
            if not search_path.is_dir():
                return f"Error: '{directory}' is not a directory"
            
            matches = []
            searched_count = 0
            
            try:
                for file_path in search_path.rglob(pattern):
                    searched_count += 1
                    if len(matches) >= max_results:
                        break
                        
                    try:
                        stat = file_path.stat()
                        size = stat.st_size
                        modified = time.strftime('%Y-%m-%d %H:%M:%S', 
                                               time.localtime(stat.st_mtime))
                        
                        relative_path = file_path.relative_to(search_path)
                        if file_path.is_file():
                            matches.append(f"  📄 {relative_path} ({size} bytes, {modified})")
                        elif file_path.is_dir():
                            matches.append(f"  📁 {relative_path}/ ({modified})")
                            
                    except (PermissionError, OSError):
                        matches.append(f"  ❌ {file_path.name} (access denied)")
            
            except Exception as e:
                return f"Error during search: {str(e)}"
            
            result = f"Search results for '{pattern}' in '{directory}':\n"
            result += f"Found {len(matches)} matches (searched {searched_count} items)\n\n"
            
            if matches:
                result += "\n".join(matches)
                if len(matches) >= max_results:
                    result += f"\n... (truncated to {max_results} results)"
            else:
                result += "  No matches found"
            
            self.logger.info(f"Searched for '{pattern}' in '{directory}' - {len(matches)} matches")
            return result
            
        except Exception as e:
            self.logger.error(f"Error searching files: {e}")
            return f"Error searching files: {str(e)}"
    
    def get_tools(self) -> Dict[str, Callable]:
        """Return all available tool functions"""
        return {
            'bb7_read_file': self.read_file,
            'bb7_write_file': self.write_file,
            'bb7_append_file': self.append_file,
            'bb7_list_directory': self.list_directory,
            'bb7_get_file_info': self.get_file_info,
            'bb7_search_files': lambda directory, pattern, max_results=50: self.search_files(directory, pattern, max_results)
        }


# For standalone testing
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    file_tool = FileTool()
    
    # Test basic operations
    print(file_tool.write_file("test_file.txt", "Hello, World!"))
    print(file_tool.read_file("test_file.txt"))
    print(file_tool.append_file("test_file.txt", "\nAppended line"))
    print(file_tool.read_file("test_file.txt"))
    print(file_tool.get_file_info("test_file.txt"))
    print(file_tool.list_directory("."))
