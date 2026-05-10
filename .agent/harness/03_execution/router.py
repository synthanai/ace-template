"""
ACE HARNESS: 03_EXECUTION | ROUTER
Status: CANONICAL
Purpose: Routes the compiled prompt to the optimal LLM based on config.yaml.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ace.execution.router")

class ExecutionRouter:
    """
    The Dispatcher. Dumb engine driven by config.yaml.
    Abstracts API calls so the OS is model-agnostic.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        self.logger = logger
        self.routes = self._load_routes(config_path)

    def _load_routes(self, config_path: str) -> Dict:
        """Loads routing tables from external YAML."""
        config_file = Path(__file__).parent / config_path
        if not config_file.exists():
            self.logger.error(f"Routing config missing: {config_file}")
            return {}
            
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f).get('execution_routes', {})
        except Exception as e:
            self.logger.error(f"Failed to parse routes: {e}")
            return {}

    def execute(self, compiled_prompt: str, route_name: str = "default") -> Optional[str]:
        """
        Simulates the LLM call using the specified route.
        """
        route_config = self.routes.get(route_name)
        if not route_config:
            self.logger.error(f"Route '{route_name}' not found in config.yaml. Halting.")
            return None

        self.logger.info(f"Routing payload via {route_config['provider']} ({route_config['model']})")
        self.logger.info(f"Constraints: Temp={route_config['temperature']}, MaxTokens={route_config['max_tokens']}")
        
        # In a real execution, this hits the API.
        # For the OS template, we mock the return.
        self.logger.info("Execution complete. Yielding payload.")
        
        return "MOCKED_LLM_RESPONSE: " + compiled_prompt[:50] + "..."

if __name__ == "__main__":
    router = ExecutionRouter()
    print("Modular Router ready. Driven by config.yaml.")
