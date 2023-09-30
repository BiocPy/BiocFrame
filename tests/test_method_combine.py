import numpy as np
import pytest

from biocframe import BiocFrame

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"

obj1 = BiocFrame(
    {
        "odd": [1, 3, 5, 7, 9],
        "even": [0, 2, 4, 6, 8],
    }
)

obj2 = BiocFrame(
    {
        "odd": [11, 33, 55, 77, 99],
        "even": [0, 22, 44, 66, 88],
    }
)


def test_basic_combine():
    merged = obj1.combine(obj2)

    assert isinstance(merged, BiocFrame)
    assert merged.shape[0] == obj1.shape[0] + obj2.shape[0]
    assert merged.shape[1] == 2


def test_basic_combine_multiple():
    merged = obj1.combine(obj2, obj1)

    assert isinstance(merged, BiocFrame)
    assert merged.shape[0] == 2 * obj1.shape[0] + obj2.shape[0]
    assert merged.shape[1] == 2


def test_basic_combine_empty():
    o1 = BiocFrame(number_of_rows=10)
    o2 = BiocFrame(number_of_rows=5)

    merged = o1.combine(o2)

    print(merged)

    assert isinstance(merged, BiocFrame)
    assert merged.shape[0] == obj1.shape[0] + obj2.shape[0]
    assert merged.shape[1] == 0
