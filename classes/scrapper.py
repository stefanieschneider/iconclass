# !/usr/bin/python
# -*- coding: utf-8 -*-

import asyncio
import warnings

from tqdm import tqdm
from utils import dump_json
from aiohttp import ClientSession


class Scrapper:
    def __init__(self, urls, output, n=10, verbose=True):
        self._urls, self._store = set(urls), set()
        self._semaphore = asyncio.Semaphore(n)
        self._file_object = open(output, 'w')

        self._verbose = verbose

    def begin(self):
        if self._file_object:
            while self._urls and self._urls != self._store:
                self._store = self._urls
                self._init_chunk()

            for url in self._urls:
                warnings.warn('Could not retrieve {}.'.format(url))

            self._file_object.close()
            self._file_object = None

    def _init_chunk(self):
        future = asyncio.ensure_future(self._begin_chunk())
        loop = asyncio.get_event_loop()

        return loop.run_until_complete(future)

    async def _begin_chunk(self):
        tasks = list()

        async with ClientSession() as session:
            for url in self._urls:
                task = self._bound_fetch(url, session)
                tasks.append(asyncio.ensure_future(task))

            self._urls = set()

            if self._verbose:
                tasks = tqdm(
                    asyncio.as_completed(tasks),
                    total=len(tasks), leave=False
                )

            return [await task for task in tasks]

    async def _bound_fetch(self, url, session):
        async def _fetch():
            try:
                async with session.get(url, timeout=60) as response:
                    return self._extract(url, await response.read())
            except (ValueError, Exception):
                self._urls.add(url)

        async with self._semaphore:
            return await _fetch()

    def _extract(self, url, html):
        json = dump_json({url: html})
        self._file_object.write(json)
