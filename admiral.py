import requests
import json
import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
import pandas as pd
start = time.time()

c=0
data = {
    "datum" : [],
    'vreme' : [],
    'domacin' : [],
    'gost' : [],
    'ki_1' : [],
    'ki_x' : [],
    'ki_2' : [],
    'gg' : [],
    'ng' : [],
    '0-2' : [],
    '3+' : []

}
url1 = "https://sport-webapi.admiralbet.rs/SportBookCacheWeb/api/offer/tree/null/true/true/true/2024-06-19T09:15:35.954/2029-06-19T09:15:05.000/false"

headers1 = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Accept": "application/utf8+json, application/json;q=0.9, text/plain;q=0.8, */*;",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "",
    "Content-Type": "application/json",
    "Language": "sr-Latn",
    "OfficeId": "138",
    "Origin": "https://admiralbet.rs",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Referer": "https://admiralbet.rs/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site"
}

response1 = requests.request("GET", url1, headers=headers1)
text1 = json.loads(response1.text)

number_of_games = text1[0]['eventsCount']

url = "https://sport-webapi.admiralbet.rs/SportBookCacheWeb/api/offer/getEventsStartingSoonFilterSelections"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Accept": "application/utf8+json, application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "",
    "Content-Type": "application/json",
    "Language": "sr-Latn",
    "OfficeId": "138",
    "Origin": "https://admiralbet.rs",
    "DNT": "1",
    "Sec-GPC": "1",
    "Connection": "keep-alive",
    "Referer": "https://admiralbet.rs/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site"
}
results =[]
def get_tasks(session):
    i=0
    tasks = []
    while(i<=(number_of_games%25+1)):
        querystring = {"sportId":"1","topN":"25","skipN":str(i*25),"isLive":"false","dateFrom":"2024-02-21T09:39:22.841","dateTo":"2029-02-21T09:38:52.000","eventMappingTypes":"","pageId":"3"}
        tasks.append(session.get(url,headers=headers, params = querystring))
        i+=1
    return tasks
async def matches():
    tasks =[]
    session = aiohttp.ClientSession()
    tasks = get_tasks(session)
    responses = await asyncio.gather(*tasks)
    for response in responses:
        results.append(await response.json())
    await session.close()
    return results
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
results = loop.run_until_complete(matches())
loop.close()
for text in results:
    for mec in text:
        if(mec['eventTypeId']==1):
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
            ki = True
            gg = True
            ng= True
            nula = True
            tri = True
            for kvote in mec['bets']:
                if(kvote['betTypeId']==135):
                    if(len(kvote['betOutcomes'])==3):
                        data['ki_1'].append(kvote['betOutcomes'][0]['odd'])
                        data['ki_x'].append(kvote['betOutcomes'][1]['odd'])
                        data['ki_2'].append(kvote['betOutcomes'][2]['odd'])
                        ki  = False
                if(kvote['betTypeId']==137):
                    if(kvote['sBV']=="2.5"):
                        for kvota in kvote['betOutcomes']:
                            if(kvota['name']=="manje"):
                                data['0-2'].append(kvota['odd'])
                                nula = False
                            if(kvota['name']=="vise"):
                                data['3+'].append(kvota['odd'])
                                tri = False
                if(kvote['betTypeId']==1380):
                    for kvota in kvote['betOutcomes']:
                        if(kvota['name']=="GG"):
                            data['gg'].append(kvota['odd'])
                            gg = False
                        if(kvota['name']=="NG"):
                            data['ng'].append(kvota['odd'])
                            ng = False
            if(ki):
                data['ki_1'].append(0)
                data['ki_2'].append(0)
                data['ki_x'].append(0)
            if(ng):
                data['ng'].append(0)
            if(gg):
                data['gg'].append(0)
            if(nula):
                data['0-2'].append(0)
            if(tri):
                data["3+"].append(0)
end = time.time()
print(end-start)
df = pd.DataFrame(data)
df.to_csv('admiralbet.csv',index = False)