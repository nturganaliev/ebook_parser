import argparse
import os
import time

import lxml
import requests

from urllib.parse import unquote
from urllib.parse import urljoin
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


class InvalidLinkException(Exception):
    "Raised when link does not exist for downloading"
    pass


def check_for_redirect(response):
    if response.history:
        raise InvalidLinkException


def download_txt(url, filename, folder='books/'):
    response = requests.get(url)
    response.raise_for_status()
    directory = os.path.join(os.path.abspath('.'), folder)
    os.makedirs(directory, exist_ok=True)
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
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(os.path.abspath('.'), folder, filename)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def parse_book_page(content):
    all_comments = ''
    soup = BeautifulSoup(content, 'lxml')
    title = soup.find(
        'div', {'id': 'content'}
    ).find('h1').text.split("::")[0].strip()
    image_url = soup.find(
        'div', {'class': 'bookimage'}
    ).find('img')['src']
    if soup.find_all('div', {'class': 'texts'}):
        comments = soup.find_all(
            'div', {'class': 'texts'}
        )
        if comments:
            for comment in comments:
                all_comments += f"{comment.find('span').text}\n"
    genre = soup.find(
        'span', {'class': 'd_book'}
    ).text.split(':')[1].strip().split(',')
    return {
        'title': title,
        'image_url':image_url,
        'genre': genre,
        'comments': all_comments
    }


def main():
    url = 'https://tululu.org'
    path = os.path.abspath('.')
    folder = 'txt'
    parser = argparse.ArgumentParser(
        description = 'Enter first and last id'\
                      'to set range to download books.'
    )
    parser.add_argument(
        'start_id',
        help='--start_id should be entered to download books.',
        default=1,
        type=int
    )
    parser.add_argument(
        'end_id',
        help='--start_id should be entered to download books.',
        default=11,
        type=int
    )
    args = parser.parse_args()
    for book_id in range(args.start_id, args.end_id):
        try:
            book_url_reponse = requests.get(f'{url}/txt.php', {'id': book_id})
            book_url_reponse.raise_for_status()
            try:
                check_for_redirect(book_url_reponse)
                page_response = requests.get(
                    f'{url}/b{book_id}/'
                )
                page_response.raise_for_status()
                content = page_response.text
                parsed_content = parse_book_page(content)
                image_url = urljoin(
                    page_response.url,
                    parsed_content['image_url']
                )
                filename = parsed_content['title']
                genre = parsed_content['genre']
                comments = parsed_content['comments']
                image_path = download_image(image_url)
                book_path = download_txt(
                    book_url_reponse.url,
                    f'{book_id}-{filename}',
                    folder
                )
                with open(
                    os.path.join(path, folder, 'comments.txt'),
                    'a'
                ) as file:
                    file.write(comments)
                print("Заголовок: ", filename)
                print(image_url)
                print(genre)
                print()
            except InvalidLinkException:
                print("Exception occured: Link to download"\
                      "book in txt format do not exist.\n")
        except requests.exceptions.HTTPError as error:
            print(error)
        except requests.exceptions.ConnectionError as error:
            print(error)
            time.sleep(30)


if __name__ == '__main__':
    main()
