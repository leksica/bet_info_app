import aiohttp
import asyncio
import json
import pandas as pd
from datetime import datetime, timedelta

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

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Accept": "application/utf8+json, application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "",
    "Content-Type": "application/json",
    "Language": "sr-Latn",
    "OfficeId": "6",
    "Origin": "https://www.pinnbet.rs",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Referer": "https://www.pinnbet.rs/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "TE": "trailers"
}

async def fetch(session, url):
    async with session.get(url, headers=headers) as response:
        return await response.json()

async def process_page(session, c):
    url = f"https://sportweb.pinnbet.rs/SportBookCacheWeb/api/offer/competitionsWithEventsStartingSoonForSportV2/25/{c*25}/false/2026-11-17T07:27:23.591/1"
    response = await fetch(session, url)
    
    if 'competitions' not in response or not response['competitions']:
        return False 

    for takm in response['competitions']:
        for mec in takm['events']:
            if 'dateTime' not in mec or 'name' not in mec:
                continue
            match_date_str = mec['dateTime']
            match_date = datetime.strptime(match_date_str, '%Y-%m-%dT%H:%M:%S')
            adjusted_match_date = match_date + timedelta(hours=1)
            datum = adjusted_match_date.strftime('%Y-%m-%d')
            sat = adjusted_match_date.strftime('%H:%M:%S')
            data['datum'].append(datum)
            data['vreme'].append(sat)            
            
            
            x = mec['name'].split(" - ")
            data['domacin'].append(x[0])
            data['gost'].append(x[1])
            
            nula, tri, gg, ng, ki = True, True, True, True, True
            for igre in mec['bets']:
                if igre['betTypeId'] == 1:
                    if len(igre['betOutcomes']) == 3 and igre['betOutcomes'][0]['odd'] is not None:
                        data['ki_1'].append(igre['betOutcomes'][0]['odd'])
                        data['ki_x'].append(igre['betOutcomes'][1]['odd'])
                        data['ki_2'].append(igre['betOutcomes'][2]['odd'])
                        ki = False
                if igre['betTypeId'] == 2 and igre['sBV'] == "2.5":
                    for igra in igre['betOutcomes']:
                        if igra['name'] == "manje":
                            data['0-2'].append(igra['odd'])
                            nula = False
                        if igra['name'] == "više" and igra['odd'] is not None:
                            data['3+'].append(igra['odd'])
                            tri = False
                if igre['betTypeId'] == 874:
                    for igra in igre['betOutcomes']:
                        if igra['name'] == "GG":
                            data['gg'].append(igra['odd'])
                            gg = False
                        if igra['name'] == "NG":
                            data['ng'].append(igra['odd'])
                            ng = False
            if ki:
                data['ki_1'].append(0)
                data['ki_x'].append(0)
                data['ki_2'].append(0)
            if nula:
                data['0-2'].append(0)
            if tri:
                data['3+'].append(0)
            if gg:
                data['gg'].append(0)
            if ng:
                data['ng'].append(0)
    
    return True  # More pages to process

async def main():
    async with aiohttp.ClientSession() as session:
        c = 0
        while True:
            more_pages = await process_page(session, c)
            if not more_pages:
                break
            c += 1

# Run the asynchronous main function
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(main())

# Convert data to DataFrame and save as CSV
df = pd.DataFrame(data)
df.to_csv('pinnbet.csv', index=False)
