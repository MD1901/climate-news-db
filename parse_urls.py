import json

import click

from database import NewspaperTextFiles
from logger import make_logger
from newspapers.registry import find_newspaper_from_url
from newspapers.registry import check_parsed_article, registry, clean_parsed_article


def parse_url(url, rewrite, logger):
    newspaper = find_newspaper_from_url(url)

    logger.info(f"{url}, parsing")

    newspaper_id = newspaper['newspaper_id']
    raw = NewspaperTextFiles(f"raw/{newspaper_id}")
    final = NewspaperTextFiles(f"final/{newspaper_id}")

    #  run the parsing
    parsed = newspaper["parser"](url)
    #  check if already in database
    #  bit silly as we have already parsed it!
    #check = final.check(parsed['article_id'])

    #  cant check if we get an error there!

    # if not rewrite and check:
    #     logger.info(r'{url}, {article_id} already exists - not parsing')

    if "error" in parsed.keys():
        error = parsed["error"]
        logger.info(f"{url}, error, {error}")

    else:
        parsed = check_parsed_article(parsed)
        if not parsed:
            logger.info(f"{url}, error, failed check_parsed_article")

        else:
            parsed = clean_parsed_article(parsed)

            article_id = parsed["article_id"]
            logger.info(f"{url}, saving, article_id={article_id}")
            raw.write(parsed["html"], article_id + ".html", "w")
            del parsed["html"]
            try:
                final.write(json.dumps(parsed), article_id + ".json", "w")
            except TypeError:
                logger.info(f"{url}, type error")


@click.command()
@click.argument("newspapers", nargs=-1)
@click.option("--rewrite/--no-rewrite", default=True)
def main(newspapers, rewrite):

    #  reads from urls.data, writes to database
    #  check if html exists

    logger = make_logger("logger.log")
    from collect_urls import main as collect_urls

    #  get all urls from urls.data
    urls = collect_urls(num=-1, newspapers=newspapers, source="urls.data", parse=False)

    for url in urls:
        parse_url(url, rewrite=rewrite, logger=logger)
