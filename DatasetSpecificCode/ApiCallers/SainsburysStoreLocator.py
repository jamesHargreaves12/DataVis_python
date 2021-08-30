import json
import os

import pandas as pd
import requests

resultsDir = '/Users/james_hargreaves/PycharmProjects/dataplay_a2/ApiCallers/SainsburysStoreResults'
def callApiAndPutInFile():
    for pageNumber in range(1,30):
        url = 'https://stores.sainsburys.co.uk/api/v1/stores/'
        params = {
            'lat': 54,
            'lon': -4,
            'limit': 50,
            'store_type': 'main,local',
            'within': 340,
            'page': pageNumber,
            'fields': 'name,location',
            'api_client_id': 'slfe'
        }
        headers = {
           # 'referer': 'https://www.tesco.com/',
           # 'origin': 'https://www.tesco.com',
           # "X-AppKey": "store-locator-web-cde",
        }
        data = requests.get(url, params=params, headers=headers)
        with open('{}/result{}.json'.format(resultsDir,pageNumber), 'w+') as fp:
            fp.write(data.text)


def parseSainsburiesResultsJson():
    locs = []
    results = os.listdir(resultsDir)
    for filename in results:
        json_obj = json.load(open(os.path.join(resultsDir, filename) , 'r'))

        for row in json_obj['results']:
            geo = row['location']
            locs.append({
                'lat': geo['lat'],
                'lng': geo['lon'],
            })
    return locs

# callApiAndPutInFile()
storeLocs = parseSainsburiesResultsJson()
print(len(storeLocs))
json.dump(storeLocs, open('/data/points/sainsburys.json', 'w+'))
# x = 1

