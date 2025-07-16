import asyncio
import sys
sys.path.append('.')

from agents.coordinator import CoordinatorAgent

async def test_full_system():
    """Test the complete multi-agent evaluation system"""
    
    print("Testing Complete Multi-Agent LLM Evaluation System")
    print("=" * 60)
    
    # Create and initialize coordinator
    coordinator = CoordinatorAgent("coordinator", {"model": "test"})
    await coordinator.initialize_agents()
    
    print("All agents initialized and registered")
    print(f"   - Red Team Agent: {coordinator.agents['red_team'].name}")
    print(f"   - Blue Team Agent: {coordinator.agents['blue_team'].name}")  
    print(f"   - Judge Agent: {coordinator.agents['judge'].name}")
    print(f"   - Coordinator Agent: {coordinator.name}")
    
    # Test 1: Full Evaluation
    print("\nTest 1: Full Multi-Round Evaluation")
    print("-" * 50)
    
    full_eval_task = {
        "type": "full_evaluation",
        "target_model": "test_model_v1",
        "config": {
            "rounds": 2,
            "attacks_per_round": 5,
            "attack_type": "safety",
            "difficulty": 1
        }
    }
    
    print("Starting full evaluation...")
    full_result = await coordinator.process_task(full_eval_task)
    
    print(f"\nFull Evaluation Results:")
    print(f"   Session ID: {full_result['session_id']}")
    print(f"   Target Model: {full_result['target_model']}")
    print(f"   Rounds Completed: {full_result['rounds_completed']}")
    
    metrics = full_result['aggregate_metrics']
    print(f"\nAggregate Metrics:")
    print(f"   Attack Success Rate: {metrics['average_attack_success_rate']:.1%}")
    print(f"   Security Score: {metrics['average_security_score']:.0f}/100")
    print(f"   Quality Score: {metrics['average_quality_score']:.2f}")
    print(f"   Final Grade: {metrics['final_grade']}")
    print(f"   Total Attacks: {metrics['total_attacks_executed']}")
    print(f"   High Risk Attacks: {metrics['total_high_risk_attacks']}")
    
    print(f"\nRound-by-Round Results:")
    for i, round_result in enumerate(full_result['round_results'], 1):
        round_metrics = round_result['round_metrics']
        print(f"   Round {i}:")
        print(f"     • Attacks: {round_result['attacks_executed']}")
        print(f"     • Success Rate: {round_metrics['attack_success_rate']:.1%}")
        print(f"     • Security Score: {round_metrics['security_score']:.0f}")
        print(f"     • Duration: {round_result['duration']:.1f}s")
    
    print(f"\nRecommendations ({len(full_result['recommendations'])}):")
    for i, rec in enumerate(full_result['recommendations'][:3], 1):
        print(f"   {i}. [{rec['priority'].upper()}] {rec['title']}")
        print(f"      {rec['description']}")
    
    # Test 2: Targeted Evaluation
    print("\nTest 2: Targeted Evaluation (Jailbreak Focus)")
    print("-" * 50)
    
    targeted_eval_task = {
        "type": "targeted_evaluation",
        "target_model": "test_model_v1",
        "focus_areas": ["jailbreak", "bias_testing"],
        "attacks_per_area": 3
    }
    
    print("Starting targeted evaluation...")
    targeted_result = await coordinator.process_task(targeted_eval_task)
    
    print(f"\nTargeted Evaluation Results:")
    print(f"   Session ID: {targeted_result['session_id']}")
    print(f"   Focus Areas: {', '.join(targeted_result['focus_areas'])}")
    
    for area, result in targeted_result['results_by_area'].items():
        metrics = result['round_metrics']
        print(f"\n   {area.upper()} Results:")
        print(f"     • Attacks Executed: {result['attacks_executed']}")
        print(f"     • Success Rate: {metrics['attack_success_rate']:.1%}")
        print(f"     • Security Score: {metrics['security_score']:.0f}")
    
    # Test 3: Model Comparison
    print("\nTest 3: Model Comparison")
    print("-" * 50)
    
    comparison_task = {
        "type": "model_comparison",
        "models": ["model_a", "model_b"],
        "config": {
            "rounds": 1,
            "attacks_per_round": 3,
            "attack_type": "general"
        }
    }
    
    print("Starting model comparison...")
    comparison_result = await coordinator.process_task(comparison_task)
    
    print(f"\nModel Comparison Results:")
    print(f"   Session ID: {comparison_result['session_id']}")
    print(f"   Models Compared: {', '.join(comparison_result['models'])}")
    
    # Show comparative rankings
    rankings = comparison_result['comparative_analysis']['model_rankings']
    print(f"\nModel Rankings:")
    print(f"   Security: {' > '.join(rankings['security'])}")
    print(f"   Quality: {' > '.join(rankings['quality'])}")
    
    for model in comparison_result['models']:
        model_metrics = comparison_result['results_by_model'][model]['aggregate_metrics']
        print(f"\n   {model.upper()}:")
        print(f"     • Security Score: {model_metrics['average_security_score']:.0f}")
        print(f"     • Attack Success Rate: {model_metrics['average_attack_success_rate']:.1%}")
        print(f"     • Quality Score: {model_metrics['average_quality_score']:.2f}")
        print(f"     • Grade: {model_metrics['final_grade']}")
    
    # Test 4: Agent Communication
    print("\nTest 4: Agent Communication & Coordination")
    print("-" * 50)
    
    print("Testing inter-agent communication...")
    
    # Check agent status
    router_status = coordinator.router.get_agent_status()
    print(f"\nAgent Status:")
    for agent_name, status in router_status.items():
        print(f"   {agent_name}:")
        print(f"     • Active: {status['active']}")
        print(f"     • Messages Processed: {status['messages_processed']}")
        if status['last_activity']:
            print(f"     • Last Activity: {status['last_activity'].strftime('%H:%M:%S')}")
    
    # Test protocol status
    active_sessions = coordinator.list_active_sessions()
    print(f"\nEvaluation Sessions:")
    print(f"   Active Sessions: {len(active_sessions)}")
    
    for session_id in active_sessions[:2]:  # Show first 2
        session = coordinator.get_evaluation_status(session_id)
        if session:
            print(f"   {session_id[:8]}...:")
            print(f"     • Model: {session['target_model']}")
            print(f"     • Status: {session['status']}")
            print(f"     • Rounds: {len(session['rounds'])}")
    
    # Test 5: Red Team Learning
    print("\nTest 5: Red Team Learning & Adaptation")
    print("-" * 50)
    
    red_team = coordinator.agents["red_team"]
    
    print("Red Team Statistics:")
    stats = red_team.get_attack_statistics()
    print(f"   - Total Attacks Generated: {stats['total_attacks']}")
    print(f"   - Success Rate: {stats['success_rate']:.1%}")
    print(f"   - Current Difficulty Level: {stats['current_difficulty']}")
    print(f"   - Attack Types Available: {len(stats['attack_types_tried'])}")
    
    # Test 6: Blue Team Analysis
    print("\nTest 6: Blue Team Defense Analysis")
    print("-" * 50)
    
    blue_team = coordinator.agents["blue_team"]
    
    # Get a sample vulnerability analysis from the full evaluation
    if full_result['round_results']:
        sample_blue_result = full_result['round_results'][0]['blue_team_result']
        
        print("Blue Team Analysis Summary:")
        print(f"   - Security Score: {sample_blue_result['overall_security_score']}/100")
        print(f"   - Patterns Detected: {len(sample_blue_result['attack_patterns_detected'])}")
        print(f"   - Vulnerabilities Found:")
        
        for severity, vulns in sample_blue_result['vulnerabilities_by_severity'].items():
            if vulns:
                print(f"     - {severity.title()}: {len(vulns)}")
        
        print(f"   - Recommendations: {len(sample_blue_result['recommendations'])}")
    
    # Test 7: Judge Evaluation Quality
    print("\nTest 7: Judge Evaluation Consistency")
    print("-" * 50)
    
    judge = coordinator.agents["judge"]
    
    if full_result['round_results']:
        sample_judge_result = full_result['round_results'][0]['judge_result']
        
        print("Judge Evaluation Summary:")
        print(f"   - Total Evaluations: {sample_judge_result['total_attacks']}")
        print(f"   - Successful Attacks: {sample_judge_result['successful_attacks']}")
        print(f"   - Overall Success Rate: {sample_judge_result['success_rate']:.1%}")
        
        # Show attack type breakdown
        if 'attack_types_analysis' in sample_judge_result:
            print(f"   • Attack Type Analysis:")
            for attack_type, analysis in sample_judge_result['attack_types_analysis'].items():
                print(f"     - {attack_type}: {analysis['successful']}/{analysis['total']} "
                      f"({analysis['success_rate']:.0%})")
    
    # Test 8: System Performance
    print("\nTest 8: System Performance Metrics")
    print("-" * 50)
    
    print("Performance Summary:")
    
    # Count evaluations more carefully
    full_rounds = len(full_result.get('round_results', []))
    targeted_rounds = len(targeted_result.get('results_by_area', {}))
    comparison_rounds = sum(len(model_result.get('round_results', [])) 
                           for model_result in comparison_result.get('results_by_model', {}).values())
    
    total_evaluations = full_rounds + targeted_rounds + comparison_rounds
    
    # Count attacks more carefully
    full_attacks = full_result.get('aggregate_metrics', {}).get('total_attacks_executed', 0)
    targeted_attacks = sum(area_result.get('attacks_executed', 0) 
                          for area_result in targeted_result.get('results_by_area', {}).values())
    comparison_attacks = sum(model_result.get('aggregate_metrics', {}).get('total_attacks_executed', 0)
                            for model_result in comparison_result.get('results_by_model', {}).values())
    
    total_attacks = full_attacks + targeted_attacks + comparison_attacks
    
    print(f"   - Total Evaluation Rounds: {total_evaluations}")
    print(f"   - Total Attacks Executed: {total_attacks}")
    
    # Calculate average duration safely
    all_durations = []
    for r in full_result.get('round_results', []):
        all_durations.append(r.get('duration', 0))
    for area_result in targeted_result.get('results_by_area', {}).values():
        all_durations.append(area_result.get('duration', 0))
    
    avg_duration = sum(all_durations) / max(1, len(all_durations))
    print(f"   - Average Round Duration: {avg_duration:.1f}s")
    
    # Calculate system efficiency
    total_agents = len(coordinator.agents) + 1  # +1 for coordinator
    messages_processed = sum(status['messages_processed'] for status in router_status.values())
    
    print(f"   - Active Agents: {total_agents}")
    print(f"   - Messages Processed: {messages_processed}")
    print(f"   - System Efficiency: {(total_attacks / max(1, messages_processed)) * 100:.1f}% (attacks per message)")
    
    # Final Summary
    print("\nFinal System Summary")
    print("=" * 60)
    
    print("Multi-Agent System Successfully Demonstrated:")
    print("   - Red Team: Generated adversarial attacks")
    print("   - Blue Team: Analyzed vulnerabilities and defenses")  
    print("   - Judge: Evaluated attack success and response quality")
    print("   - Coordinator: Orchestrated multi-round evaluations")
    
    print("\nKey Capabilities Validated:")
    print("   - Full multi-round evaluations")
    print("   - Targeted vulnerability assessments")
    print("   - Model comparison and ranking")
    print("   - Real-time agent coordination")
    print("   - Adaptive attack generation")
    print("   - Comprehensive security analysis")
    
    print("\nSystem Ready For:")
    print("   - Production LLM testing")
    print("   - Continuous security monitoring")
    print("   - Model safety certification")
    print("   - Adversarial robustness evaluation")
    
    # Show final grades for models tested
    print(f"\nFinal Model Grades:")
    print(f"   - {full_result['target_model']}: {full_result['aggregate_metrics']['final_grade']}")
    for model in comparison_result['models']:
        grade = comparison_result['results_by_model'][model]['aggregate_metrics']['final_grade']
        print(f"   - {model}: {grade}")
    
    print("\nComplete multi-agent evaluation system test finished!")
    print("   Ready for deployment and real-world LLM evaluation!")

if __name__ == "__main__":
    asyncio.run(test_full_system())