#!/usr/bin/env python3
"""
Dual AI Assistant CLI - Query ChatGPT and Gemini simultaneously
"""

import click
import asyncio
import sys
from ai_assistant import DualAIAssistant
from dotenv import load_dotenv # Add this line
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
import logging

console = Console()

def setup_logging():
    """Setup basic logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ai_assistant.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

@click.command()
@click.argument('query', required=False)
@click.option('--interactive', '-i', is_flag=True, help='Start interactive mode')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--code', '-c', is_flag=True, help='Enable code generation mode with file context')
@click.option('--project-path', '-p', default='.', help='Path to the project directory')
@click.option('--files', '-f', multiple=True, help='Include specific files for context')
def main(query, interactive, verbose, code, project_path, files):
    """
    Dual AI Assistant - Query both ChatGPT and Gemini simultaneously
    
    Examples:
        python main.py "What is artificial intelligence?"
        python main.py -i  # Interactive mode
        python main.py -v "Explain quantum computing"  # Verbose mode
    """
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    setup_logging()
    load_dotenv() # Load environment variables from .env file
    
    # Initialize the dual AI assistant
    assistant = DualAIAssistant(project_path)
    
    # Check if APIs are configured
    if not assistant.check_api_configuration():
        console.print("[red]Error: API keys not configured properly. Please check your environment variables.[/red]")
        console.print("Required environment variables:")
        console.print("- OPENAI_API_KEY")
        console.print("- GEMINI_API_KEY")
        console.print("\nSee .env.example for reference.")
        sys.exit(1)
    
    if interactive:
        start_interactive_mode(assistant, code_mode=code)
    elif query:
        if code:
            asyncio.run(process_code_query(assistant, query, list(files)))
        else:
            asyncio.run(process_single_query(assistant, query))
    else:
        console.print("[yellow]Please provide a query or use --interactive mode[/yellow]")
        console.print("Usage: python main.py 'Your question here'")
        console.print("       python main.py --interactive")
        console.print("       python main.py --code 'Generate a Python class for user management'")
        console.print("       python main.py --code --files main.py 'Add error handling to this file'")

def start_interactive_mode(assistant, code_mode=False):
    """Start interactive mode for continuous queries"""
    mode_text = "🔧 Code Generation Mode" if code_mode else "🤖 Dual AI Assistant - Interactive Mode"
    console.print(Panel.fit(mode_text, style="bold blue"))
    
    if code_mode:
        console.print("Code generation mode enabled. I can read, create, and modify files in your project.")
        console.print("Commands: 'show files' to see project structure, 'quit' to exit.\n")
    else:
        console.print("Type your questions below. Use 'quit', 'exit', or Ctrl+C to exit.\n")
    
    try:
        while True:
            query = console.input("[bold green]❓ Your question: [/bold green]")
            
            if query.lower().strip() in ['quit', 'exit', 'q']:
                console.print("[yellow]Goodbye! 👋[/yellow]")
                break
            
            if query.strip():
                if query.lower().strip() == 'show files':
                    show_project_info(assistant)
                elif code_mode:
                    asyncio.run(process_code_query(assistant, query, []))
                else:
                    asyncio.run(process_single_query(assistant, query))
                console.print()  # Add spacing between queries
            else:
                console.print("[yellow]Please enter a valid question.[/yellow]")
                
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye! 👋[/yellow]")

async def process_single_query(assistant, query):
    """Process a single query and display results from both AI models"""
    
    console.print(f"\n[bold cyan]Query:[/bold cyan] {query}")
    console.print()
    
    # Show loading message
    with console.status("[bold green]Querying both AI models..."):
        try:
            # Get responses from both models simultaneously
            chatgpt_response, gemini_response = await assistant.query_both(query)
            
        except Exception as e:
            console.print(f"[red]Error occurred: {e}[/red]")
            return
    
    # Display responses side by side
    display_dual_responses(chatgpt_response, gemini_response)

def display_dual_responses(chatgpt_response, gemini_response):
    """Display responses from pipeline: ChatGPT processing -> Gemini response"""
    
    # Extract ChatGPT's user response and Gemini prompt
    chatgpt_content = chatgpt_response.get('content', chatgpt_response.get('error', 'No response'))
    
    if "---PROMPT FOR GEMINI---" in chatgpt_content:
        user_response = chatgpt_content.split("---PROMPT FOR GEMINI---")[0].strip()
        gemini_prompt = chatgpt_content.split("---PROMPT FOR GEMINI---")[1].strip()
    else:
        user_response = chatgpt_content
        gemini_prompt = "N/A"
    
    # Create panels for pipeline display
    chatgpt_panel = Panel(
        user_response,
        title="🔄 ChatGPT Processing (1단계)",
        title_align="left",
        border_style="green" if 'content' in chatgpt_response else "red",
        padding=(1, 2)
    )
    
    gemini_panel = Panel(
        gemini_response.get('content', gemini_response.get('error', 'No response')),
        title="✨ Gemini Response (2단계)",
        title_align="left",
        border_style="blue" if 'content' in gemini_response else "red",
        padding=(1, 2)
    )
    
    # Display pipeline flow
    console.print(f"[bold cyan]파이프라인 처리 과정:[/bold cyan] 사용자 → ChatGPT → Gemini\n")
    console.print(chatgpt_panel)
    console.print()
    console.print(gemini_panel)
    
    # Show timing information if available
    if 'timing' in chatgpt_response or 'timing' in gemini_response:
        timing_info = []
        if 'timing' in chatgpt_response:
            timing_info.append(f"ChatGPT: {chatgpt_response['timing']:.2f}s")
        if 'timing' in gemini_response:
            timing_info.append(f"Gemini: {gemini_response['timing']:.2f}s")
        
        console.print(f"[dim]Response times: {' | '.join(timing_info)}[/dim]")

async def process_code_query(assistant, query, files):
    """Process a code generation query with file context and execution"""
    
    console.print(f"\n[bold cyan]Code Query:[/bold cyan] {query}")
    if files:
        console.print(f"[bold cyan]Context Files:[/bold cyan] {', '.join(files)}")
    console.print()
    
    # Show loading message
    with console.status("[bold green]Analyzing code and generating response..."):
        try:
            # Use the new generate_code_with_execution method
            result = await assistant.generate_code_with_execution(query, files, auto_execute=True)
            
        except Exception as e:
            console.print(f"[red]Error occurred: {e}[/red]")
            return
    
    # Display responses
    display_dual_responses(result["chatgpt_response"], result["gemini_response"])
    
    # Show file operations if any were executed
    if result["executed_operations"]:
        console.print("\n[bold magenta]🔧 파일 작업 실행됨:[/bold magenta]")
        for op in result["executed_operations"]:
            operation = op["operation"]
            result_info = op["result"]
            source = op["source"]
            
            if "success" in result_info:
                console.print(f"✅ [{source}] {operation['type'].upper()}: {operation['file_path']}")
                if operation["type"] == "create":
                    lines = len(operation["content"].splitlines())
                    console.print(f"   📝 {lines} 줄 생성됨")
                elif operation["type"] == "modify":
                    console.print(f"   🔧 {operation['operation']} 작업 완료")
            else:
                console.print(f"❌ [{source}] {operation['type'].upper()}: {operation['file_path']}")
                console.print(f"   오류: {result_info.get('error', 'Unknown error')}")
        
        console.print()
    elif result["auto_executed"]:
        console.print("[dim]💡 파일 작업이 필요한 요청이 아니거나 응답에서 파일 작업이 감지되지 않았습니다.[/dim]\n")

def show_project_info(assistant):
    """Show project structure and information"""
    project_info = assistant.get_project_info()
    
    console.print("[bold cyan]프로젝트 정보:[/bold cyan]")
    console.print(f"Base Path: {project_info['base_path']}")
    
    # Show Git info if available
    git_info = project_info.get('git_info', {})
    if git_info.get('is_git_repo'):
        console.print(f"Git Branch: {git_info.get('current_branch', 'unknown')}")
        console.print(f"Has Changes: {git_info.get('has_changes', False)}")
    
    # Show project structure
    console.print("\n[bold cyan]파일 구조:[/bold cyan]")
    def print_structure(structure, prefix=""):
        for name, info in structure.get('children', {}).items():
            if info.get('type') == 'directory':
                console.print(f"{prefix}📁 {name}/")
                print_structure(info, prefix + "  ")
            else:
                size = info.get('size', 0)
                size_str = f" ({size} bytes)" if size > 0 else ""
                console.print(f"{prefix}📄 {name}{size_str}")
    
    print_structure(project_info['structure'])

if __name__ == "__main__":
    main()
