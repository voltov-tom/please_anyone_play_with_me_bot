import requests

from random import choice
from os import walk, makedirs, path
from bs4 import BeautifulSoup


def get_random_picture_src():
    url = 'https://joyreactor.cc'
    site = requests.get(url)
    soup = BeautifulSoup(site.text, 'lxml')
    div = soup.find('div', {'class': 'image'})
    img = div.find('img')
    return 'https:' + img['src']


def get_random_gif_src():
    site = 'https://joyreactor.cc/tag/гифки'
    response = requests.get(site)
    soup = BeautifulSoup(response.text, 'lxml')
    span = soup.find('a', {'class': 'video_gif_source'})

    gif_name = span['href'][-11:]
    gif_local_name = './gifs/' + gif_name

    makedirs(path.dirname(gif_local_name), exist_ok=True)

    if not path.exists(gif_local_name):
        with open(gif_local_name, 'wb') as f:
            response = requests.get('https:' + span['href'])
            f.write(response.content)

    return gif_local_name


def get_random_gif_src_local():
    path = '/Users/timofeyvoltov/Desktop/gifs/'
    gifs = []

    for (dirpath, dirnames, filenames) in walk(path):
        gifs.extend(filenames)
        break

    return path + choice(gifs)


if __name__ == '__main__':
    print(get_random_gif_src())
