import json
from datetime import datetime

class Logger:
    def __init__(self, path="agent_trace_log.jsonl"):
        self.path = path

    async def log(self, **kwargs):
        kwargs["timestamp"] = datetime.utcnow().isoformat()
        print("[LOG]", kwargs)
        with open(self.path, "a") as f:
            f.write(json.dumps(kwargs) + "\n")
