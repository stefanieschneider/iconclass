# !/usr/bin/python
# -*- coding: utf-8 -*-

from classes.notation import Notation


def test_division():
    assert Notation('98').division == 9


def test_depth():
    assert Notation('11H(ANSELM)8').depth == 6
    assert Notation('7(+45)').depth == 3


def test_is_valid():
    assert not Notation('11J').is_valid()
    assert Notation('11I').is_valid()


def test_is_child():
    assert not Notation('11H').is_child(Notation('12'))
    assert Notation('11H1').is_child(Notation('11'))


def test_is_direct_child():
    assert not Notation('11H1').is_direct_child(Notation('11'))
    assert Notation('11H').is_direct_child(Notation('11'))


def test_is_basic():
    assert not Notation('95A(...)').is_basic()
    assert Notation('11H').is_basic()


def test_get_basic():
    assert Notation('7(+45)').get_basic() == '7'
    assert Notation('11').get_basic() == '11'


def test_has_queue():
    assert not Notation('95A').has_queue()
    assert Notation('95A1').has_queue()


def test_get_queue():
    assert Notation('95A1').get_queue() == '1'


def test_has_text():
    assert Notation('11H(ANSELM)8').has_text()
    assert Notation('95A(...)').has_text()


def test_get_text():
    assert Notation('11H(ANSELM)8').get_text() == 'ANSELM'


def test_has_digit():
    assert not Notation('11H(ANSELM)').has_digit()
    assert Notation('11H(ANSELM)8').has_digit()


def test_get_digit():
    assert Notation('11H(ANSELM)8').get_digit() == '8'


def test_has_key():
    assert not Notation('7').has_key()
    assert Notation('7(+45)').has_key()


def test_get_key():
    assert Notation('7(+45)').get_key() == '45'


def test_get_anti():
    assert Notation('11HH').get_anti() == Notation('11H')


def test_get_next():
    assert Notation('11').get_next() == Notation('12')
    assert Notation('11II').get_next() == Notation('11KK')

    assert Notation('11H(ANSELM)9').get_next() is None
    assert Notation('11H(ANSELM)').get_next() is None


def test_get_parents_until():
    assert Notation('11H1').get_parents_until(depth=1) == \
           [Notation('1'), Notation('11'), Notation('11H')]

    assert Notation('11H(ANSELM)').get_parents_until(depth=2) == \
           [Notation('11'), Notation('11H'), Notation('11H(...)')]
