# !/usr/bin/python
# -*- coding: utf-8 -*-

import re
import ujson
import os.path

from tqdm import tqdm
from utils import get_ext
from contextlib import ExitStack
from classes.notation import Notation

END_OF_OBJECT = re.compile(r'\n\}\n')


def _get_data(document):
    data = ujson.loads(document)
    code = list(data.keys())[0]

    return code, data[code]


def _get_progress(file_path, verbose):
    if verbose:
        return tqdm(
            total=os.path.getsize(file_path),
            desc='Read', leave=False
        )

    return ExitStack()


def _read_chunks(file_object, chunk_size=2048):
    while True:
        chunk = file_object.read(chunk_size)

        if not chunk:
            break

        yield chunk


def _wrapper(file_path, verbose):
    ext = get_ext(file_path)

    if ext == '.json':
        return parse_json(file_path, verbose)
    elif ext == '.ndjson':
        return parse_ndjson(file_path, verbose)
    else:
        raise AssertionError(
            'File must be in JSON format and '
            'could not be parsed.'
        )


def parse(file_path, lang='en', limit=-1, verbose=True):
    notations = set()

    for code, data in _wrapper(file_path, verbose):
        if lang in data['txt'] and lang in data['kw']:
            notation = Notation(code)

            if notation.is_valid() and \
                    notation not in notations:
                data = {
                    'desc': data['txt'][lang],
                    'keywords': data['kw'][lang]
                }

                notations.add(notation)

                yield notation, data

            if isinstance(limit, int) and limit >= 0:
                if len(notations) == limit:
                    break


def parse_json(file_path, verbose=False):
    with _get_progress(file_path, verbose) as progress_bar:
        with open(file_path, 'r') as file_object:
            buffer = str()  # initialize empty buffer

            for chunk in _read_chunks(file_object):
                buffer += chunk  # append chunk to buffer

                if END_OF_OBJECT.search(buffer):
                    pos = int()  # initialize start position

                    for match in END_OF_OBJECT.finditer(buffer):
                        yield _get_data(buffer[pos:match.end()])
                        pos = match.end()  # reset start position

                    buffer = buffer[match.end():]

                if verbose:
                    # only approx. timings for UTF-8 encoded files
                    progress_bar.update(len(chunk))


def parse_ndjson(file_path, verbose=False):
    with _get_progress(file_path, verbose) as progress_bar:
        with open(file_path, 'r') as file_object:
            for line in file_object:
                yield _get_data(line)

                if verbose:
                    # only approx. timings for UTF-8 encoded files
                    progress_bar.update(len(line))
