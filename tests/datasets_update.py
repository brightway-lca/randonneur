# # pylint: disable-msg-cat=WCREFI
# import pytest

# from randonneur import migrate_datasets


# @pytest.fixture
# def generic():
#     return [
#         {
#             "name": "n1",
#             "reference product": "rp1",
#             "location": "l1",
#             "unit": "u1",
#             "foo": "bar",
#             "exchanges": [],
#         },
#         {
#             "name": "n2",
#             "reference product": "rp2",
#             "location": "l2",
#             "unit": "u2",
#             "foo": "baz",
#             "exchanges": [],
#         },
#     ]


# @pytest.fixture
# def update():
#     return {
#         "update": [
#             {
#                 "source": {
#                     "name": "n1",
#                 },
#                 "target": {
#                     "location": "foo",
#                 },
#             },
#             {
#                 "source": {
#                     "name": "n2",
#                     "reference product": "rp2",
#                     "unit": "u2",
#                     "location": "l2",
#                 },
#                 "target": {
#                     "location": "bar",
#                 },
#             },
#         ]
#     }


# def test_migrate_datasets_simple(generic, update):
#     expected = [
#         {
#             "name": "n1",
#             "reference product": "rp1",
#             "location": "foo",
#             "unit": "u1",
#             "foo": "bar",
#             "exchanges": [],
#         },
#         {
#             "name": "n2",
#             "reference product": "rp2",
#             "location": "bar",
#             "unit": "u2",
#             "foo": "baz",
#             "exchanges": [],
#         },
#     ]
#     result = migrate_datasets(update, generic)
#     assert expected == result
