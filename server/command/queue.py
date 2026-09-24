from __future__ import annotations

import threading
import time
from collections import deque
from typing import Any


class CommandQueue:
    def __init__(self, max_size: int = 100):
        self.max_size = max_size
        self._queue = deque()
        self._lock = threading.Lock()

    def enqueue(self, item: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            if len(self._queue) >= self.max_size:
                return {"accepted": False, "error_code": "QUEUE_FULL", "message": "Command queue is full."}
            self._queue.append(item)
            return {"accepted": True}

    def dequeue(self):
        with self._lock:
            if not self._queue:
                return None
            return self._queue.popleft()

    def size(self) -> int:
        with self._lock:
            return len(self._queue)

    def clear(self):
        with self._lock:
            self._queue.clear()


command_queue = CommandQueue(max_size=100)
