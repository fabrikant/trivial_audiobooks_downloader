# trivial_audiobooks_downloader
Загружает аудиокниги с сайтов
1. [Audiokniga.One](https://audiokniga.one/)
1. [Книгавухе](https://knigavuhe.org/)
1. [Кот Баюн.Ру](https://kot-baun.ru/)
1. [yakniga.org](https://yakniga.org/)

Скрипт может использоваться самостоятельно, но предназначен для работы с телеграм ботом [tg-combine](https://github.com/fabrikant/tg-combine)

# Требования
1. Операционная система **Linux** тестировалось на ubuntu 24.04. На **Windows** должно работать, но не тестировалось.
1. [python3](https://www.python.org/) и venv. Чем новее, тем лучше. Тестировалось на 3.12.

# Установка
Скачиваем любым способом исходный код. Например:  
```bash
git clone https://github.com/fabrikant/audioknigaone_downloader.git
```
Переходим в каталог с исходным кодом и выполняем команду  
**Linux:**
```bash
./install.sh
```
**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
deactivate
```
На Windows также необходимо открыть файл install.sh и скачать по ссылкам дополнительные модули (то, что написано после wget).

# Использование на Linux и Windows
**Linux**

Выполнить скрипт **download-book.sh** с соответствующими параметрами
При запуске будет автоматически активировано виртуальное окружение, вызван скрипт python, а по окончанию работы деактивировано виртуальное окружение. Пример:
```bash
./download-book.sh --help
```

>**ВАЖНО!!!**
>
>**Для получения справки по доступным ключам, скрипт можно вызвать с параметром -h или --help.**

**Windows**

Перед запуском скрипта необходимо активировать виртуальное окружение командой:
```
venv\Scripts\activate
```
Далее скрипт вызывается командой аналогичной Linux, но вместо файла *sh* запускается соответствующий python файл. Например:
```
python3 download_book.py --help
```

# Использование
1. Пример загрузки книги:

    ```bash
    ./download-book.sh --output {/tmp/audiobooks} --url {https://audiokniga.one/16968-zemlja-zakata.html}
    ``` 
    >*Значения в фигурных скобках нужно заменить на свои.*
