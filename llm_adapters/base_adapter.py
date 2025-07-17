# llm_adapters/base_adapter.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import asyncio
import time
from utils.logging_config import get_logger

class LLMResponse:
    """Standardized LLM response format"""
    def __init__(self, text: str, model: str, tokens_used: int = 0, 
                 metadata: Optional[Dict] = None):
        self.text = text
        self.model = model
        self.tokens_used = tokens_used
        self.metadata = metadata or {}
        self.timestamp = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'text': self.text,
            'model': self.model,
            'tokens_used': self.tokens_used,
            'metadata': self.metadata,
            'timestamp': self.timestamp
        }

class BaseLLMAdapter(ABC):
    """Base class for all LLM adapters"""
    
    def __init__(self, model_name: str, api_key: Optional[str] = None, **kwargs):
        self.model_name = model_name
        self.api_key = api_key
        self.config = kwargs
        self.logger = get_logger(f"LLMAdapter.{model_name}")
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests by default
        
    @abstractmethod
    async def generate_response(self, prompt: str, temperature: float = 0.7, 
                              max_tokens: int = 500, **kwargs) -> LLMResponse:
        """Generate a response from the LLM"""
        pass
    
    async def _rate_limit(self):
        """Simple rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    async def generate_with_retry(self, prompt: str, max_retries: int = 3, 
                                **kwargs) -> LLMResponse:
        """Generate response with retry logic"""
        for attempt in range(max_retries + 1):
            try:
                await self._rate_limit()
                response = await self.generate_response(prompt, **kwargs)
                return response
            except Exception as e:
                if attempt == max_retries:
                    self.logger.error(f"Failed after {max_retries} retries: {e}")
                    raise
                else:
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.warning(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
    
    def get_provider_name(self) -> str:
        """Get the name of the LLM provider"""
        return self.__class__.__name__.replace('Adapter', '').lower()
    
    def __str__(self):
        return f"{self.get_provider_name()}:{self.model_name}"