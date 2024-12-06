# ----------------------
# @Time  : 2022 Apr
# @Author: Yuanhong Lan
# ----------------------
import functools
import time

from android_testing_utils.log import my_logger


def class_method_time_count_decorator(function):
    @functools.wraps(function)
    def wrapper(self, *args, **kwargs):
        before = time.time()
        res = function(self, *args, **kwargs)
        after = time.time()
        my_logger.auto_hint(
            my_logger.LogLevel.INFO, "TimeCountDecorator", False,
            f"Function {function.__name__} cost time: {round(after-before, 2)}s"
        )
        return res
    return wrapper


def normal_method_time_count_decorator(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        before = time.time()
        res = function(*args, **kwargs)
        after = time.time()
        my_logger.auto_hint(
            my_logger.LogLevel.INFO, "TimeCountDecorator", False,
            f"Function {function.__name__} cost time: {round(after-before, 2)}s"
        )
        return res
    return wrapper
