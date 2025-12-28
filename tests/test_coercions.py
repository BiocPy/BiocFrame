import pytest
from biocframe import BiocFrame
import biocutils as ut

def test_to_dict():
    obj = BiocFrame({"A": [1, 2], "B": [3, 4]})
    d = obj.to_dict()

    assert isinstance(d, dict)
    assert d["A"] == [1, 2]
    assert d["B"] == [3, 4]
    assert d is obj.get_data()

def test_to_NamedList():
    obj = BiocFrame({"A": [1, 2], "B": [3, 4]})

    nl = obj.to_NamedList()
    assert isinstance(nl, ut.NamedList)
    assert len(nl) == 2
    assert nl.get_names().as_list() == ["A", "B"]
    assert nl[0] == [1, 2]

    # Test order
    obj = BiocFrame({"B": [3, 4], "A": [1, 2]})
    obj = obj.set_column_names(["B", "A"])

    obj2 = BiocFrame({}, column_names=[])
    obj2["Z"] = [1]
    obj2["X"] = [2]

    nl2 = obj2.to_NamedList()
    assert nl2.get_names().as_list() == ["Z", "X"]
    assert nl2[0] == [1]
    assert nl2[1] == [2]
