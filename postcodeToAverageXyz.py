import csv
import math
import os
from collections import defaultdict

import pandas as pd
from tqdm import tqdm
import numpy as np
from helpers import log, FILE_LOCATIONS, FileType, get_next_bounds, LogLevel, logInfo, BASE_FILEPATH, getFilepaths


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def findLargestLessThan(xs, x):
    # just a binary search could be smarter as the values are approx
    # uniformly distributed but this is good enough for now I think
    start, end = 0, len(xs)
    count = 0
    while end - start > 1 and count < 20:
        mid = int((start + end) / 2)
        if xs[mid] < x:
            start = mid
        else:
            end = mid
        count += 1
    return xs[start]


def getDataFrameFromDataFile(fileName):
    dfFromFile = pd.read_csv(fileName, header=None)
    dfFromFile = dfFromFile[[1, 3]]
    dfFromFile.rename(columns={1: "pricePaid", 3: "postcode"}, inplace=True)
    return dfFromFile


PIXEL_FILENAME = os.path.join(BASE_FILEPATH, FILE_LOCATIONS[FileType.MASKS], 'englandWalesLowRes.csv')


def postCodeDataToAggregateXYZ(df, filepathOut, activeFieldName='pricePaid', aggregateMethod=lambda x: sum(x)/len(x)):
    logInfo('Reading postcode conversion file')
    df_postcode = pd.read_csv(
        'data/raw/postcode_to_latlong/open_postcode_geo.csv',
        header=None)
    df_postcode = df_postcode[[0, 7, 8]]
    df_postcode.rename(columns={0: 'postcode', 7: 'lat', 8: 'long'}, inplace=True)

    logInfo('File 1 has {} records'.format(df_postcode.shape[0]))

    df_postcode2 = pd.read_csv(
        'data/raw/postcode_to_latlong/ukpostcodes.csv')
    df_postcode2 = df_postcode2[['postcode', 'latitude', 'longitude']]
    df_postcode2.rename(columns={'latitude': 'lat', 'longitude': 'long'}, inplace=True)

    logInfo('File 2 has {} records'.format(df_postcode2.shape[0]))

    logInfo('Joining datasets')

    df = df.merge(df_postcode2, on='postcode', how='left')

    # those which failed to map with df_postcode
    dfFailedMap = np.logical_or(df['lat'].isna(), df['long'].isna())
    dfPostcodeNoMapDf = df[dfFailedMap][[activeFieldName, 'postcode']]
    dfPostcodeNoMapDf = dfPostcodeNoMapDf.merge(df_postcode, on='postcode', how='inner')

    df = pd.concat([df[np.logical_not(dfFailedMap)], dfPostcodeNoMapDf], ignore_index=True)

    logInfo('Loading example file for cell values')

    xyz_example = csv.reader(open(PIXEL_FILENAME))
    xyz_example = [x for x in xyz_example]  # make it a list so we have total count for tqdm
    xyz_example = xyz_example[1:]  # skip the headers

    xs = sorted([float(x) for x, _, _ in xyz_example])
    ys = sorted([float(y) for _, y, _ in xyz_example])
    minx = min(xs)
    miny = min(ys)

    logInfo('Aggregating per cell')
    aggs = defaultdict(list)
    logInfo(('shape:', df.shape))
    for index, row in tqdm(df.iterrows()):
        if not isfloat(row['lat']) or not isfloat(row['long']) or math.isnan(float(row['lat'])) or math.isnan(
                float(row['long'])):
            log('Can\'t map postcode to lat long {} ({},{})'.format(row['postcode'], row['lat'], row['long']),
                LogLevel.WARN)
            continue
        lx = findLargestLessThan(xs, float(row['long']))
        ly = findLargestLessThan(ys, float(row['lat']))
        if (lx == minx or ly == miny) and not row['postcode'].startswith('TR21') and not row['postcode'].startswith('TR25'):
            log('min value given for  row with postcode and lat long {} ({},{})'
                .format(row['postcode'], row['lat'], row['long']),  LogLevel.WARN)

        aggs[(lx, ly)].append(row[activeFieldName])

    logInfo("Writing output")
    numberPerCell = []
    zVals = []
    zValsFiltered = []
    with open(filepathOut, 'w+') as fp:
        outtemplate = "{},{},{}\n"
        fp.write(outtemplate.format('X', 'Y', 'Z'))
        for x, y in sorted(aggs.keys()):
            allPrices = aggs[x, y]
            z = aggregateMethod(allPrices)
            numberPerCell.append(len(allPrices))
            zVals.append(z)
            if z > 2000000: #2M
                log(['High value found: ', z, x, y, allPrices], LogLevel.WARN)
            if len(allPrices) > 3:
                zValsFiltered.append(z)
                fp.write(outtemplate.format(x, y, z))
    # logInfo("Number of data points per cell is:")
    # logInfo(numberPerCell)
    # logInfo("Distribution of values without filter")
    # logInfo(zVals)
    # logInfo("Distribution of values with filter")
    # logInfo(zValsFiltered)


def processPostcodeToMeanXYZLowRes(name, forceOverwrite=False):
    filepath_in, filepath_out = getFilepaths(name, FileType.POSTCODE, FileType.XYZ_LOW_RES, forceOverwrite)
    logInfo('Reading price paid files')
    df = getDataFrameFromDataFile(filepath_in)
    initialNumberOfRecords = df.shape[0]
    # throw away any rows which don't have a post code ~0.40% are thrown away for the 2020 data
    df = df[df['postcode'].notna()]
    filterNoPostcodeNumRecord = df.shape[0]
    logInfo('Removed {} out of {} ({}%)records due to missing postcode'
            .format(initialNumberOfRecords-filterNoPostcodeNumRecord,
                    initialNumberOfRecords,
                    round(100*(initialNumberOfRecords-filterNoPostcodeNumRecord)/initialNumberOfRecords,2)))

    postCodeDataToAggregateXYZ(df, filepath_out, activeFieldName='pricePaid', aggregateMethod=lambda x: sum(x)/len(x))


def processPostcodeToMedianXYZLowRes(name, forceOverwrite=False):
    filepath_in, filepath_out = getFilepaths(name, FileType.POSTCODE, FileType.XYZ_LOW_RES, forceOverwrite)
    logInfo('Reading price paid files')
    df = getDataFrameFromDataFile(filepath_in)
    initialNumberOfRecords = df.shape[0]
    # throw away any rows which don't have a post code ~0.40% are thrown away for the 2020 data
    df = df[df['postcode'].notna()]
    filterNoPostcodeNumRecord = df.shape[0]
    logInfo('Removed {} out of {} ({}%)records due to missing postcode'
            .format(initialNumberOfRecords-filterNoPostcodeNumRecord,
                    initialNumberOfRecords,
                    round(100*(initialNumberOfRecords-filterNoPostcodeNumRecord)/initialNumberOfRecords,2)))

    postCodeDataToAggregateXYZ(df, filepath_out, activeFieldName='pricePaid', aggregateMethod=lambda x: sorted(x)[len(x)//2])


if __name__ == '__main__':
    processPostcodeToMedianXYZLowRes('pricePaid18-20', True)
