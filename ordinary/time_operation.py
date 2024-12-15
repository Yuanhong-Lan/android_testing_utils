# ----------------------
# @Time  : 2024 Nov
# @Author: Yuanhong Lan
# ----------------------
import time
from dateutil.parser import parse


class TimeOperation:
    @classmethod
    def get_local_time_str(cls):
        return time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime())

    @classmethod
    def is_a_time_string(cls, s):
        try:
            parse(s, fuzzy=False)
            return True
        except Exception:
            return False
