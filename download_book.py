import logging
import requests
import shutil
from pathvalidate import sanitize_filename
from pathlib import Path
import sys
import subprocess
from tg_sender import send_to_telegram
from opf import book_info_to_xml
from common_arguments import create_common_args, parse_args
from fake_useragent import UserAgent


logger = logging.getLogger(__name__)


def get_headers():
    ua = UserAgent()
    agent = ua.firefox
    return {"User-Agent": agent}


def download_media(url, path, filename, file_number="", tg_key="", tg_chat=""):
    url_string = url
    logger.debug(f"Начало загрузки файла: {url_string}")
    full_filename = Path(path) / sanitize_filename(f"{filename}.mp3")
    if file_number != "":
        full_filename = Path(path) / sanitize_filename(
            f"{file_number:03d} {filename}.mp3"
        )
    res = requests.get(url_string, stream=True, headers=get_headers())
    if res.ok:
        with open(full_filename, "wb") as f:
            shutil.copyfileobj(res.raw, f)
        logger.warning(
            f"Успешно загружен файл: {url_string} и сохранен как {full_filename}"
        )
    else:
        msg = f"Ошибка: {res.status_code} при загрузке файла: {url_string}. Загрузка прервана."
        logger.error(msg)
        send_to_telegram(msg, tg_key, tg_chat)
        exit(0)


def download_book(
    book_url, output_folder, tg_key, tg_chat, load_cover, create_metadata
):
    if "https://audiokniga.one" in book_url:
        from websites.audiokniga_one import get_book_info
    elif "https://knigavuhe.org" in book_url:
        from websites.knigavuhe_org import get_book_info
    elif "https://kot-baun.ru" in book_url:
        from websites.kot_baun_ru import get_book_info
    elif "https://yakniga.org" in book_url:
        from websites.yakniga_org import get_book_info
    else:
        msg = f"Попытка загрузить книгу с неизвестного сайта: {book_url}"
        logger.error(msg)
        send_to_telegram(msg, tg_key, tg_chat)
        exit(0)

    msg = f"Начало загрузки книги с url: {book_url}"
    logger.warning(msg)
    send_to_telegram(msg, tg_key, tg_chat)

    res = requests.get(book_url, headers=get_headers())
    if not res.ok:
        msg = f"Ошибка {res.status_code} при загрузке страницы {book_url}.  Загрузка прервана."
        logger.error(msg)
        send_to_telegram(msg, tg_key, tg_chat)
        exit(0)

    logger.debug("Начало получения информации о книге")
    book_info, chapters = get_book_info(res.text, book_url, tg_key, tg_chat)
    logger.debug("Получена информация о книге")

    logger.debug("Создание каталога загрузки")
    book_and_reader = book_info["title"]
    if book_info["narrator"] != "":
        book_and_reader = f'{book_and_reader} - читает {book_info["narrator"]}'
    book_folder = (
        Path(output_folder)
        / sanitize_filename(book_info["author"])
        / sanitize_filename(book_and_reader)
    )
    Path(book_folder).mkdir(exist_ok=True, parents=True)
    logger.debug(f"Установлен каталог для загрузки: {book_folder}")

    # Загрузка обложки
    if load_cover:
        cover_filename = Path(book_folder) / "cover.jpg"
        logger.debug(f"Начало загрузки файла обложки с url: {book_info['cover']}")
        res = requests.get(book_info["cover"], stream=True, headers=get_headers())
        if res.ok:
            res.raw.decode_content = True
            with open(cover_filename, "wb") as f:
                shutil.copyfileobj(res.raw, f)
            logger.debug(f"Обложка сохранена в файл: {cover_filename}")
        else:
            msg = f"Ошибка {res.status_code} при загрузке файла обложки {book_info['cover']}."
            logger.error(msg)
    else:
        logger.debug("Загрузка обложки не требуется")

    # Создание файла метаданных
    if create_metadata:
        filename = Path(book_folder) / "metadata.opf"
        logger.debug(f"Начало создания файла {filename} с метаданными книги")
        xml = book_info_to_xml(book_info)
        Path(filename).write_text(xml)
        logger.debug(f"Создан файл {filename} с метаданными книги")
    else:
        logger.debug("Создание файла метаданных не требуется")

    # Загрузка файлов
    logger.debug(f"Начало загрузки файлов книги")
    for chapter in chapters:
        download_media(
            chapter["url"], book_folder, chapter["title"], "", tg_key, tg_chat
        )

    msg = (
        f"Окончание загрузки книги:\n{book_info['title']}\nавтор: {book_info['author']}"
    )
    logger.warning(msg)
    send_to_telegram(msg, tg_key, tg_chat)

    # Установка прав на каталог
    if sys.platform != "win32":
        subprocess.Popen(f"chmod -R ugo+wrX '{str(book_folder)}'", shell=True)


if __name__ == "__main__":

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.ERROR,
    )
    # Создаем общие аргументы для всех качалок
    parser = create_common_args("Загрузчик аудиокниг")
    args = parse_args(parser, logger)
    logger.info(args)

    download_book(
        args.url,
        args.output,
        args.telegram_api,
        args.telegram_chatid,
        args.cover,
        args.metadata,
    )
