import collections
import math
import os

import numpy as np
import pandas as pd
from shapely.geometry import Polygon
from tqdm import tqdm

from helpers import get_next_bounds, get_rect_verts, scale_z, verts_for_polygon, scale_to_texture, \
    get_resolution_multiplier, get_buckets, FORCE_OVERWRITE, FileType, FILE_LOCATIONS, getFilepaths, log

FLAG_AVG_DATA_NOT_AREA = True


def processEntityXyzToXyzLowResWithResolution(entityName, forceOverwrite, heightX, heightY):
    filepath_in, filepath_out = getFilepaths(entityName, FileType.XYZ, FileType.XYZ_LOW_RES, forceOverwrite)

    log("Processing {}".format(filepath_in))
    df = pd.read_csv(filepath_in)
    log("Shape {}".format(df.shape))
    xs = np.sort(df['X'].unique())
    ys = np.sort(df['Y'].unique())

    # get resolution multiplier
    res_x = get_resolution_multiplier(xs, heightX)
    res_y = get_resolution_multiplier(ys, heightY)

    log("Resolution = ({},{})".format(res_x, res_y))
    log("Put in Buckets")
    x_find_bucket, x_limits = get_buckets(xs, res_x)
    y_find_bucket, y_limits = get_buckets(ys, res_y)
    buckets = collections.defaultdict(list)
    for i, row in tqdm(df.iterrows()):
        buckets[(x_find_bucket(row['X']), y_find_bucket(row['Y']))].append(row['Z'])
    log('Convert buckets back to dataframe')
    df_dict = {'X': [], 'Y': [], 'Z': []}
    for (x, y), vals in tqdm(buckets.items()):
        min_x, max_x = x_limits[x]
        min_y, max_y = y_limits[y]
        df_dict['X'].append(min_x)
        df_dict['Y'].append(min_y)
        if FLAG_AVG_DATA_NOT_AREA:
            df_dict['Z'].append(sum(vals) / len(vals))
        else:
            df_dict['Z'].append(sum(vals) / res_x / res_y)

    df_low_res = pd.DataFrame.from_dict(df_dict)
    df_low_res.to_csv(filepath_out, index=False)


def processEntityXyzToXyzLowRes(entityName, forceOverwrite):
    processEntityXyzToXyzLowResWithResolution(entityName, forceOverwrite, 200, 200)


def processEntityXyzToXyzLowResEngWales(entityName, forceOverwrite):
    processEntityXyzToXyzLowResWithResolution(entityName, forceOverwrite, 120, 120)


if __name__ == '__main__':
    log(os.path.basename(__file__))
    processEntityXyzToXyzLowResEngWales('englandWales', True)
    # for filename in os.listdir(FILE_LOCATIONS[FileType.XYZ]):
    #     entityName = os.path.splitext(filename)[0]
    #     filepath_out = os.path.join(FILE_LOCATIONS[FileType.OBJ], entityName + '.csv')
    #
    #     if os.path.exists(filepath_out) and not FORCE_OVERWRITE:
    #         continue
    #
    #     processEntityXyzToXyzLowRes(entityName, FORCE_OVERWRITE)

