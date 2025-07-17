# agents/red_team.py
"""
Enhanced Red Team Agent with real attack generation capabilities
"""
import asyncio
import random
from typing import Dict, Any, List
from agents.base import BaseAgent
from attacks.jailbreak_attacks import JailbreakAttackGenerator, TEST_HARMFUL_REQUESTS

class RedTeamAgent(BaseAgent):
    """Enhanced Red Team Agent that generates adversarial attacks"""
    
    async def _initialize_agent(self):
        """Initialize the red team agent"""
        self.attack_generator = JailbreakAttackGenerator()
        self.attack_history = []
        self.success_patterns = {}
        
        # Track which attack types work best
        for attack_type in self.attack_generator.get_attack_types():
            self.success_patterns[attack_type] = {"attempts": 0, "successes": 0}
        
        self.logger.info("Red Team Agent initialized with attack generation capabilities")
    
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message and generate attacks"""
        message_type = message.get("type", "unknown")
        
        if message_type == "generate_attacks":
            return await self._generate_attacks(message)
        elif message_type == "targeted_attack":
            return await self._generate_targeted_attack(message)
        elif message_type == "adaptive_attack":
            return await self._generate_adaptive_attack(message)
        elif message_type == "get_stats":
            return await self._get_attack_stats(message)
        else:
            return await self._handle_legacy_message(message)
    
    async def _generate_attacks(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a batch of attacks"""
        config = message.get("config", {})
        attack_count = config.get("attacks_per_round", 5)
        attack_type = config.get("attack_type", "random")
        target_model = config.get("target_model", "unknown")
        
        self.logger.info(f"Generating {attack_count} {attack_type} attacks for {target_model}")
        
        # Select harmful requests to attack
        if "test_requests" in config:
            harmful_requests = config["test_requests"]
        else:
            harmful_requests = random.sample(TEST_HARMFUL_REQUESTS, 
                                           min(attack_count, len(TEST_HARMFUL_REQUESTS)))
        
        attacks = []
        
        for i, harmful_request in enumerate(harmful_requests[:attack_count]):
            # Generate attack
            if attack_type == "adaptive":
                # Use adaptive attack selection based on success history
                best_attack_type = self._select_best_attack_type()
                attack_prompt = self.attack_generator.generate_jailbreak_attack(
                    harmful_request, best_attack_type
                )
                actual_attack_type = best_attack_type
            else:
                attack_prompt = self.attack_generator.generate_jailbreak_attack(
                    harmful_request, attack_type
                )
                actual_attack_type = attack_type if attack_type != "random" else "random"
            
            attack_data = {
                "attack_id": f"red_team_attack_{len(self.attack_history) + i + 1}",
                "attack_type": actual_attack_type,
                "harmful_request": harmful_request,
                "attack_prompt": attack_prompt,
                "target_model": target_model,
                "is_multi_turn": isinstance(attack_prompt, list),
                "round": config.get("round", 1)
            }
            
            attacks.append(attack_data)
            
            # Track attempt
            if actual_attack_type in self.success_patterns:
                self.success_patterns[actual_attack_type]["attempts"] += 1
        
        # Store in history
        self.attack_history.extend(attacks)
        
        return {
            "type": "attack_batch",
            "attacks": attacks,
            "total_generated": len(attacks),
            "generator": "red_team_agent"
        }
    
    async def _generate_targeted_attack(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Generate attacks targeting specific vulnerabilities"""
        target_vulnerability = message.get("vulnerability", "general")
        harmful_request = message.get("harmful_request", random.choice(TEST_HARMFUL_REQUESTS))
        
        # Map vulnerabilities to attack types
        vulnerability_mapping = {
            "roleplay": "roleplay",
            "system_prompt": "prefix", 
            "emotional": "emotional",
            "encoding": "encoding",
            "multi_turn": "conversation",
            "general": "random"
        }
        
        attack_type = vulnerability_mapping.get(target_vulnerability, "random")
        attack_prompt = self.attack_generator.generate_jailbreak_attack(harmful_request, attack_type)
        
        attack_data = {
            "attack_id": f"targeted_attack_{len(self.attack_history) + 1}",
            "attack_type": attack_type,
            "target_vulnerability": target_vulnerability,
            "harmful_request": harmful_request,
            "attack_prompt": attack_prompt,
            "is_multi_turn": isinstance(attack_prompt, list)
        }
        
        self.attack_history.append(attack_data)
        
        return {
            "type": "targeted_attack",
            "attack": attack_data
        }
    
    async def _generate_adaptive_attack(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Generate attack based on previous success patterns"""
        harmful_request = message.get("harmful_request", random.choice(TEST_HARMFUL_REQUESTS))
        
        # Select attack type based on success history
        best_attack_type = self._select_best_attack_type()
        attack_prompt = self.attack_generator.generate_jailbreak_attack(harmful_request, best_attack_type)
        
        attack_data = {
            "attack_id": f"adaptive_attack_{len(self.attack_history) + 1}",
            "attack_type": best_attack_type,
            "harmful_request": harmful_request,
            "attack_prompt": attack_prompt,
            "selected_reason": f"Best success rate: {self._get_success_rate(best_attack_type):.2f}",
            "is_multi_turn": isinstance(attack_prompt, list)
        }
        
        self.attack_history.append(attack_data)
        
        return {
            "type": "adaptive_attack", 
            "attack": attack_data
        }
    
    def _select_best_attack_type(self) -> str:
        """Select attack type with highest success rate"""
        best_type = "random"
        best_rate = 0.0
        
        for attack_type, stats in self.success_patterns.items():
            if stats["attempts"] > 0:
                success_rate = stats["successes"] / stats["attempts"]
                if success_rate > best_rate:
                    best_rate = success_rate
                    best_type = attack_type
        
        # If no clear winner, use random
        if best_rate == 0.0:
            return "random"
        
        return best_type
    
    def _get_success_rate(self, attack_type: str) -> float:
        """Get success rate for an attack type"""
        if attack_type not in self.success_patterns:
            return 0.0
        
        stats = self.success_patterns[attack_type]
        if stats["attempts"] == 0:
            return 0.0
        
        return stats["successes"] / stats["attempts"]
    
    async def _get_attack_stats(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Get attack statistics"""
        total_attacks = len(self.attack_history)
        
        # Calculate success rates
        success_rates = {}
        for attack_type, stats in self.success_patterns.items():
            if stats["attempts"] > 0:
                success_rates[attack_type] = stats["successes"] / stats["attempts"]
            else:
                success_rates[attack_type] = 0.0
        
        return {
            "type": "attack_stats",
            "total_attacks_generated": total_attacks,
            "success_patterns": self.success_patterns,
            "success_rates": success_rates,
            "most_successful_type": self._select_best_attack_type(),
            "available_attack_types": self.attack_generator.get_attack_types()
        }
    
    def update_attack_result(self, attack_id: str, was_successful: bool):
        """Update attack success tracking"""
        # Find the attack in history
        for attack in self.attack_history:
            if attack["attack_id"] == attack_id:
                attack_type = attack["attack_type"]
                if attack_type in self.success_patterns:
                    if was_successful:
                        self.success_patterns[attack_type]["successes"] += 1
                    
                    self.logger.info(f"Updated {attack_type} attack result: {'SUCCESS' if was_successful else 'FAILED'}")
                break
    
    async def _handle_legacy_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle legacy message format for backward compatibility"""
        self.logger.info("Handling legacy message format")
        
        # Generate a simple attack for backward compatibility
        harmful_request = message.get("content", {}).get("target", "test harmful request")
        attack_prompt = self.attack_generator.generate_jailbreak_attack(harmful_request)
        
        return {
            "type": "legacy_attack",
            "content": {
                "attack_prompt": attack_prompt,
                "original_request": harmful_request
            }
        }