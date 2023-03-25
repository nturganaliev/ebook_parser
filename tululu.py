import os
import requests

import lxml

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        return False
    return True


def download_txt(url, filename, folder='books/'):
    response = requests.get(url)
    response.raise_for_status()
    directory = os.path.join(os.path.abspath('.'), folder)
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = sanitize_filename(filename)
    filepath = os.path.join(os.path.abspath('.'), folder, f'{filename}.txt')
    if check_for_redirect(response):
        with open(filepath, 'wb') as file:
            file.write(response.content)
        return filepath


def main():
    url = "https://tululu.org"
    for book_id in range(1, 11):
        try:
            response = requests.get(
                f'{url}/b{book_id}/'
            )
            if check_for_redirect(response):
                soup = BeautifulSoup(response.text, 'lxml')
                title, author = soup.find(
                    'div',
                    {'id': 'content'}
                ).find('h1').text.split("::")
                filename = title.strip()
                folder = 'txt'
                filepath = download_txt(
                    f'{url}/txt.php?id={book_id}',
                    f'{book_id}-{filename}',
                    folder
                )
                print(filepath)
        except requests.exceptions.HTTPError as error:
            raise error



if __name__ == '__main__':
    main()
    filepath = download_txt(
        "https://tululu.org/txt.php?id=32168",
        "Алиби"
    )
    print(filepath)
    filepath = download_txt(
        "https://tululu.org/txt.php?id=32168",
        'Али/би',
        folder='books/'
    )
    print(filepath)
    filepath = download_txt(
        "https://tululu.org/txt.php?id=32168",
        'Али\\би',
        folder='txt/')
    print(filepath)