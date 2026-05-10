"""
ACE HARNESS: 01_SANDBOX | VALIDATOR
Status: CANONICAL
Purpose: Execution isolation. Validates outputs structurally using external configuration.
"""

import re
import yaml
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple, List, Optional, Dict

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ace.sandbox.validator")

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    clean_content: Optional[str]

class ContentValidator:
    """
    The Sentinel. Driven entirely by rules.yaml. 
    Code remains rigid; rules remain flexible.
    """
    
    def __init__(self, config_path: str = "rules.yaml"):
        self.logger = logger
        self.rules = self._load_rules(config_path)

    def _load_rules(self, config_path: str) -> Dict:
        """Loads validation rules from external YAML to ensure modularity."""
        config_file = Path(__file__).parent / config_path
        if not config_file.exists():
            self.logger.warning(f"Rule file {config_file} missing. Using safe defaults.")
            return {"forbidden_patterns": [], "required_frontmatter": []}
            
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f).get('validation_rules', {})
        except Exception as e:
            self.logger.error(f"Failed to parse {config_path}: {e}")
            return {"forbidden_patterns": [], "required_frontmatter": []}

    def extract_frontmatter(self, content: str) -> Tuple[Optional[dict], str, List[str]]:
        errors = []
        if not content.startswith('---'):
            errors.append("Missing required YAML frontmatter boundary at start of file.")
            return None, content, errors
            
        parts = content.split('---', 2)
        if len(parts) < 3:
            errors.append("Malformed YAML frontmatter. Missing closing boundary.")
            return None, content, errors
            
        try:
            frontmatter = yaml.safe_load(parts[1])
            if not isinstance(frontmatter, dict):
                errors.append("Frontmatter must be a valid YAML dictionary.")
                return None, parts[2].lstrip(), errors
            return frontmatter, parts[2].lstrip(), errors
        except yaml.YAMLError as e:
            errors.append(f"YAML parsing error: {str(e)}")
            return None, parts[2].lstrip(), errors

    def validate(self, raw_content: str) -> ValidationResult:
        self.logger.info("Initializing Config-Driven Validation Protocol...")
        errors = []
        
        # 1. Frontmatter Checks
        frontmatter, body, fm_errors = self.extract_frontmatter(raw_content)
        errors.extend(fm_errors)
        
        required_keys = self.rules.get('required_frontmatter', [])
        if frontmatter:
            for key in required_keys:
                if key not in frontmatter:
                    errors.append(f"Frontmatter missing mandatory key: '{key}'")

        # 2. Structural/Style Mandates from config
        patterns = self.rules.get('forbidden_patterns', [])
        for rule in patterns:
            if re.search(rule['pattern'], raw_content):
                errors.append(f"Style violation: {rule['message']}")

        # 3. Final Verdict
        if errors:
            self.logger.warning(f"Validation FAILED with {len(errors)} errors.")
            return ValidationResult(is_valid=False, errors=errors, clean_content=None)
            
        self.logger.info("Validation PASSED. Content cleared for root workspace.")
        return ValidationResult(is_valid=True, errors=[], clean_content=raw_content)

if __name__ == "__main__":
    validator = ContentValidator()
    print("Modular Validator ready. Driven by rules.yaml.")
