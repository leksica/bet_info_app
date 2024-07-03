import requests
import json
import pandas as pd
from datetime import datetime

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

i=0
while(True):
    url = "https://beta.mozzartbet.com/betting/matches"

    payload = {"date":"all_days","sort":"bytime","currentPage":i,"pageSize":15,"sportId":1,"competitionIds":[],"search":"","matchTypeId":0}

    headers = {
        "cookie": "i18next=sr; __cf_bm=ERfqyUmAAEIMgserE9_CDK0tuSarUuuGXYrOXLieVxI-1709153715-1.0-AXQEkA0Ts3r053i3CCTA12U9wzDt0KoNFx1PbnYOYXkOO576T%2BXYy%2BnPytIC5iBsT4PpTZho2mHNYAXwPBYoAvc%3D",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Content-Type": "application/json",
        "medium": "WEB",
        "Origin": "https://beta.mozzartbet.com",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Referer": "https://beta.mozzartbet.com/sr/kladjenje/sport/1?date=all_days&sort=bytime",
        "Cookie": "i18next=sr; __cf_bm=Tj5T_TAyamtUovgI8yv0HsQbcFzP68ePbxFUHHPjONI-1709153370-1.0-AU/fwTxzJAV0XaeQB6xY3PElUQ8jD/PF6YoAOvV/wrZWNM0bjT33ibsiws/cHNi6j8F4M8a4h877uJiMVHLnxrg=",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers"
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    if(response.status_code!=200):
        break
    sve = json.loads(response.text)
    if('items' not in sve):
        break
    i+=1
    for game in sve['items']:
        if('odds' not in game):
            continue
        if('specialMatchGroupId' in game):
            continue
        ts = int(game['startTime'])
        ts/=1000
        data['datum'].append(str(datetime.fromtimestamp(ts).strftime('%Y-%m-%d')))
        data['vreme'].append(str(datetime.fromtimestamp(ts).strftime('%H:%M:%S')))
        
        map = str.maketrans({'š':'s','Š':'S','Č':'C','č':'c','ž':'z','Ž':'Z','Ć':'C','ć':'c','Đ':'Dj','đ':'dj'})
        domacin = game['home']['name'].translate(map)
        gost = game['visitor']['name'].translate(map)
        data['domacin'].append(domacin)
        data['gost'].append(gost)
        dodva=False
        tri=False
        gg=False
        ng=False
        for kvota in game['odds']:
            if(kvota['id']==1001001001):
                data['ki_1'].append(kvota['value'])
            if(kvota['id']==1001001002):
                data['ki_x'].append(kvota['value'])
            if(kvota['id']==1001001003):
                data['ki_2'].append(kvota['value'])
            if(kvota['id']==1001003002):
                data['0-2'].append(kvota['value'])
                dodva=True
            if(kvota['id']==1001003004):
                data['3+'].append(kvota['value'])
                tri=True
            if(kvota['id']==1001130001):
                data['gg'].append(kvota['value'])
                gg=True
            if(kvota['id']==1001130002):
                data['ng'].append(kvota['value'])
                ng=True
        if(not dodva):
            data['0-2'].append(0)
        if(not tri):
            data['3+'].append(0)
        if(not gg):
            data['gg'].append(0)
        if(not ng):
            data['ng'].append(0)
df = pd.DataFrame(data)

df.to_csv('mozzart.csv',index = False)
            
