from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from app.schemas.state import AgentState
from app.agents.specialized import (
    ConsistencyAgent, GrammarAgent, NoveltyAgent, 
    FactCheckAgent, AuthenticityAgent
)
from app.agents.aggregator import ReportAggregator
import logging

logger = logging.getLogger(__name__)

# Node functions
def consistency_node(state: AgentState):
    agent = ConsistencyAgent()
    result = agent.run(state)
    return {"consistency": result}

def grammar_node(state: AgentState):
    agent = GrammarAgent()
    result = agent.run(state)
    return {"grammar": result}

def novelty_node(state: AgentState):
    agent = NoveltyAgent()
    result = agent.run(state)
    return {"novelty": result}

def fact_check_node(state: AgentState):
    agent = FactCheckAgent()
    result = agent.run(state)
    return {"fact_check": result}

def authenticity_node(state: AgentState):
    agent = AuthenticityAgent()
    result = agent.run(state)
    return {"authenticity": result}

def aggregator_node(state: AgentState):
    aggregator = ReportAggregator()
    return aggregator.run(state)

# Workflow Builder
class PaperAnalysisWorkflow:
    def __init__(self, enable_checkpointing: bool = True):
        self.enable_checkpointing = enable_checkpointing

    def build(self):
        builder = StateGraph(AgentState)

        # Add Nodes
        builder.add_node("consistency", consistency_node)
        builder.add_node("grammar", grammar_node)
        builder.add_node("novelty", novelty_node)
        builder.add_node("fact_check", fact_check_node)
        builder.add_node("authenticity", authenticity_node)
        builder.add_node("aggregator", aggregator_node)

        # Parallel Execution: Start -> All Agents
        builder.add_edge(START, "consistency")
        builder.add_edge(START, "grammar")
        builder.add_edge(START, "novelty")
        builder.add_edge(START, "fact_check")
        builder.add_edge(START, "authenticity")

        # Fan-in: All Agents -> Aggregator
        builder.add_edge("consistency", "aggregator")
        builder.add_edge("grammar", "aggregator")
        builder.add_edge("novelty", "aggregator")
        builder.add_edge("fact_check", "aggregator")
        builder.add_edge("authenticity", "aggregator")

        # End
        builder.add_edge("aggregator", END)

        # Compile
        checkpointer = MemorySaver() if self.enable_checkpointing else None
        return builder.compile(checkpointer=checkpointer)
