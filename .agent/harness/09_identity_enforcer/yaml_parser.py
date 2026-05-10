"""
ACE HARNESS: 09_IDENTITY_ENFORCER | PARSER
Status: CANONICAL
Purpose: Translates the driver's root identity.yaml into execution constraints.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ace.govern.identity")

class IdentityEnforcer:
    """
    The Tuning Link. Connects the root identity.yaml to the 03_execution engine.
    Applies the elemental profile to all subsequent LLM calls.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        self.logger = logger
        self.base_dir = Path(__file__).parent
        self.config = self._load_config(config_path)
        # identity.yaml lives in the repository root
        self.identity_path = self.base_dir.parent.parent.parent / "identity.yaml"

    def _load_config(self, config_path: str) -> Dict:
        config_file = self.base_dir / config_path
        if not config_file.exists():
            return {"element_profiles": {}}
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f).get('element_profiles', {})
        except Exception as e:
            self.logger.error(f"Config error: {e}")
            return {}

    def get_driver_profile(self) -> Dict:
        """
        Reads the driver's identity and returns the exact system variables needed.
        """
        element = "FIRE" # Default fallback
        if self.identity_path.exists():
            try:
                with open(self.identity_path, 'r') as f:
                    identity = yaml.safe_load(f)
                    if identity and 'element' in identity:
                        element = identity.get('element', 'FIRE').upper()
            except Exception as e:
                self.logger.error(f"Failed to parse identity.yaml: {e}")

        self.logger.info(f"Identity Enforcer reading elemental profile: {element}")
        
        profile = self.config.get(element, self.config.get("FIRE", {}))
        return profile

if __name__ == "__main__":
    enforcer = IdentityEnforcer()
    print("Driver Profile Loaded:", enforcer.get_driver_profile())
