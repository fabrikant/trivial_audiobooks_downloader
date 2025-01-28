from tg_sender import send_to_telegram
from opf import if_to_fi
from bs4 import BeautifulSoup
import json
import logging

logger = logging.getLogger(__name__)

def get_book_info(book_html, book_url, tg_key, tg_chat):

    book_info = {
        "url": book_url,
        # "id": "",
        "title": "_",
        "author": "_",
        "authors": [],
        "narrator": "",
        "narrators": [],
        # "series": "",
        # "series_count": 0,
        # "series_num": 0,
        "genres": [],
        "cover": "",
        # "tags": [],
        "description": "",
        # "isbn": "",
        # "publishedYear": "",
        # "publishedDate": "",
        # "uuid": "",
    }

    
    book_soup = BeautifulSoup(book_html, "html.parser")
    page_title = book_soup.find("div", {"class": "page_title"})

    book_info["title"] = (
        page_title.find("span", {"itemprop": "name"}).get_text().strip()
    )

    author_soup = page_title.find("span", {"itemprop": "author"})
    if author_soup is None:
        author = "Автор неизвестен"
    else:
        author = page_title.find("span", {"itemprop": "author"}).get_text().strip()

    book_info["author"] = if_to_fi(author)
    book_info["authors"].append(book_info["author"])

    narrator_pattern = "читает"
    bs_array = page_title.find_all("span", {"class": "book_title_elem"})

    if not bs_array is None:
        for bs_narrator in bs_array:
            narrator = bs_narrator.get_text().strip()
            if narrator_pattern in narrator:
                narrator = narrator.replace(narrator_pattern, "").strip()
                book_info["narrator"] = if_to_fi(narrator)
                book_info["narrators"].append(book_info["narrator"])
                break

    bs_description = book_soup.find("div", {"class": "book_description"})
    if not bs_description is None:
        book_info["description"] = bs_description.get_text().strip()

    img_src = book_soup.find("div", {"class": "book_cover"}).find("img")["src"]
    book_info["cover"] = img_src

    bs_genres = book_soup.find("div", {"class": "book_genre_pretitle"})
    genres_list = []
    if not bs_genres is None:
        genres_list = bs_genres.get_text().split(",")
    for genre in genres_list:
        book_info["genres"].append(genre.strip().lower())

    files_text = "[{" + book_html.split("BookPlayer")[-1].split("[{")[1].strip()
    if files_text.endswith(","):
        files_text = files_text[:-1]

    files_json = None
    try:
        files_json = json.loads(files_text)
    except:
        msg = f"Не удалось получить список файлов для загрузки."
        logger.error(msg)
        send_to_telegram(msg, tg_key, tg_chat)
        exit(0)
        
    return book_info, files_json
