from biocframe.utils import match_to_indices

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def test_match_to_indices():
    obj = ["b", "n", "m"]

    sliced_ind = match_to_indices(obj, indices=[0, 2])
    assert sliced_ind is not None
    assert len(sliced_ind) == 2
    assert sliced_ind == [0, 2]

    sliced_ind = match_to_indices(obj, indices=["b", "n"])
    assert sliced_ind is not None
    assert sliced_ind == [0, 1]
    assert len(sliced_ind) == 2
