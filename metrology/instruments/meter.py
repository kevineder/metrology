from functools import wraps
from time import time

from atomic import AtomicLong

from metrology.stats import EWMA
from metrology.utils import now


def ticker(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self._tick()
        return method(self, *args, **kwargs)
    return wrapper


class Meter(object):
    """A meter measures the rate of events over time (e.g., "requests per second").
    In addition to the mean rate, you can also track 1, 5 and 15 minutes moving averages ::

      meter = Metrology.meter('requests')
      meter.mark()
      meter.count

    """
    def __init__(self, average_class=EWMA):
        self.counter = AtomicLong(0)
        self.start_time = now()
        self.last_tick = AtomicLong(self.start_time)

        self.interval = EWMA.INTERVAL
        self.minute1_rate = EWMA.m1()
        self.minute5_rate = EWMA.m5()
        self.minute15_rate = EWMA.m15()

    def _tick(self):
        old_tick, new_tick = self.last_tick.value, time()
        age = new_tick - old_tick
        ticks = int(age / self.interval)
        new_tick = old_tick + int(ticks * self.interval)
        if ticks and self.last_tick.compare_and_swap(old_tick, new_tick):
            for _ in range(ticks):
                self.tick()

    @property
    def count(self):
        """Returns the total number of events that have been recorded."""
        return self.counter.value

    def clear(self):
        self.counter.value = 0
        self.start_time = time()

        self.minute1_rate.clear()
        self.minute5_rate.clear()
        self.minute15_rate.clear()

    @ticker
    def mark(self, value=1):
        """Record an event with the meter. By default it will record one event.

        :param value: number of event to record
        """
        self.counter += value
        self.minute1_rate.update(value)
        self.minute5_rate.update(value)
        self.minute15_rate.update(value)

    def tick(self):
        self.minute1_rate.tick()
        self.minute5_rate.tick()
        self.minute15_rate.tick()

    @property
    @ticker
    def m1_rate(self):
        """Returns the one-minute average rate."""
        return self.minute1_rate.rate

    @property
    @ticker
    def m5_rate(self):
        """Returns the five-minute average rate."""
        return self.minute5_rate.rate

    @property
    @ticker
    def m15_rate(self):
        """Returns the fifteen-minute average rate."""
        return self.minute15_rate.rate

    @property
    def mean_rate(self):
        """Returns the mean rate of the events since the start of the process."""
        if self.counter.value == 0:
            return 0.0
        else:
            elapsed = time() - self.start_time
            return self.counter.value / elapsed

    def stop(self):
        pass
