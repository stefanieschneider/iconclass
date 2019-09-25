# !/usr/bin/python
# -*- coding: utf-8 -*-

import re

PUNCTUATION = re.compile(r'[^\w\s]', re.UNICODE)
MULTIPLE_WHITESPACES = re.compile(r'\s\s+')


def _strip_punctuation(document):
    document = PUNCTUATION.sub('', document)

    return MULTIPLE_WHITESPACES.sub(' ', document)


def _find_index(keyword, document):
    keyword = keyword.lower()
    document = document.lower()

    index = document.find(keyword)

    if index == -1:
        for x in keyword.split():
            if len(x) > 1:
                x = x[:6].strip()
                index = document.find(x)

                if index > -1:
                    break

    return index


def get_names(data, keep_all=True):
    def _get_names():
        desc = _strip_punctuation(data['desc'])

        for keyword in data['keywords']:
            _keyword = keyword.replace('\'', ' ')
            _keyword = _strip_punctuation(_keyword)

            index = _find_index(_keyword, desc)

            if _keyword[0].isupper() and index > -1 and not \
                    any(x.isdigit() for x in _keyword):
                yield keyword, index

    names = sorted(_get_names(), key=lambda x: x[1])
    names = [name for name, index in names]

    if not keep_all:
        names = names[0] if names else ''

    return names
