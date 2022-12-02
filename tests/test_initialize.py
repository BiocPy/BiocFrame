from biocframe.BiocFrame import BiocFrame
import pandas as pd
import pytest

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
            {"ncol2": ["a"], "deep": {"dcol1": ["j"], "dcol2": ["a"]},},
            {"ncol1": [5, 6], "ncol2": ["b", "c"],},
        ],
        "column2": ["b", "n", "m"],
    }

    bframe = BiocFrame(obj)
    assert bframe is not None


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
                {"ncol2": ["a"], "deep": {"dcol1": ["j"], "dcol2": ["a"]},},
                {"ncol1": [5, 6], "ncol2": ["b", "c"],},
            ],
            "column2": ["b", "n", "m"],
        }
    )

    bframe = BiocFrame.fromPandas(df_gr)
    assert bframe is not None


def test_empty_obj():
    bframe = BiocFrame({})
    assert bframe is not None


def test_empty_obj_with_size():
    bframe = BiocFrame({}, numberOfRows=100)
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
                    {"ncol2": ["a"], "deep": {"dcol1": ["j"], "dcol2": ["a"]},},
                ],
                "column2": ["b", "n", "m"],
            }
        )

        BiocFrame.fromPandas(df_gr)


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
