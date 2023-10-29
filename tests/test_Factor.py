from biocframe import Factor
from biocgenerics.combine import combine
import pytest
import copy
import pandas as pd


def test_Factor_basics():
    f = Factor([0, 1, 2, 0, 2, 4], levels=["A", "B", "C", "D", "E"])
    assert len(f) == 6
    assert list(f) == ["A", "B", "C", "A", "C", "E"]
    assert f.get_codes() == [0, 1, 2, 0, 2, 4]
    assert f.get_levels() == ["A", "B", "C", "D", "E"]
    assert not f.get_ordered()

    with pytest.raises(TypeError) as ex:
        Factor([0, "WHEE"], ["A", "B"])
    assert str(ex.value).find("should be integers") >= 0

    with pytest.raises(TypeError) as ex:
        Factor([0, 1], ["A", None, "B"])
    assert str(ex.value).find("non-missing strings") >= 0

    with pytest.raises(ValueError) as ex:
        Factor([0, 1, -1], ["A"])
    assert str(ex.value).find("refer to an entry") >= 0

    with pytest.raises(ValueError) as ex:
        Factor([0, 1], ["A", "B", "A"])
    assert str(ex.value).find("should be unique") >= 0

    f = Factor([None] * 10, levels=["A", "B", "C", "D", "E"])
    assert list(f) == [None] * 10


def test_Factor_basics():
    f = Factor([0, 1, 2, 0, 2, 4], levels=["A", "B", "C", "D", "E"])
    assert repr(f).startswith("Factor(")
    assert str(f).startswith("Factor of length")

    f = Factor([0, 1, 4, 2, 0, 3, 1, 3, 2, 4], levels=["A", "B", "C", "D", "E"])
    assert repr(f).startswith("Factor(")
    assert str(f).startswith("Factor of length")

    f = Factor([], levels=["A", "B", "C", "D", "E"])
    assert repr(f).startswith("Factor(")
    assert str(f).startswith("Factor of length")

    f = Factor([1], levels=["A", "B", "C", "D", "E"])
    assert repr(f).startswith("Factor(")
    assert str(f).startswith("Factor of length")

    f = Factor([i % 5 for i in range(100)], levels=["A", "B", "C", "D", "E"])
    assert repr(f).startswith("Factor(")
    assert str(f).startswith("Factor of length")


def test_Factor_getitem():
    f = Factor([0, 1, 2, 0, 2, 4], levels=["A", "B", "C", "D", "E"])
    assert f[0] == "A"
    assert f[2] == "C"
    assert f[-1] == "E"

    f2 = f[2:4]
    assert f2.get_codes() == [2, 0]
    assert f2.get_levels() == f.get_levels()

    f2 = f[[1, 3, 5]]
    assert f2.get_codes() == [1, 0, 4]
    assert f2.get_levels() == f.get_levels()

    f2 = f[[-1, -2, -3]]
    assert f2.get_codes() == [4, 2, 0]
    assert f2.get_levels() == f.get_levels()


def test_Factor_setitem():
    f = Factor([0, 1, 2, 3, 2, 1], levels=["A", "B", "C", "D", "E"])
    f2 = Factor([0, 1, 2, 3, 2, 1], levels=["A", "B", "C", "D", "E"])

    f[0:2] = f2[2:4]
    assert f.get_codes() == [2, 3, 2, 3, 2, 1]
    assert f.get_levels() == ["A", "B", "C", "D", "E"]

    f = Factor([0, 1, 2, 3, 2, 1], levels=["A", "B", "C", "D", "E"])
    f2 = Factor([0, 1, 2, 3, 2, 1], levels=["E", "D", "C", "B", "A"])
    f[[-3, -2, -1]] = f2[0:3]
    assert f.get_codes() == [0, 1, 2, 4, 3, 2]
    assert f.get_levels() == ["A", "B", "C", "D", "E"]

    f = Factor([0, 1, 2, 3, 2, 1], levels=["A", "B", "C", "D", "E"])
    f2 = Factor([0, 1, 2, 3, 2, 1], levels=["e", "d", "c", "b", "a"])
    f[:] = f2[:]
    assert f.get_codes() == [None] * 6
    assert f.get_levels() == ["A", "B", "C", "D", "E"]


def test_Factor_drop_unused_levels():
    f = Factor([0, 1, 2, 0, 2, 4], levels=["A", "B", "C", "D", "E"])
    f2 = f.drop_unused_levels()
    assert f2.get_levels() == ["A", "B", "C", "E"]
    assert list(f2) == list(f)

    f = Factor([3, 4, 2, 3, 2, 4], levels=["A", "B", "C", "D", "E"])
    f2 = f.drop_unused_levels(in_place=True)
    assert f2.get_levels() == ["C", "D", "E"]
    assert list(f2) == ["D", "E", "C", "D", "C", "E"]


def test_Factor_set_levels():
    f = Factor([0, 1, 2, 0, 2, 4], levels=["A", "B", "C", "D", "E"])
    f2 = f.set_levels(["E", "D", "C", "B", "A"])
    assert f2.get_levels() == ["E", "D", "C", "B", "A"]
    assert f2.get_codes() == [4, 3, 2, 4, 2, 0]
    assert list(f2) == list(f)

    f = Factor([0, 1, 2, 0, 2, 4], levels=["A", "B", "C", "D", "E"])
    f2 = f.set_levels(["E", "C", "A"], in_place=True)
    assert f2.get_levels() == ["E", "C", "A"]
    assert f2.get_codes() == [2, None, 1, 2, 1, 0]

    f = Factor([0, 1, 2, 0, 2, 4], levels=["A", "B", "C", "D", "E"])
    f2 = f.set_levels("E")  # reorders
    assert f2.get_levels() == ["E", "A", "B", "C", "D"]
    assert f2.get_codes() == [1, 2, 3, 1, 3, 0]

    with pytest.raises(ValueError) as ex:
        f.set_levels("F")
    assert str(ex.value).find("should already be present") >= 0

    with pytest.raises(TypeError) as ex:
        f.set_levels([None, "A"])
    assert str(ex.value).find("non-missing strings") >= 0

    with pytest.raises(ValueError) as ex:
        f.set_levels(["A", "A"])
    assert str(ex.value).find("should be unique") >= 0


def test_Factor_copy():
    f = Factor([0, 1, 2, 0, 2, 4], levels=["A", "B", "C", "D", "E"])
    out = copy.copy(f)
    assert f.get_codes() == out.get_codes()
    assert f.get_levels() == out.get_levels()

    f = Factor([0, 1, 2, 0, 2, 4], levels=["A", "B", "C", "D", "E"])
    out = copy.deepcopy(f)
    assert f.get_codes() == out.get_codes()
    assert f.get_levels() == out.get_levels()


def test_Factor_combine():
    # Same levels.
    f1 = Factor([0, 2, 4, 2, 0], levels=["A", "B", "C", "D", "E"])
    f2 = Factor([1, 3, 1], levels=["A", "B", "C", "D", "E"])
    out = combine(f1, f2)
    assert out.get_levels() == f2.get_levels()
    assert out.get_codes() == [0, 2, 4, 2, 0, 1, 3, 1]

    # Different levels.
    f1 = Factor([0, 2, 4, 2, 0], levels=["A", "B", "C", "D", "E"])
    f2 = Factor([1, 3, 1], levels=["D", "E", "F", "G"])
    out = combine(f1, f2)
    assert out.get_levels() == ["A", "B", "C", "D", "E", "F", "G"]
    assert out.get_codes() == [0, 2, 4, 2, 0, 4, 6, 4]

    f2 = Factor([1, 3, None], levels=["D", "E", "F", "G"])
    out = combine(f1, f2)
    assert out.get_codes() == [0, 2, 4, 2, 0, 4, 6, None]

    # Ordering is preserved for the same levels, lost otherwise.
    f1 = Factor([0, 2, 4, 2, 0], levels=["A", "B", "C", "D", "E"], ordered=True)
    f2 = Factor([1, 3, 1], levels=["A", "B", "C", "D", "E"], ordered=True)
    out = combine(f1, f2)
    assert out.get_ordered()

    f2 = Factor([1, 3, 2], levels=["D", "E", "F", "G"], ordered=True)
    out = combine(f1, f2)
    assert not out.get_ordered()


def test_Factor_pandas():
    f1 = Factor([0, 2, 4, 2, 0], levels=["A", "B", "C", "D", "E"])
    pcat = f1.to_pandas()
    assert pcat is not None
    assert len(pcat) == len(f1)

    f2 = Factor([1, 3, 2], levels=["D", "E", "F", "G"], ordered=True)
    pcat = f2.to_pandas()
    assert pcat is not None
    assert len(pcat) == len(f2)
    assert pcat.ordered == f2.get_ordered()


def test_Factor_init_from_list():
    f1 = Factor.from_list(["A", "B", "A", "B", "E"])

    assert isinstance(f1, Factor)
    assert len(f1) == 5
    assert len(f1.get_levels()) == 3
