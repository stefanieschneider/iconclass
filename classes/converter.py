# !/usr/bin/python
# -*- coding: utf-8 -*-

from classes.index import Index
from collections import defaultdict
from classes.notation import is_valid
from utils import dump_json, strip_bracketed


class Converter:
    def __init__(self, index):
        self._converter = defaultdict(list)

        if isinstance(index, Index):
            self.index = index

    def add(self, old_value, new_value=None):
        if is_valid(old_value):
            if new_value is None:
                self._converter[old_value].append(old_value)
            elif is_valid(new_value):
                self._converter[old_value].append(new_value)

    def add_children(self, other):
        for x in self.index.get_children_until(other):
            self.add(x)

    def add_names(self, other):
        for x in self.index.get_children(other):
            if not self.index.get(x, 'desc').startswith('other'):
                name = self.index.get(x, 'names').partition(' of ')
                name = strip_bracketed(name[0]).strip().upper()

                new_x = other.add('({})'.format(name))
                self.add(x, new_x)

                for child in self.index.get_children_until(x):
                    new_child = child.replace(x, new_x)

                    if child.has_text():
                        parents = child.get_parents_until()

                        for parent in reversed(parents):
                            if not parent.has_text():
                                new_child = parent.replace(x, new_x)
                                break

                    self.add(child, new_child)

                continue

            self.add(x, x.get_parent())

    def update(self, column):
        updater = dict()

        for key in self._converter:
            updater[key] = self.index.get(key, column)

        for key, value in updater.items():
            if value is None:
                parents = key.get_parents_until()

                for parent in reversed(parents):
                    if updater.get(parent):
                        updater[key] = updater[parent]
                        break

        for key, value in updater.items():
            if value:
                self._converter[key].append(value)

    def replace(self, old_value, new_value, exclude=None):
        if is_valid(old_value) and is_valid(new_value):
            for key, values in self._converter.items():
                if key.division != exclude:
                    values = [
                        value.replace(old_value, new_value)
                        for value in values
                    ]

                    self._converter[key] = values

    def remove_mappings(self):
        for key, values in self._converter.items():
            self._converter[key] = []

    def write(self, output):
        with open(output, 'w') as file_object:
            for key, values in self._converter.items():
                values = sorted(set(values))

                values = [
                    value.code for value in values
                    if value and is_valid(value)
                ]

                values = dump_json({key.code: values})
                file_object.write(values)
