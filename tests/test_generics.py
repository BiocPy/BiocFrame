from biocgenerics import rownames, colnames, set_colnames, set_rownames
from biocframe.BiocFrame import BiocFrame

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def test_names():
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

    assert rownames(obj) == None
    assert colnames(obj) == ["column1", "nested", "column2"]


def test_set_names():
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

    set_rownames(obj, names=["row1", "row2", "row3"])
    set_colnames(obj, names=["col1", "nn", "col2"])

    assert rownames(obj) == ["row1", "row2", "row3"]
    assert colnames(obj) == ["col1", "nn", "col2"]
