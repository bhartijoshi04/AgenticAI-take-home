from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field

# --- Domain Models ---

class Section(BaseModel):
    section_name: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class PaperMetadata(BaseModel):
    title: str
    total_sections: int
    total_word_count: int
    total_char_count: int
    extraction_timestamp: Optional[str] = None

class AnalysisResult(BaseModel):
    score: Optional[float] = None
    rating: Optional[str] = None
    details: str
    status: str


# Output Models for Agent Results
class ConsistencyOutput(BaseModel):
    score: float = Field(description="Score from 0-100 representing consistency")
    details: str = Field(description="Detailed analysis of methodology supporting claimed results")
    status: str = Field(description="Pass/Fail recommendation based on consistency")

class GrammarOutput(BaseModel):
    rating: str = Field(description="High/Medium/Low rating for grammar and professional tone")
    details: str = Field(description="Detailed evaluation of syntax and tone")
    status: str = Field(description="Pass/Fail recommendation")

class NoveltyOutput(BaseModel):
    details: str = Field(description="Qualitative description of uniqueness and existing literature search")
    status: str = Field(description="Pass/Fail recommendation based on novelty")

class FactCheckOutput(BaseModel):
    details: str = Field(description="List of verified vs. unverified claims, constants, formulas")
    status: str = Field(description="Pass/Fail recommendation")

class AuthenticityOutput(BaseModel):
    score: float = Field(description="Fabrication Probability percentage (0-100)")
    details: str = Field(description="Analysis of statistical anomalies or logical leaps")
    status: str = Field(description="Pass/Fail recommendation")
