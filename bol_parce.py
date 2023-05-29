import asyncio
import json
import random
import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


async def get_page_links(session, page, all_links):
    useragent = UserAgent()
    headers = {'User-Agent': useragent.random,
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                         '*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
               }
    url = f"https://www.bol.com/nl/nl/l/muziek-op-lp-s/54480/?page={page}"

    await asyncio.sleep(random.randint(1, 3))
    print(page)
    async with session.get(url=url, headers=headers) as response:
        response_text = await response.text()

        soup = BeautifulSoup(response_text, 'lxml')

        links_from_page = [all_links.append('https://www.bol.com/' + str(link.get('href'))) for link in
                           soup.find_all('a', class_='px_list_page_product_click list_page_product_tracking_target')]


async def get_page_data(session, link, data):
    useragent = UserAgent()
    headers = {'User-Agent': useragent.random,
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                         '*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
               }

    # После сбора ссылок со страницы age проходим по этим ссылкам и собираем инфу.
    async with session.get(url=link, headers=headers) as response:
        response_text = await response.text()
        soup = BeautifulSoup(response_text, "lxml")
        try:
            title = soup.find('span', {"data-test": "title"}).text.strip()
        except Exception as ex:
            print(ex)
            title = 'The title is missing.'
        try:
            subtitle = soup.find('span', class_='sub-title').text.strip()
        except:
            subtitle = None
        if subtitle:
            title = f'{title}.{subtitle}.'
        try:
            images = [i['src'] for i in soup.find('wsp-image-slot').find_all('img')]
        except Exception as ex:
            print(ex)
            images = "Images are missing."
        try:
            price = soup.find(
                'div', class_='price-block__highlight').find('span', class_='promo-price').text.strip().replace(
                '\n', ',').replace(' ', '')
        except Exception as ex:
            print(ex)
            price = "Price is missing."
        try:
            description = soup.find(class_='product-description').text.strip()
        except Exception as ex:
            print(ex)
            description = "Description is missing."
        try:
            tracks = [f'{y + 1}. {i.text.strip()}' for y, i in
                      enumerate(soup.find_all('span', class_="track__title"))]
        except Exception as ex:
            print(ex)
            tracks = "Tracks are missing."
        # По каждой ссылке, собираем информацию по продукту в словарь и добавляем в список data.
        product = {'title': title,
                   'images': images,
                   'url': link,
                   'price': price,
                   'description': description,
                   'tracks': tracks}
        data.append(product)


async def gather_data():
    useragent = UserAgent()
    headers = {'User-Agent': str(useragent.random),
               'Accept': '*/*',
               }

    url = "https://www.bol.com/nl/nl/l/muziek-op-lp-s/54480/"

    async with aiohttp.ClientSession() as session:
        all_links = []
        response = await session.get(url=url, headers=headers)
        soup = BeautifulSoup(await response.text(), "lxml")
        pages_count = int(soup.find(class_='pagination').find_all('a')[-2].text)
        tasks = []
        # for page in range(1, pages_count + 1):
        for page in range(1, 6):
            await asyncio.sleep(random.randint(1, 3))
            task = asyncio.create_task(get_page_links(session, page, all_links))
            tasks.append(task)

        await asyncio.gather(*tasks)
        tasks = []
        data = []
        # for link in all_links:
        for link in range(1, 20):
            await asyncio.sleep(random.randint(1, 3))
            task = asyncio.create_task(get_page_data(session, all_links[link], data))
            tasks.append(task)
        await asyncio.gather(*tasks)
    with open('data/product_data.json', 'a', encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def main():
    asyncio.run(gather_data())


if __name__ == '__main__':
    main()
