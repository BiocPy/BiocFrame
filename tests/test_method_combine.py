import numpy as np
import pytest

from biocframe import BiocFrame
from biocgenerics.combine import combine

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


def test_basic():
    merged = obj1.combine(obj2)

    assert isinstance(merged, BiocFrame)
    assert merged.shape[0] == obj1.shape[0] + obj2.shape[0]
    assert merged.shape[1] == 2


def test_multiple():
    merged = obj1.combine(obj2, obj1)

    assert isinstance(merged, BiocFrame)
    assert merged.shape[0] == 2 * obj1.shape[0] + obj2.shape[0]
    assert merged.shape[1] == 2


def test_empty():
    o1 = BiocFrame(number_of_rows=10)
    o2 = BiocFrame(number_of_rows=5)

    merged = o1.combine(o2)

    assert isinstance(merged, BiocFrame)
    assert merged.shape[0] == 15
    assert merged.shape[1] == 0


def test_with_rownames():
    obj1.row_names = ["a", "b", "c", "d", "e"]
    obj2.row_names = ["AA", "BB", "CC", "DD", "EE"]
    merged = obj1.combine(obj2)

    assert isinstance(merged, BiocFrame)
    assert merged.row_names is not None
    assert len(merged.row_names) == 10
    assert merged.shape[0] == 10
    assert merged.shape[1] == 2

    obj1.row_names = None
    merged = obj1.combine(obj2)

    assert isinstance(merged, BiocFrame)
    assert merged.row_names is not None
    assert len(merged.row_names) == 10
    assert merged.row_names == [None, None, None, None, None] + obj2.row_names
    assert merged.shape[0] == 10
    assert merged.shape[1] == 2


def test_combine_generic_preserve_types():
    on1 = BiocFrame(
        {
            "odd": np.array([1, 3, 5, 7, 9]),
            "even": [0, 2, 4, 6, 8],
        }
    )

    on2 = BiocFrame(
        {
            "odd": np.array([11, 33, 55, 77, 99]),
            "even": [0, 22, 44, 66, 88],
        }
    )

    merged = combine(on1, on2)

    assert merged is not None
    assert isinstance(merged, BiocFrame)
    assert isinstance(merged.column("odd"), np.ndarray)
    assert isinstance(merged.column("even"), list)