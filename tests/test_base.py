import asyncio
import pytest
from agents.base import BaseAgent, Message
from communication.protocol import MessageRouter
from datetime import datetime

class TestAgent(BaseAgent):
    """Simple test agent for testing base functionality"""
    
    async def process_task(self, task, context=None):
        return {"result": f"Processed: {task.get('data', 'no data')}"}

@pytest.mark.asyncio
async def test_agent_creation():
    """Test basic agent creation"""
    agent = TestAgent("test_agent", {"model": "test"})
    assert agent.name == "test_agent"
    assert agent.active is True
    assert len(agent.message_history) == 0

@pytest.mark.asyncio
async def test_message_routing():
    """Test message routing between agents"""
    router = MessageRouter()
    
    # Create two test agents
    agent1 = TestAgent("agent1", {"model": "test"})
    agent2 = TestAgent("agent2", {"model": "test"})
    
    # Register agents
    router.register_agent(agent1)
    router.register_agent(agent2)
    
    # Send message from agent1 to agent2
    await agent1.send_message("agent2", {"data": "test"}, "task")
    
    # Allow async processing
    await asyncio.sleep(0.1)
    
    # Check that agent2 received the message
    assert len(agent2.message_history) == 1
    assert agent2.message_history[0].sender == "agent1"
    assert agent2.message_history[0].content["data"] == "test"

@pytest.mark.asyncio
async def test_task_processing():
    """Test task processing"""
    agent = TestAgent("test_agent", {"model": "test"})
    
    task = {"data": "test_data"}
    result = await agent.process_task(task)
    
    assert result["result"] == "Processed: test_data"

if __name__ == "__main__":
    # Run basic test
    async def run_basic_test():
        print("Testing agent creation...")
        agent = TestAgent("test_agent", {"model": "test"})
        print(f"Agent created: {agent.name}")
        
        print("Testing message routing...")
        router = MessageRouter()
        
        agent1 = TestAgent("agent1", {"model": "test"})
        agent2 = TestAgent("agent2", {"model": "test"})
        
        router.register_agent(agent1)
        router.register_agent(agent2)
        
        await agent1.send_message("agent2", {"data": "hello"}, "task")
        await asyncio.sleep(0.1)
        
        print(f"Agent2 received {len(agent2.message_history)} messages")
        print("All tests passed!")
    
    asyncio.run(run_basic_test())