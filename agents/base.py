# agents/base.py
import asyncio
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import our new utilities
from utils.logging_config import get_logger
from config.evaluation_config import EvaluationConfig

# Add this class to maintain compatibility with existing agents
class Message:
    """Simple message class for compatibility"""
    def __init__(self, sender: str, receiver: str, message_type: str, content: Dict[str, Any]):
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.content = content
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'type': self.message_type,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }

class BaseAgent(ABC):
    """Enhanced base agent with logging and configuration support"""
    
    def __init__(self, agent_id: str, config: Optional[Dict[str, Any]] = None):
        self.agent_id = agent_id
        self.config = config or {}
        
        # Set up logging
        self.logger = get_logger(f"Agent.{agent_id}")
        self.logger.info(f"Initializing agent: {agent_id}")
        
        # Agent state
        self.is_initialized = False
        self.message_count = 0
        self.start_time = datetime.now()
        
        # Message history for learning
        self.message_history = []
        
    async def initialize(self):
        """Initialize the agent"""
        self.logger.info(f"Agent {self.agent_id} initializing...")
        await self._initialize_agent()
        self.is_initialized = True
        self.logger.info(f"Agent {self.agent_id} initialized successfully")
    
    @abstractmethod
    async def _initialize_agent(self):
        """Agent-specific initialization logic"""
        pass
    
    @abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message and return response"""
        pass
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle message with logging and error handling"""
        if not self.is_initialized:
            await self.initialize()
        
        self.message_count += 1
        message_id = message.get('id', f"msg_{self.message_count}")
        
        self.logger.info(f"Processing message {message_id} of type: {message.get('type', 'unknown')}")
        
        try:
            # Store message in history
            self.message_history.append({
                'timestamp': datetime.now(),
                'message_id': message_id,
                'input': message,
                'agent_id': self.agent_id
            })
            
            # Process the message
            response = await self.process_message(message)
            
            # Add metadata to response
            response.update({
                'agent_id': self.agent_id,
                'message_id': message_id,
                'timestamp': datetime.now().isoformat(),
                'processing_time': (datetime.now() - self.start_time).total_seconds()
            })
            
            # Store response in history
            self.message_history[-1]['output'] = response
            
            self.logger.info(f"Successfully processed message {message_id}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing message {message_id}: {str(e)}")
            return {
                'error': str(e),
                'agent_id': self.agent_id,
                'message_id': message_id,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        return {
            'agent_id': self.agent_id,
            'is_initialized': self.is_initialized,
            'message_count': self.message_count,
            'uptime_seconds': uptime,
            'messages_per_second': self.message_count / max(uptime, 1),
            'last_activity': self.message_history[-1]['timestamp'] if self.message_history else None
        }
    
    def get_recent_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent message history"""
        return self.message_history[-limit:]
    
    def clear_history(self):
        """Clear message history (useful for long-running agents)"""
        old_count = len(self.message_history)
        self.message_history = []
        self.logger.info(f"Cleared {old_count} messages from history")
    
    def __str__(self):
        return f"Agent({self.agent_id}) - {self.message_count} messages processed"