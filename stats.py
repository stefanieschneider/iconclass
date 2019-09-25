# !/usr/bin/python
# -*- coding: utf-8 -*-

from read import parse
from collections import defaultdict


def _get_stats(values):
    if isinstance(values, list):
        values = [x for x in values if x]

        if values[0].isdigit():
            values = [int(x) for x in values]

            return min(values), max(values)

        return sorted(x for x in values if len(x) < 2)


def _filter(file_path):
    test = set()

    for notation, data in parse(file_path):
        letter = notation.get_letter()
        basic = notation.get_basic()[:2]

        queue = notation.get_queue()
        digit = notation.get_digit()
        key = notation.get_key()

        if notation.has_key():
            test.add(notation)

        yield basic, letter, queue, digit, key

    print(len(test))


def get(file_path):
    stats = defaultdict(list)
    data = _filter(file_path)

    for basic, letter, queue, digit, key in data:
        if basic not in stats['basic']:
            stats['basic'].append(basic)

        if letter not in stats['letter']:
            stats['letter'].append(letter)

        if queue not in stats['queue']:
            stats['queue'].append(queue)

        if digit not in stats['digit']:
            stats['digit'].append(digit)

        if key not in stats['key']:
            stats['key'].append(key)

    for key in stats.keys():
        print(key, _get_stats(stats[key]))


if __name__ == '__main__':
    get('../../Data/Iconclass/iconclass.ndjson')
