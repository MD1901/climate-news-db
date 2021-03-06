from bs4 import BeautifulSoup
import requests

import re


def check_guardian_url(url, logger=None):
    parts = url.split('/')
    article_id = parts[-1]
    article_id = article_id.replace('.html', '')

    url = url.replace('https://www.theguardian.com/', '')
    url = url.replace(article_id, '')

    #  searching for a string like 2020/may/14
    expr = '\d{4}\/[a-z]{3}\/\d{2}'
    matches = re.findall(expr, url)
    if not matches:
        if logger:
            logger.info(f'guardian, {url}, check failed, no YYYY/month/DD in url')
        return False

    assert len(matches) == 1
    date = matches[0]

    category = url.replace(date, '')
    unwanted = ['live', 'gallery', 'audio', 'video', 'ng-interactive', 'interactive']

    for cat in unwanted:
        if cat in category:
            if logger:
                logger.info(f'guardian, {url}, check failed, in {cat} category')
            return False

    return True


def parse_guardian_html(url):
    req = requests.get(url)
    html = req.text
    soup = BeautifulSoup(html, features="html5lib")

    table = soup.findAll('div', attrs={"itemprop": 'articleBody'})
    if len(table) != 1:
        return {}
    article = ''.join([p.text for p in table[0].findAll('p')])

    # TODO function
    published = soup.findAll('time', attrs={'itemprop': 'datePublished'})
    assert len(published) == 1
    published = published[0]['datetime']

    updated = soup.findAll('time', attrs={'itemprop': 'dateModified'})
    if not updated:
        updated = soup.findAll('meta', attrs={'itemprop': 'dateModified'})
        assert len(updated) == 1
        updated = updated[0]['content']
    else:
        assert len(updated) == 1
        updated = updated[0]['datetime']

    headline = soup.findAll('h1', attrs={'itemprop': "headline", 'class':'content__headline'})
    if not headline:
        headline = soup.findAll('meta', attrs={'property': 'og:title'})
        headline = headline[0]['content']
    else:
        headline = headline[0].getText()

    headline = headline.split('|')[0]

    return {
        'newspaper_id': 'guardian',
        'body': article,
        'headline': headline,
        'article_url': url,
        'html': html,
        'article_id': url.split('/')[-1],
        'date_published': published,
        'date_modified': updated,
    }
