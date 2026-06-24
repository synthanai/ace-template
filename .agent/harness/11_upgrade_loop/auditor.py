"""
ACE HARNESS: 11_UPGRADE_LOOP | AUDITOR
Status: CANONICAL
Purpose: Self-correction. Reads telemetry to find friction and proposes structural upgrades.
"""

import json
import yaml
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ace.govern.upgrade")

class SystemAuditor:
    """
    The Synthesizer. Runs weekly (or when triggered by errors).
    Reads the telemetry logs, looks for patterns of human intervention or errors,
    and generates an actionable CPR (Canon Patch Request) for the driver.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        self.logger = logger
        self.base_dir = Path(__file__).parent
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: str) -> dict:
        config_file = self.base_dir / config_path
        if not config_file.exists():
            return {"auto_patch_enabled": False}
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f).get('upgrade_rules', {})
        except Exception as e:
            self.logger.error(f"Config error: {e}")
            return {}

    def _resolve_path(self, key: str, default: str) -> Path:
        dest = self.config.get(key, default)
        path = (self.base_dir / dest).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def run_diagnostic(self):
        """Scans telemetry for errors and outputs an upgrade proposal."""
        telemetry_path = self._resolve_path("audit_telemetry_file", "../../4-operations/telemetry.jsonl")
        proposal_dir = self._resolve_path("proposal_destination", "../../4-operations/upgrades/")
        proposal_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Initiating System Diagnostic on {telemetry_path}...")
        
        error_count = 0
        if telemetry_path.exists():
            try:
                with open(telemetry_path, 'r') as f:
                    for line in f:
                        if "FAILED" in line or "error" in line.lower():
                            error_count += 1
            except Exception as e:
                self.logger.error(f"Failed to read telemetry: {e}")

        self.logger.info(f"Diagnostic complete. {error_count} friction points detected.")
        
        # Generate CPR
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        cpr_path = proposal_dir / f"CPR_UPGRADE_{timestamp}.md"
        
        cpr_content = f"""# Canon Patch Request (CPR): OS Upgrade
**Date:** {timestamp}
**Trigger:** Diagnostic Audit
**Friction Points Detected:** {error_count}

## Analysis
The system detected {error_count} anomalies in the telemetry stream. 

## Proposed Upgrade
1. If errors stem from execution timeouts, adjust `05_task_queues` timeout limits.
2. If errors stem from prompt constraints, adjust `01_sandbox` rules.

**Auto-Patch:** {"ENABLED (Patching now)" if self.config.get("auto_patch_enabled") else "DISABLED (Awaiting human approval)"}
"""
        with open(cpr_path, 'w') as f:
            f.write(cpr_content)
            
        self.logger.info(f"Upgrade Proposal generated at {cpr_path}")

if __name__ == "__main__":
    auditor = SystemAuditor()
    auditor.run_diagnostic()
