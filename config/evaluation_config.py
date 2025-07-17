# config/evaluation_config.py
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class EvaluationConfig:
    """Main evaluation configuration"""
    # Target models to evaluate
    target_models: List[str] = None
    
    # Evaluation parameters
    evaluation_type: str = "standard"  # quick, standard, comprehensive
    attacks_per_round: int = 10
    max_rounds: int = 3
    
    # Output settings
    output_dir: str = "results"
    save_results: bool = True
    
    def __post_init__(self):
        if self.target_models is None:
            self.target_models = ["test_model"]