import time


class ManualTimer:
    def __init__(self, name=None):
        self.name = name
        self._timer = Timer(name=name)
        self._timer.__enter__()

    def print_result(self):
        return self._timer.print_result()

    @property
    def time_diff(self):
        return self._timer.time_diff


class Timer:
    def __init__(self, name=None):
        self.name = name

    def __enter__(self):
        self.start()

    def __exit__(self, type, value, traceback):
        self.print_result()

    def start(self):
        self.tstart = time.time()
        return self

    @property
    def time_diff(self):
        time_diff = time.time() - self.tstart
        return time_diff

    def print_result(self):
        time_diff = self.time_diff
        print('{} Elapsed: {}'.format('[{}] '.format(self.name) if self.name else '',
                                     time_diff))
        return time_diff


def function_timer(func):
    def wrapper(*args, **kwargs):
        t = time.time()
        r = func(*args, **kwargs)
        print('{} Elapsed: {:.5f}'.format(func.__name__, time.time() - t))
        return r

    return wrapper
