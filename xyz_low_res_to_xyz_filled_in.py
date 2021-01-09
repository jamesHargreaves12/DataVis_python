import itertools
import os

import matplotlib.pyplot as plt
import csv

from tqdm import tqdm

from helpers import FORCE_OVERWRITE, FileType, FILE_LOCATIONS
from whole_uk import UkLandmass

print(os.path.basename(__file__))


for filename in os.listdir(FILE_LOCATIONS[FileType.XYZ_LOW_RES]):
    filepath_in = os.path.join(FILE_LOCATIONS[FileType.XYZ_LOW_RES], filename)
    filepath_out = os.path.join(FILE_LOCATIONS[FileType.XYZ_FILLED_IN], filename)

    if os.path.exists(filepath_out) and not FORCE_OVERWRITE:
        continue

    ys = set()
    xs = set()
    xy_to_z = {}
    for x, y, z in tqdm(csv.reader(open(filepath_in)), position=0, leave=True):
        if x == 'X':
            # skip header row
            continue
        xs.add(x)
        ys.add(y)
        xy_to_z[(x, y)] = z

    xs_sorted = list(sorted(map(float, xs)))
    ys_sorted = list(sorted(map(float, ys)))
    diffs_y = [ys_sorted[i] - ys_sorted[i-1] for i in range(1,len(ys_sorted))]
    diffs_x = [xs_sorted[i] - xs_sorted[i-1] for i in range(1,len(xs_sorted))]
    # fairly certain this threshold currently does nothing TODO check and remove
    y_threshold = min(diffs_y)

    uk_landmass = UkLandmass('data/xyz/gbr_pd_2020_1km_UNadj_ASCII_XYZ.csv', min(diffs_x))

    seen_keys = set()
    out_template = "{},{},{}\n"
    with open(filepath_out, 'w+') as out_fp:
        out_fp.write(out_template.format("X", "Y", "Z"))
        for y in tqdm(ys):
            valid_xs = uk_landmass.filter_included_all_y(xs_sorted, float(y), y_threshold)
            for x in valid_xs:
                z = xy_to_z.get((str(x), y), "0")
                if z != "0":
                    seen_keys.add((str(x), y))
                out_fp.write(out_template.format(x, y, z))
