import collections
import math
import os

import numpy as np
import pandas as pd
from shapely.geometry import Polygon
from tqdm import tqdm

from helpers import get_next_bounds, get_rect_verts, scale_z, verts_for_cuboid, scale_to_texture, \
    get_resolution_multiplier, get_buckets, FORCE_OVERWRITE, FileType, FILE_LOCATIONS

HEIGHT_X = 200
HEIGHT_Y = 200

print(os.path.basename(__file__))

for filename in os.listdir(FILE_LOCATIONS[FileType.XYZ]):

    filepath_in = os.path.join(FILE_LOCATIONS[FileType.XYZ], filename)
    filepath_out = os.path.join(FILE_LOCATIONS[FileType.XYZ_LOW_RES], filename)

    if os.path.exists(filepath_out) and not FORCE_OVERWRITE:
        continue

    print("Processing {}".format(filepath_in))
    df = pd.read_csv(filepath_in)
    print("Shape {}".format(df.shape))
    xs = np.sort(df['X'].unique())
    ys = np.sort(df['Y'].unique())

    # get resolution multiplier
    res_x = get_resolution_multiplier(xs, HEIGHT_X)
    res_y = get_resolution_multiplier(ys, HEIGHT_Y)

    print("Resolution = ({},{})".format(res_x, res_y))
    print("Put in Buckets")
    x_find_bucket, x_limits = get_buckets(xs, res_x)
    y_find_bucket, y_limits = get_buckets(ys, res_y)
    buckets = collections.defaultdict(list)
    for i, row in tqdm(df.iterrows()):
        buckets[(x_find_bucket(row['X']), y_find_bucket(row['Y']))].append(row['Z'])
    print('Convert buckets back to dataframe')
    df_dict = {'X': [], 'Y': [], 'Z': []}
    for (x, y), vals in tqdm(buckets.items()):
        min_x, max_x = x_limits[x]
        min_y, max_y = y_limits[y]
        df_dict['X'].append(min_x)
        df_dict['Y'].append(min_y)
        df_dict['Z'].append(sum(vals) / res_x / res_y)

    df_low_res = pd.DataFrame.from_dict(df_dict)
    df_low_res.to_csv(filepath_out, index=False)
    print("*" * 30)
