import requests
import re
import csv
from bs4 import BeautifulSoup


def create_soup_object(url):
    r = requests.get(url)
    if r.ok:
        soup = BeautifulSoup(r.text, "html.parser")
    else:
        print("ERROR : Bad request !")
        soup = None
    return soup


def download_image_from_url(url, image_name):
    image = requests.get(url).content
    with open(image_name, "wb") as handler:
            handler.write(image)
            print(f"{image_name} downloaded !")


class Product:
    def __init__(self, url):
        self.url = url
        self.soup = create_soup_object(self.url)

    def __str__(self):
        return self.get_title()

    def get_url(self):
        return self.url

    def get_upc(self):
        return self.soup.td.text

    def get_title(self):
        return self.soup.h1.text

    def get_price_incl_tax(self):
        return self.soup.find_all("td")[3].text

    def get_price_excl_tax(self):
        return self.soup.find_all("td")[2].text

    def get_number_available(self):
        return self.soup.find_all("td")[5].text

    def get_category(self):
        return self.soup.find_all("a")[3].text

    def get_description(self):
        return self.soup.find_all("p")[3].text

    def get_review_rating(self):
        return self.soup.find("p", class_="star-rating").attrs["class"][1]

    def get_image_url(self):
        image_url = self.soup.find("img")["src"]
        website_url = "https://books.toscrape.com"
        return f"{website_url}{image_url[5:]}"

    def create_csv_file(self):
        filename = "book_" + re.sub("[\W_]+", "", self.get_title()).lower() + ".csv"
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(
                [
                    "Product page URL",
                    "UPC",
                    "Title",
                    "Price incl. tax",
                    "Price excl. tax",
                    "Number available",
                    "Product description",
                    "Category",
                    "Review rating",
                    "Image URL",
                ]
            )
            writer.writerow(
                [
                    self.get_url(),
                    self.get_upc(),
                    self.get_title(),
                    self.get_price_incl_tax(),
                    self.get_price_excl_tax(),
                    self.get_number_available(),
                    self.get_description(),
                    self.get_category(),
                    self.get_review_rating(),
                    self.get_image_url(),
                ]
            )
            print(f"CSV product file {filename} created !")
        return filename


class Category:
    def __init__(self, url):
        self.url = url
        self.soup = create_soup_object(self.url)

    def __str__(self):
        return self.get_name()

    def get_name(self):
        return self.soup.h1.text

    def get_books_url(self):
        books = []
        base_url = "https://books.toscrape.com/catalogue"
        # There's pagination if there are more than 20 books in a category
        page_number = 2
        # We'll scrape the first page and then go through the next ones
        while True:
            articles = self.soup.find_all("article", class_="product_pod")
            for article in articles:
                book_url = article.find("a").attrs["href"][8:]
                books.append(f"{base_url}{book_url}")
            if self.soup.find("li", class_="next"):
                next_page_url = self.url.replace(
                    "index.html", f"page-{page_number}.html"
                )
                self.soup = create_soup_object(next_page_url)
                page_number += 1
                continue
            else:
                break
        print(f"Number of books : {len(books)}")
        return books

    def create_csv_file(self):
        filename = f"category_{self.get_name()}.csv"
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            # First version of csv file with titles and urls
            # books = [ Product(url) for url in self.get_books_url()]
            # book_titles = [ book.get_title() for book in books ]
            # writer.writerow(book_titles)
            # writer.writerow(self.get_books_url())
            writer.writerow(self.get_books_url())
            print(f"{self.get_name()} category CSV file created.")
        return filename


class Website:
    def __init__(self, url):
        self.url = url
        self.soup = create_soup_object(self.url)

    def __str__(self):
        pass

    def get_categories(self):
        """
        Returns a tuple with ("name", "url") of each category
        """
        nav_menu = self.soup.find("ul", class_="nav-list")
        category_items = nav_menu.find_all("li")
        # categories = [
            # (category.find("a").text.strip(), category.find("a").get("href"))
            # for category in category_items
        # ]
        category_short_urls = [ category.find("a").get("href") for category in category_items ]
        category_urls = []
        for url in category_short_urls:
            category_urls.append(f"http://books.toscrape.com/{url}")
        # Remove 'Books' menu title
        category_urls.pop(0)
        return category_urls