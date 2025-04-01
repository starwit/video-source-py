import threading
import time

class FrameCounterThread:
    def __init__(self):
        self.counter = 0
        self.counter_lock = threading.Lock()
        self.stopped = threading.Event()
        self.thread = threading.Thread(target=self._time_counter, daemon=True)

    def start(self) -> None:
        """Start the frame capture thread."""
        if not self.thread.is_alive():
            self.thread.start()

    def _time_counter(self) -> None:
        """Increment the counter at a fixed interval."""
        while not self.stopped.is_set():
            time.sleep(1 / 15)  # 15 FPS
            with self.counter_lock:
                self.counter += 1

    def stop(self) -> None:
        """Stop the frame capture thread."""
        self.stopped.set()
        self.thread.join()

    def get_counter(self) -> int:
        """Get the current value of the counter in a thread-safe manner."""
        with self.counter_lock:
            return self.counter
