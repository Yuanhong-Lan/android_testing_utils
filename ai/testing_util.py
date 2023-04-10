# ----------------------
# @Time  : 2022 Feb
# @Author: Yuanhong Lan
# ----------------------
import torch
import random
import numpy as np
from torchsummary import summary

from android_testing_utils.log import my_logger


def eliminate_randomness(seed):
    my_logger.hint(my_logger.LogLevel.WARNING, "TestingUtil", True,
                   f" #### Eliminate randomness with seed {seed} ####")
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True


def model_info(model, input_shape):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    backbone = model.to(device)
    summary(backbone, input_shape)
