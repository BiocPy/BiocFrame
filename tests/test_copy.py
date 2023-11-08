import numpy as np
import pytest

from biocframe import BiocFrame
from copy import deepcopy

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def test_basic_copy():
    obj1 = BiocFrame(
        {
            "odd": [1, 3, 5, 7, 9],
            "even": [0, 2, 4, 6, 8],
        }
    )

    copied = obj1.copy()

    assert isinstance(copied, BiocFrame)
    assert copied.shape == obj1.shape

    copied["new_col"] = [1, 3, 5, 7, 9]

    assert (
        copied.shape == obj1.shape
    )  # well we are copying so it doesn't reflect the change
    assert obj1.data == copied.data


def test_basic_deepcopy():
    obj1 = BiocFrame(
        {
            "odd": [1, 3, 5, 7, 9],
            "even": [0, 2, 4, 6, 8],
        }
    )
    copied = deepcopy(obj1)

    assert isinstance(copied, BiocFrame)
    assert copied.shape == obj1.shape

    copied["new_col"] = [1, 3, 5, 7, 9]

    assert copied.shape != obj1.shape
    assert obj1.data != copied.data
