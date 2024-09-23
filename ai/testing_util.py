# ----------------------
# @Time  : 2022 Feb
# @Author: Yuanhong Lan
# ----------------------
import torch
import random
import numpy as np
from torchsummary import summary

from android_testing_utils.log import my_logger


class TestingUtil:
    @classmethod
    def eliminate_randomness(cls, seed):
        my_logger.auto_hint(
            my_logger.LogLevel.WARNING, cls, True, f" #### Eliminate randomness with seed {seed} ####"
        )
        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)
        np.random.seed(seed)
        random.seed(seed)
        torch.backends.cudnn.deterministic = True

    @classmethod
    def model_info(cls, model, input_shape):
        my_logger.auto_hint(my_logger.LogLevel.INFO, cls, True, f" #### Model Summary ####")
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        backbone = model.to(device)
        summary(backbone, input_shape)
