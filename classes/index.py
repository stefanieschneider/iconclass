# !/usr/bin/python
# -*- coding: utf-8 -*-

from tqdm import tqdm
from sys import getsizeof as size
from collections import defaultdict
from classes.notation import Notation


def valid_notation(function):
    def function_wrapper(self, other, *args, **kwargs):
        if isinstance(other, Notation) and other.is_valid():
            return function(self, other, *args, **kwargs)

    return function_wrapper


class Index:
    def __init__(self, verbose=True):
        self._select, self._remove = set(), set()
        self.data, self._verbose = dict(), verbose

        self._lookup = defaultdict(set)

    def __iter__(self):
        def _get_progress():
            items = sorted(self.data.items())

            if self._verbose:
                return tqdm(items, 'Process')

            return items

        for notation, data in _get_progress():
            if self._select:
                if notation in self._select:
                    yield notation, data

                continue

            yield notation, data

        for notation in self._remove:
            del self.data[notation]

    def __contains__(self, other):
        if self._select:
            if other in self._select:
                return True
        elif other in self.data:
            return True

        return False

    @valid_notation
    def add(self, other, data=None, select=False):
        if other not in self.data:
            for x in other.get_parents_until():
                self._lookup[x].add(other)

        if other not in self.data or \
                size(data) > size(self.data[other]):
            self.data[other] = data

        if isinstance(select, bool) and select:
            self._select.add(other)

    def remove(self, other, data=True):
        if other in self.data:
            if other in self._select:
                self._select.remove(other)

            if data:
                self._remove.add(other)

    def get(self, other, column=None):
        if other in self.data:
            data = self.data[other]

            if isinstance(data, dict):
                if column:
                    return data.get(column)

            return data

    @valid_notation
    def get_next(self, other):
        next_other = other.get_next()

        if self._select:
            if next_other in self._select:
                return next_other
        elif next_other in self.data:
            return next_other

    def get_children(self, other):
        return self.get_children_until(other, depth=1)

    @valid_notation
    def get_children_until(self, other, depth=None):
        def _get_until():
            for notation in self._lookup[other]:
                if notation.depth <= depth:
                    yield notation

        depth = other.depth + depth if depth else 99

        return set(_get_until())

    @valid_notation
    def get_neighbors(self, other, remove=True):
        def _get(parent):
            for x in self.get_children(parent):
                if not remove or x != other:
                    yield x

        return list(_get(other.get_parent()))
