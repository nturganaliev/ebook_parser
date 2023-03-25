import requests

from bs4 import BeautifulSoup


def main():
    # url = 'https://www.franksonnenbergonline.com/blog/are-you-grateful/'
    url = 'https://tululu.org/b1'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title, author = soup.find('div', {'id': 'content'}).find('h1').text.split("::")
    title = title.strip()
    author = author.strip()
    print(title)
    print(author)
    # title_tag = soup.find('main').find('header').find('h1')
    # title_text = title_tag.text
    # print(title_text)
    # print(soup.find('img', class_='attachment-post-image')['src'])
    # print()
    # text = soup.find('div', class_='entry-content').text
    # print(text)

if __name__ == '__main__':
    main()
