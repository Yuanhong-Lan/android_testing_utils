# ----------------------
# @Time  : 2024 Nov
# @Author: Yuanhong Lan
# ----------------------
import time


class TimeOperation:
    @classmethod
    def get_local_time_str(cls):
        return time.strftime('%Y-%m-%d-%H:%M:%S', time.localtime())
