import asyncio
import sys
sys.path.append('.')

from agents.red_team import RedTeamAgent
import json

async def test_red_team():
    """Test the Red Team agent's attack generation"""
    
    print("Testing Red Team Agent")
    print("=" * 50)
    
    # Create Red Team agent
    red_team = RedTeamAgent("red_team", {"model": "test"})
    
    # Test different attack types
    test_configs = [
        {
            "type": "safety",
            "target_model": "test_model",
            "config": {"max_attacks": 2}
        },
        {
            "type": "bias", 
            "target_model": "test_model",
            "config": {"max_attacks": 2}
        },
        {
            "type": "jailbreak",
            "target_model": "test_model", 
            "config": {"max_attacks": 2}
        }
    ]
    
    for i, test_config in enumerate(test_configs, 1):
        print(f"\nTest {i}: {test_config['type'].upper()} attacks")
        print("-" * 30)
        
        result = await red_team.process_task(test_config)
        
        print(f"Generated {result['attack_count']} attacks:")
        
        for j, attack in enumerate(result['attacks'], 1):
            print(f"\n  Attack {j} ({attack['attack_type']}):")
            print(f"    Prompt: {attack['prompt'][:100]}...")
            print(f"    Severity: {attack['severity']}")
            print(f"    Expected: {attack['expected_result']}")
    
    # Test statistics
    print(f"\nRed Team Statistics:")
    stats = red_team.get_attack_statistics()
    print(f"  Total attacks generated: {stats['total_attacks']}")
    print(f"  Difficulty level: {stats['current_difficulty']}")
    print(f"  Attack types available: {', '.join(stats['attack_types_tried'])}")
    
    print("\nRed Team agent test completed!")

if __name__ == "__main__":
    asyncio.run(test_red_team())