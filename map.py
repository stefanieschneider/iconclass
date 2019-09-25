# !/usr/bin/python
# -*- coding: utf-8 -*-

from os import listdir, path
from classes.notation import Notation
from read import parse_ndjson as parse

FOLDER_PATH = 'Data'


def get():
    def _sort_key(value):
        if value.startswith('rm'):
            return -1, value

        return 0, value

    index = dict()

    file_paths = listdir(FOLDER_PATH)
    file_paths.sort(key=_sort_key)

    for file_path in reversed(file_paths):
        if file_path.startswith(('rm', 'cv')):
            file_path = path.join(FOLDER_PATH, file_path)

            for key, values in parse(file_path):
                values = [Notation(x) for x in values]
                index[Notation(key)] = values

    return index
