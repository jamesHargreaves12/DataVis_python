import json
import os

import pandas as pd
import requests

resultsDir = '/Users/james_hargreaves/PycharmProjects/dataplay_a2/ApiCallers/MorisonsStoreResults'
def callApiAndPutInFile():
    # for pageNumber in range(1,39):
    # for pageNumber in range(1, 2):
    url = 'https://api.morrisons.com/location/v2/stores'
    params = {
        'lat':54,
        'lon':-4,
        'distance': 1000000,
        'apikey': "kxBdM2chFwZjNvG2PwnSn3sj6C53dLEY",
        'limit': 1000,
        'offset': 0,
        'storeformat': 'supermarket',
    }
    headers = {    }
    data = requests.get(url, params=params, headers=headers)
    with open('{}/result.json'.format(resultsDir), 'w+') as fp:
        fp.write(data.text)


def parseMorisonsResultsJson():
    locs = []
    results = os.listdir(resultsDir)
    for filename in results:
        json_obj = json.load(open(os.path.join(resultsDir, filename) , 'r'))

        for row in json_obj['stores']:
            geo = row['location']
            locs.append({
                'lat': geo['latitude'],
                'lng': geo['longitude'],
            })
    return locs

callApiAndPutInFile()
storeLocs = parseMorisonsResultsJson()
print(len(storeLocs))
json.dump(storeLocs, open('/data/points/morisons.json', 'w+'))
# x = 1

