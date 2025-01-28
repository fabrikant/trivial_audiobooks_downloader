from tg_sender import send_to_telegram
from opf import if_to_fi
from bs4 import BeautifulSoup
import json

def get_book_info(book_html, book_url,tg_key, tg_chat):
    book_info = {
        "url": book_url,
        # "id": "",
        "title": "_",
        "author": "_",
        "authors": [],
        "narrator": "",
        "narrators": [],
        "series": "",
        # "series_count": 0,
        "series_num": 0,
        "genres": [],
        "cover": "",
        # "tags": [],
        "description": "",
        # "isbn": "",
        "publishedYear": "",
        # "publishedDate": "",
        # "uuid": "",
    }

    site_url = "https://audiokniga.one"

    book_soup = BeautifulSoup(book_html, "html.parser")

    book_info["title"] = (
        book_soup.find("h1", {"class": "b_short-title"}).get_text().strip()
    )

    bs_about = book_soup.find("div", {"class": "fright"}).find("div", "ltext")

    bs_genre_list = bs_about.find("div", {"class": "icon_genre"}).find_all("a")
    for bs_genre in bs_genre_list:
        book_info["genres"].append(bs_genre.get_text().strip().lower())

    bs_serie = bs_about.find("div", {"class": "icon_serie"})
    if not bs_serie is None:
        book_info["series"] = bs_serie.find("a").get_text().strip()
        serie_text = bs_serie.get_text()
        if "#" in serie_text:
            book_info["series_num"] = serie_text.split("#")[-1].split(")")[0]

    book_info["author"] = if_to_fi(
        bs_about.find("div", {"class": "icon_author"}).get_text().strip()
    )
    book_info["authors"].append(book_info["author"])

    book_info["narrator"] = if_to_fi(
        bs_about.find("div", {"class": "icon_reader"}).get_text().strip()
    )
    book_info["narrators"].append(book_info["narrator"])

    bs_description = book_soup.find("div", {"class": "fullstory"})
    book_info["description"] = bs_description.get_text().strip()

    img_src = book_soup.find("img", {"class": "cover"})["src"]
    book_info["cover"] = site_url + img_src

    book_info["publishedYear"] = (
        bs_about.find("div", {"class": "icon_calendar"}).get_text().strip()
    )

    mp3_list = book_html.split("DOMContentLoaded")[-1].split("json")[1]
    mp3_list = "[{" + mp3_list.split("[{")[1].split("}]")[0] + "}]"
    files = json.loads(mp3_list)

    return book_info, files
