import numpy as np
import pytest

from biocframe.BiocFrame import BiocFrame

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
            {
                "ncol2": ["a"],
                "deep": {"dcol1": ["j"], "dcol2": ["a"]},
            },
            {
                "ncol1": [5, 6],
                "ncol2": ["b", "c"],
            },
        ],
        "column2": ["b", "n", "m"],
    }

    bframe = BiocFrame(obj)

    assert bframe is not None
    assert len(bframe.column_names) == 3
    assert (
        len(
            list(
                set(bframe.column_names).difference(
                    [
                        "column1",
                        "nested",
                        "column2",
                    ]
                )
            )
        )
        == 0
    )

    assert len(bframe.dims) == 2
    assert bframe.dims == (3, 3)

    assert bframe.row_names is None

    assert bframe.column_names is not None
    assert len(bframe.column_names) == 3

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
            {
                "ncol2": ["a"],
                "deep": {"dcol1": ["j"], "dcol2": ["a"]},
            },
            {
                "ncol1": [5, 6],
                "ncol2": ["b", "c"],
            },
        ],
        "column2": ["b", "n", "m"],
    }

    bframe = BiocFrame(obj)

    assert bframe is not None

    assert bframe.row_names is None

    bframe.row_names = ["row1", "row2", "row3"]
    assert bframe.row_names is not None
    assert len(bframe.row_names) == 3

    assert bframe.column_names is not None
    assert len(bframe.column_names) == 3

    bframe.column_names = ["col1", "col2", "col3"]

    assert bframe.column_names is not None
    assert len(bframe.column_names) == 3

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
            {
                "ncol2": ["a"],
                "deep": {"dcol1": ["j"], "dcol2": ["a"]},
            },
            {
                "ncol1": [5, 6],
                "ncol2": ["b", "c"],
            },
        ],
        "column2": ["b", "n", "m"],
    }

    bframe = BiocFrame(obj)

    assert bframe is not None

    assert bframe.row_names is None

    with pytest.raises(Exception):
        bframe.row_names = ["row1", "row2"]

    with pytest.raises(Exception):
        bframe.column_names = ["col2", "col3"]

    assert bframe.column_names is not None
    assert len(bframe.column_names) == 3

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
            {
                "ncol2": ["a"],
                "deep": {"dcol1": ["j"], "dcol2": ["a"]},
            },
            {
                "ncol1": [5, 6],
                "ncol2": ["b", "c"],
            },
        ],
        "column2": ["b", "n", "m"],
    }

    bframe = BiocFrame(obj)
    slice = bframe[0:2, 0:2]

    assert slice is not None
    assert len(slice.column_names) == 2
    assert len(list(set(slice.column_names).difference(["column1", "nested"]))) == 0

    assert len(slice.dims) == 2
    assert slice.dims == (2, 2)

    sliced_list = bframe[[0, 2], 0:2]

    assert sliced_list is not None
    assert len(sliced_list.column_names) == 2
    assert (
        len(list(set(sliced_list.column_names).difference(["column1", "nested"]))) == 0
    )

    assert len(sliced_list.dims) == 2
    assert sliced_list.dims == (2, 2)

    sliced_list = bframe[[True, False, True], [True, False, False]]
    assert sliced_list is not None
    assert sliced_list.dims == (2, 1)


def test_bframe_delete():
    obj = {
        "column1": [1, 2, 3],
        "nested": [
            {
                "ncol1": [4, 5, 6],
                "ncol2": ["a", "b", "c"],
                "deep": {"dcol1": ["j", "k", "l"], "dcol2": ["a", "s", "l"]},
            },
            {
                "ncol2": ["a"],
                "deep": {"dcol1": ["j"], "dcol2": ["a"]},
            },
            {
                "ncol1": [5, 6],
                "ncol2": ["b", "c"],
            },
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
            {
                "ncol2": ["a"],
                "deep": {"dcol1": ["j"], "dcol2": ["a"]},
            },
            {
                "ncol1": [5, 6],
                "ncol2": ["b", "c"],
            },
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
    assert len(slice.column_names) == 2
    assert len(list(set(slice.column_names).difference(["column1", "nested"]))) == 0

    assert len(slice.dims) == 2
    assert slice.dims == (2, 2)

    slice_nbframe = slice.column("nested")
    assert isinstance(slice_nbframe, BiocFrame)
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
            {
                "ncol2": ["a"],
                "deep": {"dcol1": ["j"], "dcol2": ["a"]},
            },
            {
                "ncol1": [5, 6],
                "ncol2": ["b", "c"],
            },
        ],
        "column2": ["b", "n", "m"],
    }

    bframe = BiocFrame(obj)
    assert bframe is not None

    iterCount = 0
    for k, v in bframe:
        iterCount += 1

    assert iterCount == bframe.dims[0]


def test_slice_empty_obj():
    bframe = BiocFrame({}, number_of_rows=100)
    assert bframe is not None

    sliced_bframe = bframe[10:30, :]
    assert sliced_bframe is not None

    assert sliced_bframe.shape == (20, 0)
