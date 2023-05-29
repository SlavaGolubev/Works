import json
import re
import time
from selenium import webdriver
from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup
import lxml
from selenium.webdriver.common.by import By


def refresh_list(r_count):
    useragent = UserAgent
    # options = webdriver.ChromeOptions()
    # options.add_argument(f'user-agent={useragent.random}')
    # options.add_argument('--disable-blink-features=AutomationControlled')
    if r_count:
        url = f'https://re.kufar.by/l/minsk/snyat/kvartiru-dolgosrochno/{r_count}k?cur=USD&size=30'
    else:
        url = 'https://re.kufar.by/l/minsk/snyat/kvartiru-dolgosrochno'


    # driver = webdriver.Chrome(
    #     executable_path=r'C:\Users\giftm\PycharmProjects\TelebotProject\lessons\selenium chrome driver\chromedriver.exe',
    #     options=options)
    #
    # try:
    #     driver.get(url=url)
    #     time.sleep(3)
    #     accept_cookie = driver.find_element(By.XPATH, "//button[text()='Принять']")
    #     if accept_cookie:
    #         accept_cookie.click()
    #     time.sleep(3)
    #     close_button = driver.find_element(By.XPATH, "//button[text()='Закрыть']")
    #     if close_button:
    #         close_button.click()
    #
    #     time.sleep(3000)
    #
    # except Exception as ex:
    #     print(ex)
    # finally:
    #     driver.close()
    #     driver.quit()

    req = requests.get(url, headers={'user-agent': f'{useragent.random}'})

    src = req.text

    with open('flats.html', 'w', encoding='utf-8') as file:
        file.write(src)

    with open('flats.html', encoding='utf-8') as file:
        src = file.read()

    flats_page = []
    soup = BeautifulSoup(src, 'lxml')
    cards_block = soup.find_all('a', class_=lambda x: x and x.startswith('styles_wrapper__'))
    for card_block in cards_block:
        link = card_block.get('href')
        price_block = card_block.find(class_=lambda x: x and x.startswith('styles_price')).find_all('span')
        price = f'{price_block[0].text} ({price_block[1].text[:-1]}) в мес.'
        apartment_block = card_block.find(class_=lambda x: x and x.startswith('styles_parameters__'))
        apartment = apartment_block.text
        address = card_block.find(class_=lambda x: x and x.startswith('styles_address')).text
        photos = card_block.find(class_=lambda x: x and x.startswith('styles_image')).find_all('img')
        photos = list({i.get('data-src') for i in photos if i.get('data-src') is not None})
        try:
            description = card_block.find('p', class_=lambda x: x and x.startswith('styles_body')).text
        except:
            description = None

        if description:
            data = {'apartment': apartment,
                    'price': price,
                    'address': address,
                    'photos': photos,
                    'link': link,
                    'description': description}
        else:
            data = {'apartment': apartment,
                    'price': price,
                    'address': address,
                    'photos': photos,
                    'link': link,
                    }
        flats_page.append(data)

        with open('flats.json', 'w', encoding='utf-8') as json_file:
            json.dump(flats_page, json_file, indent=4, ensure_ascii=False)
