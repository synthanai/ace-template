"""
ACE HARNESS: 05_TASK_QUEUES | MANAGER
Status: CANONICAL
Purpose: Asynchronous state. Manages long-running processes in the background.
"""

import json
import yaml
import logging
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ace.queues.manager")

class JobManager:
    """
    The Orchestrator. Reads queue_rules to determine concurrency limits.
    Prevents the user's terminal from freezing by parking long workloads.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        self.logger = logger
        self.base_dir = Path(__file__).parent
        self.config = self._load_config(config_path)
        self.queue_dir = self._resolve_queue_path()

    def _load_config(self, config_path: str) -> Dict:
        config_file = self.base_dir / config_path
        if not config_file.exists():
            return {"queue_directory": "../../4-operations/queues", "max_concurrent_jobs": 3}
            
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f).get('queue_rules', {})
        except Exception as e:
            self.logger.error(f"Config error: {e}")
            return {"queue_directory": "../../4-operations/queues"}

    def _resolve_queue_path(self) -> Path:
        dest = self.config.get("queue_directory", "../../4-operations/queues")
        q_path = (self.base_dir / dest).resolve()
        q_path.mkdir(parents=True, exist_ok=True)
        return q_path

    def get_active_job_count(self) -> int:
        """Counts how many jobs are currently in 'RUNNING' state."""
        count = 0
        for job_file in self.queue_dir.glob("*.json"):
            try:
                with open(job_file, 'r') as f:
                    data = json.load(f)
                    if data.get("status") == "RUNNING":
                        count += 1
            except Exception:
                pass
        return count

    def dispatch(self, workflow_name: str, payload: Dict[str, Any]) -> Optional[str]:
        """
        Dispatches a workflow to the background if constraints allow.
        """
        allowed = self.config.get("allowed_workflows", [])
        if allowed and workflow_name not in allowed:
            self.logger.error(f"Workflow '{workflow_name}' not permitted in background queue.")
            return None

        max_jobs = self.config.get("max_concurrent_jobs", 3)
        if self.get_active_job_count() >= max_jobs:
            self.logger.error(f"Concurrency limit reached ({max_jobs}). Job rejected.")
            return None

        job_id = str(uuid.uuid4())[:8]
        job_file = self.queue_dir / f"job_{job_id}.json"
        
        job_state = {
            "id": job_id,
            "workflow": workflow_name,
            "status": "QUEUED",
            "payload": payload
        }
        
        with open(job_file, 'w') as f:
            json.dump(job_state, f, indent=2)
            
        self.logger.info(f"Job {job_id} dispatched. Terminal released to user.")
        return job_id

if __name__ == "__main__":
    manager = JobManager()
    manager.dispatch("spar", {"topic": "Queue Architecture"})
