import threading
from collections.abc import Callable
from typing import Any


class Debouncer:
    def __init__(self, interval_seconds: float, callback: Callable[[set[str]], Any]):
        self.interval = interval_seconds
        self.callback = callback
        self.collected_domains: set[str] = set()
        self.timer: threading.Timer | None = None
        self.lock = threading.Lock()

    def add(self, domain: str) -> None:
        with self.lock:
            self.collected_domains.add(domain)
            if self.timer:
                self.timer.cancel()
            self.timer = threading.Timer(self.interval, self._trigger)
            self.timer.start()

    def _trigger(self) -> None:
        with self.lock:
            domains_to_process = self.collected_domains.copy()
            self.collected_domains.clear()
            self.timer = None

        if domains_to_process:
            self.callback(domains_to_process)

    def flush(self) -> None:
        with self.lock:
            if self.timer:
                self.timer.cancel()
                self.timer = None
            domains_to_process = self.collected_domains.copy()
            self.collected_domains.clear()

        if domains_to_process:
            self.callback(domains_to_process)
