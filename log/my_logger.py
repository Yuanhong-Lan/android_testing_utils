# ----------------------
# @Time  : 2021 Oct
# @Author: Yuanhong Lan
# ----------------------

import os
import datetime

from enum import Enum
from multiprocessing import Lock


class LogLevel(Enum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    EXCEPTION = 50
    CRITICAL = 100


lock = Lock()


def output(*args, **kwargs):
    with lock:
        print(*args, **kwargs)


def new_line():
    output(flush=True)


def hint(log_level: LogLevel, tag: str, time: bool, info=""):
    s = str(info)
    if s.endswith('\n'):
        s = s[:-1]
    if time:
        output(f"{log_level} | {tag} | {datetime.datetime.now()} | {s}", flush=True)
    else:
        output(f"{log_level} | {tag} | {s}", flush=True)


def append_event_extraction_log(location, info=""):
    info = f"{datetime.datetime.now()}    {info}"
    cmd = f"echo {info} >> {location}/event_extraction_log.txt"
    os.system(cmd)
