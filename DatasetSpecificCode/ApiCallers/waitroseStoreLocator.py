import json
import os

import pandas as pd
import requests

resultsDir = '/Users/james_hargreaves/PycharmProjects/dataplay_a2/DatasetSpecificCode/ApiCallers/WaitroseStoreResults'

# NOTE that this will only return 5 results so not completed.
def callApiAndPutInFile():
    url = 'https://www.waitrose.com/shop/NearestBranchesCmd'
    params = {
        'latitude':54,
        'longitude':-4,
        "fromMultipleBranch": True,
        '_': '1630322446214',

        # 'distance': 1000000,
        # 'apikey': "kxBdM2chFwZjNvG2PwnSn3sj6C53dLEY",
        'limit': 1000,
        # 'offset': 0,
        # 'storeformat': 'supermarket',
    }
    headers = { }
    data = requests.get(url, params=params, headers=headers)
    with open('{}/result.json'.format(resultsDir), 'w+') as fp:
        fp.write(data.text)



def parseWaitroseResultsJson():
    locs = []
    results = os.listdir(resultsDir)
    for filename in results:
        json_obj = json.load(open(os.path.join(resultsDir, filename) , 'r'))

        for row in json_obj['branchList']:
            geo = row['location']
            locs.append({
                'lat': geo['latitude'],
                'lng': geo['longitude'],
            })
    return locs

# callApiAndPutInFile()
storeLocs = parseWaitroseResultsJson()
print(len(storeLocs))
json.dump(storeLocs, open('/data/points/morisons.json', 'w+'))
# x = 1

