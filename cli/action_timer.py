import threading
import time


class ActionTimer:
    def __init__(self, intervals, actions):
        self.intervals = intervals
        self.actions = actions
        self.index = 0
        self.timer = None
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        if self.index < len(self.actions):
            self.actions[self.index]()
            self.index += 1
            self.start()  # Schedule the next action

    def start(self):
        if not self.is_running and self.index < len(self.intervals):
            self.timer = threading.Timer(self.intervals[self.index], self._run)
            self.timer.start()
            self.is_running = True

    def stop(self):
        if self.timer:
            self.timer.cancel()
        self.is_running = False


class ActionTimerAngleDist(ActionTimer):
    def __init__(self, intervals, actions, angles, dists):
        super().__init__(intervals, actions)
        self.angles = angles
        self.dists = dists

    def _run(self):
        self.is_running = False
        if self.index < len(self.intervals):
            self.actions(self.angles[self.index], self.dists[self.index])
            self.index += 1
            self.start()  # Schedule the next action


start = time.perf_counter_ns()
end = time.perf_counter_ns()

# Example usage
if __name__ == '__main__':
    def move_forward():
        print("Move forward")


    def move_left():
        print("Move left")


    # intervals = [1, 1]  # Time intervals in seconds
    # actions = [move_forward, move_left]  # Corresponding actions
    #
    # action_timer = ActionTimer(intervals, actions)
    #
    # # The main thread can continue doing other things
    #
    # for i in range(2):
    #     print(f"Main thread working... {i}")
    #     time.sleep(1)


    def move(angle, dist):
        print(f"Moving {angle} to {dist}")
        global start
        global stop
        stop = time.perf_counter_ns()
        print(f"Intervall measured: {(stop - start) / 1000000} milliseconds")
        start = time.perf_counter_ns()


    intervals = [3, 1, 4, 2]  # Time intervals in seconds
    actions = move  # Corresponding actions
    angles = [0, 90, 180, 270, 360]
    dists = [20, 10, 2, 7, 33]

    move(angles[0], dists[0])
    start = time.perf_counter_ns()
    action_timer = ActionTimerAngleDist(intervals, actions, angles[1:], dists[1:])

    for i in range(10):
        print(f"Main thread working... {i}")
        time.sleep(1)
