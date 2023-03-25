import argparse
import os

import lxml
import requests

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
    url = "https://tululu.org"
    path = os.path.abspath('.')
    folder = 'txt'
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--start_id',
        help='--start_id should be entered to download books.',
        default=1,
        type=int
    )
    parser.add_argument(
        '--end_id',
        help='--start_id should be entered to download books.',
        default=11,
        type=int
    )
    args = parser.parse_args()
    for book_id in range(args.start_id, args.end_id):
        try:
            book_url_reponse = requests.get(f'{url}/txt.php', {'id': book_id})
            book_url_reponse.raise_for_status()
            if check_for_redirect(book_url_reponse):
                page_response = requests.get(
                    f'{url}/b{book_id}/'
                )
                page_response.raise_for_status()
                content = page_response.text
                page_data = parse_book_page(content)
                image_url = urljoin(url, page_data['image_url'])
                filename = page_data['title']
                genre = page_data['genre']
                comments = page_data['comments']
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
