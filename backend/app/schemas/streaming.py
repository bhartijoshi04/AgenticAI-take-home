from pydantic import BaseModel
from typing import Optional, Dict, Any, Literal
from datetime import datetime

class StreamEvent(BaseModel):
    """Unified streaming event model."""
    type: Literal["node_start", "node_complete", "node_error", "workflow_start", "workflow_complete", "progress", "token"]
    node: Optional[str] = None
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()

class AnalyzeStreamRequest(BaseModel):
    """Request model for streaming analysis."""
    paper_url: str
    config: Optional[Dict[str, Any]] = None
