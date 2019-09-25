# !/usr/bin/python
# -*- coding: utf-8 -*-

from read import parse
from utils import dump_json
from classes.index import Index
from helpers.filter_keywords import get_names


def _get_names(notation, index):
    for child in index.get_children(notation):
        yield index.get(child, 'names')


def _filter(file_path):
    index = Index()

    for notation, data in parse(file_path):
        if not (notation.has_key() or notation.has_text()):
            data['names'] = get_names(data, keep_all=False)

            if data['names'] and notation.depth > 3:
                parent = notation.get_parent()
                index.add(parent, dict(), select=True)

            index.add(notation, data, select=False)

    return index


def get(file_path, output):
    index = _filter(file_path)

    for notation, data in index:
        names = list(_get_names(notation, index))
        data['ratio'] = len(set(names)) / len(names)

        if len(names) > 2 and data['ratio'] >= 0.8:
            index.add(notation, data, select=True)
            continue

        index.remove(notation, data=False)

    with open(output, 'w') as file_object:
        for notation, data in sorted(index):
            for parent in notation.get_parents_until(4):
                if parent in index:
                    continue

            values = dump_json({notation.code: data})
            file_object.write(values)


if __name__ == '__main__':
    file_path = '../../../Data/Iconclass/iconclass.ndjson'
    get(file_path, '../Data/gt_hidden-structural.ndjson')
