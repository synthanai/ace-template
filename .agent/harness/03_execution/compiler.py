"""
ACE HARNESS: 03_EXECUTION | COMPILER
Status: CANONICAL
Purpose: Assembles templates, inputs, and constraints into a final LLM payload.
"""

import logging
from typing import Dict

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ace.execution.compiler")

class PromptCompiler:
    """
    The Weaver. Takes the physical template from 02_registry, 
    injects the dynamic user variables, and attaches systemic constraints.
    """
    
    def __init__(self):
        self.logger = logger

    def compile(self, template_content: str, variables: Dict[str, str], system_constraints: str = "") -> str:
        """
        Replaces {{variable}} markers in the template with actual content.
        """
        self.logger.info("Compiling prompt payload...")
        compiled_prompt = template_content
        
        for key, value in variables.items():
            marker = f"{{{{{key}}}}}"
            if marker in compiled_prompt:
                compiled_prompt = compiled_prompt.replace(marker, str(value))
            else:
                self.logger.warning(f"Variable '{key}' provided but not found in template.")

        if system_constraints:
            compiled_prompt = f"{system_constraints}\n\n---\n{compiled_prompt}"

        self.logger.info("Compilation complete.")
        return compiled_prompt
