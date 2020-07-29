import json

import requests
from bs4 import BeautifulSoup

from newspapers.utils import check_match


def check_fox_url(url, logger):
    unwanted = ['category', 'video', 'radio', 'person']
    if not check_match(url, unwanted):
        logger.info(f'fox, {url}, check failed')
        return False
    return True


def check_for_strong_link(p):
    """Looking for a strong tag inside a link"""
    for child in p.children:
        if child.name == 'a':
            for child in child.children:
                if child.name == 'strong':
                    print(f'not taking {child.text}')
                    return True


def parse_fox_html(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, features="html.parser")

    table = soup.findAll('div', attrs={"class": "article-body"})
    if len(table) != 1:
        return {}

    article = []
    for p in table[0].findAll('p'):
        flag = check_for_strong_link(p)
        if not flag:
            article.append(p.text)

    article = ''.join(article)
    #  hack for coronavirus tag that appears in later articles
    article = article.replace(
        'Get all the latest news on\xa0coronavirus\xa0and more delivered daily to your inbox.\xa0Sign up here.',
        ''
    )

    #  info about published date
    scripts = soup.findAll('script', attrs={'type': 'application/ld+json'})
    assert len(scripts) == 2
    article_metadata = str(scripts[0].contents[0])
    article_metadata = article_metadata.replace('\n', '')
    article_metadata = json.loads(article_metadata)
    headline = soup.findAll('h1', attrs={'class': 'headline'})
    assert len(headline) == 1
    headline = headline[0].get_text()

    return {
        'newspaper': 'Fox News',
        'newspaper_id': 'fox',
        'body': article,
        'headline': headline,
        'html': html,
        'article_url': url,
        'article_id': url.split('/')[-1],
        'date_published': article_metadata['datePublished'],
        'date_modified': article_metadata['dateModified']
    }


if __name__ == '__main__':
    import requests

    url = 'https://www.foxnews.com/opinion/joe-bastardi-climate-change-agenda-is-being-driven-by-hysteria-not-facts'
    out = parse_fox_html(url)

    html = requests.get(url).text
    soup = BeautifulSoup(html, features="html.parser")

    table = soup.findAll('div', attrs={"class": "article-body"})


    for p in table[0].findAll('p'):
        flag = check_for_strong_link(p)

