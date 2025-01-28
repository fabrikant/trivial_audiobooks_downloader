from tg_sender import send_to_telegram
from opf import if_to_fi
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
import json


def get_headers():
    ua = UserAgent()
    agent = ua.firefox
    return {"User-Agent": agent}


def get_mp3_query():
    return """query getBook($bookAlias: String, $authorAliasName: String) {
    book(aliasName: $bookAlias, authorAliasName: $authorAliasName) {
        id
        chapters {
        collection {
            id
            name
            duration
            fileUrl
            __typename
        }
        __typename
        }
        __typename
    }
    }"""


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
    site_url = "https://yakniga.org"
    book_soup = BeautifulSoup(book_html, "html.parser")

    author = book_soup.find("span", {"class": "book__author"}).get_text().strip()
    book_info["author"] = if_to_fi(author)
    book_info["authors"].append(book_info["author"])

    book_info["title"] = book_soup.find("h1").get_text()
    # Убираем автора из названия книги
    book_info["title"] = book_info["title"].replace(f"{author}", "").strip()
    if book_info["title"].startswith("-"):
        book_info["title"] = book_info["title"][1:].strip()

    book_info["narrator"] = if_to_fi(
        book_soup.find("span", {"class": "book__reader"}).get_text().strip()
    )
    book_info["narrators"].append(book_info["narrator"])
    book_info["description"] = (
        book_soup.find("div", {"class": "page__description"}).get_text().strip()
    )

    img_src = (
        book_soup.find("div", {"class": "book__image"})
        .find("img")["src"]
        .split(site_url)
    )
    book_info["cover"] = f"{site_url}{img_src[-1]}"

    genres_list = book_soup.find("div", {"class": "book__genre"}).find_all("a")
    for genre in genres_list:
        book_info["genres"].append(genre.get_text().strip())

    # Загрузка файлов
    book_url_array = book_url.split("/")
    data = {
        "operationName": "getBook",
        "variables": {
            "authorAliasName": book_url_array[-2],
            "bookAlias": book_url_array[-1],
        },
        "query": get_mp3_query(),
    }

    files = []
    res = requests.post(f"{site_url}/graphql", headers=get_headers(), json=data)
    if res.ok:
        chapters = json.loads(res.text)["data"]["book"]["chapters"]["collection"]
        for chapter in chapters:
            files.append(
                {"url": site_url + chapter["fileUrl"], "title": chapter["name"]}
            )

    return book_info, files
