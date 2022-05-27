#!/usr/bin/python3
#-*- coding: utf-8 -*-

import os
import sys
import pymp
import errno
import getopt
import requests
import markdownify
import multiprocessing

from bs4 import BeautifulSoup
from urllib.parse import urlparse

DIR_ARCTICLE = 'article'
DIR_FAVORITES = 'favorites'
DIR_PICTURE = 'picture'
DIR_SINGLES = 'singles'
HABR_TITLE = "https://habr.com"

def callback(el):
    try :
        soup = BeautifulSoup(str(el), features='html.parser')
        return soup.find('code')['class'][0]
    except :
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
                print(f"[info]: Директория: {dir} создана")
            except OSError as e:
                print(f"[error]: Ошибка создания директории: {dir}")

    def save_md(self, name: str, text: str):
        with open(name + ".md", "w") as fd:
            fd.write(f'# {name}\n')
            fd.write(text)

    def save_html(self, name: str, text: str):
        with open(name + ".html", "w") as fd:
            fd.write(f'<h1>{name}</h1>')
            fd.write(text)

    def save_comments(self, name: str, text: str):
        lst = text.split('\n')
        lst.reverse()

        with open(name + "_comments.md", "w") as fd:
            fd.write("\n".join(lst))
    
    def get_comments(self, url_soup):        
        comments = url_soup.findAll('link', {'type': 'application/rss+xml'})
        
        for c in comments :
            try:
                r = requests.get(c.get('href'))
            except requests.exceptions.RequestException as e:
                print("[error]: Ошибка получения статьи: ", c.get('href'))
                return
            
            url_soup = BeautifulSoup(r.text, 'lxml')
            
            return markdownify.markdownify(str(url_soup), heading_style="ATX", code_language_callback=callback)
    
    def get_article(self, url, name = None):
        try:
            r = requests.get(url)
        except requests.exceptions.RequestException as e:
            print("[error]: Ошибка получения статьи: ", url)
            return
        
        url_soup = BeautifulSoup(r.text, 'lxml')
        comment = self.get_comments(url_soup)
        
        posts = url_soup.findAll('div', {'class': 'tm-article-body'})
        pictures = url_soup.findAll('img')
        
        # одиночное скачивание статьи
        if name == None :
            
            habrSD.create_dir(DIR_SINGLES)
            os.chdir(DIR_SINGLES)
            
            name = self.dir_cor_name(url_soup.find('title').string)
            
            self.create_dir(name)
            os.chdir(name)
        
        for p in posts :
            
            h = markdownify.markdownify(str(p), heading_style="ATX", code_language_callback=callback)
            
            _p = str(p).replace("<pre><code class=", "<source lang=").replace("</code></pre>", "</source>")
            
            # создаем дирректорию под картинки
            self.create_dir(DIR_PICTURE)
            os.chdir(DIR_PICTURE)
            self.save_pictures(pictures)
                
            os.chdir('../')
            
            self.save_html(name, _p)
            self.save_md(name, h)
            self.save_comments(name, str(comment))
            
            print(f"[info]: Статья: {name} сохранена")

    def save_pictures(self, pictures):
        for link in pictures:
            if link.get('data-src'):
                try:
                    img_data = requests.get(link.get('data-src')).content

                    a = urlparse(link.get('data-src'))

                    with open(os.path.basename(a.path), 'wb') as handler:
                        handler.write(img_data)
                except requests.exceptions.RequestException as e:
                    print("[error]: Ошибка получения картинки: ", link.get('data-src'))

    def get_articles(self, url):
        
        page_number = 1
        
        while True:
        
            try:
                r = requests.get(url + "page" + str(page_number))
            except requests.exceptions.RequestException as e:
                print("[error]: Ошибка получения статей: ", url)
                return
        
            url_soup = BeautifulSoup(r.text, 'lxml')
        
            posts = url_soup.findAll('a', {'class': 'tm-article-snippet__title-link'})

            if (len(posts) == 0) :
                break

            self.posts += posts
            page_number = page_number + 1
    
    def parse_articles(self):
        print(f"[info]: Будет загружено: {len(self.posts)} статей.")
        
        with pymp.Parallel(multiprocessing.cpu_count()) as pmp:
            #for p in self.posts :
            for i in pmp.range(0, len(self.posts)):
                p = self.posts[i]
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

    def help(self):
        print('./main.py [-h] [-uf] user_name')
        sys.exit()

if __name__ == '__main__':
    habrSD = habrArticleSrcDownloader()
    
    try:
        opts, args = getopt.getopt(sys.argv, "h")
    except getopt.GetoptError:
        habrSD.help()
    
    if len(args) == 1 or args[1] == '-h' :
        habrSD.help()
    elif args[1] == '-u' :
        try :
            habrSD.main("https://habr.com/ru/users/" + args[2] + "/posts/", DIR_ARCTICLE)
        except Exception as ex:
            print("[error]: Ошибка получения данных от :", args[2])
            print(ex)
    elif args[1] == '-f' :
        try :
            habrSD.main("https://habr.com/ru/users/" + args[2] + "/favorites/posts/", DIR_FAVORITES)
        except Exception as ex:
            print("[error]: Ошибка получения данных от :", args[2])
            print(ex)
    elif args[1] == '-s' :
        try :            
            habrSD.get_article("https://habr.com/ru/post/" + args[2])
        except Exception as ex:
            print("[error]: Ошибка получения данных от :", args[2])
            print(ex)

# apt install libomp-dev
