from biocframe.DataFrame import DataFrame

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def test_dataframe():

    obj = {
        "column1": [1, 2, 3],
        "nested": {
            "ncol1": [4, 5, 6],
            "ncol2": ["a", "b", "c"],
            "deep": {"dcol1": ["j", "k", "l"], "dcol2": ["a", "s", "l"]},
        },
        "column2": ["b", "n", "m"],
    }

    df = DataFrame(obj)

    assert df is not None
    assert len(df.colnames) == 3
    assert (
        len(
            list(
                set(df.colnames).difference(
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


def test_dataframe_slice():

    obj = {
        "column1": [1, 2, 3],
        "nested": {
            "ncol1": [4, 5, 6],
            "ncol2": ["a", "b", "c"],
            "deep": {"dcol1": ["j", "k", "l"], "dcol2": ["a", "s", "l"]},
        },
        "column2": ["b", "n", "m"],
    }

    df = DataFrame(obj)
    slice = df[0:2, 0:2]

    assert slice is not None
    assert len(slice.colnames) == 2
    assert len(list(set(slice.colnames).difference(["column1", "nested"]))) == 0

    assert len(slice.dims) == 2
    assert slice.dims == (2, 2)
