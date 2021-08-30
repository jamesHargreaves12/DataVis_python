import json
import os

import pandas as pd
import requests

resultsDir = '/Users/james_hargreaves/PycharmProjects/dataplay_a2/ApiCallers/MandSStoreResults'
def callApiAndPutInFile():
    # for pageNumber in range(1,39):
    # for pageNumber in range(1, 2):
    url = 'https://api.marksandspencer.com/v1/stores'
    params = {
        'latlong':'54,-4',
        'limit': 10000,
        'radius': 700,
        'apikey': 'aVCi8dmPbHgHrdCv9gNt6rusFK98VokK'
    }
    headers = { }
    data = requests.get(url, params=params, headers=headers)
    with open('{}/result.json'.format(resultsDir), 'w+') as fp:
        fp.write(data.text)


def parseMandSResultsJson():
    locs = []
    results = os.listdir(resultsDir)
    for filename in results:
        json_obj = json.load(open(os.path.join(resultsDir, filename) , 'r'))

        for row in json_obj['results']:
            geo = row['coordinates']
            locs.append({
                'lat': geo['latitude'],
                'lng': geo['longitude'],
            })
    return locs

callApiAndPutInFile()
storeLocs = parseMandSResultsJson()
print(len(storeLocs))
json.dump(storeLocs, open('/data/points/mands.json', 'w+'))
# x = 1

