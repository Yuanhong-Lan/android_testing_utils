# ----------------------
# @Time  : 2025 Jun
# @Author: Yuanhong Lan
# ----------------------
from typing import List

from android_testing_utils.log import my_logger


class DataFeatureOperation:
    @classmethod
    def analyze_major_data_features_of_list_data(cls, data_list: List):
        if not data_list:
            my_logger.auto_hint(
                my_logger.LogLevel.WARNING, cls, True,
                "[DATA Feature] The data list is empty, no features to analyze."
            )
            return

        count = len(data_list)
        total = 0
        max_val = data_list[0]
        min_val = data_list[0]
        positive_count = 0
        negative_count = 0
        zero_count = 0

        for num in data_list:
            total += num
            if num > max_val:
                max_val = num
            if num < min_val:
                min_val = num
            if num > 0:
                positive_count += 1
            elif num < 0:
                negative_count += 1
            else:
                zero_count += 1

        mean = round(total / count, 4)
        my_logger.auto_hint(
            my_logger.LogLevel.INFO, cls, True,
            f"[DATA Feature] "
            f"Count: {count}, Mean: {mean}, Max: {max_val}, Min: {min_val}, "
            f"Positive Count: {positive_count}, Negative Count: {negative_count}, Zero Count: {zero_count}"
        )
