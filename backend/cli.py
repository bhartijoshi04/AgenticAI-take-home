#!/usr/bin/env python3
"""
CLI Interface for Agentic Research Paper Analyzer
Provides a streaming, interactive experience for analyzing arXiv papers.
"""
import asyncio
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Third-party imports
import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich.prompt import Prompt
from dotenv import load_dotenv

# Local imports
sys.path.append(str(Path(__file__).parent))
from app.services.arxiv_service import ArxivService
from app.services.chunking_service import ChunkingService
from app.core.workflow import PaperAnalysisWorkflow

# Load environment variables
load_dotenv()

# Initialize console with rich formatting
console = Console()

class CLIAnalyzer:
    """
    Main CLI analyzer class with streaming capabilities.
    """
    
    def __init__(self):
        self.console = console
        self.data_dir = Path(__file__).parent / "app" / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize services
        self.arxiv_service = ArxivService()
        self.chunking_service = ChunkingService()
        # Build the workflow application
        self.workflow_app = PaperAnalysisWorkflow(enable_checkpointing=True).build()
        
        # Simple agent names mapping for display
        self.agent_names = {
            "consistency": "Consistency Analysis",
            "grammar": "Grammar & Style", 
            "novelty": "Novelty Assessment",
            "fact_check": "Fact Verification",
            "authenticity": "Authenticity Check",
            "aggregator": "Report Generation"
        }
    
    def display_header(self):
        """Display the main application header."""
        header_text = Text("🤖 RESEARCH PAPER ANALYSER", style="bold bright_green")
        header_panel = Panel(
            header_text,
            border_style="bright_green",
            padding=(1, 2),
            title="[bold bright_white]Agentic AI System[/bold bright_white]",
            title_align="center"
        )
        self.console.print(header_panel)
        self.console.print()
    
    def get_user_input(self) -> str:
        """Get arXiv URL from user with validation."""
        self.console.print(
            Panel(
                "[bold cyan]Please enter an arXiv paper URL or ID[/bold cyan]\n\n"
                "Examples:\n"
                "• https://arxiv.org/abs/2301.12345\n"
                "• https://arxiv.org/pdf/2301.12345.pdf\n"
                "• 2301.12345",
                title="📝 Input Required",
                border_style="cyan"
            )
        )
        
        while True:
            try:
                url = Prompt.ask("[bold cyan]arXiv URL or ID[/bold cyan]", console=self.console)
                
                if not url.strip():
                    self.console.print("[red]❌ Please enter a valid URL or ID[/red]")
                    continue
                
                # Validate by trying to extract paper ID
                paper_id = self.arxiv_service.extract_paper_id(url)
                self.console.print(f"[green]✅ Detected paper ID: {paper_id}[/green]")
                return url.strip()
                
            except ValueError as e:
                self.console.print(f"[red]❌ Invalid input: {e}[/red]")
            except KeyboardInterrupt:
                self.console.print("\n[yellow]👋 Goodbye![/yellow]")
                sys.exit(0)
    
    
    async def fetch_and_save_paper(self, url: str) -> Path:
        """Fetch paper content and save as markdown."""
        self.console.print("\n[bold yellow]📥 Fetching paper from arXiv...[/bold yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task("Downloading paper content...", total=None)
            
            try:
                # Fetch paper content
                markdown_content = self.arxiv_service.get_paper_content(url)
                
                # Save markdown
                paper_id = self.arxiv_service.extract_paper_id(url)
                markdown_path = self.data_dir / f"{paper_id}.md"
                
                with open(markdown_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                progress.update(task, completed=100, description="✅ Paper downloaded successfully")
                time.sleep(0.5)  # Brief pause to show completion
                
                self.console.print(f"[green]✅ Markdown saved to: {markdown_path}[/green]")
                return markdown_path
                
            except Exception as e:
                progress.update(task, description=f"❌ Failed: {str(e)}")
                raise
    
    async def chunk_and_save_paper(self, markdown_path: Path) -> Path:
        """Chunk paper into sections and save as JSON."""
        self.console.print("\n[bold yellow]✂️ Processing paper sections...[/bold yellow]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task("Chunking paper into sections...", total=None)
            
            try:
                # Read markdown content
                with open(markdown_path, 'r', encoding='utf-8') as f:
                    markdown_content = f.read()
                
                # Chunk the content
                chunked_data = self.chunking_service.chunk_text(markdown_content)
                
                # Save chunked data
                paper_id = markdown_path.stem
                json_path = self.data_dir / f"{paper_id}_chunked.json"
                
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(chunked_data, f, indent=2, ensure_ascii=False)
                
                progress.update(task, completed=100, description="✅ Paper chunked successfully")
                time.sleep(0.5)
                
                # Display section summary
                metadata = chunked_data["paper_metadata"]
                self.console.print(
                    Panel(
                        f"[bold]Title:[/bold] {metadata['title']}\n"
                        f"[bold]Sections:[/bold] {metadata['total_sections']}\n"
                        f"[bold]Words:[/bold] {metadata['total_word_count']:,}\n"
                        f"[bold]Characters:[/bold] {metadata['total_char_count']:,}",
                        title="📊 Paper Summary",
                        border_style="blue"
                    )
                )
                
                self.console.print(f"[green]✅ Chunked data saved to: {json_path}[/green]")
                return json_path
                
            except Exception as e:
                progress.update(task, description=f"❌ Failed: {str(e)}")
                raise
    
    async def run_streaming_analysis(self, json_path: Path, markdown_path: Path) -> str:
        """Run the analysis workflow with streaming updates."""
        self.console.print("\n[bold yellow]🚀 Starting agent analysis...[/bold yellow]")
        
        # Load chunked data
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Read original markdown content needed for context
        with open(markdown_path, 'r', encoding='utf-8') as f:
            paper_content = f.read()
        
        # Create config for checkpointing
        config = {
            "configurable": {
                "thread_id": str(uuid.uuid4()),
                "checkpoint_ns": "paper_analysis"
            }
        }
        
        # Prepare initial state
        initial_state = {
            "paper_content": paper_content,
            "paper_metadata": data["paper_metadata"],
            "sections": data["sections"],
            "consistency": {},
            "grammar": {},
            "novelty": {},
            "fact_check": {},
            "authenticity": {},
            "final_report": ""
        }
        
        self.console.print("\n[cyan]Multi-Agent Analysis Pipeline Starting...[/cyan]")
        
        final_state = None
        
        try:
            # Run streaming workflow
            # Using .stream() with mode="updates" to get node outputs as they complete
            for output in self.workflow_app.stream(initial_state, config=config):
                # output is a dict like {'node_name': {...updates...}}
                
                for node_name, node_output in output.items():
                    agent_display_name = self.agent_names.get(node_name, node_name.title())
                    
                    if node_name == "aggregator":
                        self.console.print(f"  [bold magenta]📊 {agent_display_name} Compiling Report...[/bold magenta]")
                        if "final_report" in node_output:
                            final_state = node_output # Capturing final output
                    else:
                        # Agent nodes return dicts like {"consistency": {...result...}}
                        # We need to extract the specific result key
                        result_data = node_output.get(node_name, {})
                        
                        status = result_data.get("status", "Unknown")
                        if status == "Pass":
                            status_color = "green"
                            emoji = "✅"
                        elif status == "Fail":
                            status_color = "red"
                            emoji = "❌"
                        else:
                            status_color = "yellow"
                            emoji = "⚠️"
                            
                        # Format detail string
                        details = ""
                        if "score" in result_data and result_data["score"] is not None:
                            details = f"(Score: {result_data['score']})"
                        elif "rating" in result_data and result_data["rating"] is not None:
                            details = f"(Rating: {result_data['rating']})"
                            
                        self.console.print(f"  {emoji} [bold {status_color}]{agent_display_name}[/bold {status_color}] Completed {details}")
                        
                # Small delay for visual pacing
                time.sleep(0.1)

            self.console.print(f"\n[green]All agents completed.[/green]")
            
            # If final_state wasn't captured in stream (e.g. if we need full state), invoke to get it
            # But normally aggregator output should have it.
            # Let's ensure we have the full state
            # Note: with MemorySaver checkpointer, we can get state by config
            # But the stream loop should have given us the final update from aggregator
            
            # Reconstruct final state logic if needed, but aggregator result has final_report
            if final_state and "final_report" in final_state:
                return final_state["final_report"]
            
            # Fallback
            full_state = self.workflow_app.get_state(config).values
            return full_state.get("final_report", "No report generated.")
            
        except Exception as e:
            self.console.print(f"\n[red]❌ Analysis failed: {e}[/red]")
            import traceback
            traceback.print_exc()
            raise
    
    async def save_report(self, report: str, paper_id: str) -> Path:
        """Save the final report as markdown."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.data_dir / f"{paper_id}_report_{timestamp}.md"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.console.print(f"\n[green]✅ Report saved to: {report_path}[/green]")
        return report_path
    
    def display_report_preview(self, report: str):
        """Display a preview of the generated report."""
        lines = report.split('\n')
        preview_lines = []
        
        # Extract executive summary or first 15 lines
        in_summary = False
        summary_lines = 0
        
        for line in lines:
            if "Executive Summary" in line:
                in_summary = True
            elif in_summary and line.startswith("##") and "Executive Summary" not in line:
                break
            elif in_summary:
                preview_lines.append(line)
                summary_lines += 1
                if summary_lines > 20:  # Limit preview length
                    break
        
        if not preview_lines:
            preview_lines = lines[:15]  # Fallback to first 15 lines
        
        preview_text = '\n'.join(preview_lines)
        
        self.console.print(
            Panel(
                preview_text,
                title="[bold green]📋 Analysis Report Preview[/bold green]",
                border_style="green",
                expand=False
            )
        )
    
    async def run_full_analysis(self):
        """Run the complete analysis pipeline."""
        try:
            # Display header
            self.display_header()
            
            # Get user input
            if hasattr(self, 'get_user_input') and callable(self.get_user_input):
                 # This check handles the override in main()
                 url = self.get_user_input()
            else:
                 # Should not happen given init but safe fallback
                 url = Prompt.ask("Enter URL")
            
            # Extract paper ID for file naming
            paper_id = self.arxiv_service.extract_paper_id(url)
            
            # Step 1: Fetch and save paper
            markdown_path = await self.fetch_and_save_paper(url)
            
            # Step 2: Chunk and save sections
            json_path = await self.chunk_and_save_paper(markdown_path)
            
            # Step 3: Run streaming analysis
            report = await self.run_streaming_analysis(json_path, markdown_path)
            
            # Step 4: Save report
            report_path = await self.save_report(report, paper_id)
            
            # Step 5: Display completion and preview
            self.console.print("\n" + "="*80)
            self.console.print(
                Panel(
                    "[bold bright_green]🎉 Analysis Complete![/bold bright_green]\n\n"
                    f"[cyan]📄 Paper ID:[/cyan] {paper_id}\n"
                    f"[cyan]📊 Chunked Data:[/cyan] {json_path.name}\n"
                    f"[cyan]📋 Report:[/cyan] {report_path.name}",
                    title="[bold green]✅ Success[/bold green]",
                    border_style="bright_green"
                )
            )
            
            # Display report preview
            self.display_report_preview(report)
            
            # Ask if user wants to see full report
            if Prompt.ask(
                "\n[cyan]Would you like to see the full report?[/cyan]", 
                choices=["y", "n"], 
                default="n"
            ) == "y":
                self.console.print("\n" + "="*80)
                self.console.print(report)
            
        except KeyboardInterrupt:
            self.console.print("\n[yellow]🛑 Analysis interrupted by user[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red] Error during analysis: {e}[/red]")
            raise

@click.command()
@click.option('--url', help='arXiv paper URL or ID (optional, can be provided interactively)')
def main(url: Optional[str] = None):
    """
    🤖 Agentic Research Paper Analyzer CLI
    
    Analyze arXiv papers using multiple AI agents with real-time streaming updates.
    """
    # Check for required environment variables
    if not os.getenv("GOOGLE_API_KEY"):
        console.print(
            Panel(
                "[red]❌ GOOGLE_API_KEY environment variable not found![/red]\n\n"
                "Please set your Google AI Studio API key:\n"
                "[cyan]export GOOGLE_API_KEY='your-api-key-here'[/cyan]\n\n"
                "Or add it to your .env file.\n"
                "Get your API key from: https://aistudio.google.com/app/apikey",
                title="[bold red]Configuration Error[/bold red]",
                border_style="red"
            )
        )
        sys.exit(1)
    
    # Initialize and run analyzer
    analyzer = CLIAnalyzer()
    
    if url:
        # If URL provided via command line, set it and run
        console.print(f"[cyan]Using provided URL: {url}[/cyan]")
        analyzer.get_user_input = lambda: url
    
    try:
        asyncio.run(analyzer.run_full_analysis())
    except Exception as e:
        console.print(f"[red]Fatal error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
