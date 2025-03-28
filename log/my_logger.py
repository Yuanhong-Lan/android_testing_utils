# ----------------------
# @Time  : 2021 Oct
# @Author: Yuanhong Lan
# ----------------------

import datetime
import os
from enum import Enum
from functools import total_ordering
from multiprocessing import Lock

import yaml


@total_ordering
class LogLevel(Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    EXCEPTION = 50
    CRITICAL = 100

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


CURRENT_LOG_LEVEL = LogLevel[
    yaml.safe_load(open(os.path.join(os.path.dirname(__file__), "log_config.yaml")))["LOG_LEVEL"]
]
lock = Lock()


def output(*args, **kwargs):
    with lock:
        print(*args, **kwargs)


def new_line():
    output(flush=True)


def hint(log_level: LogLevel, tag: str, time: bool, info="", file_stream=None):
    if log_level < CURRENT_LOG_LEVEL:
        return

    s = str(info)
    if s.endswith('\n'):
        s = s[:-1]
    if time:
        output(f"{log_level} | {tag} | {datetime.datetime.now()} | {s}", flush=True, file=file_stream)
    else:
        output(f"{log_level} | {tag} | {s}", flush=True, file=file_stream)


def auto_hint(log_level: LogLevel, tag, time: bool, info="", file_stream=None):
    if type(tag) == str:
        real_tag = tag
    elif type(tag) == type:
        real_tag = f"(AUTO-CLASS) {tag.__name__}"
    elif callable(tag):
        real_tag = f"(AUTO-FUNC) {tag.__name__}"
    else:
        real_tag = f"(AUTO-INST) {tag.__class__.__name__}"
    hint(log_level, real_tag, time, info, file_stream)


def append_event_extraction_log(location, info=""):
    info = f"{datetime.datetime.now()}    {info}"
    cmd = f"echo {info} >> {location}/event_extraction_log.txt"
    os.system(cmd)
