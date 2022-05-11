#!/usr/bin/python3
#-*- coding: utf-8 -*-

import os
import sys
import errno
import getopt
import requests
import markdownify

from bs4 import BeautifulSoup
from urllib.parse import urlparse

DIR_ARCTICLE = 'article'
DIR_PICTURE = 'picture'
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
        self.posts = None

    def callback(self, el):
        if (el.has_attr('class')) :
            #print(el['class'][0])
            return el['class'][0]
        
        return None

    def create_dir(self, dir):        
        if not os.path.exists(dir):
            try:
                os.makedirs(dir)
                print("[info]: Директория: " + dir + " создана")
            except OSError as e:
                print("[error]: Ошибка создания директории: ", dir)

    def save_md(self, name, str):
        fd = open(name + ".md", "w")
        fd.write(str)
        fd.close()
        
    def save_html(self, name, str):
        fd = open(name + ".html", "w")
        fd.write(str)
        fd.close()

    def get_article(self, name, url):
        try:
            r = requests.get(url)
        except requests.exceptions.RequestException as e:
            print("[error]: Ошибка получения статьи: ", url)
            return
        
        url_soup = BeautifulSoup(r.text, 'lxml')
        
        posts = url_soup.findAll('div', {'class': 'tm-article-body'})
        pictures = url_soup.findAll('img')
        
        for p in posts :
            
            h = markdownify.markdownify(str(p), heading_style="ATX", code_language_callback=callback)
            
            _p = str(p).replace("<pre><code class=", "<source lang=").replace("</code></pre>", "</source>")
            
            os.chdir(DIR_PICTURE)
            for link in pictures:

                if (link.get('data-src')) :
                    try :
                        img_data = requests.get(link.get('data-src')).content
                        
                        a = urlparse(link.get('data-src'))
                        os.path.basename(a.path)
                
                        with open(os.path.basename(a.path), 'wb') as handler:
                            handler.write(img_data)
                    except requests.exceptions.RequestException as e:
                        print("[error]: Ошибка получения картинки: ", link.get('data-src'))
                
            os.chdir('../')
            
            self.save_html(name, _p)
            self.save_md(name, h)
            
            print("[info]: Статья: " + name + " сохранена")

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
            
            if (self.posts != None) :
                self.posts = self.posts + posts
            else:
                self.posts = posts
                
            page_number = page_number + 1
    
    def parse_articles(self):
        post_number = len(self.posts)

        for p in self.posts :
            print("[info]: Скачивается:", p.text)
            name = p.text.replace("/", " ")
            dir_path = str(post_number) + " " + name
            
            # создаем директории с названиями статей
            self.create_dir(dir_path)
            # заходим в директорию статьи
            os.chdir(dir_path)
            
            # создаем дирректорию под картинки
            self.create_dir(DIR_PICTURE)
            
            self.get_article(name, HABR_TITLE + p.get('href'))
            
            # выходим из директории статьи
            os.chdir('../')
            
            post_number = post_number - 1
            
    def main(self, url):
        # создаем папку для статей
        self.create_dir(DIR_ARCTICLE)
        os.chdir(DIR_ARCTICLE)
        
        # создаем папку с именем автора
        self.dir_author = url.split('/')[5]
        self.create_dir(self.dir_author)
        os.chdir(self.dir_author)
        
        self.get_articles(url)
        
        self.parse_articles()
        
        os.chdir('../')

    def help(self):
        print('./main.py [-h] [url]')
        sys.exit()

if __name__ == '__main__':
    habrSD = habrArticleSrcDownloader()
    
    try:
        opts, args = getopt.getopt(sys.argv, "h")
    except getopt.GetoptError:
        habrSD.help()
    
    if len(args) == 1 :
        habrSD.help()
    else :
        if args[1] == '-h':
            habrSD.help()
        else :
            try :
                habrSD.main("https://habr.com/ru/users/" + args[1] + "/posts/")
            except :
                print("[error]: Ошибка получения данных от :", args[1])

# python3-lxml
