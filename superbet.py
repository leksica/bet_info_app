import json
import aiohttp
import asyncio
import pandas as pd
from datetime import datetime
from datetime import timedelta


t_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


url = "https://production-superbet-offer-rs.freetls.fastly.net/sb-rs/api/v2/sr-Latn-RS/events/by-date"

querystring = {"offerState": "prematch", "startDate": t_string, "endDate": "2025-02-16 09:00:00"}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://superbet.rs",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Referer": "https://superbet.rs/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
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

async def fetch_initial_data(session):
    async with session.get(url, headers=headers, params=querystring) as response:
        return await response.json()

async def fetch_event_data(session, event_id):
    url1 = f"https://production-superbet-offer-rs.freetls.fastly.net/sb-rs/api/v2/sr-Latn-RS/events/{event_id}"
    querystring1 = {"matchIds": event_id}
    async with session.get(url1, headers=headers, params=querystring1) as response:
        return await response.json()

async def process_event_data(session, game, data):
    if game['sportId'] == 5 and game['marketCount'] > 0 and game['odds'] is not None:
        event_data = await fetch_event_data(session, game['eventId'])
        for kvota in event_data['data']:
            if('odds' not in kvota):
                continue
            x = kvota['matchName'].split("·")
            mapa = str.maketrans({'š': 's', 'Š': 'S', 'Č': 'C', 'č': 'c', 'ž': 'z', 'Ž': 'Z', 'Ć': 'C', 'ć': 'c', 'Đ': 'Dj', 'đ': 'dj'})
            domacin = x[0].translate(mapa)
            gost = x[1].translate(mapa)
            data['domacin'].append(domacin)
            data['gost'].append(gost)

            match_date_str = kvota['matchDate']  
            match_date = datetime.strptime(match_date_str, '%Y-%m-%d %H:%M:%S')
            adjusted_match_date = match_date + timedelta(hours=1)
            datum = adjusted_match_date.strftime('%Y-%m-%d')
            sat = adjusted_match_date.strftime('%H:%M:%S')
            data['datum'].append(datum)
            data['vreme'].append(sat)
            
            ki = gg = ng = nula = tri = True
            
            for spec in kvota['odds']:
                if spec['marketGroupOrder'] == 1:
                    if spec['name'] == "1":
                        data['ki_1'].append(spec['price'])
                    if spec['name'] == "X":
                        data['ki_x'].append(spec['price'])
                    if spec['name'] == "2":
                        data['ki_2'].append(spec['price'])
                        ki = False
                if spec['marketGroupOrder'] == 1739:
                    if spec['name'] == "Da":
                        data['gg'].append(spec['price'])
                        gg = False
                    if spec['name'] == "Ne":
                        data['ng'].append(spec['price'])
                        ng = False
                if spec['marketGroupOrder'] == 1737:
                    if spec['name'] == "Manje 2.5":
                        data['0-2'].append(spec['price'])
                        nula = False
                    if spec['name'] == "Više 2.5":
                        data['3+'].append(spec['price'])
                        tri = False
            
            if ki:
                data['ki_1'].append(0)
                data['ki_2'].append(0)
                data['ki_x'].append(0)
            if ng:
                data['ng'].append(0)
            if gg:
                data['gg'].append(0)
            if nula:
                data['0-2'].append(0)
            if tri:
                data["3+"].append(0)

async def main():
    async with aiohttp.ClientSession() as session:
        initial_data = await fetch_initial_data(session)
        
        tasks = []
        for game in initial_data['data']:
            tasks.append(process_event_data(session, game, data))
        
        await asyncio.gather(*tasks)
        
        df = pd.DataFrame(data)
        df.to_csv('superbet.csv', index=False)

asyncio.run(main())