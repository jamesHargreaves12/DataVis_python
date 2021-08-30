import json
import os

import pandas as pd
import requests

resultsDir = '/Users/james_hargreaves/PycharmProjects/dataplay_a2/ApiCallers/tescoStoreResults'
def callApiAndPutInFile():
    for pageStart in range(0,2800,100):
        url = ' https://api.tesco.com/tescolocation/v3/locations/search'
        params = {
            'offset': pageStart,
            'limit': 100,
            # 'sort:': 'near:%2251.5,-0.58%22',
            'filter': 'category:Store AND isoCountryCode:x-uk',
            'fields': 'name,geo',
        }
        headers = {
           'referer': 'https://www.tesco.com/',
           'origin': 'https://www.tesco.com',
           "X-AppKey": "store-locator-web-cde",
        }
        data = requests.get(url, params=params, headers=headers)
        with open('{}/result{}.json'.format(resultsDir,pageStart), 'w+') as fp:
            fp.write(data.text)


def parseTescoResultsJson():
    locs = []
    results = os.listdir(resultsDir)
    for filename in results:
        json_obj = json.load(open(os.path.join(resultsDir, filename) , 'r'))

        for row in json_obj['results']:
            if 'geo' not in row['location']:
                # contact tesco about the results
                print(row)
                continue
            geo = row['location']['geo']['coordinates']
            locs.append({
                'lng': geo['longitude'],
                'lat': geo['latitude'],
            })
    return locs

# callApiAndPutInFile()
storeLocs = parseTescoResultsJson()
print(len(storeLocs))
json.dump(storeLocs, open('/data/points/tesco.json', 'w+'))
x = 1

