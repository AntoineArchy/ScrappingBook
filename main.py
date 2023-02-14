from dataclasses import dataclass, field
import os
from typing import List, Optional
import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime

INSTANT_SAVE = True
SAVE_IMG = True
INVALID_CHAR = ["<", ">", ":", "\"", "/", "\\", "|", "?", "*"]
CSV_EN_TETE = ["product_page_url", "universal_product_code (upc)", "title",
               "price_including_tax", "price_excluding_tax", "number_available",
               "product_description", "category", "review_rating",
               "image_url"]

RATTING_MAP = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}

LibraryURL = {
    "BookToScrap": "http://books.toscrape.com/"
}


def get_new_path(path: str) -> str:
    """
    Iterate path name adding "(i+1)" at the end of the path util a not existing one is found
    """
    ind = 0
    while os.path.exists(f"{path}({ind})"):
        ind += 1
    return f"{path}({ind})"


def shorten_relative_url(url: str) -> str:
    """
    Shorten a relative path by removing the starting "../[...]"
    """
    url_parts = url.split("/")
    ind = 0
    for part in url_parts:
        if part == "..":
            ind += 3  # 2 for the 2 char of "..", +1 for the "/" we've split
            continue
        break
    return url[ind:]


def clear_file_name(file_name: str) -> str:
    """
    Check if any char on the file name is an invalid char, return a compatible file name
    """
    for char in file_name:
        if char not in INVALID_CHAR:
            continue
        file_name = file_name.replace(char, "")
    return file_name


def write_img_to_disk(url: str, directory_path: str, file_name: str) -> None:
    """
    Take an image URL, a directory path and a filename (no extension) and write the image as jpg.
    """
    full_path = os.path.join(directory_path, file_name)
    if os.path.exists(f"{full_path}.jpg"):
        full_path = get_new_path(full_path)

    with open(f"{full_path}.jpg", 'wb') as f:
        f.write(requests.get(url, timeout=20).content)


def write_to_csv(directory_path: str, file_name: str, data: List) -> None:
    """
    Take a directory path, a filename and processed data, write them to a csv file with the given "en
    tete"/"header"
    """
    writing_path = os.path.join(directory_path, file_name)
    if os.path.exists(writing_path):
        writing_path = get_new_path(writing_path)

    with open(writing_path, 'w', encoding="utf-8", newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow(CSV_EN_TETE)
        for book in data:
            writer.writerow(book)


@dataclass
class Book:
    """
    Basic representation of a book object
    """
    url: str
    upc: int
    book_title: str
    price_inc_tax: float
    prince_exc_tax: float
    available_unit: int
    description: str
    category: str
    ratting: int
    img_url: str

    def get_save(self) -> List:
        return [self.url, self.upc, self.book_title,
                self.price_inc_tax, self.prince_exc_tax, self.available_unit,
                self.description, self.category, self.ratting, self.img_url]


class BTSFactory:
    """
    Factory are the main interface between the scrapper and a particular website.
    They start from a URL and return standardized data ready to use.

    Since all website are build differently, each factory must be fine-tuned for one particular competitor.
    This one is a proof of concept for "http://books.toscrape.com/"
    """

    def __init__(self, working_path: str, library_name: str) -> None:
        save_path = os.path.join(working_path, library_name)

        if os.path.exists(save_path):
            save_path = get_new_path(save_path)

        os.mkdir(save_path)
        os.mkdir(os.path.join(save_path, "book_cover"))

        self.library_name = library_name
        self.save_path = save_path
        self.cover_save_path = os.path.join(save_path, "book_cover")

    def get_book_obj_from_book_url(self, book_url: str) -> Book:
        """
        Transform a URL into a Book object,
        component assignation is fine-tuned for BookToScrap.com
        """

        page = requests.get(book_url, timeout=20)
        soup = BeautifulSoup(page.content, 'html.parser')

        book_title = soup.find("h1").string

        book_data = soup.find_all("td")

        upc = book_data[0].string

        # We remove the devise sign ("£")
        price_inc_tax = float(book_data[2].text[1:])
        price_exc_tax = float(book_data[3].text[1:])

        # And clear the availability to a number
        available = book_data[5].string.split("(")[1].replace(" available)", "")

        if desc_title := soup.find("div", id="product_description"):
            description = desc_title.find_next_sibling().text

        else:
            description = "No description data"

        book_category = soup.find_all("a")[3].string

        first_star = soup.find("i", class_="icon-star")
        star_number = first_star.parent.get('class')[-1]
        # We transform from text to int, default to -1 if no ratting is found
        ratting = RATTING_MAP.get(star_number.lower(), -1)

        img_url = soup.find("img")
        img_relative_path = img_url['src']
        img_full_path = f"{LibraryURL[self.library_name]}{shorten_relative_url(img_relative_path)}"

        return Book(url=book_url, upc=upc, book_title=book_title,
                    price_inc_tax=price_inc_tax, prince_exc_tax=price_exc_tax, available_unit=available,
                    description=description, category=book_category, ratting=ratting, img_url=img_full_path)

    def get_category_url_from_library_url(self, url: str) -> dict[str: str]:
        """
        Transform an Index page URL into a dict of {Category_Name: Category URL}
        component assignation is fine-tuned for BookToScrap.com
        """
        page = requests.get(url, timeout=20)
        soup = BeautifulSoup(page.content, "html.parser")

        category = soup.find('ul', class_="nav nav-list").find_all('a')

        # The first elt of "category" is the index page, we don't want it to be mapped so [1:]:
        category_relative_url = [elt.get("href") for elt in category[1:]]

        # We clean up the "_{index}" that bookToScrap use as the end of category names, so the ".split("_")[0]"
        # We then turn it into a dict : {category_name : category_url}.
        category_data = {
            cat.split("/")[-2].split("_")[0]: f"{LibraryURL[self.library_name]}/{cat}"
            for cat in category_relative_url
        }

        return category_data

    def get_books_url_from_category_url(self, category_url: str) -> List[str]:
        """
        Transform a category URL into a list of books URL from this category. If a next page is found the
        URL are added to the list;
        component assignation is fine-tuned for BookToScrap.com
        """

        print(f"Scrapping : {category_url}")
        page = requests.get(category_url, timeout=20)
        soup = BeautifulSoup(page.content, "html.parser")

        product_list = list()
        for product in soup.find_all("div", class_="image_container"):
            thumbnail = product.find("a")
            link = thumbnail.get("href")
            product_list.append(f"{LibraryURL[self.library_name]}catalogue/{shorten_relative_url(link)}")

        if has_second_page := soup.find("li", class_="next"):
            next_url_end = has_second_page.a.get("href")
            actual_url_end = category_url.split("/")[-1]
            next_url = category_url.replace(actual_url_end, next_url_end)
            product_list.extend(self.get_books_url_from_category_url(next_url))
        return product_list

    def get_book_list_from_category_url(self, category_url: str) -> List[Book]:
        """
        Transform a category url into a list of scrapped book object
        """
        books_url = self.get_books_url_from_category_url(category_url)
        scrapped_books = [self.get_book_obj_from_book_url(url) for url in books_url]
        return scrapped_books


LibraryFactory = {
    "BookToScrap": BTSFactory
}


@dataclass
class Category:
    """
    Used to order books from online library,
    Mainly a container for books but can be easily extended for any purpose.

    Can be saved to disk.
    """

    url: str
    category_name: str
    books: Optional[List] = field(default_factory=list)

    def register_book_obj(self, book: Book) -> None:
        """
        Add a new book to the category book list
        """
        if book in self.books:
            return
        self.books.append(book)

    def register_book_from_factory(self, factory: BTSFactory) -> None:
        """
        Send category link to the assigned factory and register the newly made book object into this category.
        """
        for book in factory.get_book_list_from_category_url(self.url):
            self.register_book_obj(book)

    def get_category_data(self) -> List:
        """
         Return a list of all book_data in the category
         """
        return [book.get_save() for book in self.books]

    def write_category_to_csv(self, save_path: str, save_img: bool = False) -> None:
        """
        Get the save data of the full category and write it as CSV at the specified save_path, under the
        category name.
        Image save can be toggled on or off
        """
        to_save_data = self.get_category_data()

        write_to_csv(directory_path=save_path, file_name=f"{self.category_name}.csv", data=to_save_data)

        if not save_img:
            return

        # The factory is in charge of creating the "book cover" but we have to make a #CategoryName directory
        if not os.path.exists(os.path.join(save_path, "book_cover", self.category_name)):
            os.mkdir(os.path.join(save_path, "book_cover", self.category_name))

        for book_data in to_save_data:
            write_img_to_disk(url=book_data[-1], directory_path=os.path.join(save_path, "book_cover", self.category_name),
                              file_name=clear_file_name(book_data[2]))


@dataclass
class OnlineLibrary:
    """
    Represent a vendor website, books are stored in their appropriate category,
    Mainly a container for category but can be easily extended for any purpose.

    Can be saved to disk.
    """
    library_name: str
    factory: callable
    categories: Optional[List] = field(default_factory=list)

    def register_category_obj(self, category: Category) -> None:
        """
        Add a new category to the library
        """
        if category in self.categories:
            return
        self.categories.append(category)

    def register_category_from_factory(self, instant_save: bool = False) -> None:
        """
        Find every category from this website URL, transform them in Category object and feed them the books data
        """

        for category_name, category_url in self.factory.get_category_url_from_library_url(LibraryURL[self.library_name]).items():
            self.register_category_obj(Category(category_url, category_name))
            self.categories[-1].register_book_from_factory(self.factory)

            if instant_save:
                self.categories[-1].write_category_to_csv(self.factory.save_path, save_img=SAVE_IMG)

    def save_library_to_disk(self) -> None:
        """
        Save the library to disk by writing every category into his own csv files.
        """
        for category in self.categories:
            category.write_category_to_csv(self.factory.save_path, save_img=True)


def scrap(save_path):
    start_time = datetime.now()
    print(f"Starting scrapping, save_path : {save_path}")
    for online_library_name, online_library_URL, in LibraryURL.items():

        factory = LibraryFactory.get(online_library_name, False)
        if not factory:
            print(f"No factory known for library : {online_library_name}.")
            continue

        print(f"Creating library : {online_library_name}")
        library = OnlineLibrary(online_library_name, factory(save_path, online_library_name))
        library.register_category_from_factory(instant_save=INSTANT_SAVE)

    print(f"Total exec time : {datetime.now() - start_time}")


if __name__ == "__main__":
    scrap(os.getcwd())
