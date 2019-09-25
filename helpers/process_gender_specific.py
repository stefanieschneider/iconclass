# !/usr/bin/python
# -*- coding: utf-8 -*-

from read import parse
from classes.index import Index
from classes.notation import Notation
from classes.genderize import Genderize
from classes.converter import Converter
from helpers.filter_keywords import get_names


def _with_names(notation, index):
    if len(index.get_children_until(notation)) > 2:
        children = index.get_children(notation)

        if children and not any(x.has_text() for x in children):
            test_names = [index.get(x, 'names') for x in children]

            if len(set(test_names)) / len(test_names) > 0.85:
                return True

    return False


def _filter(file_path):
    index = Index()

    for notation, data in parse(file_path):
        if notation.division != 3 and not notation.has_key():
            data['names'] = get_names(data, keep_all=False)

            if not (notation.has_text() or notation.depth > 7 or
                    data['desc'].startswith(('other', 'early'))):
                gender = Genderize(data['desc']).code

                if gender:
                    data['gender'] = Notation(gender)
                    index.add(notation, data, select=True)
                    continue

            index.add(notation, data, select=False)

    return index


def convert(file_path, output):
    converter = Converter(index=_filter(file_path))

    for notation, data in converter.index:
        next_notation = converter.index.get_next(notation)
        next_data = converter.index.get(next_notation)

        if next_data and data['gender'] != next_data['gender']:
            full_desc = data['desc'] + next_data['desc']

            if notation.division == 4 or 'female' in full_desc:
                converter.add(notation)
                converter.add(next_notation)

                if _with_names(notation, converter.index):
                    new_notation = notation.add('(...)')
                    converter.add(notation, new_notation)

                    converter.add_names(notation)
                    converter.add_names(next_notation)
                else:
                    converter.add_children(notation)
                    converter.add_children(next_notation)

                converter.replace(next_notation, notation, 4)

    converter.update('gender')
    converter.write(output)


if __name__ == '__main__':
    file_path = '../../../Data/Iconclass/iconclass.ndjson'
    convert(file_path, '../Data/cv_gender-specific.ndjson')
