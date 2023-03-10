# # pylint: disable-msg-cat=WCREFI
# from copy import copy, deepcopy

# import pytest

# from randonneur import migrate_exchanges


# @pytest.fixture
# def generic():
#     return [
#         {
#             "name": "n1",
#             "reference product": "rp1",
#             "location": "l1",
#             "unit": "u1",
#             "foo": "bar",
#             "exchanges": [
#                 {
#                     "amount": 1,
#                     "name": "n1",
#                     "product": "rp1",
#                     "unit": "u1",
#                     "location": "l1",
#                     "extra": "yes please",
#                 },
#                 {
#                     "amount": 42,
#                     "name": "n2",
#                     "product": "rp1",
#                     "unit": "u1",
#                     "location": "l2",
#                     "extra": "yes please",
#                 },
#             ],
#         }
#     ]


# @pytest.fixture
# def creation():
#     return {
#         "create": [
#             {
#                 "targets": [
#                     {
#                         "name": "hey",
#                         "product": "everybody",
#                         "unit": "look at",
#                         "location": "me!",
#                     }
#                 ],
#                 "dataset": {
#                     "name": "n1",
#                     "reference product": "rp1",
#                     "location": "l1",
#                     "unit": "u1",
#                     "over": "there",
#                 },
#             },
#             {
#                 "targets": [
#                     {
#                         "name": "1001",
#                         "product": "1002",
#                         "unit": "1003",
#                         "location": "1004",
#                     }
#                 ],
#             },
#         ]
#     }


# def test_migrate_exchanges_create_simple(generic, creation):
#     result = migrate_exchanges(
#         creation,
#         copy(generic),
#     )
#     assert len(result[0]["exchanges"]) == 4


# def test_migrate_exchanges_create_empty(generic, creation):
#     result = migrate_exchanges(
#         {"create": []},
#         copy(generic),
#     )
#     assert len(result[0]["exchanges"]) == 2


# def test_migrate_exchanges_create_missing(generic, creation):
#     result = migrate_exchanges(
#         {},
#         copy(generic),
#     )
#     assert len(result[0]["exchanges"]) == 2


# def test_migrate_exchanges_create_dataset_filter(generic, creation):
#     result = migrate_exchanges(
#         creation, copy(generic), dataset_filter=lambda x: x["name"] == "n2"
#     )
#     assert len(result[0]["exchanges"]) == 2
#     result = migrate_exchanges(
#         creation, copy(generic), dataset_filter=lambda x: x["name"] == "n1"
#     )
#     assert len(result[0]["exchanges"]) == 4


# def test_migrate_exchanges_create_custom_fields(generic, creation):
#     result = migrate_exchanges(creation, deepcopy(generic), fields=("name", "location"))
#     assert len(result[0]["exchanges"]) == 4
#     result = migrate_exchanges(
#         creation, deepcopy(generic), fields=("name", "location", "over")
#     )
#     assert len(result[0]["exchanges"]) == 3


# def test_migrate_exchanges_create_custom_fields_match_missing(generic, creation):
#     result = migrate_exchanges(
#         creation, deepcopy(generic), fields=("name", "location", "missing")
#     )
#     assert len(result[0]["exchanges"]) == 4


# def test_migrate_exchanges_create_multiple_identical(generic):
#     change = {
#         "create": [
#             {
#                 "targets": [
#                     {
#                         "name": "1001",
#                         "product": "1002",
#                         "unit": "1003",
#                         "location": "1004",
#                     },
#                     {
#                         "name": "1001",
#                         "product": "1002",
#                         "unit": "1003",
#                         "location": "1004",
#                     },
#                 ],
#             },
#         ]
#     }
#     result = migrate_exchanges(
#         change,
#         deepcopy(generic),
#     )
#     assert len(result[0]["exchanges"]) == 4
