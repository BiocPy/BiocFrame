import numpy as np
import pytest

from biocframe import BiocFrame, relaxed_combine_rows
from biocutils import combine, combine_columns, Names

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
    merged = combine(obj1, obj2)

    assert isinstance(merged, BiocFrame)
    assert merged.shape[0] == obj1.shape[0] + obj2.shape[0]
    assert merged.shape[1] == 2


def test_multiple():
    merged = combine(obj1, obj2, obj1)

    assert isinstance(merged, BiocFrame)
    assert merged.shape[0] == 2 * obj1.shape[0] + obj2.shape[0]
    assert merged.shape[1] == 2


def test_empty():
    o1 = BiocFrame(number_of_rows=10)
    o2 = BiocFrame(number_of_rows=5)

    merged = combine(o1, o2)

    assert isinstance(merged, BiocFrame)
    assert merged.shape[0] == 15
    assert merged.shape[1] == 0


def test_with_rownames():
    obj1.row_names = ["a", "b", "c", "d", "e"]
    obj2.row_names = ["AA", "BB", "CC", "DD", "EE"]
    merged = combine(obj1, obj2)

    assert isinstance(merged, BiocFrame)
    assert isinstance(merged.get_row_names(), Names)
    assert len(merged.row_names) == 10
    assert merged.shape[0] == 10
    assert merged.shape[1] == 2

    obj1.row_names = None
    merged = combine(obj1, obj2)

    assert isinstance(merged, BiocFrame)
    assert merged.row_names is not None
    assert len(merged.row_names) == 10
    assert merged.row_names.as_list() == [""] * 5 + obj2.row_names.as_list()
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


def test_combine_with_extras():
    obj1 = BiocFrame(
        {
            "column1": [1, 2, 3],
            "column2": [4, 5, 6],
        },
        column_data=BiocFrame({"foo": [-1, -2], "bar": ["A", "B"]}),
        metadata={"YAY": 2},
    )

    obj2 = BiocFrame(
        {
            "column1": [1, 2, 3],
            "column2": [4, 5, 6],
        },
    )

    merged = combine(obj1, obj2)
    assert merged.metadata == obj1.metadata
    assert merged.column_data.shape == obj1.column_data.shape


def test_relaxed_combine_rows():
    obj1 = BiocFrame(
        {
            "column1": [1, 2, 3],
            "column2": np.array([4, 5, 6], dtype=np.int8),
        },
    )

    obj2 = BiocFrame(
        {"column1": [-1, -2, -3], "column3": ["A", "B", "C"]},
    )

    obj3 = BiocFrame(
        {"column2": np.array([-4, -5, -6], dtype=np.int8)},
    )

    merged = relaxed_combine_rows(obj1, obj2, obj3)
    assert merged.get_column_names().as_list() == ["column1", "column2", "column3"]
    assert merged.column("column1") == [1, 2, 3, -1, -2, -3, None, None, None]
    assert (
        merged.column("column2").mask
        == np.ma.array([False, False, False, True, True, True, False, False, False])
    ).all()
    assert (
        merged.column("column2").data == np.ma.array([4, 5, 6, 0, 0, 0, -4, -5, -6])
    ).all()
    assert merged.column("column3") == [
        None,
        None,
        None,
        "A",
        "B",
        "C",
        None,
        None,
        None,
    ]


def test_combine_columns_basic():
    obj1 = BiocFrame(
        {
            "odd": [1, 3, 5, 7, 9],
            "even": [0, 2, 4, 6, 8],
        }
    )

    obj2 = BiocFrame(
        {
            "foo": [11, 33, 55, 77, 99],
            "bar": [0, 22, 44, 66, 88],
        }
    )

    merged = combine_columns(obj1, obj2)
    assert isinstance(merged, BiocFrame)
    assert merged.get_column_names().as_list() == ["odd", "even", "foo", "bar"]
    assert merged.get_column("odd") == [1, 3, 5, 7, 9]
    assert merged.get_column("bar") == [0, 22, 44, 66, 88]

    with pytest.raises(ValueError) as ex:
        combine_columns(obj1, obj1)
    assert str(ex.value).find("must have different columns") >= 0

    with pytest.raises(ValueError) as ex:
        combine_columns(obj1, obj2[1:4, :])
    assert str(ex.value).find("same number of rows") >= 0


def test_combine_columns_with_column_data():
    obj1 = BiocFrame(
        {
            "odd": [1, 3, 5, 7, 9],
            "even": [0, 2, 4, 6, 8],
        }
    )

    obj2 = BiocFrame(
        {
            "foo": [11, 33, 55, 77, 99],
            "bar": [0, 22, 44, 66, 88],
        }
    )

    merged = combine_columns(obj1, obj2)
    assert merged.get_column_data() is None

    obj1.set_column_data(BiocFrame({"A": [1, 2]}), in_place=True)
    obj2.set_column_data(BiocFrame({"A": [3, 4]}), in_place=True)
    merged = combine_columns(obj1, obj2)
    assert merged.get_column_data().column("A") == [1, 2, 3, 4]

    obj1.set_column_data(None, in_place=True)
    with pytest.raises(ValueError) as ex:
        combine_columns(obj1, obj2)
    assert str(ex.value).find("Failed to combine 'column_data'") >= 0
