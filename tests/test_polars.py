import pytest

import polars as pl
from biocframe import BiocFrame
from biocutils import Names

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def test_from_polars():
    obj = pl.DataFrame(
        {
            "a": [None, 2, 3, 4],
            "b": [0.5, None, 2.5, 13],
            "c": [True, True, False, None],
        }
    )

    bframe = BiocFrame.from_polars(obj)
    assert bframe is not None
    assert isinstance(bframe.get_column_names(), Names)
    assert list(bframe.get_column_names()) == ["a", "b", "c"]


def test_to_polars():
    obj = BiocFrame(
        {
            "a": [None, 2, 3, 4],
            "b": [0.5, None, 2.5, 13],
            "c": [True, True, False, None],
        }
    )

    plframe = obj.to_polars()
    assert plframe is not None
    assert isinstance(plframe, pl.DataFrame)
    assert plframe.columns == ["a", "b", "c"]


def test_to_polars_nested():
    obj = BiocFrame(
        {
            "a": [None, 2, 3],
            "b": [0.5, None, 2.5],
            "c": [True, True, False],
            "nested": BiocFrame(
                {
                    "ncol1": [4, 5, 6],
                    "ncol2": ["a", "b", "c"],
                    "deep": ["j", "k", "l"],
                }
            ),
        }
    )

    plframe = obj.to_polars()
    assert plframe is not None
    assert isinstance(plframe, pl.DataFrame)
    assert len(plframe.columns) == 6
    assert plframe.columns == [
        "a",
        "b",
        "c",
        "nested.ncol1",
        "nested.ncol2",
        "nested.deep",
    ]
