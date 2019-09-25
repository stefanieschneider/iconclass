# !/usr/bin/python
# -*- coding: utf-8 -*-

import re

from read import parse
from utils import get_bracketed
from classes.index import Index
from classes.converter import Converter
from classes.notation import Notation, is_valid

SCHEME = re.compile(
    r'\d{2}(?:[A-IK-Z]{1,2})?(?![a-z])'
    r'(?:\d*)?(?:\([^+)]+\))?(?:\d*)'
)

USE_CODE = re.compile(r'(?:^|\s)[Uu]se\s(.*)')


def _filter(file_path):
    index = Index()

    for notation, data in parse(file_path):
        if not notation.has_key():
            text = USE_CODE.findall(data['desc'])

            if text:
                match = ''.join(text[0].split())
                match = SCHEME.findall(match)

                if match and is_valid(Notation(match[0])):
                    valid_notation = Notation(match[0])

                    if valid_notation.has_text():
                        new_value = get_bracketed(text[0])
                        old_value = get_bracketed(valid_notation)

                        valid_notation = valid_notation.\
                            replace(old_value[0], new_value[0])

                    data['valid'] = valid_notation
                    index.add(notation, data, select=True)
                    continue

            index.add(notation, data, select=False)

    return index


def convert(file_path, output):
    converter = Converter(_filter(file_path))

    for notation, data in converter.index:
        if data['valid'] in converter.index.data:
            converter.add(notation, data['valid'])

    converter.write(output)


if __name__ == '__main__':
    file_path = '../../../Data/Iconclass/iconclass.ndjson'
    convert(file_path, '../Data/cv_invalid.ndjson')
