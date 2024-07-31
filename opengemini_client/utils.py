import threading


class AtomicInt:

    def __init__(self, value=0):
        self._value = value
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self._value += 1
            if self._value > 100000:
                self._value = 0
            return self._value
