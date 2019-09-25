# !/usr/bin/python
# -*- coding: utf-8 -*-

from read import parse
from classes.index import Index
from collections import defaultdict
from utils import dump_json, get_bracketed


def _filter(file_path):
    index = Index()

    for notation, data in parse(file_path):
        if not (notation.has_key() or notation.has_digit()):
            if notation.has_text() and not notation.has_name():
                parent = notation.get_parent()
                index.add(parent, dict(), select=True)

            index.add(notation, data, select=False)

    return index


def get(file_path, output):
    index = _filter(file_path)

    with open(output, 'w') as file_object:
        for notation, _ in sorted(index):
            data = defaultdict(list)

            for x in index.get_children_until(notation, 2):
                if x.has_text() and x.has_name():
                    name = get_bracketed(x.code)

                    data['names'].append(name[0])
                    data['codes'].append(x.code)

            data['names'] = sorted(set(data['names']))
            data['codes'] = sorted(set(data['codes']))

            values = dump_json({notation.code: data})
            file_object.write(values)


if __name__ == '__main__':
    file_path = '../../../Data/Iconclass/iconclass.ndjson'
    get(file_path, '../Data/gt_bracketed-text.ndjson')
