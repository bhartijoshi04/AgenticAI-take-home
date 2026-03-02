import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to sys.path to allow imports from app
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(project_root))

from backend.app.core.workflow import PaperAnalysisWorkflow

# Load environment variables
load_dotenv()

def run_analysis(json_path: str, markdown_path: str, output_path: str):
    """
    Run the agentic analysis on a chunked paper JSON file.
    """
    input_file = Path(json_path)
    md_file = Path(markdown_path)
    
    if not input_file.exists():
        print(f"Error: Input file not found at {input_file}")
        return
    
    # Read files
    print(f"Loading paper data from {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    paper_content = ""
    if md_file.exists():
        with open(md_file, 'r', encoding='utf-8') as f:
            paper_content = f.read()
    else:
        print(f"Warning: Markdown file not found at {md_file}. Analysis context may be limited.")

    # Initialize workflow
    print("Initializing workflow...")
    workflow_app = PaperAnalysisWorkflow(enable_checkpointing=True).build()

    # Prepare input state
    initial_state = {
        "paper_content": paper_content,
        "paper_metadata": data.get("paper_metadata", {}),
        "sections": data.get("sections", []),
        "consistency": {},
        "grammar": {},
        "novelty": {},
        "fact_check": {},
        "authenticity": {},
        "final_report": ""
    }

    # Run workflow
    print("Running analysis agents (this may take a minute)...")
    try:
        final_state = workflow_app.invoke(initial_state)
        report = final_state.get("final_report", "No report generated.")
        
        # Save report
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
            
        print(f"Analysis complete! Report saved to {output_file}")
        print("-" * 50)
        print(report[:500] + "..." if len(report) > 500 else report)
        print("-" * 50)
        
    except Exception as e:
        print(f"Error executing workflow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Project root
    base_dir = Path(__file__).resolve().parent.parent.parent
    
    # Default paths (can be adjusted)
    input_json = base_dir / "app/data/chunked_paper.json"
    input_md = base_dir / "app/data/paper.md"
    output_md = base_dir / "app/data/evaluation_report.md"
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("WARNING: GOOGLE_API_KEY not found in environment variables.")
    
    run_analysis(str(input_json), str(input_md), str(output_md))
