# habrArticleSrcDownloader

Скрипт python3 для скачивания исходников статей с [habr](https://habr.com/)  
Тестировал на **python 3.6.9**, под **Linux Mint 19.3**.

## Как использовать:

### Установка:
```bash
apt-get install python3-lxml libomp-dev
pip3 install -r requirements.txt
```

### Использование:
```
usage: main.py [-h] (-u USER_NAME_FOR_ARTICLES | -f USER_NAME_FOR_FAVORITES | -s ARTICLE_ID)

Скрипт для скачивания статей с https://habr.com/

options:
  -h, --help            show this help message and exit
  -u USER_NAME_FOR_ARTICLES
                        Скачать статьи пользователя
  -f USER_NAME_FOR_FAVORITES
                        Скачать закладки пользователя
  -s ARTICLE_ID         Скачать одиночную статью
```

Например:

```bash
./src/main.py -u jessy_james
```
```bash
./src/main.py -f jessy_james
```
```bash
./src/main.py -s 665634
```

Взять имя пользователя можно из ссылки профиля

<img src="https://habrastorage.org/webt/4e/ur/ml/4eurmlni9b4f15fuqpuz4wrolmq.png" />


Если все было сделано успешно, то Вы увидите примерно следующее:
```bash
./src/main.py -u jessy_james
[info]: Скачивается: C/C++ из Python (ctypes) на Android
[info]: Директория: 16 C C++ из Python (ctypes) на Android создана
[info]: Директория: picture создана
[info]: Статья: C C++ из Python (ctypes) на Android сохранена
[info]: Скачивается: Своя docking station для ноутбука
[info]: Директория: 15 Своя docking station для ноутбука создана
[info]: Директория: picture создана
[info]: Статья: Своя docking station для ноутбука сохранена
[info]: Скачивается: Tango Controls hdbpp-docker
[info]: Директория: 14 Tango Controls hdbpp-docker создана
[info]: Директория: picture создана

...

[info]: Скачивается: Игрушка ГАЗ-66 на пульте управления. Часть 2
[info]: Директория: 2 Игрушка ГАЗ-66 на пульте управления. Часть 2 создана
[info]: Директория: picture создана
[info]: Статья: Игрушка ГАЗ-66 на пульте управления. Часть 2 сохранена
[info]: Скачивается: Игрушка ГАЗ-66 на пульте управления. Часть 1
[info]: Директория: 1 Игрушка ГАЗ-66 на пульте управления. Часть 1 создана
[info]: Директория: picture создана
[info]: Статья: Игрушка ГАЗ-66 на пульте управления. Часть 1 сохранена

```
