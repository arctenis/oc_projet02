import scrape


if __name__ == "__main__":
    url = "https://books.toscrape.com"
    website = scrape.Website(url)

    for category_url in website.get_categories():
        category = scrape.Category(category_url)
        category.create_csv_file()
        for book_url in category.get_books_url():
            book = scrape.Product(book_url)
            scrape.download_image_from_url(book.get_image_url(), f"{book.get_title()}.jpg")