# pylint: disable-msg-cat=WCREFI
from randonneur.utils import as_tuple


def test_as_tuple_convert_list():
    given = {"foo": "bar", "this": ["that", "other thing"]}
    fields = ("foo", "this")
    assert as_tuple(given, fields) == ("bar", ("that", "other thing"))


def test_as_tuple_str_tuple_set():
    given = {"foo": "bar", "this": ("that", "other thing"), "weee": {1, 2, 3}}
    fields = ("foo", "this", "weee")
    assert as_tuple(given, fields) == ("bar", ("that", "other thing"), {1, 2, 3})


def test_as_tuple_none_for_missing_fields():
    given = {"foo": "bar", "this": ("that", "other thing")}
    fields = ("foo", "this", "weee")
    assert as_tuple(given, fields) == ("bar", ("that", "other thing"), None)


def test_as_tuple_only_given_fields():
    given = {"foo": "bar", "this": ("that", "other thing"), "weee": {1, 2, 3}}
    fields = ("foo", "this")
    assert as_tuple(given, fields) == ("bar", ("that", "other thing"))


def test_as_tuple_not_sort_fields():
    given = {"foo": "bar", "this": ("that", "other thing")}
    fields = ("this", "foo")
    assert as_tuple(given, fields) == (("that", "other thing"), "bar")
