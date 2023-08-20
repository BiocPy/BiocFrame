from random import random

from biocframe.BiocFrame import BiocFrame

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def test_bframe():
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

    bframe = BiocFrame(obj)

    assert bframe is not None
    assert len(bframe.column_names) == 6
    assert (
        len(
            list(
                set(bframe.column_names).difference(
                    ["seqnames", "starts", "ends", "strand", "score", "GC"]
                )
            )
        )
        == 0
    )

    assert len(bframe.dims) == 2
    assert bframe.dims == (200, 6)

    # assign new columns
    bframe.column_names = ["chr", "start", "end", "strands", "scores", "GCs"]

    sliced_df = bframe[3:7, 2:5]

    assert sliced_df is not None
    assert sliced_df.dims == (4, 3)
    assert (
        len(list(set(sliced_df.column_names).difference(["end", "strands", "scores"])))
        == 0
    )
