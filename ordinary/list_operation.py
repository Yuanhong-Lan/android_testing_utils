# ----------------------
# @Time  : 2024 Dec
# @Author: Yuanhong Lan
# ----------------------
class ListOperation:
    @classmethod
    def non_repetition_list_subtract(cls, list1, list2):
        return list(set(list1) - set(list2))