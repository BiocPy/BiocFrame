import pandas as pd
import pytest

import biocframe
from biocframe import BiocFrame
from biocutils import Names

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def test_initialize_obj():
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
    assert isinstance(bframe.get_column_names(), Names)


def test_initialize_pandas():
    df_gr = pd.DataFrame(
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

    bframe = biocframe.from_pandas(df_gr)
    assert bframe is not None


def test_empty_obj():
    bframe = BiocFrame({})
    assert bframe is not None


def test_empty_obj_with_size():
    bframe = BiocFrame({}, number_of_rows=100)
    assert bframe is not None


def test_should_fail():
    with pytest.raises(Exception):
        df_gr = pd.DataFrame(
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
                ],
                "column2": ["b", "n", "m"],
            }
        )

        biocframe.from_pandas(df_gr)


def test_nested_biocFrame():
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

    nested_col = bframe.column("nested")
    assert nested_col is not None
    assert isinstance(nested_col, BiocFrame)
    assert nested_col.row_names is None
    assert len(nested_col.column_names) == 3


def test_extra_bits():
    bframe = BiocFrame(
        {
            "column1": [1, 2, 3],
        },
        column_data=BiocFrame({"foo": [1], "bar": ["A"]}),
        metadata={"YAY": 2},
    )

    assert isinstance(bframe.column_data, BiocFrame)
    assert bframe.metadata["YAY"] == 2

    # Setters work correctly.
    bframe.column_data = BiocFrame({"STUFF": [2.5]})
    assert list(bframe.column_data.column_names) == ["STUFF"]

    bframe.metadata = {"FOO": "A"}
    assert bframe.metadata["FOO"] == "A"


def test_with_add_deletions():
    obj1 = BiocFrame(
        {
            "column1": [1, 2, 3],
            "column2": [4, 5, 6],
        },
        column_data=BiocFrame({"foo": [-1, -2], "bar": ["A", "B"]}),
        metadata={"YAY": 2},
    )

    assert isinstance(obj1.column_data, BiocFrame)

    obj1["new_column"] = [10, 11, "12"]
    assert obj1.shape == (3, 3)
    assert len(obj1.column_data) == 3

    # welp assume i made a mistake earlier
    obj1["new_column"] = [10, 11, 12]
    assert obj1.shape == (3, 3)
    assert len(obj1.column_data) == 3

    # lets delete
    del obj1["new_column"]
    assert obj1.shape == (3, 2)
    assert len(obj1.column_data) == 2
