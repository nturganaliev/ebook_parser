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
    title, author = list(
        map(str.strip, soup.select('div#content h1')[0].text.split("::"))
    )
    image_url = soup.select('div.bookimage img')[0]['src']
    if soup.select('div.texts'):
        comments = soup.select('div.texts')
        if comments:
            for comment in comments:
                all_comments += f"{comment.find('span').text}\n"
    genre = [a.text for a in soup.select('span.d_book a')]
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
    images_folder = 'images'
    book_links = []
    books_description = []
    books_description_folder = books_folder
    parser = argparse.ArgumentParser(
        description = 'Enter first and last id'\
                      'to set range to download books.'
    )
    parser.add_argument(
        '--start_page',
        help='--start_page should be entered to download books.',
        nargs='?',
        default=1,
        type=int
    )
    parser.add_argument(
        '--end_page',
        help='--end_page should be entered to download books.',
        nargs='?',
        default=702,
        type=int
    )
    parser.add_argument(
        '--skip_images',
        help='--skip_images should be entered to skip downloading images.',
        action='store_true'
    )
    parser.add_argument(
        '--dest_folder',
        nargs='?',
        help='--dest_folder should be entered to change downloading path.',
        type=str
    )
    parser.add_argument(
        '--json_path',
        nargs='?',
        help='--json_path should be entered to change' \
             'downloading path of books description file.',
        type=str
    )
    parser.add_argument(
        '--skip_txt',
        help='--skip_txt should be entered to skip downloading books.',
        action='store_true'
    )
    args = parser.parse_args()
    if args.dest_folder:
        books_folder = args.dest_folder
        images_folder = args.dest_folder

    if args.json_path:
        books_description_folder = args.json_path
        os.makedirs(books_description_folder, exist_ok=True)

    for page in range(args.start_page, args.end_page):
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
            if not args.skip_images:
                image_path = download_image(
                    image_url,
                    images_folder
                )
            else:
                image_path = None
            if not args.skip_txt:
                book_path = download_txt(
                    book_url_response.url,
                    f'{index}-я книга. {title}',
                    books_folder
                )
            else:
                book_path = None
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
        os.path.join(path, books_description_folder, 'books_description.json'),
        'wb',
    ) as file:
        file.write(
            json.dumps(
                books_description,
                ensure_ascii=False,
                indent=4
            ).encode('utf8')
        )


if __name__ == '__main__':
    main()
