import csv
import math
import os
import sys
from collections import defaultdict
import fiona
from shapely.geometry import shape, point
from shapely.ops import cascaded_union
import matplotlib.pyplot as plt
from tqdm import tqdm
import geopandas as gpd
import pandas as pd
import shapely.wkt

from helpers import FileType, getFilepaths

csv.field_size_limit(sys.maxsize)


withPlot = False
minArea = 0.05


def plot(filepath):
    df = pd.read_csv(filepath)
    df['geometry'] = df['geometry'].apply(shapely.wkt.loads)

    pds_poly = gpd.GeoDataFrame(df)
    pds_poly = pds_poly.set_crs('EPSG:4326')
    pds_poly.plot(column='Z', cmap='viridis')
    plt.grid()
    plt.show()


def ProcessMSOAEntityGeoDfToMerged(entityName, forceOverwrite=False):
    filepath_in, filepath_out = getFilepaths(entityName, FileType.MSOA_GEO_DF, FileType.MSOA_MERGED, forceOverwrite)
    print('reading and loading data structures')
    zs = {}
    key_to_pop = {}
    polys = {}
    v_to_key = defaultdict(set)
    key_to_vs = defaultdict(set)
    a = []
    key = 0
    ignore_keys = set()
    with open(filepath_in, 'r') as fp:
        reader = csv.reader(fp)
        next(reader)  # skip headers
        for i, (z, p, pop) in tqdm(enumerate(reader)):
            loaded = shapely.wkt.loads(p)
            ps = [loaded] if p.startswith('POLYGON') else list(loaded)
            for poly in ps:
                zs[key] = float(z)
                key_to_pop[key] = float(pop)
                polys[key] = poly
                a.append((key, poly.area))
                for v in poly.exterior.coords:
                    key_to_vs[key].add(v)
                    v_to_key[v].add(key)
                key += 1

    print(sorted(a, key=lambda x: x[1])[-1])
    sorted_as = sorted(a, key=lambda x: x[1])

    print('merging')
    i = 0
    # This is expensive at relatively deterministic for any z value so the result could be turned into a map and then
    # dramatically sped up. But once again this is an optimisation.
    while sorted_as[0][1] < minArea:
        i += 1
        sorted_as = sorted(a, key=lambda x: x[1])
        first = True
        smallestKey = 0
        while smallestKey in ignore_keys or first:
            first = False
            smallestKey, smallestArea = sorted_as.pop(0)

        vs = key_to_vs[smallestKey]
        neighboursSeenOnce = set()
        neighboursSeenAtLeastTwice = set()
        for v in vs:
            for nKey in v_to_key[v]:
                if nKey in neighboursSeenOnce:
                    neighboursSeenAtLeastTwice.add(nKey)
                    neighboursSeenOnce.remove(nKey)
                elif nKey not in neighboursSeenAtLeastTwice:
                    neighboursSeenOnce.add(nKey)
        neighboursSeenAtLeastTwice.remove(smallestKey)
        neighboursSeenAtLeastTwice -= ignore_keys
        if len(neighboursSeenAtLeastTwice) == 0:
            ignore_keys.add(smallestKey)
            continue
        smallestNeighbourKey = neighboursSeenAtLeastTwice.pop()
        smallestNeighbourArea = polys[smallestNeighbourKey].area
        for nKey in neighboursSeenAtLeastTwice:
            area = polys[nKey].area
            if smallestNeighbourArea > area:
                smallestNeighbourArea = area
                smallestNeighbourKey = nKey
        newPoly = cascaded_union([polys[smallestKey], polys[smallestNeighbourKey]])

        polys[key] = newPoly
        popSmallest = key_to_pop[smallestKey]
        popNeighbour = key_to_pop[smallestNeighbourKey]
        key_to_pop[key] = popSmallest + popNeighbour
        zs[key] = (zs[smallestKey] * popSmallest + zs[smallestNeighbourKey] * popNeighbour) / (
                popSmallest + popNeighbour)
        # would likely be more efficient to also move the data from the larger data structures but that is an
        # optimisation we can do later.
        a = [x for x in a if x[0] not in [smallestKey, smallestNeighbourKey]] + [(key, newPoly.area)]
        for v in newPoly.exterior.coords:
            key_to_vs[key].add(v)
            v_to_key[v].add(key)
        key += 1
        ignore_keys.add(smallestKey)
        ignore_keys.add(smallestNeighbourKey)
        if i % 100 == 0:
            print(i, smallestArea)

    print('writing')
    template = "{},\"{}\"\n"
    with open(filepath_out, 'w+') as fp:
        fp.write("Z,geometry\n")
        for k in (polys.keys() - ignore_keys):
            fp.write(template.format(zs[k], polys[k]))

    # Can be useful for debugging:
    # with open('./data/tmp/testMergedOrder.csv','w+') as fp:
    #     fp.write("Z,geometry\n")
    #     for i,k in enumerate(polys.keys() - ignore_keys):
    #         fp.write(template.format(i, polys[k]))

    if withPlot:
        print('plotting')
        plot(filepath_out)

    print('finished')


if __name__ == '__main__':
    ProcessMSOAEntityGeoDfToMerged('FY2018NetAnnualIncome', True)
