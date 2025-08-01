"""
Dual AI Assistant - Core functionality for querying ChatGPT and Gemini APIs
"""

import asyncio
import time
import logging
import os
from typing import Dict, Tuple, Any, Union, List

# OpenAI imports
from openai import OpenAI

# Gemini imports  
from google import genai
from google.genai import types

# Local file management
from file_manager import FileManager

logger = logging.getLogger(__name__)

class DualAIAssistant:
    """Main class for handling dual AI model queries with file management capabilities"""
    
    def __init__(self, project_path: str = "."):
        """Initialize the dual AI assistant with API clients and file manager"""
        self.openai_client = None
        self.gemini_client = None
        self.file_manager = FileManager(project_path)
        self._setup_clients()
    
    def _setup_clients(self):
        """Setup OpenAI and Gemini clients with API keys from environment"""
        try:
            # Setup OpenAI client
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                self.openai_client = OpenAI(api_key=openai_api_key)
                logger.info("OpenAI client initialized successfully")
            else:
                logger.warning("OpenAI API key not found in environment variables")
            
            # Setup Gemini client
            gemini_api_key = os.getenv("GEMINI_API_KEY")
            if gemini_api_key:
                self.gemini_client = genai.Client(api_key=gemini_api_key)
                logger.info("Gemini client initialized successfully")
            else:
                logger.warning("Gemini API key not found in environment variables")
                
        except Exception as e:
            logger.error(f"Error setting up API clients: {e}")
    
    def check_api_configuration(self) -> bool:
        """Check if both API clients are properly configured"""
        return self.openai_client is not None and self.gemini_client is not None
    
    async def query_both(self, query: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Query in pipeline: User -> ChatGPT -> Gemini
        ChatGPT processes and refines the user's request, then Gemini responds to ChatGPT's output
        
        Args:
            query: The question/prompt from user
            
        Returns:
            Tuple of (chatgpt_response, gemini_response) dictionaries
        """
        
        # Step 1: Get ChatGPT to process and refine the user's request
        chatgpt_result = await self._query_chatgpt_as_processor(query)
        
        if "error" in chatgpt_result:
            return chatgpt_result, {"error": "Skipped due to ChatGPT error"}
        
        # Step 2: Use ChatGPT's refined output as input for Gemini
        gemini_result = await self._query_gemini_with_processed_input(
            original_query=query,
            processed_query=chatgpt_result.get("content", "")
        )
        
        return chatgpt_result, gemini_result
    
    async def _query_chatgpt_as_processor(self, query: str) -> Dict[str, Any]:
        """
        Query ChatGPT to process and refine user requests for Gemini
        
        Args:
            query: The original user question/prompt
            
        Returns:
            Dictionary with processed content and timing
        """
        if not self.openai_client:
            return {"error": "OpenAI client not initialized"}
        
        start_time = time.time()
        
        try:
            # Run the synchronous OpenAI call in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.openai_client.chat.completions.create(
                    model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                    messages=[
                        {
                            "role": "system", 
                            "content": """You are a helpful AI assistant in a dual AI pipeline system with file management capabilities. Your role is to:
1. Analyze user requests for code generation, file operations, or project management
2. Provide a comprehensive response including any file operations you recommend
3. Create a detailed prompt for Gemini to handle code generation or advanced analysis

Available file operations context will be provided if relevant. You can recommend:
- Creating new files
- Modifying existing files
- Reading project structure
- Running commands
- Searching in files

Please respond in Korean if the user writes in Korean.

Format your response exactly as follows:
[Your complete response to the user, including any file operations or code recommendations]

---PROMPT FOR GEMINI---
[A detailed, specific prompt for Gemini to generate code, modify files, or provide technical implementation details]"""
                        },
                        {"role": "user", "content": query}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
            )
            
            end_time = time.time()
            
            content = response.choices[0].message.content
            
            logger.debug(f"ChatGPT response received in {end_time - start_time:.2f} seconds")
            
            return {
                "content": content,
                "timing": end_time - start_time,
                "model": "gpt-4o"
            }
            
        except Exception as e:
            end_time = time.time()
            logger.error(f"ChatGPT API error: {e}")
            return {
                "error": f"ChatGPT API error: {str(e)}",
                "timing": end_time - start_time
            }
    
    async def _query_gemini_with_processed_input(self, original_query: str, processed_query: str) -> Dict[str, Any]:
        """
        Query Gemini API with processed input from ChatGPT
        
        Args:
            original_query: The original user question
            processed_query: The processed output from ChatGPT
            
        Returns:
            Dictionary with response content and timing
        """
        if not self.gemini_client:
            return {"error": "Gemini client not initialized"}
        
        start_time = time.time()
        
        # Extract the prompt for Gemini from ChatGPT's response
        if "---PROMPT FOR GEMINI---" in processed_query:
            gemini_prompt = processed_query.split("---PROMPT FOR GEMINI---")[-1].strip()
        else:
            # Fallback: use the full processed query
            gemini_prompt = processed_query
        
        try:
            # Run the synchronous Gemini call in a thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.gemini_client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=gemini_prompt
                )
            )
            
            end_time = time.time()
            
            content = response.text if response.text else "No response generated"
            
            logger.debug(f"Gemini response received in {end_time - start_time:.2f} seconds")
            
            return {
                "content": content,
                "timing": end_time - start_time,
                "model": "gemini-2.5-flash"
            }
            
        except Exception as e:
            end_time = time.time()
            logger.error(f"Gemini API error: {e}")
            return {
                "error": f"Gemini API error: {str(e)}",
                "timing": end_time - start_time
            }
    
    async def query_chatgpt_only(self, query: str) -> Dict[str, Any]:
        """Query only ChatGPT"""
        return await self._query_chatgpt_as_processor(query)
    
    async def query_gemini_only(self, query: str) -> Dict[str, Any]:
        """Query only Gemini with original query"""
        return await self._query_gemini_with_processed_input(query, query)
    
    # File management methods
    def get_project_info(self) -> Dict[str, Any]:
        """Get comprehensive project information"""
        return {
            "structure": self.file_manager.get_project_structure(),
            "git_info": self.file_manager.get_git_info(),
            "base_path": str(self.file_manager.base_path)
        }
    
    def read_file(self, file_path: str) -> Dict[str, Any]:
        """Read a file from the project"""
        return self.file_manager.read_file(file_path)
    
    def write_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Write content to a file"""
        return self.file_manager.write_file(file_path, content)
    
    def search_files(self, pattern: str) -> list[Dict[str, Any]]:
        """Search for pattern in project files"""
        return self.file_manager.search_in_files(pattern)
    
    async def query_with_file_context(self, query: str, include_files: list[str] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Query with file context for code generation and modification"""
        
        # Gather file context
        context_info = ""
        
        if include_files:
            context_info += "=== RELEVANT FILES ===\n"
            for file_path in include_files:
                file_content = self.read_file(file_path)
                if "content" in file_content:
                    context_info += f"\n--- {file_path} ---\n{file_content['content']}\n"
                else:
                    context_info += f"\n--- {file_path} (ERROR) ---\n{file_content.get('error', 'Unknown error')}\n"
        
        # Add project structure
        project_info = self.get_project_info()
        context_info += f"\n=== PROJECT STRUCTURE ===\n{project_info['structure']}\n"
        
        # Combine query with context
        enhanced_query = f"{query}\n\n{context_info}"
        
        return await self.query_both(enhanced_query)
    
    async def generate_code_with_execution(self, query: str, include_files: list[str] = None, auto_execute: bool = True) -> Dict[str, Any]:
        """Generate code and optionally execute file operations automatically"""
        
        # Gather file context
        context_info = ""
        
        if include_files:
            context_info += "=== RELEVANT FILES ===\n"
            for file_path in include_files:
                file_content = self.read_file(file_path)
                if "content" in file_content:
                    context_info += f"\n--- {file_path} ---\n{file_content['content']}\n"
                else:
                    context_info += f"\n--- {file_path} (ERROR) ---\n{file_content.get('error', 'Unknown error')}\n"
        
        # Add project structure
        project_info = self.get_project_info()
        context_info += f"\n=== PROJECT STRUCTURE ===\n{project_info['structure']}\n"
        
        # Enhanced prompt for code generation with execution
        enhanced_query = f"""
{query}

{context_info}

IMPORTANT: If this request involves creating or modifying files, please provide:
1. A clear response explaining what you're going to do
2. The exact file operations needed in this format:

<FILE_OPERATIONS>
<CREATE file="path/to/file.py">
file content here
</CREATE>

<MODIFY file="path/to/existing.py" operation="append">
content to append
</MODIFY>

<MODIFY file="path/to/existing.py" operation="replace" search="old code" with="new code">
</MODIFY>
</FILE_OPERATIONS>

Please respond in Korean if the user query is in Korean.
"""
        
        # Get AI responses
        chatgpt_result, gemini_result = await self.query_both(enhanced_query)
        
        # Parse and execute file operations if auto_execute is True
        executed_operations = []
        if auto_execute:
            # Check both responses for file operations
            for response_name, response in [("ChatGPT", chatgpt_result), ("Gemini", gemini_result)]:
                if "content" in response:
                    operations = self._parse_file_operations(response["content"])
                    for op in operations:
                        result = self._execute_file_operation(op)
                        executed_operations.append({
                            "source": response_name,
                            "operation": op,
                            "result": result
                        })
        
        return {
            "chatgpt_response": chatgpt_result,
            "gemini_response": gemini_result,
            "executed_operations": executed_operations,
            "auto_executed": auto_execute
        }
    
    def _parse_file_operations(self, content: str) -> List[Dict[str, Any]]:
        """Parse file operations from AI response"""
        operations = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for CREATE operations
            if line.startswith('<CREATE file="'):
                file_path = line.split('file="')[1].split('"')[0]
                file_content = ""
                i += 1
                
                # Collect content until </CREATE>
                while i < len(lines) and not lines[i].strip().startswith('</CREATE>'):
                    file_content += lines[i] + '\n'
                    i += 1
                
                operations.append({
                    "type": "create",
                    "file_path": file_path,
                    "content": file_content.rstrip('\n')
                })
            
            # Look for MODIFY operations
            elif line.startswith('<MODIFY file="'):
                parts = line.split('"')
                file_path = parts[1]
                
                operation_type = "append"  # default
                search_text = ""
                replace_text = ""
                
                if 'operation="' in line:
                    operation_type = line.split('operation="')[1].split('"')[0]
                
                if 'search="' in line:
                    search_text = line.split('search="')[1].split('"')[0]
                
                if 'with="' in line:
                    replace_text = line.split('with="')[1].split('"')[0]
                
                # Collect content for append operations
                if operation_type == "append":
                    content = ""
                    i += 1
                    while i < len(lines) and not lines[i].strip().startswith('</MODIFY>'):
                        content += lines[i] + '\n'
                        i += 1
                    
                    operations.append({
                        "type": "modify",
                        "file_path": file_path,
                        "operation": operation_type,
                        "content": content.rstrip('\n')
                    })
                elif operation_type == "replace":
                    operations.append({
                        "type": "modify",
                        "file_path": file_path,
                        "operation": operation_type,
                        "search": search_text,
                        "replace": replace_text
                    })
            
            i += 1
        
        return operations
    
    def _execute_file_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a parsed file operation"""
        try:
            if operation["type"] == "create":
                result = self.file_manager.write_file(
                    operation["file_path"], 
                    operation["content"]
                )
                logger.info(f"Created file: {operation['file_path']}")
                return result
            
            elif operation["type"] == "modify":
                if operation["operation"] == "append":
                    # Read existing content and append
                    existing = self.file_manager.read_file(operation["file_path"])
                    if "content" in existing:
                        new_content = existing["content"] + "\n" + operation["content"]
                    else:
                        new_content = operation["content"]
                    
                    result = self.file_manager.write_file(
                        operation["file_path"], 
                        new_content
                    )
                    logger.info(f"Appended to file: {operation['file_path']}")
                    return result
                
                elif operation["operation"] == "replace":
                    # Read existing content and replace
                    existing = self.file_manager.read_file(operation["file_path"])
                    if "content" in existing:
                        new_content = existing["content"].replace(
                            operation["search"], 
                            operation["replace"]
                        )
                        result = self.file_manager.write_file(
                            operation["file_path"], 
                            new_content
                        )
                        logger.info(f"Modified file: {operation['file_path']}")
                        return result
                    else:
                        return {"error": f"Could not read file for modification: {operation['file_path']}"}
            
            return {"error": f"Unknown operation type: {operation['type']}"}
            
        except Exception as e:
            logger.error(f"Error executing file operation: {e}")
            return {"error": f"Failed to execute operation: {str(e)}"}
