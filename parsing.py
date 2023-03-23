import requests

from random import choice
from bs4 import BeautifulSoup


def get_random_picture_src():
    url = 'https://www.google.com/search?q=valorant+meme&newwindow=1&client=safari&rls=en&sxsrf=AJOqlzV654H14JhZ43J2TyBqUQwFA2dU-g:1679584892775&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiIs52nrfL9AhXRFXcKHWWBCxsQ_AUoAXoECAEQAw&biw=1536&bih=800&dpr=1'
    site = requests.get(url)
    soup = BeautifulSoup(site.text, 'lxml')
    img = choice(soup.find_all('img'))
    return img['src']
