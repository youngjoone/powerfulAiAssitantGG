"""
File Manager for AI Assistant - Handles local file operations and code generation
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class FileManager:
    """Manages file operations and code generation for the AI assistant"""
    
    def __init__(self, base_path: str = "."):
        """Initialize file manager with base path"""
        self.base_path = Path(base_path).resolve()
        logger.info(f"FileManager initialized with base path: {self.base_path}")
    
    def get_project_structure(self, max_depth: int = 3) -> Dict[str, Any]:
        """Get the structure of the current project"""
        def scan_directory(path: Path, depth: int = 0) -> Dict[str, Any]:
            if depth > max_depth:
                return {}
            
            structure = {"type": "directory", "children": {}}
            
            try:
                for item in path.iterdir():
                    if item.name.startswith('.') and item.name not in ['.env', '.gitignore']:
                        continue
                    
                    if item.is_dir():
                        if item.name not in ['__pycache__', 'node_modules', '.git']:
                            structure["children"][item.name] = scan_directory(item, depth + 1)
                    else:
                        # Get file info
                        try:
                            stat = item.stat()
                            structure["children"][item.name] = {
                                "type": "file",
                                "size": stat.st_size,
                                "extension": item.suffix
                            }
                        except Exception as e:
                            logger.warning(f"Could not get stats for {item}: {e}")
                            structure["children"][item.name] = {"type": "file"}
                            
            except PermissionError:
                logger.warning(f"Permission denied accessing {path}")
            
            return structure
        
        return scan_directory(self.base_path)
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read content of a file"""
        try:
            full_path = self.base_path / file_path
            
            if not full_path.exists():
                return {"error": f"File not found: {file_path}"}
            
            if not full_path.is_file():
                return {"error": f"Path is not a file: {file_path}"}
            
            # Check if file is text-based
            text_extensions = {'.py', '.js', '.html', '.css', '.json', '.txt', '.md', '.yml', '.yaml', '.xml', '.sql', '.sh', '.bat'}
            if full_path.suffix.lower() not in text_extensions:
                return {"error": f"File type not supported for reading: {full_path.suffix}"}
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "content": content,
                "path": str(full_path.relative_to(self.base_path)),
                "size": len(content),
                "lines": len(content.splitlines())
            }
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return {"error": f"Failed to read file: {str(e)}"}
    
    def write_file(self, file_path: str, content: str, create_dirs: bool = True) -> Dict[str, Any]:
        """Write content to a file"""
        try:
            full_path = self.base_path / file_path
            
            if create_dirs:
                full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"File written successfully: {file_path}")
            return {
                "success": True,
                "path": str(full_path.relative_to(self.base_path)),
                "size": len(content),
                "lines": len(content.splitlines())
            }
            
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return {"error": f"Failed to write file: {str(e)}"}
    
    def modify_file(self, file_path: str, modifications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Modify a file with specific operations"""
        try:
            # Read current content
            read_result = self.read_file(file_path)
            if "error" in read_result:
                return read_result
            
            lines = read_result["content"].splitlines()
            
            # Apply modifications
            for mod in modifications:
                operation = mod.get("operation")
                
                if operation == "replace_line":
                    line_num = mod.get("line_number", 1) - 1  # Convert to 0-based
                    new_content = mod.get("new_content", "")
                    if 0 <= line_num < len(lines):
                        lines[line_num] = new_content
                
                elif operation == "insert_line":
                    line_num = mod.get("line_number", 1) - 1  # Convert to 0-based
                    new_content = mod.get("new_content", "")
                    if 0 <= line_num <= len(lines):
                        lines.insert(line_num, new_content)
                
                elif operation == "delete_line":
                    line_num = mod.get("line_number", 1) - 1  # Convert to 0-based
                    if 0 <= line_num < len(lines):
                        del lines[line_num]
                
                elif operation == "append":
                    new_content = mod.get("new_content", "")
                    lines.append(new_content)
            
            # Write modified content
            modified_content = "\n".join(lines)
            return self.write_file(file_path, modified_content)
            
        except Exception as e:
            logger.error(f"Error modifying file {file_path}: {e}")
            return {"error": f"Failed to modify file: {str(e)}"}
    
    def search_in_files(self, pattern: str, file_extensions: List[str] = None) -> List[Dict[str, Any]]:
        """Search for a pattern in files"""
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.html', '.css', '.json', '.txt', '.md']
        
        results = []
        
        try:
            for root, dirs, files in os.walk(self.base_path):
                # Skip hidden directories and common build/cache directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
                
                for file in files:
                    if any(file.endswith(ext) for ext in file_extensions):
                        file_path = Path(root) / file
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                for line_num, line in enumerate(lines, 1):
                                    if pattern.lower() in line.lower():
                                        results.append({
                                            "file": str(file_path.relative_to(self.base_path)),
                                            "line_number": line_num,
                                            "line_content": line.strip(),
                                            "match": pattern
                                        })
                        except Exception as e:
                            logger.warning(f"Could not search in file {file_path}: {e}")
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
        
        return results
    
    def run_command(self, command: str, cwd: str = None) -> Dict[str, Any]:
        """Run a shell command in the project directory"""
        try:
            work_dir = self.base_path / cwd if cwd else self.base_path
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": command,
                "success": result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Command timed out after 30 seconds"}
        except Exception as e:
            logger.error(f"Error running command '{command}': {e}")
            return {"error": f"Failed to run command: {str(e)}"}
    
    def get_git_info(self) -> Dict[str, Any]:
        """Get git repository information"""
        git_info = {}
        
        # Check if it's a git repository
        if (self.base_path / '.git').exists():
            git_info["is_git_repo"] = True
            
            # Get current branch
            branch_result = self.run_command("git branch --show-current")
            if branch_result.get("success"):
                git_info["current_branch"] = branch_result["stdout"].strip()
            
            # Get recent commits
            commits_result = self.run_command("git log --oneline -5")
            if commits_result.get("success"):
                git_info["recent_commits"] = commits_result["stdout"].strip().split("\n")
            
            # Get status
            status_result = self.run_command("git status --porcelain")
            if status_result.get("success"):
                git_info["has_changes"] = bool(status_result["stdout"].strip())
                git_info["status"] = status_result["stdout"].strip()
        else:
            git_info["is_git_repo"] = False
        
        return git_info