# ----------------------
# @Time  : 2022 Jul
# @Author: Yuanhong Lan
# ----------------------
import numpy as np
from numpy import ndarray


def cos_similarity(a: ndarray, b: ndarray) -> float:
    assert a.ndim == 1, f"The dim of a should be 1, but was {a.ndim}"
    assert a.shape == b.shape, f"The shape of a and b should be the same, but was {a.shape} and {b.shape}"
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return round(dot_product / (norm_a * norm_b), 5)


def cos_similarity_normalized(a: ndarray, b: ndarray):
    temp = cos_similarity(a, b)
    upper_bound = 1
    lower_bound = -1
    return (temp - lower_bound) / (upper_bound - lower_bound)


def self_cos_similarty_compare(embedding_list):
    n = len(embedding_list)
    res = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            res[i][j] = cos_similarity_normalized(embedding_list[i], embedding_list[j])
    return np.round(res, 4)