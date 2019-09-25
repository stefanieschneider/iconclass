# !/usr/bin/python
# -*- coding: utf-8 -*-

import ujson

from utils import dump_json
from classes.scrapper import Scrapper
from urllib.parse import urlparse, urlunparse


class Iconclass(Scrapper):
    def __init__(self, output, n=10, verbose=True):
        url = 'http://iconclass.org/{}.json'
        urls = [url.format(i) for i in range(2)]

        super().__init__(urls, output, n, verbose)

    def _extract(self, url, html):
        data = ujson.loads(html)
        url = list(urlparse(url))

        json = dump_json(data)
        self._file_object.write(json)

        for child in data['c']:
            url[2] = child + '.json'
            self._urls.add(urlunparse(url))


if __name__ == '__main__':
    Iconclass('iconclass.ndjson').begin()
