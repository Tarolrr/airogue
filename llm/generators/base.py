"""
Base generator classes for content generation.
These classes provide the foundation for all specialized generators.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class BaseGenerator(ABC):
    """Base class for all content generators."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4.1-nano-2025-04-14", temperature: float = 1.0):
        """
        Initialize the base generator.
        
        Args:
            api_key: Optional OpenAI API key. If None, will use the OPENAI_API_KEY environment variable.
            model: The OpenAI model to use.
            temperature: Temperature for generation (0.0 to 2.0).
        """
        self.model_name = model
        self.temperature = temperature
        self.api_key = api_key
        # The LLM will be initialized when needed, not at creation time
        self._llm = None
        
    @property
    def llm(self):
        """Lazy initialization of the LLM to avoid unnecessary API key checks."""
        if self._llm is None:
            kwargs = {
                "model": self.model_name, 
                "temperature": self.temperature
            }
            if self.api_key:
                kwargs["api_key"] = self.api_key
                
            self._llm = ChatOpenAI(**kwargs)
            
        return self._llm
        
    def create_prompt(self, template_messages):
        """
        Create a ChatPromptTemplate from a list of message templates.
        
        Args:
            template_messages: List of message dictionaries with roles and content.
            
        Returns:
            ChatPromptTemplate: The created prompt template.
        """
        return ChatPromptTemplate.from_messages(template_messages)
    
    @abstractmethod
    def generate(self, *args, **kwargs):
        """
        Generate content based on the input parameters.
        
        This method must be implemented by all subclasses.
        """
        pass


class GeneratorPipeline:
    """
    A pipeline that combines multiple generators to create complex content.
    """
    
    def __init__(self, generators: Dict[str, BaseGenerator]):
        """
        Initialize the pipeline with a dictionary of generators.
        
        Args:
            generators: Dictionary mapping generator names to generator instances.
        """
        self.generators = generators
        
    def run(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the pipeline with the given inputs.
        
        Args:
            inputs: Dictionary of inputs for the generators.
            
        Returns:
            Dictionary of generator outputs.
        """
        raise NotImplementedError("GeneratorPipeline.run not implemented yet")
