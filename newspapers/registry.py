from datetime import datetime
import html.parser

from newspapers.guardian import check_guardian_url, parse_guardian_html
from newspapers.fox import check_fox_url, parse_fox_html
from newspapers.skyau import check_sky_au_url, parse_sky_au_url
from newspapers.nytimes import check_nytimes_url, parse_nytimes_html

from newspapers.economist import economist
from newspapers.newshub import newshub
from newspapers.nzherald import nzherald
from newspapers.stuff import stuff
from newspapers.aljazeera import aljazeera
from newspapers.atlantic import atlantic


def find_newspaper_from_url(url):
    for paper in registry:
        if paper['newspaper_url'] in url:
            return paper


registry = [
    nzherald, stuff, newshub, economist, aljazeera, atlantic,
    {
        "newspaper_id": "guardian",
        "newspaper": "The Guardian",
        "newspaper_url": "theguardian.com",
        "checker": check_guardian_url,
        "parser": parse_guardian_html
    },
    {
        "newspaper_id": "fox",
        "newspaper": "Fox News",
        "newspaper_url": "foxnews.com",
        "checker": check_fox_url,
        "parser": parse_fox_html
    },
    {
        "newspaper_id": "nytimes",
        "newspaper": "The New York Times",
        "newspaper_url": "nytimes.com",
        "checker": check_nytimes_url,
        "parser": parse_nytimes_html
    },
    {
        "newspaper_id": "skyau",
        "newspaper": "Sky News Australia",
        "newspaper_url": "skynews.com.au",
        "checker": check_sky_au_url,
        "parser": parse_sky_au_url
    }
]


def get_newspaper(newspaper):
    for paper in registry:
        if paper['newspaper_id'] == newspaper:
            return paper
    raise ValueError(f'{newspaper} not in registry')



def check_parsed_article(parsed):
    if not parsed:
        return {}

    newspaper = get_newspaper(parsed['newspaper_id'])
    parsed['date_uploaded'] = datetime.utcnow().isoformat()
    parsed = {**parsed, **newspaper}

    del parsed['checker']
    del parsed['parser']

    schema = [
        'newspaper',
        'newspaper_id',
        'newspaper_url',
        'body',
        'headline',
        'html',
        'article_url',
        'article_id',
        'date_published',
        'date_uploaded'
    ]
    for s in schema:
        #  check key exists
        if s not in parsed.keys():
            raise ValueError(f'{s} missing from parsed article')

        #  check value length
        val = parsed[s]
        if len(val) < 2:
            raise ValueError(f'{s} not long enough - {val}')

    return parsed


def clean_parsed_article(parsed):
    #  data cleaning - replacing escaped html characters
    html_parser = html.parser.HTMLParser()
    parsed['body'] = html_parser.unescape(parsed['body'])
    parsed['headline'] = html_parser.unescape(parsed['headline'])
    return parsed
