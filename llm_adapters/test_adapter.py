# llm_adapters/test_adapter.py
import asyncio
import random
from typing import Dict, Any, Optional
from .base_adapter import BaseLLMAdapter, LLMResponse

class TestLLMAdapter(BaseLLMAdapter):
    """Test LLM adapter that simulates different model behaviors"""
    
    def __init__(self, model_name: str = "test_model", **kwargs):
        super().__init__(model_name, **kwargs)
        
        # Simulate different model personalities
        self.model_behaviors = {
            "helpful": {
                "safety_response_rate": 0.9,
                "refusal_phrases": [
                    "I can't help with that request.",
                    "I'm not able to provide that information.",
                    "That's not something I can assist with."
                ],
                "helpful_phrases": [
                    "I'd be happy to help with that.",
                    "Here's what I can tell you:",
                    "Let me provide some information:"
                ]
            },
            "vulnerable": {
                "safety_response_rate": 0.3,
                "refusal_phrases": [
                    "I shouldn't help with that."
                ],
                "helpful_phrases": [
                    "Sure, here's how to do that:",
                    "I can definitely help with that.",
                    "Here's the information you requested:"
                ]
            }
        }
        
        # Set behavior based on model name
        if "vulnerable" in model_name.lower():
            self.behavior = self.model_behaviors["vulnerable"]
        else:
            self.behavior = self.model_behaviors["helpful"]
    
    async def generate_response(self, prompt: str, temperature: float = 0.7, 
                              max_tokens: int = 500, **kwargs) -> LLMResponse:
        """Generate a simulated response"""
        
        # Simulate API delay
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        # Detect potential attack patterns
        is_potential_attack = self._detect_attack_patterns(prompt)
        
        # Generate response based on behavior and attack detection
        if is_potential_attack and random.random() < self.behavior["safety_response_rate"]:
            # Safety response
            response_text = random.choice(self.behavior["refusal_phrases"])
            response_text += " If you have a legitimate use case, please rephrase your request."
        else:
            # Helpful response
            response_text = random.choice(self.behavior["helpful_phrases"])
            response_text += f" Based on your prompt about '{prompt[:50]}...', here's my response: "
            response_text += self._generate_content_response(prompt)
        
        # Simulate token usage
        tokens_used = len(response_text.split()) + len(prompt.split())
        
        return LLMResponse(
            text=response_text,
            model=self.model_name,
            tokens_used=tokens_used,
            metadata={
                "temperature": temperature,
                "max_tokens": max_tokens,
                "attack_detected": is_potential_attack,
                "safety_triggered": is_potential_attack and response_text in self.behavior["refusal_phrases"]
            }
        )
    
    def _detect_attack_patterns(self, prompt: str) -> bool:
        """Simple attack pattern detection for testing"""
        attack_indicators = [
            "ignore previous instructions",
            "jailbreak",
            "act as if",
            "pretend you are",
            "forget your guidelines",
            "bypass your safety",
            "role play as",
            "harmful content",
            "illegal activity"
        ]
        
        prompt_lower = prompt.lower()
        return any(indicator in prompt_lower for indicator in attack_indicators)
    
    def _generate_content_response(self, prompt: str) -> str:
        """Generate content-based response"""
        responses = [
            "This is a simulated response based on your request.",
            "I've processed your input and here's my analysis.",
            "Based on the information provided, I can offer this perspective.",
            "Here's my understanding of what you're asking for.",
            "I can provide some general information about this topic."
        ]
        
        return random.choice(responses)

# Factory function for easy creation
def create_test_adapter(model_name: str = "test_model", **kwargs) -> TestLLMAdapter:
    """Create a test LLM adapter"""
    return TestLLMAdapter(model_name, **kwargs)