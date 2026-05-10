"""
ACE HARNESS: 10_CRON_CHOREOGRAPHY | DAEMON
Status: CANONICAL
Purpose: The Heartbeat. Processes background queues and scheduled tasks.
"""

import time
import json
import yaml
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ace.orchestration.cron")

class Choreographer:
    """
    The Heartbeat. Polls the queue directory and processes files left by 05_task_queues.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        self.logger = logger
        self.base_dir = Path(__file__).parent
        self.config = self._load_config(config_path)
        self.queue_dir = self._resolve_queue_path()

    def _load_config(self, config_path: str) -> dict:
        config_file = self.base_dir / config_path
        if not config_file.exists():
            return {"poll_interval_seconds": 60, "queue_directory": "../../4-operations/queues"}
            
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f).get('cron_rules', {})
        except Exception as e:
            self.logger.error(f"Config error: {e}")
            return {"poll_interval_seconds": 60, "queue_directory": "../../4-operations/queues"}

    def _resolve_queue_path(self) -> Path:
        dest = self.config.get("queue_directory", "../../4-operations/queues")
        return (self.base_dir / dest).resolve()

    def process_queue(self):
        """Finds all 'QUEUED' jobs and processes them."""
        if not self.queue_dir.exists():
            self.logger.warning("Queue directory missing. Skipping cycle.")
            return

        for job_file in self.queue_dir.glob("*.json"):
            try:
                with open(job_file, 'r+') as f:
                    job = json.load(f)
                    if job.get("status") == "QUEUED":
                        self.logger.info(f"Picked up Job {job.get('id')}. Executing workflow: {job.get('workflow')}")
                        
                        # Set to running
                        job["status"] = "RUNNING"
                        f.seek(0)
                        json.dump(job, f, indent=2)
                        f.truncate()
                        
                        # In a real environment, this imports 03_execution and runs it.
                        time.sleep(2) # Mock execution time
                        
                        job["status"] = "COMPLETED"
                        f.seek(0)
                        json.dump(job, f, indent=2)
                        f.truncate()
                        
                        self.logger.info(f"Job {job.get('id')} completed successfully.")
            except Exception as e:
                self.logger.error(f"Failed to process {job_file}: {e}")

    def run_daemon(self, max_cycles: int = 1):
        """Runs the event loop."""
        self.logger.info("Choreographer daemon started.")
        interval = self.config.get("poll_interval_seconds", 60)
        
        for _ in range(max_cycles): # Limited for the template test
            self.process_queue()
            if max_cycles > 1:
                time.sleep(interval)

if __name__ == "__main__":
    daemon = Choreographer()
    daemon.run_daemon()
