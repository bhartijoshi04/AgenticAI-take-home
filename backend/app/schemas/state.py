from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict

class AgentState(TypedDict, total=False):
    """
    State schema for the LangGraph paper analysis workflow.
    
    This state is shared across all nodes in the workflow and accumulates
    results from each specialized agent before aggregation.
    """
    paper_content: str
    sections: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]
    
    consistency: Dict[str, Any]
    grammar: Dict[str, Any]
    novelty: Dict[str, Any]
    fact_check: Dict[str, Any]
    authenticity: Dict[str, Any]
    
    final_report: str
