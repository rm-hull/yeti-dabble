import json
import time
import threading
from typing import Set, Callable


class Debouncer:
    def __init__(self, interval_seconds: float, callback: Callable[[Set[str]], None]):
        self.interval = interval_seconds
        self.callback = callback
        self.collected_domains: Set[str] = set()
        self.timer: threading.Timer | None = None
        self.lock = threading.Lock()

    def add(self, domain: str):
        with self.lock:
            self.collected_domains.add(domain)
            if self.timer:
                self.timer.cancel()
            self.timer = threading.Timer(self.interval, self._trigger)
            self.timer.start()

    def _trigger(self):
        with self.lock:
            domains_to_process = self.collected_domains.copy()
            self.collected_domains.clear()
            self.timer = None

        if domains_to_process:
            self.callback(domains_to_process)

    def flush(self):
        with self.lock:
            if self.timer:
                self.timer.cancel()
                self.timer = None
            domains_to_process = self.collected_domains.copy()
            self.collected_domains.clear()

        if domains_to_process:
            self.callback(domains_to_process)
