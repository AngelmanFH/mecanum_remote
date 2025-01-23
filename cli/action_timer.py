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
    def __init__(self, action, angles, dists):
        super().__init__(intervals=list(), actions=action)
        self.angles = angles
        self.dists = dists
        self.lastrun = time.perf_counter_ns()
        # run first command at start
        self.actions(self.angles[0], self.dists[0])
        self.speed = 200


    def compute_intervalls(self):
        for dist in self.dists:
            self.intervals.append(self.calc_time(dist, self.speed))

    def _run(self):
        self.is_running = False

        stop = time.perf_counter_ns()
        print(f"Intervall measured: {round((stop - self.lastrun) / 1000000, 1)} milliseconds")
        self.lastrun = stop

        if self.index < len(self.intervals):
            self.index += 1
            self.actions(self.angles[self.index], self.dists[self.index])

            self.start()  # Schedule the next action

    @staticmethod
    def calc_time(distance, speed):
        time = distance / speed
        return time

    @staticmethod
    def n_from_s(speed):
        millirevs_per_min = int(round(speed * 60 * 1000 / 628.3))
        return millirevs_per_min


def calc_time(distance, speed):
    time = distance / speed
    return time


def n_from_s(speed):
    millirevs_per_min = int(round(speed * 60 * 1000 / 628.3))
    return millirevs_per_min


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
        # if not hasattr(move, "lasttime"):
        #     move.lasttime = time.perf_counter_ns()
        # else:
        #     stop = time.perf_counter_ns()
        #     print(f"Intervall measured: {round((stop - move.lasttime) / 1000000, 1)} milliseconds")
        #     move.lasttime = stop

        # global start
        # global stop
        # stop = time.perf_counter_ns()
        # print(f"Intervall measured: {(stop - start) / 1000000} milliseconds")
        print(f"Moving at {angle}° for {dist} mm")
        # start = time.perf_counter_ns()


    # intervals = [2, 1, 0.2, 0.7, 3.3]  # Time intervals in seconds
    intervals = []
    actions = move  # Corresponding actions
    angles = [0, 90, 180, 270, 360, 0]
    dists = [200, 400, 600, 100, 50, 0]
    speed = 200
    millirevs_per_min = n_from_s(speed)

    for i in range(0, len(angles) - 1):
        _time = calc_time(dists[i], speed)
        intervals.append(_time)

    print(f"Speed is {speed} mm/s")
    print(f"That is {millirevs_per_min} milli-revolutions per minute")
    move(angles[0], dists[0])
    start = time.perf_counter_ns()
    action_timer = ActionTimerAngleDist(intervals, actions, angles[1:], dists[1:])

    for i in range(2):
        # print(f"Main thread working... {i}")
        time.sleep(1)
