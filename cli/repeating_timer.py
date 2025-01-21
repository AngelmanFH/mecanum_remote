import threading
import time


class RepeatedTimer:
    def __init__(self, interval, callback):
        self.interval = interval
        self.callback = callback
        self.timer = None
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.callback()

    def start(self):
        if not self.is_running:
            start = time.perf_counter_ns()
            self.timer = threading.Timer(self.interval, self._run)
            self.timer.start()
            self.is_running = True
            stop = time.perf_counter_ns()
            print(f"Starting timer thread took {(stop - start) / 1000000} millisecsonds")

    def stop(self):
        if self.timer:
            self.timer.cancel()
        self.is_running = False

    def update(self, interval=None, callback=None):
        self.stop()
        if interval:
            self.interval = interval
        if callback:
            self.callback = callback
        self.start()

class OneshotTimer(RepeatedTimer):
    def _run(self):
        self.is_running = False
        # self.start()
        self.callback()


if __name__ == "__main__":
    # Example usage
    def hello():
        print("Hello, world!")


    rt = RepeatedTimer(2, hello)  # Calls hello() every 2 seconds

    # Dynamically change the callback and interval


    time.sleep(5)
    rt.update(interval=1, callback=lambda: print("Updated callback!"))  # Calls the new callback every 1 second
    time.sleep(10)
    rt.stop()


    count = 0
    def hello_once():
        print("Hello, world - only one time!")

    onetime = OneshotTimer(2, hello_once)
    # onetime.start()
    time.sleep(5)
    onetime.update(0.5, callback=lambda: print("onetime update!"))