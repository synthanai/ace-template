"""
ACE HARNESS: 02_REGISTRY | MANAGER
Status: CANONICAL
Purpose: Asset Index. Tracks, validates, and serves available templates and prompts.
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ace.registry.manager")

class RegistryManager:
    """
    The Librarian. Reads template_index.yaml and dynamically serves 
    the exact physical template files to the workflows.
    """
    
    def __init__(self, index_file: str = "template_index.yaml"):
        self.logger = logger
        self.base_dir = Path(__file__).parent
        self.index_path = self.base_dir / index_file
        self.index = self._load_index()

    def _load_index(self) -> Dict:
        """Loads the registry mapping from YAML."""
        if not self.index_path.exists():
            self.logger.error(f"Registry index missing: {self.index_path}")
            return {}
            
        try:
            with open(self.index_path, 'r') as f:
                return yaml.safe_load(f).get('templates', {})
        except Exception as e:
            self.logger.error(f"Failed to parse registry index: {e}")
            return {}

    def fetch_template(self, template_key: str) -> Optional[str]:
        """
        Retrieves the physical content of a template.
        Throws a clean warning if the template doesn't exist.
        """
        template_meta = self.index.get(template_key)
        if not template_meta:
            self.logger.warning(f"Template '{template_key}' not found in registry.")
            return None
            
        template_path = self.base_dir / template_meta.get('path', '')
        if not template_path.exists():
            self.logger.error(f"Physical file missing for '{template_key}': {template_path}")
            return None
            
        try:
            with open(template_path, 'r') as f:
                content = f.read()
            self.logger.info(f"Served template: {template_key}")
            return content
        except Exception as e:
            self.logger.error(f"Failed to read template '{template_key}': {e}")
            return None

    def validate_registry(self) -> bool:
        """Audits the registry to ensure all mapped files exist on disk."""
        self.logger.info("Auditing Registry...")
        is_healthy = True
        for key, meta in self.index.items():
            path = self.base_dir / meta.get('path', '')
            if not path.exists():
                self.logger.error(f"Broken link in registry: [{key}] points to missing file '{path}'")
                is_healthy = False
                
        if is_healthy:
            self.logger.info("Registry audit PASSED. All assets present.")
        return is_healthy

if __name__ == "__main__":
    registry = RegistryManager()
    registry.validate_registry()
