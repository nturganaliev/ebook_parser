import argparse
import json
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
    response.raise_for_status()


def get_book_links_from_category(category_url):
    link_list = []
    response = requests.get(category_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    links = soup.find('div', {'id': 'content'}).find_all('a')
    for link in links:
        if (link['href'].startswith('/b')
            and urljoin(category_url, link['href']) not in link_list):
            link_list.append(urljoin(category_url, link['href']))
    return link_list


def get_book_id(link):
    return urlparse(link).path.split('/')[1][1:]


def download_txt(url, filename, folder='books/'):
    response = requests.get(url)
    check_for_redirect(response)
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
    title, author = soup.find(
        'div', {'id': 'content'}
    ).find('h1').text.split("::")
    title = title.strip()
    author = author.strip()
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
        'author': author,
        'image_url': image_url,
        'genre': genre,
        'comments': all_comments
    }


def main():
    url = 'https://tululu.org/'
    category_url = 'https://tululu.org/l55/'
    path = os.path.abspath('.')
    books_folder = 'books'
    book_links = []
    books_description = []
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
    for page in range(args.start_id, args.end_id):
        book_links += get_book_links_from_category(f'{category_url}{page}')

    for index, link in enumerate(book_links):
        try:
            book_id = get_book_id(link)
            book_url_response = requests.get(
                urljoin(url, 'txt.php'),
                {'id': book_id}
            )
            check_for_redirect(book_url_response)

            page_response = requests.get(
                f'{url}/b{book_id}/'
            )
            check_for_redirect(page_response)

            content = page_response.text
            parsed_content = parse_book_page(content)
            image_url = urljoin(
                page_response.url,
                parsed_content['image_url']
            )
            title = parsed_content['title']
            author = parsed_content['author']
            genres = parsed_content['genre']
            comments = parsed_content['comments']
            image_path = download_image(image_url)
            book_path = download_txt(
                book_url_response.url,
                f'{index}-я книга. {title}',
                books_folder
            )
            books_description.append({
                'title': title,
                'author': author,
                'img_src': image_path,
                'book_path': book_path,
                'comments': comments,
                'gengres': genres
            })
            print("Заголовок: ", title)
            print(image_url)
            print(genres)
            print()
        except InvalidLinkException:
            print("Exception occured: Link to download"\
                  "book in txt format do not exist.\n")
        except requests.exceptions.HTTPError as error:
            print(error)
            print()
        except requests.exceptions.ConnectionError as error:
            print(error)
            print()
            time.sleep(30)
    with open(
        os.path.join(path, books_folder, 'books_description.json'),
        'wb',
    ) as file:
        file.write(json.dumps(books_description, ensure_ascii=False, indent=4).encode('utf8'))


if __name__ == '__main__':
    main()
