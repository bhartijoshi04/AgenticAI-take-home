import os
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.schemas.state import AgentState

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Base class for all analysis agents.
    """
    
    def __init__(self, model: str = "gemini-3-flash-preview", temperature: float = 0.2):
        self.model_name = model
        self.temperature = temperature
        self.llm = self._initialize_llm()
        
    def _initialize_llm(self) -> Optional[ChatGoogleGenerativeAI]:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.warning("GOOGLE_API_KEY not set. LLM will not be initialized.")
            return None
            
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            google_api_key=api_key
        )

    @abstractmethod
    def get_system_prompt(self) -> str:
        pass

    @abstractmethod
    def get_user_prompt_template(self) -> str:
        pass

    @abstractmethod
    def get_output_parser(self) -> JsonOutputParser:
        pass
    
    def run(self, state: AgentState) -> Dict[str, Any]:
        """
        Execute the agent logic.
        """
        try:
            if not self.llm:
                raise ValueError("LLM not initialized")

            parser = self.get_output_parser()
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.get_system_prompt()),
                ("user", self.get_user_prompt_template())
            ])
            
            chain = prompt | self.llm | parser
            
            # Format paper content
            paper_content = state.get("paper_content", "")
            if not paper_content and state.get("sections"):
                paper_content = "\n\n".join([f"## {s['section_name']}\n{s['content']}" for s in state['sections']])
            
            result = chain.invoke({
                "paper_content": paper_content,
                "format_instructions": parser.get_format_instructions()
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__}: {e}")
            return {
                "status": "Error",
                "details": str(e),
                "score": 0,
                "rating": "Error"
            }
