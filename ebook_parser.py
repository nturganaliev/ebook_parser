import os
import requests


path = os.path.abspath('.')
directory = os.path.join(path, 'books')
if not os.path.exists(directory):
    os.makedirs(directory)

url = "https://tululu.org/txt.php"


for book_id in range(1, 11):
    params = {'id': f'{book_id}' }
    response = requests.get(url, params)
    response.raise_for_status()
    with open(f'{directory}/id{book_id}.txt', 'wb') as file:
        file.write(response.content)