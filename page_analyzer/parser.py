from bs4 import BeautifulSoup
import requests


def make_soup(url):
    markup = requests.get(url).text
    soup = BeautifulSoup(markup, 'html.parser')
    if soup.find('h1'):
        h1 = soup.find('h1').string
    else:
        h1 = ''
    if soup.find('title'):
        title = soup.find('title').string
    else:
        title = ''
    if soup.find('meta', attrs={"name": "description"}):
        description = soup.find(
            'meta', attrs={"name": "description"})['content']
    else:
        description = ''
    return {'h1': h1, 'title': title, 'description': description}
