from biocutils import extract_row_names, extract_column_names
from biocframe import BiocFrame

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

    assert extract_row_names(obj) == None
    assert extract_column_names(obj) == ["column1", "nested", "column2"]
