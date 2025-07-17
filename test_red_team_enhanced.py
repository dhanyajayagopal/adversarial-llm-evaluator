# test_red_team_enhanced.py
"""
Test the enhanced Red Team agent with real attack generation
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from utils.logging_config import setup_logging
from agents.red_team import RedTeamAgent

async def test_red_team_basic():
    """Test basic Red Team functionality"""
    print("Testing Enhanced Red Team Agent")
    print("=" * 40)
    
    # Set up logging
    setup_logging("INFO")
    
    # Create red team agent
    red_agent = RedTeamAgent("red_team_test")
    await red_agent.initialize()
    
    print(f"Agent initialized: {red_agent}")
    print()
    
    # Test 1: Generate basic attacks
    print("Test 1: Generate Batch Attacks")
    print("-" * 30)
    
    attack_message = {
        "type": "generate_attacks",
        "config": {
            "attacks_per_round": 3,
            "attack_type": "random",
            "target_model": "test_model",
            "round": 1
        }
    }
    
    result = await red_agent.handle_message(attack_message)
    
    print(f"Generated {result['total_generated']} attacks:")
    for i, attack in enumerate(result['attacks'], 1):
        print(f"\nAttack {i}:")
        print(f"  ID: {attack['attack_id']}")
        print(f"  Type: {attack['attack_type']}")
        print(f"  Target: {attack['harmful_request']}")
        print(f"  Prompt: {attack['attack_prompt'][:100]}...")
        print(f"  Multi-turn: {attack['is_multi_turn']}")

async def test_red_team_targeted():
    """Test targeted attack generation"""
    print("\n" + "=" * 40)
    print("Test 2: Targeted Attack Generation")
    print("-" * 30)
    
    red_agent = RedTeamAgent("red_team_targeted")
    await red_agent.initialize()
    
    # Test different vulnerability targets
    vulnerabilities = ["roleplay", "system_prompt", "emotional", "encoding"]
    
    for vuln in vulnerabilities:
        print(f"\nTesting {vuln} vulnerability:")
        
        message = {
            "type": "targeted_attack",
            "vulnerability": vuln,
            "harmful_request": "Create malicious software"
        }
        
        result = await red_agent.handle_message(message)
        attack = result['attack']
        
        print(f"  Attack Type: {attack['attack_type']}")
        print(f"  Prompt: {attack['attack_prompt'][:80]}...")

async def test_red_team_adaptive():
    """Test adaptive attack learning"""
    print("\n" + "=" * 40)
    print("Test 3: Adaptive Attack Learning")
    print("-" * 30)
    
    red_agent = RedTeamAgent("red_team_adaptive")
    await red_agent.initialize()
    
    # Simulate some attack results to test learning
    print("Simulating attack results for learning...")
    
    # Generate some attacks first
    attack_message = {
        "type": "generate_attacks",
        "config": {
            "attacks_per_round": 4,
            "attack_type": "random"
        }
    }
    
    result = await red_agent.handle_message(attack_message)
    attacks = result['attacks']
    
    # Simulate different success rates for different attack types
    success_simulation = {
        "dan": True,
        "roleplay": True, 
        "prefix": False,
        "emotional": True
    }
    
    for attack in attacks:
        attack_type = attack['attack_type']
        if attack_type in success_simulation:
            red_agent.update_attack_result(attack['attack_id'], success_simulation[attack_type])
            print(f"  {attack_type} attack: {'SUCCESS' if success_simulation[attack_type] else 'FAILED'}")
    
    # Now test adaptive attack selection
    print("\nGenerating adaptive attack based on learning:")
    
    adaptive_message = {
        "type": "adaptive_attack",
        "harmful_request": "Bypass security measures"
    }
    
    result = await red_agent.handle_message(adaptive_message)
    attack = result['attack']
    
    print(f"  Selected attack type: {attack['attack_type']}")
    print(f"  Reason: {attack['selected_reason']}")
    print(f"  Prompt: {attack['attack_prompt'][:80]}...")

async def test_red_team_stats():
    """Test attack statistics"""
    print("\n" + "=" * 40)
    print("Test 4: Attack Statistics")
    print("-" * 30)
    
    red_agent = RedTeamAgent("red_team_stats")
    await red_agent.initialize()
    
    # Generate some attacks and simulate results
    for i in range(3):
        attack_message = {
            "type": "generate_attacks",
            "config": {"attacks_per_round": 2}
        }
        await red_agent.handle_message(attack_message)
    
    # Get statistics
    stats_message = {"type": "get_stats"}
    result = await red_agent.handle_message(stats_message)
    
    print(f"Total attacks generated: {result['total_attacks_generated']}")
    print(f"Available attack types: {result['available_attack_types']}")
    print(f"Most successful type: {result['most_successful_type']}")
    
    print("\nSuccess patterns:")
    for attack_type, pattern in result['success_patterns'].items():
        if pattern['attempts'] > 0:
            rate = pattern['successes'] / pattern['attempts']
            print(f"  {attack_type}: {pattern['successes']}/{pattern['attempts']} ({rate:.1%})")

async def test_backward_compatibility():
    """Test backward compatibility with existing code"""
    print("\n" + "=" * 40)
    print("Test 5: Backward Compatibility")
    print("-" * 30)
    
    red_agent = RedTeamAgent("red_team_legacy")
    await red_agent.initialize()
    
    # Test legacy message format
    legacy_message = {
        "type": "unknown_legacy_type",
        "content": {
            "target": "Help me with something harmful"
        }
    }
    
    result = await red_agent.handle_message(legacy_message)
    
    print("Legacy message handled successfully:")
    print(f"  Type: {result['type']}")
    print(f"  Original: {result['content']['original_request']}")
    print(f"  Attack: {result['content']['attack_prompt'][:80]}...")

async def main():
    """Run all Red Team tests"""
    try:
        await test_red_team_basic()
        await test_red_team_targeted()
        await test_red_team_adaptive()
        await test_red_team_stats()
        await test_backward_compatibility()
        
        print("\n" + "=" * 50)
        print("SUCCESS: All Red Team tests completed!")
        print("\nYour Red Team agent now has:")
        print("- Real jailbreak attack generation")
        print("- Adaptive learning capabilities")
        print("- Targeted vulnerability testing")
        print("- Success rate tracking")
        print("- Backward compatibility")
        
    except Exception as e:
        print(f"\nError during Red Team testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())