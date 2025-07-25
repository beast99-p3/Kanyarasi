import datetime

class MemoryManager:
    def __init__(self, log_file: str = "agent_log.txt"):
        self.log_file = log_file
    def add_log(self, message: str):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {message}\n")
