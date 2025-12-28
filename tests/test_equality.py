import pytest
import numpy as np
from biocframe import BiocFrame

def test_equality_basics():
    obj1 = BiocFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
    obj2 = BiocFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
    assert obj1 == obj2

    # Different data
    obj3 = BiocFrame({"A": [1, 2, 4], "B": ["x", "y", "z"]})
    assert obj1 != obj3

    # Different column names
    obj4 = BiocFrame({"A": [1, 2, 3], "C": ["x", "y", "z"]})
    assert obj1 != obj4

    # Different dims
    obj5 = BiocFrame({"A": [1, 2]})
    assert obj1 != obj5

def test_equality_metadata_columndata():
    obj1 = BiocFrame(
        {"A": [1, 2]},
        metadata={"m": 1},
        column_data=BiocFrame({"annot": [10]}, row_names=["A"])
    )
    obj2 = BiocFrame(
        {"A": [1, 2]},
        metadata={"m": 1},
        column_data=BiocFrame({"annot": [10]}, row_names=["A"])
    )
    assert obj1 == obj2

    # Metadata mismatch
    obj3 = obj1.copy()
    obj3.metadata = {"m": 2}
    assert obj1 != obj3

    # Column data mismatch
    obj4 = obj1.copy()
    obj4.column_data = BiocFrame({"annot": [20]}, row_names=["A"])
    assert obj1 != obj4

def test_equality_nested():
    obj1 = BiocFrame({
        "A": [1],
        "nested": BiocFrame({"B": [2]})
    })
    obj2 = BiocFrame({
        "A": [1],
        "nested": BiocFrame({"B": [2]})
    })
    assert obj1 == obj2

    obj3 = BiocFrame({
        "A": [1],
        "nested": BiocFrame({"B": [3]})
    })
    assert obj1 != obj3

def test_equality_numpy():
    obj1 = BiocFrame({"A": np.array([1, 2, 3])})
    obj2 = BiocFrame({"A": np.array([1, 2, 3])})
    assert obj1 == obj2

    obj3 = BiocFrame({"A": np.array([1, 2, 4])})
    assert obj1 != obj3

def test_equality_pandas():
    try:
        import pandas as pd
    except ImportError:
        pytest.skip("pandas not installed")

    obj1 = BiocFrame({"A": pd.Series([1, 2, 3])})
    obj2 = BiocFrame({"A": pd.Series([1, 2, 3])})

    # This triggers the exception handling block for ambiguous truth values
    assert obj1 == obj2

    obj3 = BiocFrame({"A": pd.Series([1, 2, 4])})
    assert obj1 != obj3

def test_equality_polars():
    try:
        import polars as pl
    except ImportError:
        pytest.skip("polars not installed")

    obj1 = BiocFrame({"A": pl.Series([1, 2, 3])})
    obj2 = BiocFrame({"A": pl.Series([1, 2, 3])})
    assert obj1 == obj2

    obj3 = BiocFrame({"A": pl.Series([1, 2, 4])})
    assert obj1 != obj3
