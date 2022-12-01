from biocframe.utils import match_to_indices

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


# def test_utils_extract_keys():

#     obj = {
#         "column1": [1, 2, 3],
#         "nested": {"ncol1": [4, 5, 6], "ncol2": ["a", "b", "c"]},
#         "column2": ["b", "n", "m"],
#     }

#     keys, dims = extract_keys(obj)

#     assert keys is not None
#     assert len(keys) == 4
#     assert (
#         len(
#             list(
#                 set(keys).difference(
#                     ["column1", "nested.ncol1", "nested.ncol2", "column2"]
#                 )
#             )
#         )
#         == 0
#     )

#     assert len(set(dims)) == 1

#     obj = {
#         "column1": [1, 2, 3],
#         "nested": {
#             "ncol1": [4, 5, 6],
#             "ncol2": ["a", "b", "c"],
#             "deep": {"dcol1": ["j", "k", "l"], "dcol2": ["a", "s", "l"]},
#         },
#         "column2": ["b", "n", "m"],
#     }

#     keys, dims = extract_keys(obj)

#     assert keys is not None
#     assert len(keys) == 6
#     assert (
#         len(
#             list(
#                 set(keys).difference(
#                     [
#                         "column1",
#                         "nested.ncol1",
#                         "nested.ncol2",
#                         "nested.deep.dcol1",
#                         "nested.deep.dcol2",
#                         "column2",
#                     ]
#                 )
#             )
#         )
#         == 0
#     )

#     assert len(set(dims)) == 1


# def test_utils_extract_keys_should_fail():
#     obj = {
#         "column1": [1, 2],
#         "nested": {
#             "ncol1": [4, 5, 6],
#             "ncol2": ["a", "b", "c"],
#             "deep": {"dcol1": ["j", "k", "l"], "dcol2": ["a", "s", "l"]},
#         },
#         "column2": ["b", "n", "m"],
#     }

#     keys, dims = extract_keys(obj)

#     assert keys is not None
#     assert len(keys) == 6
#     assert (
#         len(
#             list(
#                 set(keys).difference(
#                     [
#                         "column1",
#                         "nested.ncol1",
#                         "nested.ncol2",
#                         "nested.deep.dcol1",
#                         "nested.deep.dcol2",
#                         "column2",
#                     ]
#                 )
#             )
#         )
#         == 0
#     )

#     assert len(set(dims)) == 2


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
