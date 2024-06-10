import pytest

import polars as pl
from biocframe import BiocFrame
from biocutils import Names

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def test_polars_init():
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

