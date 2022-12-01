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

    df = BiocFrame(obj)

    assert df is not None
    assert len(df.columnNames) == 3
    assert (
        len(
            list(
                set(df.columnNames).difference(
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

    assert len(df.dims) == 2
    assert df.dims == (3, 3)

    assert df.rowNames is None

    assert df.columnNames is not None
    assert len(df.columnNames) == 3

    assert df.metadata is None

    assert len(df.dims) == 2
    assert df.dims == (3, 3)

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

    df = BiocFrame(obj)

    assert df is not None

    assert df.rowNames is None

    df.rowNames = ["row1", "row2", "row3"]
    assert df.rowNames is not None
    assert len(df.rowNames) == 3

    assert df.columnNames is not None
    assert len(df.columnNames) == 3

    df.columnNames = ["col1", "col2", "col3"]

    assert df.columnNames is not None
    assert len(df.columnNames) == 3

    assert df.metadata is None

    df.metadata = {"a": "b"}
    assert df.metadata is not None

    df["new_col"] = [1, 2, 3]

    assert df is not None

    assert len(df.dims) == 2
    assert df.dims == (3, 4)

    df["col2"] = [1, 2, 3]

    assert df is not None

    assert len(df.dims) == 2
    assert df.dims == (3, 4)


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

    df = BiocFrame(obj)

    assert df is not None

    assert df.rowNames is None

    with pytest.raises(Exception):
        df.rowNames = ["row1", "row2"]

    with pytest.raises(Exception):
        df.columnNames = ["col2", "col3"]

    assert df.columnNames is not None
    assert len(df.columnNames) == 3

    with pytest.raises(Exception):
        df["new_col"] = [2, 3]

    assert df is not None

    assert len(df.dims) == 2
    assert df.dims == (3, 3)

    with pytest.raises(Exception):
        df["col2"] = [1, 2]

    assert df is not None

    assert len(df.dims) == 2
    assert df.dims == (3, 3)


def test_dataframe_slice():

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

    df = BiocFrame(obj)
    slice = df[0:2, 0:2]

    assert slice is not None
    assert len(slice.columnNames) == 2
    assert len(list(set(slice.columnNames).difference(["column1", "nested"]))) == 0

    assert len(slice.dims) == 2
    assert slice.dims == (2, 2)


def test_dataframe_ufuncs():

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

    df = BiocFrame(obj)

    new_df = np.sqrt(df)
    assert new_df is not None
