import json
import re
import time
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def test_request(url, retry=5):
    useragent = UserAgent
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/112.0.0.0 Safari/537.36 OPR/98.0.0.0"
    }
    try:
        response = requests.get(url=url, headers=headers)
        print(f"[+] {url} {response.status_code}")
    except Exception as ex:
        time.sleep(3)
        if retry:
            print(f"[INFO] retry={retry} => {url}")
            return test_request(url, retry=(retry - 1))
        else:
            raise
    else:
        return response


def get_category_links(url):
    product_links = {}
    response = test_request(url)
    with open('products.html', 'w', encoding='utf-8') as file:
        file.write(response.text)
    with open('products.html', encoding='utf-8') as file:
        response = file.read()
    soup = BeautifulSoup(response, 'lxml')
    cat_list = soup.find('ul', {'id': 'categoriesList'})
    links = ['https://www.rawlplug.com' + i.get('href') for i in cat_list.find_all('a', {'itemprop': 'url'})]
    print(links)
    visited_pages = set()
    for link in links:
        get_product_links(link, product_links, visited_pages)
    with open("links.txt", 'w', encoding='utf-8') as file:
        file.write(str(product_links))
    print('start')
    print(product_links)
    gather_data(product_links)


def get_product_links(link, product_links, visited_pages):
    if link not in visited_pages:
        visited_pages.add(link)
        response = test_request(link).text
        soup = BeautifulSoup(response, 'lxml')
        data = []
        if soup.find('ul', {'id': 'categoriesList'}):
            cat_list = soup.find('ul', {'id': 'categoriesList'})
            links = ['https://www.rawlplug.com' + i.get('href') for i in cat_list.find_all('a', {'itemprop': 'url'})]
            for link in links:
                get_product_links(link, product_links, visited_pages)
        elif soup.find('ul', {'id': 'productsList'}):
            try:
                category_branch = soup.find('ol', class_='breadcrumb')
                category_branch = '/'.join(
                    [item.text for item in category_branch.find_all('span', {'itemprop': 'name'})[2:]])
            except:
                category_branch = '/'.join(link.split('/')[4:])
            product_list = soup.find('ul', {'id': 'productsList'})
            product_links[category_branch] = list()
            product_urls = [product_links[category_branch].append(f'https://www.rawlplug.com{link.get("href")}') for
                            link in
                            product_list.find_all('a')]
        else:
            pass
    else:
        pass


def gather_data(urls):
    data_list = []
    for link in urls:
        for item in urls[link]:
            get_data(link, item, data_list)
    with open('data.json', 'w', encoding='utf-8') as file:
        json.dump(data_list, file, indent=4, ensure_ascii=False)


def get_data(category_branch, link, data_list):
    print(link)
    response = test_request(link).text
    soup = BeautifulSoup(response, 'lxml')
    try:
        title = soup.find('h1', {'id': 'Описание-продукта'}).text.strip()
    except:
        title = 'Название отсутствует'
    try:
        images = soup.find('div', {'id': 'productImages'})
        images = images.find_all('img')
        images = [item.get('src') for item in images if 'small' not in item.get('src')]
    except:
        images = 'Изображения отсутствуют'
    try:
        passport_link = f"https://www.rawlplug.com{soup.find('a', class_='icon icon-download').get('href')}".strip()
    except:
        passport_link = 'Ссылка на паспорт отсутствует'
    try:
        youtube_link = soup.find('div', {'id': 'productImages'}).find('iframe').get('src').strip()
    except:
        youtube_link = None
    try:
        description = soup.find('dd', {'id': 'Описание-продукта'}).text.strip().replace(
            '                                               ', '')
    except:
        description = 'Описание отсутствует'
    try:
        item_number = [item.text.strip() for item in
                       soup.find('td', class_=re.compile(r'(_id_INDEX).*')).find_all('span')]
    except:
        item_number = 'Артикул отсутствует'
    product_data = {'title': title,
                    'category branch': category_branch,
                    'images': images,
                    'passport link': passport_link,
                    'youtube link': youtube_link,
                    'description': description,
                    'item number': item_number}
    data_list.append(product_data)


if __name__ == '__main__':
    get_category_links(url='https://www.rawlplug.com/ru/produkcya')

