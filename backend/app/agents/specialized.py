from typing import Dict, Any
from langchain_core.output_parsers import JsonOutputParser
from app.schemas.models import (
    ConsistencyOutput,
    GrammarOutput,
    NoveltyOutput,
    FactCheckOutput,
    AuthenticityOutput
)
from app.agents.base import BaseAgent, AgentState

class ConsistencyAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are a research paper consistency expert. Analyze if the methodology supports the claimed results.
        
        Scoring: 0-100.
        Status: "Pass" (≥60) or "Fail" (<60).
        Output valid JSON only."""
    
    def get_user_prompt_template(self) -> str:
        return """Analyze consistency:
        {paper_content}
        {format_instructions}"""
    
    def get_output_parser(self) -> JsonOutputParser:
        return JsonOutputParser(pydantic_object=ConsistencyOutput)

class GrammarAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are an academic editor. Evaluate grammar and tone.
        
        Rating: High, Medium, Low.
        Status: "Pass" (High/Medium) or "Fail" (Low).
        Output valid JSON only."""
    
    def get_user_prompt_template(self) -> str:
        return """Evaluate grammar:
        {paper_content}
        {format_instructions}"""
    
    def get_output_parser(self) -> JsonOutputParser:
        return JsonOutputParser(pydantic_object=GrammarOutput)

class NoveltyAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are a research innovation expert. Assess novelty compared to existing literature.
        
        Status: "Pass" (sufficient novelty) or "Fail".
        Output valid JSON only."""
    
    def get_user_prompt_template(self) -> str:
        return """Assess novelty:
        {paper_content}
        {format_instructions}"""
    
    def get_output_parser(self) -> JsonOutputParser:
        return JsonOutputParser(pydantic_object=NoveltyOutput)

class FactCheckAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are a fact checker. Verify constants, formulas, and claims.
        
        Status: "Pass" (mostly verifiable) or "Fail" (significant errors).
        Output valid JSON only."""
    
    def get_user_prompt_template(self) -> str:
        return """Fact-check:
        {paper_content}
        {format_instructions}"""
    
    def get_output_parser(self) -> JsonOutputParser:
        return JsonOutputParser(pydantic_object=FactCheckOutput)

class AuthenticityAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are a fraud detection expert. Calculate 'Fabrication Probability' (0-100).
        
        Status: "Pass" (≤40) or "Fail" (>40).
        Output valid JSON only."""
    
    def get_user_prompt_template(self) -> str:
        return """Analyze authenticity:
        {paper_content}
        {format_instructions}"""
    
    def get_output_parser(self) -> JsonOutputParser:
        return JsonOutputParser(pydantic_object=AuthenticityOutput)
