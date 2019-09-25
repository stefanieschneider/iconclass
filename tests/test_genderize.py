# !/usr/bin/python
# -*- coding: utf-8 -*-

from classes.genderize import Genderize


def test_female():
    text = 'female satyrs (in general)'
    assert Genderize(text).code == '31A72'


def test_male():
    text = 'stigmatization of male saint'
    assert Genderize(text).code == '31A71'


def test_none():
    text = 'god the father in the form of light'
    assert Genderize(text).code is None
