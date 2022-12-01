from biocframe.BiocFrame import BiocFrame
from random import random

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def test_dataframe():

    obj = {
        "seqnames": [
            "chr1",
            "chr2",
            "chr2",
            "chr2",
            "chr1",
            "chr1",
            "chr3",
            "chr3",
            "chr3",
            "chr3",
        ]
        * 20,
        "starts": range(100, 300),
        "ends": range(110, 310),
        "strand": ["-", "+", "+", "*", "*", "+", "+", "+", "-", "-"] * 20,
        "score": range(0, 200),
        "GC": [random() for _ in range(10)] * 20,
    }

    df = BiocFrame(obj)

    assert df is not None
    assert len(df.columnNames) == 6
    assert (
        len(
            list(
                set(df.columnNames).difference(
                    ["seqnames", "starts", "ends", "strand", "score", "GC"]
                )
            )
        )
        == 0
    )

    assert len(df.dims) == 2
    assert df.dims == (200, 6)

    # assign new columns
    df.columnNames = ["chr", "start", "end", "strands", "scores", "GCs"]

    sliced_df = df[3:7, 2:5]

    assert sliced_df is not None
    assert sliced_df.dims == (4, 3)
    assert (
        len(list(set(sliced_df.columnNames).difference(["end", "strands", "scores"])))
        == 0
    )
