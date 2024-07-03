from datetime import datetime,timedelta
import json
import pytz
import pandas as pd
import time
import asyncio
import aiohttp
import requests

start = time.time()

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

now = datetime.now()
d_string = now.strftime("%Y-%m-%d")
t_string = now.astimezone(pytz.timezone('GMT')).strftime("%H:%M:%S")

url2 = "https://meridianbet.rs/sails/sidebars/standard"
headers2 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Referer": "https://meridianbet.rs/sr/kladjenje/fudbal",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers"
}

response1 = requests.get(url2, headers=headers2)
response_text = response1.json()['sports'][0]

games = []
list_of_ids = []

for country in response_text['regions']:
    id_list = []
    for liga in country['leagues']:
        id_list.append(str(liga['id']))
    list_of_ids.append(",".join(id_list))

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Accept": "",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Referer": "https://meridianbet.rs/sr/kladjenje/fudbal",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin"
}

headers1 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Referer": "https://meridianbet.rs/sr/kladjenje/fudbal/engleska",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers"
}

async def fetch_json(session, url, headers):
    async with session.get(url, headers=headers) as response:
        return await response.json()

async def get_league_games():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for league_ids in list_of_ids:
            url = f"https://meridianbet.rs/sails/sport-leagues-with-events/58/leagues/{league_ids}/date/{d_string}T{t_string}+01:00/filter/all/filterPosition/0,0,0"
            tasks.append(fetch_json(session, url, headers))
        responses = await asyncio.gather(*tasks)
        return responses

async def get_game_details():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for game in games:
            url = f"https://meridianbet.rs/sails/events/{game}"
            tasks.append(fetch_json(session, url, headers1))
        responses = await asyncio.gather(*tasks)
        return responses

async def main():
    league_games_responses = await get_league_games()
    for result in league_games_responses:
        for mac in result['events']:
            for mec in mac['events']:
                games.append(mec['id'])

    game_details_responses = await get_game_details()
    for game in game_details_responses:
        match_date_str = mec['startTime'][:19]
        match_date = datetime.strptime(match_date_str, '%Y-%m-%dT%H:%M:%S')
        adjusted_match_date = match_date + timedelta(hours=2)
        datum = adjusted_match_date.strftime('%Y-%m-%d')
        sat = adjusted_match_date.strftime('%H:%M:%S')
        data['datum'].append(datum)
        data['vreme'].append(sat)

        data['domacin'].append(game['team'][0]['name'])
        data['gost'].append(game['team'][1]['name'])
        ki, gg, gol = False, False, False

        for igre in game['market']:
            if igre['templateName'] in ["1x2", "Match Result"]:
                data['ki_1'].append(igre['selection'][0]['price'])
                data['ki_x'].append(igre['selection'][1]['price'])
                data['ki_2'].append(igre['selection'][2]['price'])
                ki = True
            if igre['templateName'] in ["Both teams to score", "Both Teams To Score"]:
                data["gg"].append(igre['selection'][0]['price'])
                data["ng"].append(igre['selection'][1]['price'])
                gg = True
            if 'overUnder' in igre and igre['overUnder'] == "2.5" and igre['templateName'] == "Total":
                data["0-2"].append(igre['selection'][0]['price'])
                data["3+"].append(igre['selection'][1]['price'])
                gol = True

        if not ki:
            data["ki_1"].append(0)
            data["ki_x"].append(0)
            data["ki_2"].append(0)
        if not gg:
            data['gg'].append(0)
            data['ng'].append(0)
        if not gol:
            data['0-2'].append(0)
            data['3+'].append(0)

asyncio.run(main())

df = pd.DataFrame(data)
df.to_csv('meridian.csv', index=False)

end = time.time()
print(f"Execution time: {end - start} seconds")
