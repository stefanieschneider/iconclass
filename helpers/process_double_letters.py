# !/usr/bin/python
# -*- coding: utf-8 -*-

from read import parse
from itertools import chain
from nltk import word_tokenize
from classes.index import Index
from difflib import SequenceMatcher
from collections import defaultdict
from classes.notation import Notation
from classes.converter import Converter
from classes.genderize import Genderize, get_anti


def _add_genders(notation, gender, converter):
    def _add_gender(notation, gender, anti=True):
        if anti:
            notation = notation.get_anti()
            gender = get_anti(gender)

        data = converter.index.get(notation)

        if data:
            data['gender'] = Notation(gender)
            converter.index.add(notation, data)

            if not anti and notation.division != 9:
                anti_notation = notation.get_anti()

                if anti_notation not in converter.index and \
                        not anti_notation.has_text():
                    anti_notation = anti_notation.get_parent()

                converter.add(notation, anti_notation)
            else:
                converter.add(notation)
        elif not anti:
            parent = notation.get_anti().get_parent()
            converter.add(notation, parent)

        return converter

    converter = _add_gender(notation, gender, False)
    converter = _add_gender(notation, gender, True)

    return converter


def _get_sequence(document_1, document_2):
    def _split(document):
        if not isinstance(document, list):
            document = word_tokenize(document)

        return document

    return SequenceMatcher(
        a=_split(document_1), b=_split(document_2)
    )


def _get_diff(document_1, document_2):
    sequence = _get_sequence(document_1, document_2)
    op_codes = sequence.get_opcodes()

    for code, i_0, i_1, j_0, j_1 in op_codes:
        if code == 'delete':
            yield ' '.join(sequence.a[i_0:i_1])
        elif code == 'replace':
            yield (
                ' '.join(sequence.a[i_0:i_1]),
                ' '.join(sequence.b[j_0:j_1])
            )
        elif code == 'insert':
            yield ' '.join(sequence.b[j_0:j_1])


def _get_addition(notation, index):
    text_1 = index.get(notation, 'desc')
    letter = notation.get_letter()

    if letter.lower() in text_1.split():
        key = text_1.split(' - ')

        if len(key) > 2:
            return key[2].strip()

    text_2 = index.get(notation.get_anti(), 'desc')

    if text_2 and len(text_2) > 3:
        return list(_get_diff(text_1, text_2))


def _get_gender(groups):
    text = [v.keys() for v in groups.values()]
    text = set(chain.from_iterable(text))

    return {x: Genderize(x).code for x in text}


def _clean_groups(groups):
    for basic, group in groups.items():
        sorted_addition = sorted(
            group.items(), key=lambda x: len(x[1])
        )

        if 'other' in group:
            notations = [x for x, _ in group['other']]
            addition = sorted_addition[-1][0]

            if len(sorted_addition) != 2:
                addition = group['other'][0][1]

                if isinstance(addition[0], tuple):
                    addition = [x for x, _ in addition]

                addition = ', '.join(addition)

            groups[basic][addition].extend(notations)
            del groups[basic]['other']

    return groups


def _to_groups(index):
    groups = defaultdict(lambda: defaultdict(list))

    for notation, _ in index:
        addition = _get_addition(notation, index)
        basic = notation.get_basic()

        if basic not in groups:
            prev_addition = None

        if addition and isinstance(addition, str):
            prev_addition = addition

        if prev_addition:
            groups[basic][prev_addition].append(notation)
            continue

        groups[basic]['other'].append((notation, addition))

    return _clean_groups(groups)


def _filter(file_path):
    index = Index()

    for notation, data in parse(file_path):
        if not (notation.has_key() or notation.has_name()):
            if notation.depth > 2:
                data['desc'] = data['desc'].lower()

                if len(notation.get_letter()) == 2:
                    index.add(notation, data, select=True)
                    continue

        index.add(notation, data, select=False)

    return index


def convert(file_path, output):
    converter = Converter(_filter(file_path))

    groups = _to_groups(converter.index)
    gender_additions = _get_gender(groups)

    for basic, group in groups.items():
        for addition, notations in group.items():
            gender = gender_additions.get(addition)

            if gender:
                for notation in notations:
                    for x in converter.index.get_children_until(notation):
                        if (x.has_key() and x.strip_key() == notation) or \
                                (notation.has_text() and x.has_text()):
                            converter = _add_genders(x, gender, converter)

                    if notation.has_text():
                        for x in converter.index.get_neighbors(notation):
                            converter = _add_genders(x, gender, converter)

                    converter = _add_genders(notation, gender, converter)

    converter.update('gender')
    converter.write(output)


if __name__ == '__main__':
    file_path = '../../../Data/Iconclass/iconclass.ndjson'
    convert(file_path, '../Data/cv_double-letters.ndjson')
