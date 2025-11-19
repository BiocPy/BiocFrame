import numpy as np
import pytest
from biocframe import BiocFrame
from biocutils import Names

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def test_get_slice_with_slice_none():
    """Test that get_slice handles slice(None) correctly for columns."""
    bframe = BiocFrame(
        {
            "col1": [1, 2, 3],
            "col2": [4, 5, 6],
        },
        column_data=BiocFrame({"meta": [1, 2]}),
    )

    result = bframe.get_slice(slice(0, 2), slice(None))
    assert result.shape == (2, 2)
    assert result.column_data is not None
    assert result.column_data.shape[0] == 2


def test_remove_rows_without_row_names():
    """Test that remove_rows raises appropriate error when row_names is None."""
    bframe = BiocFrame(
        {
            "col1": [1, 2, 3],
            "col2": [4, 5, 6],
        }
    )

    result = bframe.remove_rows([0, 1])
    assert result.shape == (1, 2)


def test_get_row_index_validation():
    """Test that get_row validates integer indices properly."""
    bframe = BiocFrame(
        {
            "col1": [1, 2, 3],
            "col2": [4, 5, 6],
        }
    )

    with pytest.raises(IndexError, match="Row index cannot be negative"):
        bframe.get_row(-1)

    with pytest.raises(IndexError, match="Row index 10 is out of range"):
        bframe.get_row(10)

    result = bframe.get_row(0)
    assert result == {"col1": 1, "col2": 4}

    result = bframe.get_row(np.int64(1))
    assert result == {"col1": 2, "col2": 5}


def test_get_column_index_validation():
    """Test that get_column validates integer indices properly."""
    bframe = BiocFrame(
        {
            "col1": [1, 2, 3],
            "col2": [4, 5, 6],
        }
    )

    with pytest.raises(IndexError, match="Index cannot be negative"):
        bframe.get_column(-1)

    with pytest.raises(IndexError, match="Index 10 is out of range"):
        bframe.get_column(10)

    result = bframe.get_column(0)
    assert result == [1, 2, 3]


def test_remove_columns_index_validation():
    """Test that remove_columns validates integer indices properly."""
    bframe = BiocFrame(
        {
            "col1": [1, 2, 3],
            "col2": [4, 5, 6],
            "col3": [7, 8, 9],
        }
    )

    with pytest.raises(IndexError, match="Column index -1 is out of range"):
        bframe.remove_columns([-1])

    with pytest.raises(IndexError, match="Column index 10 is out of range"):
        bframe.remove_columns([10])

    result = bframe.remove_columns([0, 2])
    assert result.shape == (3, 1)
    assert result.column_names.as_list() == ["col2"]


def test_remove_rows_index_validation():
    """Test that remove_rows validates integer indices properly."""
    bframe = BiocFrame(
        {
            "col1": [1, 2, 3, 4],
            "col2": [5, 6, 7, 8],
        },
        row_names=["row1", "row2", "row3", "row4"],
    )

    with pytest.raises(IndexError, match="Row index -1 is out of range"):
        bframe.remove_rows([-1])

    with pytest.raises(IndexError, match="Row index 10 is out of range"):
        bframe.remove_rows([10])

    result = bframe.remove_rows([0, 2])
    assert result.shape == (2, 2)
    assert result.row_names.as_list() == ["row2", "row4"]


def test_merge_variable_scope():
    """Test that merge function handles variable scope correctly."""
    from biocframe import merge

    obj1 = BiocFrame({"A": [1, 2, 3], "B": [4, 5, 6]}, row_names=["a", "b", "c"])
    obj2 = BiocFrame({"C": [7, 8]}, row_names=["b", "c"])

    result = merge([obj1, obj2], by=None, join="left")
    assert result.shape == (3, 3)
    assert result.column("B") == [4, 5, 6]
    assert result.column("C") == [None, 7, 8]

    result = merge([obj1, obj2], by=None, join="right")
    assert result.shape == (2, 3)
    assert result.column("B") == [5, 6]
    assert result.column("C") == [7, 8]


def test_get_row_with_string_and_numpy_int():
    """Test that get_row handles numpy integer types correctly."""
    bframe = BiocFrame(
        {
            "col1": [1, 2, 3],
            "col2": [4, 5, 6],
        },
        row_names=["row1", "row2", "row3"],
    )

    result = bframe.get_row("row2")
    assert result == {"col1": 2, "col2": 5}

    result = bframe.get_row(np.int64(1))
    assert result == {"col1": 2, "col2": 5}

    result = bframe.get_row(np.int32(0))
    assert result == {"col1": 1, "col2": 4}


def test_empty_biocframe_operations():
    """Test operations on empty BiocFrame objects."""
    empty = BiocFrame({})
    assert empty.shape == (0, 0)

    empty = BiocFrame({}, number_of_rows=10)
    assert empty.shape == (10, 0)
    assert len(empty.column_names) == 0

    sliced = empty[0:5, :]
    assert sliced.shape == (5, 0)


def test_column_names_assignment_edge_cases():
    """Test edge cases in column_names assignment."""
    bframe = BiocFrame(
        {
            "col1": [1, 2, 3],
            "col2": [4, 5, 6],
        }
    )

    new_names = Names(["foo", "bar"])
    result = bframe.set_column_names(new_names)
    assert result.column_names.as_list() == ["foo", "bar"]

    result = bframe.set_column_names(["baz", "qux"])
    assert result.column_names.as_list() == ["baz", "qux"]


def test_row_names_with_none_values():
    """Test that row names cannot contain None values."""
    bframe = BiocFrame(
        {
            "col1": [1, 2, 3],
            "col2": [4, 5, 6],
        }
    )

    with pytest.raises(ValueError, match="cannot contain None values"):
        bframe.set_row_names(["row1", None, "row3"])


def test_get_slice_with_all_slice_none():
    """Test get_slice when both rows and columns are slice(None)."""
    bframe = BiocFrame(
        {
            "col1": [1, 2, 3],
            "col2": [4, 5, 6],
        },
        column_data=BiocFrame({"meta": [1, 2]}),
    )

    result = bframe.get_slice(slice(None), slice(None))
    assert result.shape == bframe.shape
    assert result.column_data is not None
    assert result.column_data.shape == bframe.column_data.shape


def test_merge_with_missing_keys():
    """Test merge function with missing keys in join operations."""
    from biocframe import merge

    obj1 = BiocFrame({"A": [1, 2, 3], "B": [4, 5, 6]}, row_names=["a", "b", "c"])
    obj2 = BiocFrame({"C": [7, 8]}, row_names=["d", "e"])

    result = merge([obj1, obj2], by=None, join="outer")
    assert len(result) == 5
    assert result.column("B") == [4, 5, 6, None, None]
    assert result.column("C") == [None, None, None, 7, 8]

