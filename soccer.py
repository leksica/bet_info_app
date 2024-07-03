import json
import aiohttp
import asyncio
from datetime import datetime, timedelta
import pandas as pd

url = "https://www.soccerbet.rs/restapi/offer/sr/sport/S/mob"
querystring = {"annex": "0", "desktopVersion": "2.27.13", "locale": "sr"}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Referer": "https://www.soccerbet.rs/sr/sportsko-kladjenje/fudbal/S",
    "Cookie": "org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=sr",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers"
}

data = {
    "datum": [],
    'vreme': [],
    'domacin': [],
    'gost': [],
    'ki_1': [],
    'ki_x': [],
    'ki_2': [],
    'gg': [],
    'ng': [],
    '0-2': [],
    '3+': []
}

async def fetch_data(session):
    async with session.get(url, headers=headers, params=querystring) as response:
        return await response.json()

async def process_data():
    async with aiohttp.ClientSession() as session:
        response = await fetch_data(session)
        html = response
        c = 0

        for game in html['esMatches']:
            c += 1
            start = game['kickOffTime']
            ts = int(start) / 1000
            dt_string = datetime.utcfromtimestamp(ts)
            adj_dt = dt_string + timedelta(hours=2)

            date = (adj_dt).strftime('%Y-%m-%d')
            time = (adj_dt).strftime('%H:%M:%S')

            data['datum'].append(date)
            data['vreme'].append(time)
            data['domacin'].append(game['home'])
            data['gost'].append(game['away'])
            data["ki_1"].append(game['betMap']['1']['NULL']['ov'])
            data["ki_x"].append(game['betMap']['2']['NULL']['ov'])
            data["ki_2"].append(game['betMap']['3']['NULL']['ov'])

            data['gg'].append(game['betMap'].get('272', {}).get('NULL', {}).get('ov', 0))
            data['ng'].append(game['betMap'].get('273', {}).get('NULL', {}).get('ov', 0))
            data['0-2'].append(game['betMap'].get('22', {}).get('NULL', {}).get('ov', 0))
            data['3+'].append(game['betMap'].get('24', {}).get('NULL', {}).get('ov', 0))

        df = pd.DataFrame(data)
        df.to_csv('soccer.csv', index=False)
        print(c)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(process_data())
