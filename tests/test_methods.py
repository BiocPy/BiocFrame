import numpy as np
import pytest
import pandas as pd
from biocframe.BiocFrame import BiocFrame
from biocutils import Factor, StringList
import biocutils as ut

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

    assert bframe.metadata == {}

    assert len(bframe.dims) == 2
    assert bframe.dims == (3, 3)


def test_bframe_set_columns():
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
    assert isinstance(bframe.get_row_names(), StringList)
    assert len(bframe.row_names) == 3

    assert bframe.column_names is not None
    assert len(bframe.column_names) == 3

    bframe.column_names = ["col1", "col2", "col3"]

    assert bframe.column_names is not None
    assert len(bframe.column_names) == 3

    assert bframe.metadata == {}

    bframe.metadata = {"a": "b"}
    assert bframe.metadata is not None


def test_bframe_set_columns():
    obj = {
        "column1": [1, 2, 3],
        "column2": ["b", "n", "m"],
    }

    bframe = BiocFrame(obj)

    bframe2 = bframe.set_column("new_col", [1, 2, 3])
    assert bframe2.column("new_col") == [1, 2, 3]
    assert not bframe.has_column("new_col")
    assert bframe2.dims == (3, 3)

    bframe2 = bframe.set_column("column2", [1, 2, 3])
    assert bframe2.column("column2") == [1, 2, 3]
    assert bframe.column("column2") == ["b", "n", "m"]
    assert bframe2.dims == (3, 2)

    # In-place modification works correctly.
    copy = bframe.__deepcopy__()
    copy.set_column("column2", [1, 2, 3], in_place=True)
    assert copy.column("column2") == [1, 2, 3]

    # Now trying multiple columns.
    bframe2 = bframe.set_columns({ "column1": ["A", "B", "C"], "column3": ["a", "b", "c"], "column4": [9, 8, 7] })
    assert bframe2.column("column1") == ["A", "B", "C"]
    assert bframe2.has_column("column3")
    assert bframe2.has_column("column4")

    # Making sure that the mcols is properly handled.
    bframe2a = bframe.set_mcols(BiocFrame({
        "prop1": [1,2],
        "prop2": np.array([1,2], dtype=np.int32),
        "prop3": np.ma.array(np.array([-1,-2], dtype=np.int8))
    }))
    bframe2b = bframe2a.set_columns({ "column1": ["A", "B", "C"], "column3": ["a", "b", "c"], "column4": [9, 8, 7] })
    final_mcols = bframe2b.get_mcols()
    assert final_mcols.column("prop1") == [1,2,None,None]
    assert final_mcols.column("prop2").dtype == np.int32
    assert list(final_mcols.column("prop2")) == list(bframe2a.get_mcols().column("prop2")) + [np.ma.masked]*2
    assert final_mcols.column("prop3").dtype == np.int8
    assert list(final_mcols.column("prop3")) == list(bframe2a.get_mcols().column("prop3")) + [np.ma.masked]*2


def test_bframe_setters_with_rows():
    obj = {
        "column1": [1, 2, 3, 4, 5],
        "column2": ["b", "n", "m", "a", "c"],
    }

    bframe = BiocFrame(obj)
    bframe[1:3, "column1"] = [20, 30]
    assert bframe.column("column1") == [1, 20, 30, 4, 5]

    bframe = BiocFrame(obj)
    bframe[1:3, ["column1", "column2"]] = BiocFrame(
        {"column1": [20, 30], "column2": ["E", "F"]}
    )
    assert bframe.column("column1") == [1, 20, 30, 4, 5]
    assert bframe.column("column2") == ["b", "E", "F", "a", "c"]

    # Works even when columns are out of order.
    bframe = BiocFrame(obj)
    bframe[1:3, ["column2", "column1"]] = BiocFrame(
        {"column1": [20, 30], "column2": ["E", "F"]}
    )
    assert bframe.column("column1") == [1, 20, 30, 4, 5]
    assert bframe.column("column2") == ["b", "E", "F", "a", "c"]


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


def test_bframe_slice_with_extras():
    bframe = BiocFrame(
        {
            "column1": [1, 2, 3],
            "column2": [4, 5, 6],
        },
        mcols=BiocFrame({"foo": [-1, -2], "bar": ["A", "B"]}),
        metadata={"YAY": 2},
    )

    subframe = bframe[0:2, :]
    assert subframe.mcols.shape[0] == bframe.mcols.shape[1]
    assert subframe.metadata == bframe.metadata

    subframe = bframe[:, [1]]
    assert subframe.mcols.shape[0] == 1
    assert subframe.mcols.column("foo") == [-2]
    assert subframe.metadata == bframe.metadata


def test_bframe_unary_slice():
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

    unary_col = bframe[[True, False, True], [True, False, False]]
    assert unary_col is not None
    assert isinstance(unary_col, BiocFrame)
    assert len(unary_col) == 2

    unary_row = bframe[[1], :]
    assert unary_row is not None
    assert isinstance(unary_row, BiocFrame)
    assert len(unary_row) == 1

    unary_row = bframe[1, :]
    assert unary_row is not None
    assert isinstance(unary_row, dict)
    assert len(unary_row.keys()) == 3

    unary_col = bframe[[True, False, True], 2]
    assert unary_col is not None
    assert isinstance(unary_col, list)
    assert len(unary_col) == 2


def test_bframe_remove_column():
    obj = {
        "column1": [1, 2, 3],
        "column2": ["b", "n", "m"],
    }

    bframe = BiocFrame(obj)
    bframe2 = bframe.remove_column("column2")
    assert not bframe2.has_column("column2")
    assert bframe.has_column("column2")

    bframe2 = bframe.remove_columns(["column2", "column1"])
    assert bframe2.shape == (3, 0)

    # Works in place.
    copy = bframe.__deepcopy__()
    copy.remove_column("column1", in_place=True)
    assert copy.has_column("column2")
    assert copy.shape == (3, 1)

    # Handles the mcols correctly.
    bframe2a = bframe.set_mcols(BiocFrame({ "prop1": [1,2] }))
    bframe2b = bframe2a.remove_column("column1")
    assert bframe2b.get_mcols().column("prop1") == [2]


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


def test_nested_biocFrame_preserve_types():
    obj = {
        "column1": [1, 2, 3],
        "nested": BiocFrame(
            {
                "ncol1": [4, 5, 6],
                "ncol2": ["a", "b", "c"],
                "deep": ["j", "k", "l"],
            }
        ),
        "column2": np.array([1, 2, 3]),
    }

    bframe = BiocFrame(obj)
    assert bframe is not None

    sliced = bframe[0:2, :]

    assert isinstance(sliced, BiocFrame)
    assert isinstance(sliced.column("nested"), BiocFrame)
    assert isinstance(sliced.row(0), dict)
    assert isinstance(sliced.column("column2"), np.ndarray)


def test_export_pandas():
    obj = BiocFrame(
        {
            "column1": [1, 2, 3],
            "nested": BiocFrame(
                {
                    "ncol1": [4, 5, 6],
                    "ncol2": ["a", "b", "c"],
                    "deep": ["j", "k", "l"],
                }
            ),
            "column2": np.array([1, 2, 3]),
        }
    )

    pdf = obj.to_pandas()
    assert pdf is not None
    assert isinstance(pdf, pd.DataFrame)
    assert len(pdf) == len(obj)
    assert len(set(pdf.columns).difference(obj.colnames)) == 0

    obj["factor"] = Factor([0, 2, 1], levels=["A", "B", "C"])
    pdf = obj.to_pandas()
    assert pdf is not None
    assert isinstance(pdf, pd.DataFrame)
    assert len(pdf) == len(obj)
    assert len(set(pdf.columns).difference(obj.colnames)) == 0
    assert pdf["factor"] is not None


def test_names_generics():
    obj = BiocFrame(
        {
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
    )

    assert ut.extract_row_names(obj) == None
    assert ut.extract_column_names(obj) == ["column1", "nested", "column2"]
    assert isinstance(ut.extract_column_names(obj), StringList)


def test_set_names():
    obj = BiocFrame(
        {
            "column1": [1, 2, 3],
            "column2": [4, 5, 6],
        }
    )

    latest = obj.set_column_names(["FOO", "BAR"])
    assert isinstance(latest.get_column_names(), StringList)
    assert latest.get_column_names() == ["FOO", "BAR"]
    assert latest.column("FOO") == obj.column("column1")
    assert latest.column("BAR") == obj.column("column2")

    latest = obj.set_row_names(["A", "B", "C"])
    assert isinstance(latest.get_row_names(), StringList)
    assert latest.get_row_names() == ["A", "B", "C"]

    with pytest.raises(ValueError) as ex:
        obj.set_row_names([None, 1, 2])
    assert str(ex.value).find("cannot contain None") >= 0

    with pytest.raises(ValueError) as ex:
        obj.set_column_names([None, None])
    assert str(ex.value).find("cannot contain None") >= 0

    with pytest.raises(ValueError) as ex:
        obj.set_column_names(["A", "A"])
    assert str(ex.value).find("duplicate column name") >= 0
