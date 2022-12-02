from biocframe.BiocFrame import BiocFrame
import pytest
import numpy as np

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def test_bframe_basic_ops():

    obj = {
        "column1": [1, 2, 3],
        "nested": [
            {
                "ncol1": [4, 5, 6],
                "ncol2": ["a", "b", "c"],
                "deep": {"dcol1": ["j", "k", "l"], "dcol2": ["a", "s", "l"]},
            },
            {"ncol2": ["a"], "deep": {"dcol1": ["j"], "dcol2": ["a"]},},
            {"ncol1": [5, 6], "ncol2": ["b", "c"],},
        ],
        "column2": ["b", "n", "m"],
    }

    bframe = BiocFrame(obj)

    assert bframe is not None
    assert len(bframe.columnNames) == 3
    assert (
        len(list(set(bframe.columnNames).difference(["column1", "nested", "column2",])))
        == 0
    )

    assert len(bframe.dims) == 2
    assert bframe.dims == (3, 3)

    assert bframe.rowNames is None

    assert bframe.columnNames is not None
    assert len(bframe.columnNames) == 3

    assert bframe.metadata is None

    assert len(bframe.dims) == 2
    assert bframe.dims == (3, 3)


def test_bframe_setters():

    obj = {
        "column1": [1, 2, 3],
        "nested": [
            {
                "ncol1": [4, 5, 6],
                "ncol2": ["a", "b", "c"],
                "deep": {"dcol1": ["j", "k", "l"], "dcol2": ["a", "s", "l"]},
            },
            {"ncol2": ["a"], "deep": {"dcol1": ["j"], "dcol2": ["a"]},},
            {"ncol1": [5, 6], "ncol2": ["b", "c"],},
        ],
        "column2": ["b", "n", "m"],
    }

    bframe = BiocFrame(obj)

    assert bframe is not None

    assert bframe.rowNames is None

    bframe.rowNames = ["row1", "row2", "row3"]
    assert bframe.rowNames is not None
    assert len(bframe.rowNames) == 3

    assert bframe.columnNames is not None
    assert len(bframe.columnNames) == 3

    bframe.columnNames = ["col1", "col2", "col3"]

    assert bframe.columnNames is not None
    assert len(bframe.columnNames) == 3

    assert bframe.metadata is None

    bframe.metadata = {"a": "b"}
    assert bframe.metadata is not None

    bframe["new_col"] = [1, 2, 3]

    assert bframe is not None

    assert len(bframe.dims) == 2
    assert bframe.dims == (3, 4)

    bframe["col2"] = [1, 2, 3]

    assert bframe is not None

    assert len(bframe.dims) == 2
    assert bframe.dims == (3, 4)


def test_bframe_setters_should_fail():

    obj = {
        "column1": [1, 2, 3],
        "nested": [
            {
                "ncol1": [4, 5, 6],
                "ncol2": ["a", "b", "c"],
                "deep": {"dcol1": ["j", "k", "l"], "dcol2": ["a", "s", "l"]},
            },
            {"ncol2": ["a"], "deep": {"dcol1": ["j"], "dcol2": ["a"]},},
            {"ncol1": [5, 6], "ncol2": ["b", "c"],},
        ],
        "column2": ["b", "n", "m"],
    }

    bframe = BiocFrame(obj)

    assert bframe is not None

    assert bframe.rowNames is None

    with pytest.raises(Exception):
        bframe.rowNames = ["row1", "row2"]

    with pytest.raises(Exception):
        bframe.columnNames = ["col2", "col3"]

    assert bframe.columnNames is not None
    assert len(bframe.columnNames) == 3

    with pytest.raises(Exception):
        bframe["new_col"] = [2, 3]

    assert bframe is not None

    assert len(bframe.dims) == 2
    assert bframe.dims == (3, 3)

    with pytest.raises(Exception):
        bframe["col2"] = [1, 2]

    assert bframe is not None

    assert len(bframe.dims) == 2
    assert bframe.dims == (3, 3)


def test_bframe_slice():

    obj = {
        "column1": [1, 2, 3],
        "nested": [
            {
                "ncol1": [4, 5, 6],
                "ncol2": ["a", "b", "c"],
                "deep": {"dcol1": ["j", "k", "l"], "dcol2": ["a", "s", "l"]},
            },
            {"ncol2": ["a"], "deep": {"dcol1": ["j"], "dcol2": ["a"]},},
            {"ncol1": [5, 6], "ncol2": ["b", "c"],},
        ],
        "column2": ["b", "n", "m"],
    }

    bframe = BiocFrame(obj)
    slice = bframe[0:2, 0:2]

    assert slice is not None
    assert len(slice.columnNames) == 2
    assert len(list(set(slice.columnNames).difference(["column1", "nested"]))) == 0

    assert len(slice.dims) == 2
    assert slice.dims == (2, 2)


def test_bframe_delete():

    obj = {
        "column1": [1, 2, 3],
        "nested": [
            {
                "ncol1": [4, 5, 6],
                "ncol2": ["a", "b", "c"],
                "deep": {"dcol1": ["j", "k", "l"], "dcol2": ["a", "s", "l"]},
            },
            {"ncol2": ["a"], "deep": {"dcol1": ["j"], "dcol2": ["a"]},},
            {"ncol1": [5, 6], "ncol2": ["b", "c"],},
        ],
        "column2": ["b", "n", "m"],
    }

    bframe = BiocFrame(obj)
    del bframe["nested"]

    assert bframe is not None
    assert bframe.dims == (3, 2)


def test_bframe_ufuncs():

    obj = {
        "column1": [1, 2, 3],
        "nested": [
            {
                "ncol1": [4, 5, 6],
                "ncol2": ["a", "b", "c"],
                "deep": {"dcol1": ["j", "k", "l"], "dcol2": ["a", "s", "l"]},
            },
            {"ncol2": ["a"], "deep": {"dcol1": ["j"], "dcol2": ["a"]},},
            {"ncol1": [5, 6], "ncol2": ["b", "c"],},
        ],
        "column2": ["b", "n", "m"],
    }

    bframe = BiocFrame(obj)

    new_bframe = np.sqrt(bframe)
    assert new_bframe is not None

def test_nested_biocFrame_slice():

    obj = {
        "column1": [1, 2, 3],
        "nested": BiocFrame(
            {
                "ncol1": [4, 5, 6],
                "ncol2": ["a", "b", "c"],
                "deep": ["j", "k", "l"],
            }
        ),
        "column2": ["b", "n", "m"],
    }

    bframe = BiocFrame(obj)
    assert bframe is not None

    slice = bframe[0:2, 0:2]

    assert slice is not None
    assert len(slice.columnNames) == 2
    assert len(list(set(slice.columnNames).difference(["column1", "nested"]))) == 0

    assert len(slice.dims) == 2
    assert slice.dims == (2, 2)

    slice_nbframe = slice.column("nested")
    assert len(slice_nbframe.dims) == 2
    assert slice_nbframe.dims == (2, 3)

def test_bframe_iter():

    obj = {
        "column1": [1, 2, 3],
        "nested": [
            {
                "ncol1": [4, 5, 6],
                "ncol2": ["a", "b", "c"],
                "deep": {"dcol1": ["j", "k", "l"], "dcol2": ["a", "s", "l"]},
            },
            {"ncol2": ["a"], "deep": {"dcol1": ["j"], "dcol2": ["a"]},},
            {"ncol1": [5, 6], "ncol2": ["b", "c"],},
        ],
        "column2": ["b", "n", "m"],
    }

    bframe = BiocFrame(obj)
    assert bframe is not None

    iterCount = 0
    for k,v in bframe:
        iterCount += 1

    assert iterCount == bframe.dims[0]