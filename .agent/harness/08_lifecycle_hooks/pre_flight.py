"""
ACE HARNESS: 08_LIFECYCLE_HOOKS | PRE-FLIGHT
Status: CANONICAL
Purpose: Rituals. Verifies user state (e.g., daily limits) before allowing execution.
"""

import yaml
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ace.govern.lifecycle")

class PreFlightHook:
    """
    The Ritual Engine. Runs immediately when the user types a command.
    Ensures the human is in the correct state to operate the OS.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        self.logger = logger
        self.base_dir = Path(__file__).parent
        self.config = self._load_config(config_path)
        # identity.yaml lives in the root directory
        self.identity_path = self.base_dir.parent.parent.parent / "identity.yaml"

    def _load_config(self, config_path: str) -> dict:
        config_file = self.base_dir / config_path
        if not config_file.exists():
            return {"require_morning_ritual": False, "max_daily_p0_tasks": 3}
            
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f).get('lifecycle_rules', {})
        except Exception as e:
            self.logger.error(f"Config error: {e}")
            return {"require_morning_ritual": False}

    def _read_identity(self) -> dict:
        if not self.identity_path.exists():
            return {"element": "DEFAULT"}
        try:
            with open(self.identity_path, 'r') as f:
                return yaml.safe_load(f)
        except:
            return {"element": "DEFAULT"}

    def run_checks(self, current_p0_count: int = 0) -> bool:
        """
        Executes all pre-flight ritual checks.
        """
        self.logger.info("Initiating Pre-Flight Rituals...")
        
        # Check 1: Hard Constraints
        max_tasks = self.config.get("max_daily_p0_tasks", 3)
        if current_p0_count >= max_tasks:
            self.logger.error(f"HARD CONSTRAINT HIT: You have reached your max {max_tasks} P0 tasks.")
            self.logger.error("OS halted to prevent cognitive overload. Step away from the keyboard.")
            return False
            
        # Check 2: Identity Alignment
        if self.config.get("check_identity_alignment"):
            identity = self._read_identity()
            element = identity.get("element", "DEFAULT")
            self.logger.info(f"Identity loaded: {element} Protocol active.")
            
        # Check 3: Rituals
        if self.config.get("require_morning_ritual"):
            self.logger.info("Ritual Check: Have you set your daily intention? (Y/N)")
            # In live environment, waits for user input.
            pass
            
        self.logger.info("Pre-Flight complete. Driver is sovereign. Engaging engine.")
        return True

if __name__ == "__main__":
    hook = PreFlightHook()
    hook.run_checks(current_p0_count=1)
