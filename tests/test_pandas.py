import numpy as np
import pytest
import pandas as pd
from biocframe.BiocFrame import BiocFrame
from biocutils import Factor

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


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
    assert len(set(pdf.columns).difference(obj.colnames)) == 3

    obj["factor"] = Factor([0, 2, 1], levels=["A", "B", "C"])
    pdf = obj.to_pandas()
    assert pdf is not None
    assert isinstance(pdf, pd.DataFrame)
    assert len(pdf) == len(obj)
    assert len(set(pdf.columns).difference(obj.colnames)) == 3
    assert pdf["factor"] is not None

    emptyobj = BiocFrame(number_of_rows=100)
    pdf = emptyobj.to_pandas()
    assert len(pdf) == len(emptyobj)
