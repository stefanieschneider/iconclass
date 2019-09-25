# !/usr/bin/python
# -*- coding: utf-8 -*-

from read import parse
from utils import is_in
from classes.index import Index
from classes.converter import Converter


def _filter(file_path):
    index, terms = Index(), ['allegori', 'symboli']

    for notation, data in parse(file_path):
        if notation.depth > 1:
            if is_in(terms, data['desc'].lower()) or \
                    notation.code[-1] == '0':
                index.add(notation, data, select=True)
                continue

        index.add(notation, data, select=False)

    return index


def convert(file_path, output):
    converter = Converter(index=_filter(file_path))

    for notation, data in converter.index:
        parents = notation.get_parents_until()

        if not any(x in converter.index for x in parents):
            converter.add(notation)
            converter.add_children(notation)

    converter.remove_mappings()
    converter.write(output)


if __name__ == '__main__':
    file_path = '../../../Data/Iconclass/iconclass.ndjson'
    convert(file_path, '../Data/rm_allegorical.ndjson')
