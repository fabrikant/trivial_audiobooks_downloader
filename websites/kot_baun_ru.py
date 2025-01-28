from tg_sender import send_to_telegram
from opf import if_to_fi
from bs4 import BeautifulSoup


def get_book_info(book_html, book_url, tg_key, tg_chat):

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
        # "publishedYear": "",
        # "publishedDate": "",
        # "uuid": "",
    }

    site_url = "https://kot-baun.ru"
    book_soup = BeautifulSoup(book_html, "html.parser")

    about_keys = {
        "Автор": "author",
        "Озвучка": "narrator",
        "Категория": "genres",
        "Серия": "series",
    }
    about_list = book_soup.find("ul", {"class": "short-list"}).find_all("li")
    for about_item in about_list:
        text_list = about_item.get_text().split(":")
        if text_list[0] in about_keys.keys():
            if about_keys[text_list[0]] == "genres":
                for genre in text_list[1].split("/"):
                    book_info["genres"].append(genre.strip().lower())
            elif about_keys[text_list[0]] == "series":
                series_list = text_list[1].split("/")
                book_info["series"] = series_list[0].strip()
                num = series_list[-1].split(" ")[-1]
                try:
                    book_info["series_num"] = int(num)
                except:
                    pass
            else:
                book_info[about_keys[text_list[0]]] = text_list[1].strip()

    title = book_soup.find("h1", {"class": "short-title"}).get_text()
    book_info["title"] = title.split("/")[0].strip()

    book_info["author"] = if_to_fi(book_info["author"])
    book_info["authors"].append(book_info["author"])

    book_info["narrator"] = if_to_fi(book_info["narrator"])
    book_info["narrators"].append(book_info["narrator"])

    bs_description = book_soup.find("div", {"class": "full-text"})
    book_info["description"] = bs_description.get_text().strip()

    img_src = book_soup.find("div", {"class": "fimg"}).find("img")["src"]
    book_info["cover"] = site_url + img_src

    files = []
    bs_files = book_soup.find("ul", {"data-preload": "metadata"}).find_all("li")

    for bs_file in bs_files:
        files.append({"url": bs_file["data-url"], "title": bs_file["data-title"]})

    return book_info, files
