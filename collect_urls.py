import random
import time
from urllib.error import HTTPError

import click

from database import TextFiles
from logger import make_logger
from newspapers.registry import registry
from googlesearch import search
from parse_urls import parse_url


def get_newspapers_from_registry(newspapers):
    if (newspapers == ["all",]) or (newspapers == ()):
        return registry
    else:
        return [n for n in registry if n["newspaper_id"] in newspapers]


def collect_from_google(num, newspaper, logger=None):
    if logger:
        logger.info(f'searching for {num} from {newspaper["newspaper"]}')

    urls = google_search(newspaper["newspaper_url"], stop=num)
    urls = [url for url in urls if newspaper["checker"](url, logger)]

    if logger:
        logger.info(f'search: found {len(urls)} for {newspaper["newspaper"]}')
    return urls


def google_search(url, query="climate change", stop=10, backoff=1.0, logger=None):
    #  protects against a -1 example
    if stop <= 0:
        raise ValueError("stop of {stop} is invalid - change the --num argument")

    try:
        query = f"{query} site:{url}"

        time.sleep((2 ** backoff) + random.random())

        urls = list(
            search(query, start=1, stop=stop, pause=4.0, user_agent="climatecode")
        )
        return urls

    except HTTPError as e:
        if logger:
            logger.info(f"{e} at backoff {backoff}")
        return google_search(url, query, stop, backoff=backoff + 1)


@click.command()
@click.argument("newspapers", nargs=-1)
@click.option(
    "-n",
    "--num",
    default=5,
    help="Number of urls to attempt to collect.",
    show_default=True,
)
@click.option(
    "--source", default="google", help="Where to look for urls.", show_default=True
)
@click.option(
    "--parse/--no-parse",
    default=True,
    help="Whether to parse the urls after collecting them.",
)
def cli(num, newspapers, source, parse):
    return main(num, newspapers, source, parse)


def main(num, newspapers, source, parse):
    logger = make_logger("logger.log")
    logger.info(f"collecting {num} from {newspapers} from {source}")

    home = TextFiles()

    newspapers = get_newspapers_from_registry(newspapers)
    print(newspapers)

    collection = []
    for paper in newspapers:
        if source == "google":
            urls = collect_from_google(num, paper, logger)
            if logger:
                logger.info(f"saving {len(urls)} to file")
            home.write(urls, "urls.data", "a")

        elif source == "urls.data":
            urls = home.get("urls.data")
            urls = urls.split("\n")
            urls.remove("")
            urls = [
                u
                for u in urls
                if paper["newspaper_url"] in u
                if paper["checker"](u, logger)
            ][:num]

            if logger:
                logger.info(f"loaded {len(urls)} urls from {source}")

        collection.extend(urls)

    collection = set(collection)
    logger.info(f"collected {len(collection)} urls")

    if parse:
        for url in collection:
            parse_url(url, rewrite=True, logger=logger)

    return collection
