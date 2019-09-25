# !/usr/bin/python
# -*- coding: utf-8 -*-

from read import parse
from classes.index import Index
from classes.converter import Converter


def _filter(file_path):
    index = Index()

    for notation, data in parse(file_path):
        if not (notation.has_text() or notation.has_key()):
            if notation.depth > 1 and notation.code[-1] == '9' \
                    and not data['desc'].startswith('other'):
                index.add(notation, data, select=True)

        index.add(notation, data, select=False)

    return index


def convert(file_path, output):
    converter = Converter(index=_filter(file_path))

    for notation, data in converter.index:
        sibling = notation.get_parent().add('8')

        if sibling not in converter.index.data:
            converter.add(notation)
            converter.add_children(notation)

    converter.remove_mappings()
    converter.write(output)


if __name__ == '__main__':
    file_path = '../../../Data/Iconclass/iconclass.ndjson'
    convert(file_path, '../Data/rm_broken-sequence.ndjson')
