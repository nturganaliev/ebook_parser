# Загрузчик электронных книг.

Данный скрипт скачивает книги с сайта [tutulu.org](https://tutulu.org)


### Требования к окружению

Операционная система (ОС): `Ubuntu 22.04`, должен работать и в других ОС без проблем.</br>
Версия интерпретатора: `Python 3.10.6`, думаю поддерживается с большинством версий Python3.</br>
Версия пакет менеджера: `pip3 22.3.1`</br>


### Как установить

- Нужно скачать проект на локальную машину следующей командой:

```bash
git git@github.com:nturganaliev/ebook_parser.git

```

Python3 должен быть уже установлен.</br>
Затем используйте `pip` (или `pip3`, м.б. конфликт с Python2)
для установки зависимостей наберите команду в терминале:
```bash
pip install -r requirements.txt
```

### Использование

Если из терминала (командной строки) наберете следующую команду,
скачает по умолчанию книги с id=1 по id=10.

```bash

python3 tululu.py

```


Также можно скачать другие книги указав нужный диапазон:

```bash

python3 tululu.py 10 15

```


## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
