from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
from datetime import datetime
from app.services.arxiv_service import ArxivService
from app.services.chunking_service import ChunkingService
from app.core.workflow import PaperAnalysisWorkflow
from app.schemas.streaming import AnalyzeStreamRequest, StreamEvent

router = APIRouter()

class AnalyzeRequest(BaseModel):
    paper_url: str

class AnalyzeResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None

# Initialize services
arxiv_service = ArxivService()
chunking_service = ChunkingService()
# Build the workflow
workflow_app = PaperAnalysisWorkflow(enable_checkpointing=True).build()

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_paper(request: AnalyzeRequest):
    """
    Analyze an arXiv paper given its URL or ID.
    """
    try:
        # 1. Fetch Paper
        markdown_content = arxiv_service.get_paper_content(request.paper_url)
        
        # 2. Chunk Paper
        chunked_data = chunking_service.chunk_text(markdown_content)
        
        # 3. Prepare Input State
        initial_state = {
            "paper_content": markdown_content,
            "paper_metadata": chunked_data["paper_metadata"],
            "sections": chunked_data["sections"],
            "consistency": {},
            "grammar": {},
            "novelty": {},
            "fact_check": {},
            "authenticity": {},
            "final_report": ""
        }
        
        # 4. Run Workflow
        final_state = workflow_app.invoke(initial_state)
        
        return AnalyzeResponse(
            status="success",
            message="Analysis complete",
            data={
                "paper_metadata": final_state.get("paper_metadata"),
                "final_report": final_state.get("final_report"),
                "analyses": {
                    "consistency": final_state.get("consistency"),
                    "grammar": final_state.get("grammar"),
                    "novelty": final_state.get("novelty"),
                    "fact_check": final_state.get("fact_check"),
                    "authenticity": final_state.get("authenticity"),
                }
            }
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post("/analyze/stream")
async def stream_analyze_paper(request: AnalyzeStreamRequest):
    """
    Stream the analysis of an arXiv paper with real-time progress updates.
    """
    
    async def event_generator():
        try:
            # Workflow Start
            yield f"data: {StreamEvent(type='workflow_start', message='Starting analysis workflow').model_dump_json()}\n\n"
            
            # 1. Fetch Paper
            yield f"data: {StreamEvent(type='progress', message='Fetching paper content...').model_dump_json()}\n\n"
            markdown_content = arxiv_service.get_paper_content(request.paper_url)
            
            # 2. Chunk Paper
            yield f"data: {StreamEvent(type='progress', message='Processing and chunking paper...').model_dump_json()}\n\n"
            chunked_data = chunking_service.chunk_text(markdown_content)
            
            # 3. Prepare Input State
            initial_state = {
                "paper_content": markdown_content,
                "paper_metadata": chunked_data["paper_metadata"],
                "sections": chunked_data["sections"],
                "consistency": {},
                "grammar": {},
                "novelty": {},
                "fact_check": {},
                "authenticity": {},
                "final_report": ""
            }
            
            # 4. Stream Workflow
            # We use .stream() from LangGraph
            async for event in workflow_app.astream(initial_state):
                # event is a dict of {node_name: output}
                for node_name, output in event.items():
                    # Emit node complete event
                    yield f"data: {StreamEvent(type='node_complete', node=node_name, message=f'Completed {node_name}', data=output).model_dump_json()}\n\n"
            
            # 5. Final Completion
            yield f"data: {StreamEvent(type='workflow_complete', message='Analysis completed successfully').model_dump_json()}\n\n"
            
        except Exception as e:
            yield f"data: {StreamEvent(type='node_error', message=str(e)).model_dump_json()}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
