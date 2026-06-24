"""
ACE HARNESS: 07_PERMISSION_GATES | GAUGE
Status: CANONICAL
Purpose: Stops the OS and demands human approval for high-risk actions.
"""

import yaml
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ace.govern.gauge")

class PermissionGate:
    """
    The Brake Pedal. Reads gate_rules.
    If an AI agent requests a destructive action, it blocks execution until the driver confirms.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        self.logger = logger
        self.base_dir = Path(__file__).parent
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: str) -> dict:
        config_file = self.base_dir / config_path
        if not config_file.exists():
            return {"require_human_approval": []}
            
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f).get('gate_rules', {})
        except Exception as e:
            self.logger.error(f"Config error: {e}")
            return {"require_human_approval": []}

    def verify_action(self, action_type: str) -> bool:
        """
        Checks if an action requires explicit human permission.
        """
        high_risk_actions = self.config.get("require_human_approval", [])
        
        if action_type in high_risk_actions:
            self.logger.warning(f"GAUGE TRIGGERED: Action '{action_type}' requires explicit human approval.")
            # In a live environment, this halts the process and waits for CLI input.
            self.logger.info("Awaiting driver override...")
            return False
            
        self.logger.info(f"Action '{action_type}' cleared by GAUGE.")
        return True

if __name__ == "__main__":
    gate = PermissionGate()
    gate.verify_action("delete_files")
