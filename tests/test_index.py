# !/usr/bin/python
# -*- coding: utf-8 -*-

import pytest

from classes.index import Index
from classes.notation import Notation

NOTATIONS = {
    Notation('1'): {'desc': 'Religion and Magic'},
    Notation('11'): {'desc': 'Christian religion'},
    Notation('11K'): {'desc': 'devil(s) and demon(s)'},
    Notation('12'): {'desc': 'non-Christian religions'}
}


@pytest.fixture()
def data():
    index = Index()

    for key, value in NOTATIONS.items():
        index.add(key, value)

    return index


def test_contains(data):
    for key in NOTATIONS:
        assert key in data


def test_add(data):
    data.add(Notation('13'))
    assert Notation('13') in data


def test_remove(data):
    for key in NOTATIONS:
        data.remove(key)
        assert key not in data


def test_get(data):
    for key, value in NOTATIONS.items():
        if isinstance(value, dict):
            column = list(value.keys())[0]

            assert data.get(key, column) == \
                NOTATIONS[key][column]

        assert data.get(key) == NOTATIONS[key]


def test_get_next(data):
    assert data.get_next(Notation('11')) == Notation('12')
    assert data.get_next(Notation('12')) is None


def test_get_children(data):
    assert sorted(data.get_children(Notation('1'))) == \
           sorted([Notation('11'), Notation('12')])


def test_get_children_until(data):
    assert sorted(data.get_children_until(Notation('1'))) == \
           sorted([Notation('11'), Notation('12'), Notation('11K')])


def test_get_neighbors(data):
    assert data.get_neighbors(Notation('11')) == [Notation('12')]
