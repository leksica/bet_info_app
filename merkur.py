import aiohttp
import asyncio
import json
from datetime import datetime
import pandas as pd
import time

start = time.time()

url1 = "https://www.merkurxtip.rs/restapi/offer/sr/categories/sport/S/g"
querystring1 = {"annex": "0", "desktopVersion": "1.31.5"}

headers1 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Referer": "https://www.merkurxtip.rs/desk/sr/sportsko-kladjenje/fudbal/S",
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

async def fetch(session, url, headers, params):
    async with session.get(url, headers=headers, params=params) as response:
        return await response.json()

async def fetch_all(session, urls):
    tasks = []
    for url, headers, params in urls:
        tasks.append(fetch(session, url, headers, params))
    return await asyncio.gather(*tasks)

async def main():
    querystring1 = {"annex": "0", "desktopVersion": "1.31.5"}

    async with aiohttp.ClientSession() as session:
        liga_response = await fetch(session, url1, headers1, querystring1)
        urls = []
        
        for liga in liga_response['categories']:
            id = liga['id']
            league_url = f"https://www.merkurxtip.rs/restapi/offer/sr/sport/S/league-group/{id}/desk"
            querystring1 = {"annex": "0", "desktopVersion": "1.31.5", "locale": "sr"}
            urls.append((league_url, headers1, querystring1))
        
        league_responses = await fetch_all(session, urls)
        game_urls = []

        for text in league_responses:
            for game in text['esMatches']:
                game_url = f"https://www.merkurxtip.rs/restapi/offer/sr/match/{game['id']}"
                querystring = {"annex": "0", "desktopVersion": "1.31.8", "locale": "sr"}
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Sec-GPC": "1",
                    "Connection": "keep-alive",
                    "Referer": f"https://www.merkurxtip.rs/desk/sr/sportsko-kladjenje/fudbal/S/super-liga/2314082/special/radnik-sur-v-partizan/127943947",
                    "Cookie": "org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=sr",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "same-origin",
                    "TE": "trailers"
                }
                game_urls.append((game_url, headers, querystring))

        game_responses = await fetch_all(session, game_urls)

        for game in game_responses:
            ts = int(game['kickOffTime']) / 1000
            data['datum'].append(str(datetime.fromtimestamp(ts).strftime('%Y-%m-%d')))
            data['vreme'].append(str(datetime.fromtimestamp(ts).strftime('%H:%M:%S')))
            data['domacin'].append(game['home'])
            data['gost'].append(game['away'])
            data['ki_1'].append(game['odds'].get('1', 0))
            data['ki_x'].append(game['odds'].get('2', 0))
            data['ki_2'].append(game['odds'].get('3', 0))
            data['gg'].append(game['odds'].get('272', 0))
            data['ng'].append(game['odds'].get('273', 0))
            data['0-2'].append(game['odds'].get('22', 0))
            data['3+'].append(game['odds'].get('24', 0))

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main())
loop.close()

df = pd.DataFrame(data)
df.to_csv('merkur.csv', index=False)

end = time.time()
print(end-start)
