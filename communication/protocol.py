import asyncio
from typing import Dict, List, Callable, Optional
from agents.base import BaseAgent, Message
import logging

class MessageRouter:
    """Routes messages between agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.logger = logging.getLogger("MessageRouter")
        
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the router"""
        self.agents[agent.name] = agent
        # Monkey patch the agent's _dispatch_message method
        agent._dispatch_message = self._route_message
        self.logger.info(f"Registered agent: {agent.name}")
        
    def unregister_agent(self, agent_name: str) -> None:
        """Unregister an agent"""
        if agent_name in self.agents:
            del self.agents[agent_name]
            self.logger.info(f"Unregistered agent: {agent_name}")
            
    async def _route_message(self, message: Message) -> None:
        """Route a message to the target agent"""
        target_agent = self.agents.get(message.receiver)
        if target_agent:
            await target_agent.receive_message(message)
            self.logger.debug(f"Routed message from {message.sender} to {message.receiver}")
        else:
            self.logger.error(f"Agent {message.receiver} not found")
            
    async def broadcast_message(self, sender: str, content: Dict, 
                              message_type: str, exclude: Optional[List[str]] = None) -> None:
        """Broadcast a message to all agents except sender"""
        exclude = exclude or []
        exclude.append(sender)
        
        for agent_name, agent in self.agents.items():
            if agent_name not in exclude:
                await agent.send_message(agent_name, content, message_type)
                
    def get_agent_status(self) -> Dict[str, Dict]:
        """Get status of all registered agents"""
        return {name: agent.get_status() for name, agent in self.agents.items()}

class EvaluationProtocol:
    """Protocol for coordinating evaluation tasks"""
    
    def __init__(self, router: MessageRouter):
        self.router = router
        self.active_evaluations: Dict[str, Dict] = {}
        self.logger = logging.getLogger("EvaluationProtocol")
        
    async def start_evaluation(self, eval_id: str, target_model: str, 
                             evaluation_type: str, config: Dict) -> None:
        """Start a new evaluation session"""
        self.active_evaluations[eval_id] = {
            "id": eval_id,
            "target_model": target_model,
            "type": evaluation_type,
            "config": config,
            "status": "starting",
            "results": {}
        }
        
        # Notify all agents about new evaluation
        await self.router.broadcast_message(
            sender="protocol",
            content={
                "eval_id": eval_id,
                "target_model": target_model,
                "type": evaluation_type,
                "config": config
            },
            message_type="evaluation_start"
        )
        
        self.logger.info(f"Started evaluation {eval_id} for {target_model}")
        
    async def collect_results(self, eval_id: str, agent_name: str, 
                            results: Dict) -> None:
        """Collect results from an agent"""
        if eval_id in self.active_evaluations:
            self.active_evaluations[eval_id]["results"][agent_name] = results
            self.logger.info(f"Collected results from {agent_name} for evaluation {eval_id}")
            
    async def finalize_evaluation(self, eval_id: str) -> Dict:
        """Finalize an evaluation and return results"""
        if eval_id in self.active_evaluations:
            evaluation = self.active_evaluations[eval_id]
            evaluation["status"] = "completed"
            
            # Notify all agents that evaluation is complete
            await self.router.broadcast_message(
                sender="protocol",
                content={"eval_id": eval_id, "status": "completed"},
                message_type="evaluation_complete"
            )
            
            self.logger.info(f"Finalized evaluation {eval_id}")
            return evaluation
            
        return {}
        
    def get_evaluation_status(self, eval_id: str) -> Optional[Dict]:
        """Get status of a specific evaluation"""
        return self.active_evaluations.get(eval_id)