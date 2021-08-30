import json
import os

import requests

from helpers import noOverwriteOpen, log

resultsDir = '/Users/james_hargreaves/PycharmProjects/dataplay_a2/ApiCallers/IcelandStoreResults'

def callApiAndPutInFile():
    url = 'https://www.iceland.co.uk/on/demandware.store/Sites-icelandfoodsuk-Site/default/Stores-GetNearestStores'
    centers = [(51.9, 0.05) , (51.9, -2.27), (51, -4.56), (52.7, -3.06), (54, -1.66), (55.5, -3.41), (58.1,-2.72), (57.1,-6.1), (53.9,-5.88) ]
    for i, (lat, lon) in enumerate(centers):
        params = {
            'latitude':lat,
            'longitude':lon,
            'countryCode':'GB',
            'distanceUnit': 'mi',
            'maxdistance': 500000,
        }
        headers = {}
        data = requests.get(url, params=params, headers=headers)
        with noOverwriteOpen('{}/result{}.json'.format(resultsDir,i)) as fp:
            fp.write(data.text)


def testCallApiAndPutInFile():
    url = 'https://www.iceland.co.uk/on/demandware.store/Sites-icelandfoodsuk-Site/default/Stores-GetNearestStores'
    centers = [(57.7, -5.74)]
    for i, (lat, lon) in enumerate(centers):
        params = {
            'latitude':lat,
            'longitude':lon,
            'countryCode':'GB',
            'distanceUnit': 'mi',
            'maxdistance': 500000,
        }
        headers = {}
        data = requests.get(url, params=params, headers=headers)
        with noOverwriteOpen('{}/test_Api{}.json'.format(resultsDir,i)) as fp:
            fp.write(data.text)
            log(data)


def parseIcelandResultsJson():
    locs = []
    results = os.listdir(resultsDir)
    alreadySeen = set()
    for filename in results:
        json_obj = json.load(open(os.path.join(resultsDir, filename) , 'r'))

        for key in json_obj['stores']:
            geo = json_obj['stores'][key]
            if (geo['latitude'][:8],geo['longitude'][:8]) in alreadySeen:
                continue
            alreadySeen.add((geo['latitude'][:8],geo['longitude'][:8]))
            locs.append({
                'lat': geo['latitude'],
                'lng': geo['longitude'],
            })
    return locs


testCallApiAndPutInFile()
#
#
#
# callApiAndPutInFile()
# storeLocs = parseIcelandResultsJson()
# print(len(storeLocs))
# json.dump(storeLocs, open('/Users/james_hargreaves/PycharmProjects/dataplay_a2/data/points/iceland.json', 'w+'))
# x = 1

