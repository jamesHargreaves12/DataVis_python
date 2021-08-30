import json
import pandas as pd
import requests


def callApiAndPutInFile(filename='mcdonaldsStores.json'):
    url = 'https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do'
    data = requests.get(url, params={
        'method': 'searchLocation',
        'latitude': '54.294075',
        'longitude': '-3.814595',
        # 'radius': '50',
        'radius': '510',
        # 'maxResults': '15',
        'maxResults': '1500',
        'country': 'gb',
        'language': 'en-gb',
        'showClosed': 'true'
    }, headers={'referer': 'https://www.mcdonalds.com/gb/en-gb/restaurant-locator.html'})
    with open(filename,'w+') as fp:
        fp.write(data.text)

def parseMcdonaldsResultsJson(filename='mcdonaldsStores.json'):
    json_obj = json.load(open('../../mcdonaldsStores.json', 'r'))
    result = []
    for row in json_obj['features']:
        coords = row['geometry']['coordinates']
        result.append({
            'lat': coords[1],
            'lng': coords[0],
        })
    return result

# callApiAndPutInFile()
# storeLocs = parseMcdonaldsResultsJson()
# x = 1

# To do this properly we would want to intersect a cone with a vornoi cell for each point on the map - then further interesect the entire thing with a frame of the uk
# It would be much easier to just calculate the minimum distance of each pixel to the locations hmmmm