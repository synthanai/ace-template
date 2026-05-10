"""
ACE HARNESS: 04_SESSION_LOGS | TELEMETRY
Status: CANONICAL
Purpose: Telemetry. Stores physical records of human-agent friction and performance.
"""

import json
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ace.logs.telemetry")

class TelemetryEngine:
    """
    The Memory Loop. Silently records execution metadata to the 4-operations folder.
    Provides the data required for the 11_upgrade_loop to self-correct.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        self.logger = logger
        self.base_dir = Path(__file__).parent
        self.config = self._load_config(config_path)
        self.log_file = self._resolve_log_path()

    def _load_config(self, config_path: str) -> Dict:
        config_file = self.base_dir / config_path
        if not config_file.exists():
            return {"destination": "../../4-operations/telemetry.jsonl", "metrics_to_capture": []}
            
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f).get('logging_rules', {})
        except Exception as e:
            self.logger.error(f"Config error: {e}")
            return {"destination": "../../4-operations/telemetry.jsonl"}

    def _resolve_log_path(self) -> Path:
        """Resolves the destination path, creating parent dirs if necessary."""
        dest = self.config.get("destination", "../../4-operations/telemetry.jsonl")
        log_path = (self.base_dir / dest).resolve()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        return log_path

    def record_event(self, workflow_name: str, metrics: Dict[str, Any], status: str = "SUCCESS"):
        """
        Appends a structured JSONL event to the telemetry ledger.
        """
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "workflow": workflow_name,
            "status": status,
            "metrics": metrics
        }
        
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
            self.logger.info(f"Telemetry logged for '{workflow_name}'.")
        except Exception as e:
            self.logger.error(f"Failed to write telemetry: {e}")

if __name__ == "__main__":
    telemetry = TelemetryEngine()
    telemetry.record_event("smoke_test", {"execution_time_ms": 120, "tokens": 0}, "SUCCESS")
