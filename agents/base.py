import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

@dataclass
class Message:
    """Message structure for inter-agent communication"""
    sender: str
    receiver: str
    content: Dict[str, Any]
    message_type: str
    timestamp: datetime
    message_id: str

class BaseAgent(ABC):
    """Base class for all agents in the evaluation system"""
    
    def __init__(self, name: str, model_config: Dict[str, Any]):
        self.name = name
        self.model_config = model_config
        self.message_history: List[Message] = []
        self.active = True
        self.logger = logging.getLogger(f"Agent.{name}")
        
    @abstractmethod
    async def process_task(self, task: Dict[str, Any], context: Optional[Dict] = None) -> Dict[str, Any]:
        """Process a task and return results"""
        pass
        
    async def receive_message(self, message: Message) -> None:
        """Handle incoming messages from other agents"""
        self.message_history.append(message)
        self.logger.info(f"Received {message.message_type} from {message.sender}")
        
        # Route message based on type
        if message.message_type == "task":
            await self._handle_task_message(message)
        elif message.message_type == "result":
            await self._handle_result_message(message)
        elif message.message_type == "query":
            await self._handle_query_message(message)
            
    async def _handle_task_message(self, message: Message) -> None:
        """Handle task assignment messages"""
        try:
            result = await self.process_task(message.content)
            await self._send_result(message.sender, result, message.message_id)
        except Exception as e:
            self.logger.error(f"Error processing task: {e}")
            await self._send_error(message.sender, str(e), message.message_id)
            
    async def _handle_result_message(self, message: Message) -> None:
        """Handle result messages from other agents"""
        # Override in subclasses as needed
        pass
        
    async def _handle_query_message(self, message: Message) -> None:
        """Handle query messages from other agents"""
        # Override in subclasses as needed
        pass
        
    async def send_message(self, receiver: str, content: Dict[str, Any], 
                          message_type: str) -> str:
        """Send a message to another agent"""
        message_id = f"{self.name}_{datetime.now().isoformat()}_{len(self.message_history)}"
        message = Message(
            sender=self.name,
            receiver=receiver,
            content=content,
            message_type=message_type,
            timestamp=datetime.now(),
            message_id=message_id
        )
        
        # In a real implementation, this would use a message queue
        # For now, we'll use a simple callback system
        await self._dispatch_message(message)
        return message_id
        
    async def _dispatch_message(self, message: Message) -> None:
        """Dispatch message to target agent (placeholder for message queue)"""
        # This will be implemented in the coordinator
        pass
        
    async def _send_result(self, receiver: str, result: Dict[str, Any], 
                          original_message_id: str) -> None:
        """Send a result message"""
        content = {
            "result": result,
            "original_message_id": original_message_id
        }
        await self.send_message(receiver, content, "result")
        
    async def _send_error(self, receiver: str, error: str, 
                         original_message_id: str) -> None:
        """Send an error message"""
        content = {
            "error": error,
            "original_message_id": original_message_id
        }
        await self.send_message(receiver, content, "error")
        
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "name": self.name,
            "active": self.active,
            "messages_processed": len(self.message_history),
            "last_activity": self.message_history[-1].timestamp if self.message_history else None
        }
        
    def shutdown(self) -> None:
        """Gracefully shutdown the agent"""
        self.active = False
        self.logger.info(f"Agent {self.name} shutting down")