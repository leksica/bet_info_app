import requests
import json
import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
import pandas as pd

start = time.time()

today = datetime.now()
d = today.strftime("%Y-%m-%d")
t = today.strftime("%H:%M:%S")

url = "https://sports-sm-distribution-api.de-2.nsoftcdn.com/api/v1/events"

querystring = {
    "deliveryPlatformId": "3",
    "dataFormat": '{"default":"object","events":"array","outcomes":"array"}',
    "language": '{"default":"sr-Latn","events":"sr-Latn","sport":"sr-Latn","category":"sr-Latn","tournament":"sr-Latn","team":"sr-Latn","market":"sr-Latn"}',
    "timezone": "Europe/Budapest",
    "company": "{}",
    "companyUuid": "4f54c6aa-82a9-475d-bf0e-dc02ded89225",
    "filter[sportId]": "18",
    "filter[from]": f"{d}T{t}",
    "sort": "startsAt,categoryPosition,categoryName,tournamentPosition,tournamentName",
    "offerTemplate": "WEB_OVERVIEW",
    "shortProps": "1"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Referer": "https://sports-sm-web.7platform.net/?companyId=4f54c6aa-82a9-475d-bf0e-dc02ded89225&lang=sr-Latn&auth=b2b&gateway=true&companyName=balkanbet&integrationType=gravityGateway&platform=seven&application=web&section=1-offer&sport=18-fudbal"
}

response = requests.get(url, headers=headers, params=querystring)
text = json.loads(response.text)

data = {
    "datum": [],
    "vreme": [],
    "domacin": [],
    "gost": [],
    "ki_1": [],
    "ki_x": [],
    "ki_2": [],
    "gg": [],
    "ng": [],
    "0-2": [],
    "3+": []
}

games = [str(game['a']) for game in text['data']['events']]

headers1 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Origin": "https://sports-sm-web.7platform.net",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Referer": "https://sports-sm-web.7platform.net/?companyId=4f54c6aa-82a9-475d-bf0e-dc02ded89225&lang=sr-Latn&auth=b2b&gateway=true&companyName=balkanbet&integrationType=gravityGateway&platform=seven&application=web&section=1-offer&sport=18-fudbal"
}

results = []

async def fetch_game_details(session, game_id):
    url1 = f"https://sports-sm-distribution-api.de-2.nsoftcdn.com/api/v1/events/{game_id}"
    querystring1 = {
        "companyUuid": "4f54c6aa-82a9-475d-bf0e-dc02ded89225",
        "id": game_id,
        "language": '{"default":"sr-Latn","events":"sr-Latn","sport":"sr-Latn","category":"sr-Latn","tournament":"sr-Latn","team":"sr-Latn","market":"sr-Latn"}',
        "timezone": "Europe/Budapest",
        "dataFormat": '{"default":"array","markets":"array","events":"array"}'
    }
    async with session.get(url1, headers=headers1, params=querystring1) as response:
        return await response.json()

async def matches():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_game_details(session, game_id) for game_id in games]
        return await asyncio.gather(*tasks)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
results = loop.run_until_complete(matches())
loop.close()

for game in results:
    print(game)
    game_data = game['data']
    match_date_str = game_data['startsAt'][0:19]
    match_date = datetime.strptime(match_date_str, '%Y-%m-%dT%H:%M:%S')
    adjusted_match_date = match_date + timedelta(hours=1)
    datum = adjusted_match_date.strftime('%Y-%m-%d')
    sat = adjusted_match_date.strftime('%H:%M:%S')
    data['datum'].append(datum)
    data['vreme'].append(sat)
    map = str.maketrans({'š': 's', 'Š': 'S', 'Č': 'C', 'č': 'c', 'ž': 'z', 'Ž': 'Z', 'Ć': 'C', 'ć': 'c', 'Đ': 'Dj', 'đ': 'dj'})
    domacin = game_data['competitors'][0]['name'].translate(map)
    gost = game_data['competitors'][1]['name'].translate(map)
    data['domacin'].append(domacin)
    data['gost'].append(gost)
    ki = False
    gg = False
    gol = False
    for igre in game_data['markets']:
        if igre['name'] == "KONAČAN ISHOD":
            for kvota in igre['outcomes']:
                print(kvota['odd'], end=" ")
            data['ki_1'].append(igre['outcomes'][0]['odd'])
            data['ki_x'].append(igre['outcomes'][1]['odd'])
            data['ki_2'].append(igre['outcomes'][2]['odd'])
            ki = True
        if igre['name'] == "OBA TIMA DAJU GOL":
            for kvota in igre['outcomes']:
                if kvota['name'] == "GG":
                    print(kvota['odd'], end=" ")
                    data['gg'].append(kvota['odd'])
                if kvota['name'] == "NG":
                    print(kvota['odd'], end=" ")
                    data['ng'].append(kvota['odd'])
                    gg = True
        if igre['name'] == "UKUPNO GOLOVA":
            for kvota in igre['outcomes']:
                if kvota['name'] == "0-2":
                    print(kvota['odd'], end=" ")
                    data["0-2"].append(kvota['odd'])
                if kvota['name'] == "3+":
                    print(kvota['odd'], end=" ")
                    data["3+"].append(kvota['odd'])
                    gol = True
    if not ki:
        data['ki_1'].append(0)
        data['ki_x'].append(0)
        data['ki_2'].append(0)
    if not gg:
        data['gg'].append(0)
        data['ng'].append(0)
    if not gol:
        data["0-2"].append(0)
        data["3+"].append(0)

df = pd.DataFrame(data)
df.to_csv('balkanbet.csv', index=False)
end = time.time()
print(end - start)
