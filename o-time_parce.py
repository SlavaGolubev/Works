import os

import html5lib
import openpyxl
import requests
from bs4 import BeautifulSoup
import lxml
from fake_useragent import UserAgent

ua = UserAgent()
headers = {
    'user-agent': ua.random
}

session = requests.Session()


def get_data(url):
    response = session.get(url, headers=headers)
    if 'dist=29' in url:
        soup = BeautifulSoup(response.text, 'html.parser')
    else:
        soup = BeautifulSoup(response.text, 'lxml')
    raw_data = soup.find_all('div', class_=['results1', 'results2'])
    workbook = openpyxl.Workbook()
    workbook.remove(workbook.active)
    sheet = workbook.create_sheet(title=soup.find('div', class_='startname').find('b').text)
    sheet['A1'] = 'Место'
    sheet['B1'] = 'Стартовый номер'
    sheet['C1'] = 'Фамилия, Имя'
    sheet['D1'] = 'Результат Ган Тайм'
    sheet['E1'] = 'Результат Чип Тайм'
    sheet['F1'] = 'Возрастная группа'
    sheet['G1'] = 'Дистанция'

    row = 2
    distance = soup.find('option', attrs={'selected': True}).text.strip()
    for item in raw_data:
        numb = item.find('div', class_='rank').text.strip()
        st_numb = item.find('div', class_='rbib').text.strip()
        name = item.find('div', class_='rname').find('b').text.strip()
        try:
            gun_time = item.find('div', class_='rres').text.split(' ')[1][:-2].strip()
        except:
            gun_time = item.find('div', class_='rres').text[:-2].strip()
        try:
            run_time = item.find('div', class_='rres').text.split(' ')[2][:-2].strip()
        except:
            run_time = item.find('div', class_='rpace').text.strip()
        try:
            age_group = item.find('div', class_='rank_a').text[:-4].strip()
        except:
            age_group = None

        sheet[f'A{row}'] = numb
        sheet[f'B{row}'] = st_numb
        sheet[f'C{row}'] = name
        sheet[f'D{row}'] = gun_time
        sheet[f'E{row}'] = run_time
        sheet[f'F{row}'] = age_group
        sheet[f'G{row}'] = distance
        row += 1
    if not os.path.exists('data'):
        os.makedirs('data')
    workbook.save(f"data/{soup.find('div', class_='startname').find('font', {'size': '+1'}).text}({distance}).xlsx")


def main():
    url = input('Вставьте ссылку на протокол.')
    get_data(url)


if __name__ == "__main__":
    main()
