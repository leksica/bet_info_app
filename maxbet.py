import requests
import json
import asyncio
import aiohttp
import time
from datetime import datetime
import pandas as pd

start = time.time()

url = "https://www.maxbet.rs/restapi/offer/sr/categories/sport/S/l"

querystring = {"annex":"3","desktopVersion":"2.24.89","locale":"sr"}

payload = ""
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Referer": "https://www.maxbet.rs/leagues/S",
    "Cookie": "your-cookie-here",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers"
}
response = requests.request("GET", url, data=payload, headers=headers, params=querystring)
competition = []
a = 1
takmicenja_fudbal = json.loads(response.text)
for takm in takmicenja_fudbal['categories']:
    if a:
        a = 0
        continue
    competition.append(takm['id'])

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

querystring1 = {"annex": "3", "desktopVersion": "2.24.89", "locale": "sr"}
headers1 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "X-INSTANA-T": "d55204082031b541",
    "X-INSTANA-S": "d55204082031b541",
    "X-INSTANA-L": "1,correlationType=web;correlationId=d55204082031b541",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Referer": "https://www.maxbet.rs/leagues/S",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers"
}

results = []

def get_tasks(session):
    tasks = []
    for id in competition:
        url1 = f"https://www.maxbet.rs/restapi/offer/sr/sport/S/league/{id}/mob"
        tasks.append(session.get(url1, headers=headers1, params=querystring1))
    return tasks

async def fetch_with_retry(session, url, headers, params, retries=3):
    for attempt in range(retries):
        try:
            async with session.get(url, headers=headers, params=params) as response:
                return await response.json()
        except aiohttp.ClientDisconnectedError as e:
            if attempt < retries - 1:
                continue
            else:
                raise e

async def matches():
    async with aiohttp.ClientSession() as session:
        tasks = get_tasks(session)
        responses = await asyncio.gather(*tasks)
        for response in responses:
            try:
                results.append(await response.json())
            except aiohttp.ClientError as e:
                print(f"Error fetching data: {e}")
    return results

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
results = loop.run_until_complete(matches())
loop.close()

for rez in results:
    for result in rez['esMatches']: 
        ts = int(result['kickOffTime'])
        ts /= 1000
        if 'odds' not in result:
            print(result['id'])
            continue
        data['datum'].append(str(datetime.fromtimestamp(ts).strftime('%Y-%m-%d')))
        data['vreme'].append(str(datetime.fromtimestamp(ts).strftime('%H:%M:%S')))
        data['domacin'].append(result['home'])
        data['gost'].append(result['away'])
        data['ki_1'].append(result['odds'].get('1', 0))
        data['ki_x'].append(result['odds'].get('2', 0))
        data['ki_2'].append(result['odds'].get('3', 0))
        data['gg'].append(result['odds'].get('272', 0))
        data['ng'].append(result['odds'].get('273', 0))
        data['0-2'].append(result['odds'].get('22', 0))
        data['3+'].append(result['odds'].get('24', 0))

end = time.time()
print(end - start)

df = pd.DataFrame(data)
df.to_csv('maxbet.csv', index=False)
