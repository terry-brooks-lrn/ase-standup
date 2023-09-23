import datetime
import functools
from loguru import logger
import pendulum
import os
import time


class Rotator:
    def __init__(self, *, size, interval, log_path):
        now = datetime.datetime.now()

        self._size_limit = size
        self._log = log_path
        self._interval = interval

    def should_rotate(self, message, file):
        file.seek(0, 2)
        if file.tell() + len(message) > self._size_limit:
            return True
        excess = message.record["time"].timestamp() - self._time_limit.timestamp()
        if excess >= 0:
            if now.diff(os.path.getmtime(self._log)).in_days() > self._interval:
                return True
        return False


def logger_wraps(*, entry=True, exit=True, level="DEBUG"):
    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(
                    level, "Entering '{}' (args={}, kwargs={})", name, args, kwargs
                )
            result = func(*args, **kwargs)
            if exit:
                logger_.log(
                    level,
                    "Exiting '{}' (result={}) - Time Of Exection {:f} s",
                    name,
                    result,
                    end - start,
                )
            return result

        return wrapped

    return wrapper
