#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import asyncio
import aiohttp
import async_timeout
import sys
import os


async def run(urls=None, output_path='.'):
    '''
    Async to get url and save it as file in the provided path
    '''
    for url in urls:
        filename = url.split('/')[-1]
        async with aiohttp.ClientSession() as session:
            content = await fetch(session, url)
            write_file(content, os.path.join(output_path, filename))

def write_file(content, filename):
    with open(filename, 'wb') as f:
        f.write(content)

async def fetch(session, url):
    print('Downloading {0}'.format(url))
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            content = await response.read()
            # print(content)
            return content

if __name__ == '__main__':
    start_time = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(None))
    print(time.time() - start_time)
