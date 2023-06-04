import asyncio
import random
import time

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import gspread
from oauth2client.service_account import ServiceAccountCredentials

ua = UserAgent()

headers = {
    'user-agent': ua.random
}

session = requests.Session()


async def get_data(links):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        'causal-root-388518-8183a6cff79b.json', scope)
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_url(
        'https://docs.google.com/spreadsheets/d/1zeoOdQi3nbJck9MXz_RsgeRBjCJ4YyNmn6DUwsi1WRY/edit#gid=0')
    worksheet = spreadsheet.get_worksheet(0)
    row = ["Фамилия", "Имя Отчество", "Должность", "Компетенции", "Город", "Рейтинг", "Стаж, лет",
           "Ссылка на специалиста"]
    worksheet.append_row(row)
    for link in links:
        response = session.get(link, headers=headers).text
        soup = BeautifulSoup(response, 'lxml')
        last_name = soup.find('div', class_='doctorDetail__info').find('h1').text.split(' ')[0]
        full_name = ' '.join(soup.find('div', class_='doctorDetail__info').find('h1').text.split(' ')[1:])
        post = soup.find('div', class_='doctorDetail__speciality').text.strip()
        try:
            competences = soup.find('section', class_='doctorDetail__methods container').find('ul',
                                                                                              class_='checkMarks')
            competences = ''.join([item.text.strip() + '\n' for item in competences.find_all('li')])
        except:
            competences = None
        try:
            city = soup.find('span', class_='doctorDetail__online-city').text[7:]
        except:
            city = None
        try:
            rate = soup.find('span', {'id': 'avgrat'}).text
        except:
            rate = None
        try:
            experience = soup.find_all('div', class_='doctorDetail__experience')[1].text[7:].strip()
        except:
            experience = None
        link = link
        row = [last_name, full_name, post, competences, city, rate, experience, link]
        time.sleep(random.randint(1, 4))
        print(1)
        worksheet.append_row(row)


# async def get_links(url):
#     response = session.get(url, headers=headers).text
#     soup = BeautifulSoup(response, 'lxml')
#     links = ['https://dr-ost.ru' + item.get('onclick').replace('location.href=', '').replace("'", '') for item in
#              soup.find_all('div', class_='doctor__info__photo lazy')]
#     return links
import os


async def get_links_from_files(path):
    html_files = [file for file in os.listdir(path) if file.endswith(".html")]

    links = []
    for file in html_files:
        file_path = os.path.join(path, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
            soup = BeautifulSoup(html_content, 'lxml')
            file_links = ['https://dr-ost.ru' + item.get('onclick').replace('location.href=', '').replace("'", '') for
                          item in
                          soup.find_all('div', class_='doctor__info__photo lazy')]
            links.extend(file_links)
    print(links)
    return links


def main():
    links = asyncio.run(get_links_from_files('cities'))
    asyncio.run(get_data(links))


if __name__ == '__main__':
    main()
