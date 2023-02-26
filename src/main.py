#!/usr/bin/python3
#-*- coding: utf-8 -*-

import os
import argparse
import pymp
import requests
import markdownify
import multiprocessing

from bs4 import BeautifulSoup
from urllib.parse import urlparse

DIR_ARCTICLE = 'article'
DIR_FAVORITES = 'favorites'
DIR_PICTURE = 'picture'
DIR_VIDEO = 'video'
DIR_SINGLES = 'singles'
HABR_TITLE = "https://habr.com"


def callback(el):
    try:
        soup = BeautifulSoup(str(el), features='html.parser')
        return soup.find('code')['class'][0]
    except:
        return None


class habrArticleSrcDownloader():

    def __init__(self):
        self.dir_author = ''
        self.posts = []
        self.comments = None

    def dir_cor_name(self, _str):
        for ch in ['#', '%', '&', '{', '}', '\\', '?', '<', '>', '*', '/', '$', '‘', '“', ':', '@', '`', '|']:
            _str = _str.replace(ch, ' ')

        return _str

    def create_dir(self, dir):
        if not os.path.exists(dir):
            try:
                os.makedirs(dir)
                if not args.quiet:
                    print("[info]: Директория: {} создана".format(dir))
            except OSError:
                print("[error]: Ошибка создания директории: {}".format(dir))

    def save_md(self, name: str, text: str):
        with open(name + ".md", "w", encoding="UTF-8") as fd:
            fd.write(f'# {name}\n')
            fd.write(text)

    def save_html(self, name: str, text: str):
        with open(name + ".html", "w", encoding="UTF-8") as fd:
            fd.write(f'<h1>{name}</h1>')
            fd.write(text)

    def save_comments(self, name: str, text: str):
        lst = text.split('\n')
        lst.reverse()

        with open(name + "_comments.md", "w", encoding="UTF-8") as fd:
            fd.write("\n".join(lst))

    def get_comments(self, url_soup):
        comments = url_soup.findAll('link', {'type': 'application/rss+xml'})

        for c in comments:
            try:
                r = requests.get(c.get('href'))
            except requests.exceptions.RequestException:
                print("[error]: Ошибка получения статьи: ", c.get('href'))
                return

            url_soup = BeautifulSoup(r.text, 'lxml')

            return markdownify.markdownify(str(url_soup), heading_style="ATX", code_language_callback=callback)

    def get_article(self, url, name=None):
        try:
            r = requests.get(url)
        except requests.exceptions.RequestException:
            print("[error]: Ошибка получения статьи: ", url)
            return

        url_soup = BeautifulSoup(r.text, 'lxml')
        comment = self.get_comments(url_soup)

        posts = url_soup.findAll('div', {'class': 'tm-article-body'})
        pictures = url_soup.findAll('img')
        video = url_soup.findAll('div', {'class': 'tm-iframe_temp'})

        # одиночное скачивание статьи
        if name is None:

            habrSD.create_dir(DIR_SINGLES)
            os.chdir(DIR_SINGLES)

            name = self.dir_cor_name(url_soup.find('h1', 'tm-article-snippet__title tm-article-snippet__title_h1').string)

            self.create_dir(name)
            os.chdir(name)

        for p in posts:

            if args.local_pictures:
                pictures_names = p.findAll('img')
                for link in pictures_names:
                    link = link.get('src')
                    filename = 'picture/' + link.split('/')[len(link.split('/')) - 1]
                    p = str(p)
                    p = p.replace(str(link), str(filename))

            p = str(p)

            h = markdownify.markdownify(p, heading_style="ATX", code_language_callback=callback)

            _p = p.replace("<pre><code class=", "<source lang=").replace("</code></pre>", "</source>")

            # создаем дирректорию под картинки
            self.create_dir(DIR_PICTURE)
            os.chdir(DIR_PICTURE)
            self.save_pictures(pictures)
            os.chdir('../')

            # создаем дирректорию под видео
            self.create_dir(DIR_VIDEO)
            os.chdir(DIR_VIDEO)
            self.save_video(video)
            os.chdir('../')

            self.save_html(name, _p)
            self.save_md(name, h)
            self.save_comments(name, str(comment))

            if not args.quiet:
                print(f"[info]: Статья: {name} сохранена")

    def save_pictures(self, pictures):
        for link in pictures:
            if link.get('data-src'):
                try:
                    img_data = requests.get(link.get('data-src')).content

                    a = urlparse(link.get('data-src'))

                    with open(os.path.basename(a.path), 'wb') as handler:
                        handler.write(img_data)
                except requests.exceptions.RequestException:
                    print("[error]: Ошибка получения картинки: ", link.get('data-src'))

    def save_video(self, video):
        with open('video.txt', 'w') as f:
            for link in video:
                if link.get('data-src'):
                    print(link.get('data-src'), file=f)

    def get_articles(self, url):
        page_number = 1

        while True:
            try:
                r = requests.get(url + "page" + str(page_number))
            except requests.exceptions.RequestException:
                print("[error]: Ошибка получения статей: ", url)
                return

            url_soup = BeautifulSoup(r.text, 'lxml')

            posts = url_soup.findAll('a', {'class': 'tm-article-snippet__title-link'})

            if len(posts) == 0:
                break

            self.posts += posts
            page_number = page_number + 1

    def parse_articles(self):
        print(f"[info]: Будет загружено: {len(self.posts)} статей.")

        with pymp.Parallel(multiprocessing.cpu_count()) as pmp:
            #for p in self.posts :
            for i in pmp.range(0, len(self.posts)):
                p = self.posts[i]
                if not args.quiet:
                    print("[info]: Скачивается:", p.text)

                name = self.dir_cor_name(p.text)

                dir_path = '{:03}'.format(len(self.posts) - i) + " " + name

                # создаем директории с названиями статей
                self.create_dir(dir_path)
                # заходим в директорию статьи
                os.chdir(dir_path)

                self.get_article(HABR_TITLE + p.get('href'), name)

                # выходим из директории статьи
                os.chdir('../')

    def main(self, url, dir):
        # создаем папку для статей
        self.create_dir(dir)
        os.chdir(dir)

        # создаем папку с именем автора
        self.dir_author = url.split('/')[5]
        self.create_dir(self.dir_author)
        os.chdir(self.dir_author)

        self.get_articles(url)

        self.parse_articles()

        os.chdir('../')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Скрипт для скачивания статей с https://habr.com/")
    parser.add_argument('-q', '--quiet', help="Quiet mode", action='store_true')
    parser.add_argument('-l', '--local-pictures',
                        help="Использовать абсолютный путь к изображениям в сохранённых файлах", action='store_true')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-u', help="Скачать статьи пользователя", type=str, dest='user_name_for_articles')
    group.add_argument('-f', help="Скачать закладки пользователя", type=str, dest='user_name_for_favorites')
    group.add_argument('-s', help="Скачать одиночную статью", type=str, dest='article_id')

    args = parser.parse_args()

    if args.user_name_for_articles:
        output_name = args.user_name_for_articles + "/posts/"
        output = DIR_ARCTICLE
    elif args.user_name_for_favorites:
        output_name = args.user_name_for_favorites + "/favorites/posts/"
        output = DIR_FAVORITES
    else:
        output_name = args.article_id

    habrSD = habrArticleSrcDownloader()
    try:
        if not args.article_id:
            habrSD.main("https://habr.com/ru/users/" + output_name, output)
        else:
            habrSD.get_article("https://habr.com/ru/post/" + output_name)
    except Exception as ex:
        print("[error]: Ошибка получения данных от :", output_name)
        print(ex)

# apt install libomp-dev
