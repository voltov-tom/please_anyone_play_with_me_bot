import requests

from bs4 import BeautifulSoup


def get_random_picture_src():
    url = 'https://joyreactor.cc'
    site = requests.get(url)
    soup = BeautifulSoup(site.text, 'lxml')
    div = soup.find('div', {'class': 'image'})
    img = div.find('img')
    return 'https:' + img['src']


def get_random_gif_src():
    url = 'https://joyreactor.cc/tag/гифки'
    site = requests.get(url)
    soup = BeautifulSoup(site.text, 'lxml')
    span = soup.find('a', {'class': 'video_gif_source'})
    return 'https:' + span['href']


if __name__ == '__main__':
    print('https:' + get_random_picture_src())
    print('https:' + get_random_gif_src())
