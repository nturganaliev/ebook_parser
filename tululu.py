import os
import requests

import lxml

from urllib.parse import unquote
from urllib.parse import urljoin
from urllib.parse import urlparse
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
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def download_image(url, folder='images/'):
    filename = urlparse(url).path.split("/")[-1]
    response = requests.get(url)
    response.raise_for_status()
    directory = os.path.join(os.path.abspath('.'), folder)
    if not os.path.exists(directory):
        os.makedirs(directory)
    filepath = os.path.join(os.path.abspath('.'), folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def main():
    url = "https://tululu.org"
    for book_id in range(1, 11):
        try:
            book_url_reponse = requests.get(f'{url}/txt.php', {'id': book_id})
            if check_for_redirect(book_url_reponse):
                title_response = requests.get(
                    f'{url}/b{book_id}/'
                )
                soup = BeautifulSoup(title_response.text, 'lxml')
                title = soup.find(
                    'div',{'id': 'content'}
                ).find('h1').text.split("::")[0]
                filename = title.strip()
                folder = 'txt'
                image_url = urljoin(
                    url, soup.find('div', class_='bookimage'
                    ).find('img')['src']
                )
                image_path = download_image(
                    image_url
                )
                book_path = download_txt(
                    book_url_reponse.url,
                    f'{book_id}-{filename}',
                    folder
                )
                print("Заголовок: ", filename)
                print(image_url)
                print()
        except requests.exceptions.HTTPError as error:
            raise error
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



if __name__ == '__main__':
    main()