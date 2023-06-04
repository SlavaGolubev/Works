import json
import os

import requests
from fake_useragent import UserAgent
import asyncio
import base64
from io import BytesIO
from PIL import Image

ua = UserAgent()

headers = {
    'user-agent': ua.random
}


async def get_data(url):
    eqID = url.split('/')[6]
    pgID = url.split('/')[-1]

    cookies = {
        's_evar47': 'First%20Visit',
        's_evar50': 'Weekday',
        'AMCVS_8CC867C25245ADC30A490D4C%40AdobeOrg': '1',
        's_ecid': 'MCMID%7C41192755302381635064608422300906211548',
        's_cc': 'true',
        'AMCV_8CC867C25245ADC30A490D4C%40AdobeOrg': '-1124106680%7CMCIDTS%7C19510%7CMCMID%7C41192755302381635064608422300906211548%7CMCAAMLH-1686212656%7C6%7CMCAAMB-1686212656%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1685615056s%7CNONE%7CMCAID%7CNONE%7CMCCIDH%7C-1427732020%7CvVersion%7C5.2.0',
        'AWSALB': 'z7mvly5sXMEgkQatgmJASFwcyxNl5DdHnvUWwgl/4hSAq359qK8au7KKjPUsqaIwcNUX70C6DAtCEuKV6XtlRaAtwwqsoGrMZrb6t60Q/E8utYnoIJjRmRGfIsNS',
        'AWSALBCORS': 'z7mvly5sXMEgkQatgmJASFwcyxNl5DdHnvUWwgl/4hSAq359qK8au7KKjPUsqaIwcNUX70C6DAtCEuKV6XtlRaAtwwqsoGrMZrb6t60Q/E8utYnoIJjRmRGfIsNS',
        's_ppvl': 'ru_ru%2520%253A%2520partslookup%2520%253A%2520sidebyside%2520%253A%2520ST766452%2520-%2520%25u0428%25u043F%25u0438%25u043B%25u044C%25u043A%25u0438%2520%25u043F%25u0440%25u0438%25u0432%25u043E%25u0434%25u0430%252C%2520%25u043A%25u043E%25u0440%25u043E%25u0442%25u043A%25u0438%25u0435%252C%2520%25u043F%25u0440%25u0430%25u0432%25u0430%25u044F%2520%25u0441%25u0442%25u043E%25u0440%25u043E%25u043D%25u0430%2C100%2C100%2C746%2C903%2C746%2C1536%2C864%2C1.25%2CP',
        's_ppv': 'ru_ru%2520%253A%2520partslookup%2520%253A%2520sidebyside%2520%253A%2520ST766452%2520-%2520%25u0428%25u043F%25u0438%25u043B%25u044C%25u043A%25u0438%2520%25u043F%25u0440%25u0438%25u0432%25u043E%25u0434%25u0430%252C%2520%25u043A%25u043E%25u0440%25u043E%25u0442%25u043A%25u0438%25u0435%252C%2520%25u043F%25u0440%25u0430%25u0432%25u0430%25u044F%2520%25u0441%25u0442%25u043E%25u0440%25u043E%25u043D%25u0430%2C100%2C100%2C746%2C903%2C746%2C1536%2C864%2C1.25%2CP',
        's_evar48': '3%3A26%20AM%7CThursday',
        's_evar49': '3%3A26%20AM%7CThursday',
        'OptanonConsent': 'isGpcEnabled=0&datestamp=Thu+Jun+01+2023+11%3A26%3A09+GMT%2B0300+(%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0%2C+%D1%81%D1%82%D0%B0%D0%BD%D0%B4%D0%B0%D1%80%D1%82%D0%BD%D0%BE%D0%B5+%D0%B2%D1%80%D0%B5%D0%BC%D1%8F)&version=202304.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=362b7109-58d0-4297-8e9d-b250e392ba59&interactionCount=1&landingPath=https%3A%2F%2Fpartscatalog.deere.com%2Fjdrc%2Fsidebyside%2Fequipment%2F74407%2Freferrer%2Fnavigation%2FpgId%2F131928171&groups=C0001%3A1%2CC0003%3A1%2CC0004%3A1%2CC0002%3A1',
    }

    headers = {
        'authority': 'partscatalog.deere.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache,no-store',
        'captcha-token': '03AL8dmw-0aPfC_2zSS0zems8_Cvcld_Y6cuWBYrp53Tbm3TK6pm0KsMmg5PhQQs3TNrmwIA2HOqqgQ7KpIClKO0PJtBCI6szcbrW028H8I5IKmmXxctz_VynMto-vpVlVcnvpBTUWFjtKnQZp0VDUv7__ziyv2KdV8QvK0vEXaaWoCKogdMCA3Pv8wXnkHuq9y1vKsBtl0gxQtgF3SQDBImL6wEm_qicx2xXh6O9IGRdM6cHHF_0AhsOYqa1hZKXd-EJI9IKtOyrSxXmbenrVh9InqQiKEaiLLLTSrzIypro7_VI_sASg1R1A0L3tKMtYQFS530HmkmLdcLWrfv5t4ou6Py0UHP0dOXKlvC6w7oi81V_ShfSYm44Rs9MRz2VNg4N0SWI7GNOW85zpSOCV8OUNCyV-Tv9VR-fBC7xc11gCDHZEdV8olpPuHu3WB2NeznJL90EXvQd2rNhyvAx7VocAPcyAk7xf5VusVAsbS-MyDoBPdR1fFwUwB8ft8vWx0p_SlBlvarD4A8Z0_xGm9ma3CG-GLE699hD22kptN2KrZyvqD8P_DDhpLz47SHAkzOPrjdPjLwKS6uuwxsa1i42Ub1XUr7Q0Nat7MCkzdSdX5anMp8XAQ_a1RvuKugU-5TIBuFtMsMqa39k_ouurCzrYJjghrBRWTjeTcsBtQDzOFU6uYbEZM4aEQQmcCVhuCwlC2FLQAk6oJr6chP5P4wkxxXWusrQqZEjW0MAoywEcS4imGbaLlRsrgZ0wjOApI-T4hdQvgQxhhJDVwVIRt0ou2nQUOOgIEzva8-kwJ284BnSWMfrTHGkQj1oudU2MGysveBusNUAjklOwyXn3Y_Xnd7OZHjER3vnOXM7agRC82Ozy1UObf6PJ4VZG_tC7183RPV_pcfutzLLWwaWr9jNyVCo5ZcdCPAR8UrFsZ-qZdHtgni6jnIf1lxjQL2RaWEmwxysW9KnnLFqKZdxMSL16Jr06ApzsX3ReEUh0LAfN89RPYttoxFj_RQ4x8eJyUVOpli31-yMiwiEUXVsa1GPn7ds26GWC50WsmMWpG90IlHE35EPHL7dDYSWs1qa6F0dPAISiafmAORgxa3OmzUmkc8o66A-_KhEZBd1cBRUXCxckkpY8wVyZd05iV8gYJOl0pu5sN8BJI3dgqgEzr_b51Rm3CC7wcDDzO7-upn3Jsrl6W95U0wzQOiFwJ1iJ1F59PdVZw7hp7u1Bec-SSDY7F6JbPyKSqP9jMSPOF0PTx9nF4KMYW_eMYp-6zTZdMWj7GmFiqMQsxhpIfzsG2GOTj7bup_1Agb7ErJd6NJeCmse_b1Q-pgLpO-mBphuArZ8RSe8AmuxQzpVqAvklf5-ldePA0Zhzjv8_cf0IByeSXtcbB98MiOLJlIK1D_LnWJkXYunmJzUWzNAS9oRsvKXkOQimPyYnY3dGRslJtFlZICIlPkgW7otrdrjxX57qKPyqAMa-AFzSj0qATE-uYXhuwtdZiCESVA',
        'captcha-version': 'Enterprise',
        'content-type': 'application/json',
        'expires': '0',
        'origin': 'https://partscatalog.deere.com',
        'pragma': 'no-cache',
        'product-line': 'JDRC',
        'referer': 'https://partscatalog.deere.com/jdrc/sidebyside/equipment/74407/referrer/navigation/pgId/131928171',
        'sec-ch-ua': '"Chromium";v="112", "Not_A Brand";v="24", "Opera";v="98"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 OPR/98.0.0.0',
    }

    json_data = {
        'eqID': eqID,
        'pgID': pgID,
        'fr': {
            'businessRegion': 1241,
            'filtersEnabled': True,
            'encodedFilters': None,
            'encodedFiltersHash': None,
            'filteringLevel': None,
            'currentPin': None,
            'equipmentRefId': '74407',
        },
        'brID': '1241',
        'locale': 'ru-RU',
        'fromSearch': False,
        'includeRelatedPictorials': True,
    }

    # {'id': 131928171, 'name': 'Шпильки привода, короткие, правая сторона', 'code': 'ST766452', 'catKey': 'PC12231', 'image': 'iVBORw0KGgoAAAANSUhEUgAACFAAAATcAQAAAACBlN71AAA6tklEQVR42u2dz8/zynXfKSgNsyhMA92kgGGmK2+N3k0MGO8kf4H/hXRTb114kwI3d3QjtOqiiAJ4EwNG+J9YeqKFGuDCXHRfSVBgdic+FhCR1Wi+XQx
    response = requests.post(
        'https://partscatalog.deere.com/jdrc-services/v1/sidebyside/sidebysidePage',
        cookies=cookies,
        headers=headers,
        json=json_data,
    )
    response = response.json()
    name = response['name']
    image_bytes = base64.b64decode(response['image'])
    image = Image.open(BytesIO(image_bytes))
    if not os.path.exists(f'data/{name}'):
        os.makedirs(f'data/{name}')
    image.save(f'data/{name}/{name}', "PNG")
    parts = []
    for item in response['partItems']:
        parts.append(
            {'Запчасть': item['partDescription'], 'Артикул': item['partNumber'], 'Треб. кол-во': item['quantityReq']})
    data = {'Наименование': name,
            'Код': response['code'],
            'Артикул': response['catKey'],
            'Запчасти': parts
            }

    with open(f'data/{name}/{name}.json', 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def main():
    asyncio.run(
        get_data('https://partscatalog.deere.com/jdrc/sidebyside/equipment/74407/referrer/navigation/pgId/131934003'))


if __name__ == '__main__':
    main()
