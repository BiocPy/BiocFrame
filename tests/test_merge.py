from biocframe import BiocFrame, merge
import pytest


def test_merge_BiocFrame_simple():
    obj1 = BiocFrame({"A": [1, 2, 3, 4], "B": [3, 4, 5, 6]})
    obj2 = BiocFrame(
        {
            "C": ["A", "B"],
            "A": [2, 3],
        }
    )
    obj3 = BiocFrame(
        {
            "D": [True, False, False],
            "A": [-1, 0, 3],
        }
    )

    combined = merge([obj1, obj2], by="A", join="left")
    assert combined.get_column_names().as_list() == ["A", "B", "C"]
    assert combined.column("A") == [1, 2, 3, 4]
    assert combined.column("B") == [3, 4, 5, 6]
    assert combined.column("C") == [None, "A", "B", None]

    combined = merge([obj2, obj3], by="A", join="right")
    assert combined.get_column_names().as_list() == ["C", "A", "D"]
    assert combined.column("C") == [None, None, "B"]
    assert combined.column("A") == [-1, 0, 3]
    assert combined.column("D") == [True, False, False]

    combined = merge([obj2, obj1], by="A", join="inner")
    assert combined.get_column_names().as_list() == ["C", "A", "B"]
    assert combined.column("A") == [2, 3]
    assert combined.column("B") == [4, 5]
    assert combined.column("C") == ["A", "B"]

    combined = merge([obj3, obj1], by="A", join="outer")
    assert combined.get_column_names().as_list() == ["D", "A", "B"]
    assert combined.column("D") == [True, False, False, None, None, None]
    assert combined.column("A") == [-1, 0, 3, 1, 2, 4]
    assert combined.column("B") == [None, None, 5, 3, 4, 6]

    # Works with integers.
    combined = merge([obj1, obj2, obj3], by=[0, 1, 1], join="outer")
    assert combined.get_column_names().as_list() == ["A", "B", "C", "D"]
    assert combined.column("A") == [1, 2, 3, 4, -1, 0]
    assert combined.column("B") == [3, 4, 5, 6, None, None]
    assert combined.column("C") == [None, "A", "B", None, None, None]
    assert combined.column("D") == [None, None, False, None, True, False]


def test_merge_BiocFrame_row_names():
    obj1 = BiocFrame({"B": [3, 4, 5, 6]}, row_names=[1, 2, 3, 4])
    obj2 = BiocFrame(
        {"C": ["A", "B"]},
        row_names=[2, 3],
    )
    obj3 = BiocFrame(
        {
            "D": [True, False, False],
            "A": ["1", "0", "3"],
        }
    )

    combined = merge([obj1, obj2], by=None, join="left")
    assert combined.get_column_names().as_list() == ["B", "C"]
    assert combined.get_row_names().as_list() == ["1", "2", "3", "4"]
    assert combined.column("B") == [3, 4, 5, 6]
    assert combined.column("C") == [None, "A", "B", None]

    combined = merge([obj3, obj2], by=["A", None], join="inner")
    assert combined.get_column_names().as_list() == ["D", "A", "C"]
    assert combined.column("D") == [False]
    assert combined.column("A") == ["3"]
    assert combined.column("C") == ["B"]

    combined = merge([obj2, obj3], by=[None, "A"], join="outer")
    assert combined.get_column_names().as_list() == ["C", "D"]
    assert combined.get_row_names().as_list() == ["2", "3", "1", "0"]
    assert combined.column("D") == [None, False, True, False]
    assert combined.column("C") == ["A", "B", None, None]


def test_merge_BiocFrame_duplicate_keys():
    obj1 = BiocFrame({"B": [3, 4, 5, 6]}, row_names=[1, 1, 2, 3])
    obj2 = BiocFrame(
        {"C": ["A", "B"]},
        row_names=[3, 3],
    )

    combined = merge([obj1, obj2], by=None, join="left")
    assert combined.get_column_names().as_list() == ["B", "C"]
    assert combined.get_row_names().as_list() == ["1", "1", "2", "3"]
    assert combined.column("B") == [3, 4, 5, 6]
    assert combined.column("C") == [None, None, None, "A"]

    combined = merge([obj1, obj2], by=None, join="right")
    assert combined.get_column_names().as_list() == ["B", "C"]
    assert combined.get_row_names().as_list() == ["3", "3"]
    assert combined.column("B") == [6, 6]
    assert combined.column("C") == ["A", "B"]

    # Intersects/unions will eventually just deduplicate, though.
    combined = merge([obj1, obj2], by=None, join="outer")
    assert combined.get_column_names().as_list() == ["B", "C"]
    assert combined.get_row_names().as_list() == ["1", "2", "3"]
    assert combined.column("B") == [3, 5, 6]
    assert combined.column("C") == [None, None, "A"]


def test_merge_BiocFrame_duplicate_columns():
    obj1 = BiocFrame({"B": [3, 4, 5, 6], "A": [0, 1, 2, 3]})

    with pytest.raises(ValueError) as ex:
        merge([obj1, obj1], by="A")
    assert str(ex.value).find("duplicate columns")

    combined = merge([obj1, obj1], by="A", rename_duplicate_columns=True)
    assert combined.get_column_names().as_list() == ["B", "A", "B (2)"]
    assert combined.column("B (2)") == [3, 4, 5, 6]


def test_merge_BiocFrame_column_data():
    # A simple case.
    obj1 = BiocFrame({"B": [3, 4, 5, 6]}, row_names=[1, 2, 3, 4])
    obj2 = BiocFrame(
        {"C": ["A", "B"]},
        row_names=[1, 3],
    )

    combined = merge([obj1, obj2], by=None, join="left")
    assert combined.get_column_data() is None

    obj1.set_column_data(BiocFrame({"foo": [True]}), in_place=True)
    combined = merge([obj1, obj2], by=None, join="left")
    comcol = combined.get_column_data()
    assert combined.get_column_names().as_list() == ["B", "C"]
    assert comcol.column("foo") == [True, None]

    obj2.set_column_data(BiocFrame({"foo": [False]}), in_place=True)
    combined = merge([obj1, obj2], by=None, join="left")
    comcol = combined.get_column_data()
    assert comcol.column("foo") == [True, False]

    # Now a more complicated case.
    obj1 = BiocFrame(
        {
            "B": [3, 4, 5, 6],
            "A": [1, 0, 2, 3],
        }
    )
    obj2 = BiocFrame(
        {
            "A": [0, 3],
            "C": ["A", "B"],
        }
    )

    combined = merge([obj1, obj2], by="A", join="left")
    assert combined.get_column_data() is None

    obj1.set_column_data(BiocFrame({"foo": [True, False]}), in_place=True)
    combined = merge([obj1, obj2], by="A", join="left")
    comcol = combined.get_column_data()
    assert combined.get_column_names().as_list() == ["B", "A", "C"]
    assert comcol.column("foo") == [True, False, None]

    obj2.set_column_data(BiocFrame({"foo": ["WHEE", False]}), in_place=True)
    combined = merge([obj1, obj2], by="A", join="left")
    comcol = combined.get_column_data()
    assert comcol.column("foo") == [True, False, False]
