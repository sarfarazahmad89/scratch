#!/usr/bin/env python
"""
Downloads file fast using multiple http streams/range header
"""
import asyncio
import logging
import math
import os
import sys
from datetime import datetime
from functools import wraps
from typing import Optional
from urllib import parse

import httpx
import typer
from typing_extensions import Annotated

logger = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(funcName)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def typer_async(func):
    """
    wraps/faciliates asyncio.run() for typer.run()
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


def url_validator(url):
    """
    validates url
    """
    try:
        result = parse.urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


@typer_async
async def main(
    url: Annotated[str, typer.Argument()],
    outputfile: Annotated[Optional[str], typer.Option("-o", help="short or full path to the target file")] = "",
    conncount: Annotated[
        Optional[int],
        typer.Option("-n", help="number of parallel connections to use for the download"),
    ] = 8,
    timeout: Annotated[
        Optional[float],
        typer.Option("-t", help="timeout seconds for network inactivity"),
    ] = 15,
):
    if not url_validator(url):
        logger.error("%s is not a valid HTTP url. exiting ..", url)
        sys.exit(1)

    logger.info("attempting to fetch %s and write into %s", url, outputfile)
    await download(url, conncount, timeout, outputfile)


class ContentRange:
    """
    Iterator generates start-end ranges for each http download_range task
    """

    def __init__(self, length, conns):
        assert conns > 0
        self.conns = conns
        self.length = length
        self.start = 0
        self.end = 0
        self.counter = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.counter != 0:
            self.start = math.floor(self.length / (self.conns) * self.counter) + 1
        self.end = math.floor(self.length / (self.conns) * (self.counter + 1))
        self.counter += 1
        if self.counter == self.conns + 1:
            raise StopIteration
        return (self.start, self.end)


async def download_range(url, timeout, start, end, outfile):
    """
    task to download a select range and write it to a file
    """
    client = httpx.AsyncClient(follow_redirects=True, timeout=timeout)
    length = 0
    headers = {"range": f"bytes={start}-{end}"}
    with open(outfile, "wb") as outfile_fd:
        async with client.stream("GET", url, headers=headers) as response:
            length = response.headers["Content-Length"]
            async for chunk in response.aiter_bytes():
                outfile_fd.write(chunk)
    logger.info("wrote %s bytes to %s", length, outfile)


async def download(url, conncount, timeout, outfile=None):
    """
    orchestrates the downloads by determining content-length,
    spawning download_range() tasks etc.
    """
    logger.info("timeout is set to %s seconds", timeout)
    start_time = datetime.now()
    if not outfile:
        outfile = url.split("/")[-1]
    client = httpx.AsyncClient(follow_redirects=True)
    response = await client.head(url)
    headers_lc = [h.lower() for h in response.headers]
    if "content-length" not in headers_lc:
        logger.error("`content-length` not reported by the server. exiting.")
        return

    if "accept-ranges" not in headers_lc:
        logger.warning("%s does not accept byte ranges. this will be a single threaded download", url)
        conns = 1
    else:
        conns = conncount

    length = response.headers["Content-Length"]
    logger.info("content length is %s bytes. using {conns} parallel connections to download.", length)

    tasks = {}
    file_idx = 0
    for start, end in ContentRange(int(length), conns):
        file_n = f".{outfile}.{file_idx}"
        task = asyncio.create_task(download_range(url, timeout, start, end, file_n))
        tasks[file_n] = task
        file_idx += 1

    try:
        await asyncio.gather(*tasks.values())
    except Exception:
        logger.error("download failed. cleaning up and exiting.")
        for file_n, task in tasks.items():
            task.cancel()
            if os.path.exists(file_n):
                os.remove(file_n)
        return

    logger.info("concatenating/collapsing chunks into %s", outfile)
    with open(outfile, "wb") as outfile_fd:
        for i in range(file_idx):
            chunk_path = f".{outfile}.{i}"
            with open(chunk_path, "rb") as source_fd:
                outfile_fd.write(source_fd.read())
            os.remove(chunk_path)
    logger.info("wrote %s", outfile)
    end_time = datetime.now()
    logger.info("download took %s", end_time - start_time)


def launch():
    """
    entrypoint for console_scripts
    """
    typer.run(main)


if __name__ == "__main__":
    launch()
