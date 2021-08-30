import os
import csv

from tqdm import tqdm

from helpers import FORCE_OVERWRITE, FileType, FILE_LOCATIONS, getFilepaths, log
from whole_uk import UkLandmass

SOURCE_OF_TRUTH_FILEPATH = 'data/masks/uk.csv'
SOURCE_OF_TRUTH_ENGLAND_WALES = 'data/masks/englandWales.csv'


def processEntityLowResToFilledIn(entityName, forceOverwrite=False, sourceOfTruth=SOURCE_OF_TRUTH_FILEPATH):
    filepath_in, filepath_out = getFilepaths(entityName, FileType.XYZ_LOW_RES, FileType.XYZ_FILLED_IN, forceOverwrite)
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
    diffs_y = [ys_sorted[i] - ys_sorted[i - 1] for i in range(1, len(ys_sorted))]
    diffs_x = [xs_sorted[i] - xs_sorted[i - 1] for i in range(1, len(xs_sorted))]
    # fairly certain this threshold currently does nothing TODO check and remove
    y_threshold = min(diffs_y)
    x_threshold = min(diffs_x)

    uk_landmass = UkLandmass(sourceOfTruth, x_threshold)
    count = 0
    out_template = "{},{},{}\n"
    with open(filepath_out, 'w+') as out_fp:
        out_fp.write(out_template.format("X", "Y", "Z"))
        for y in tqdm(ys):
            valid_xs = uk_landmass.filter_included_all_y(xs_sorted, float(y), y_threshold, x_threshold)
            for x in valid_xs:
                z = xy_to_z.get((str(x), y), 'nothing found')
                if z == 'nothing found':
                    out_fp.write(out_template.format(x, y, 0))
                    count += 1
                else:
                    out_fp.write(out_template.format(x, y, z))
    log("0 value filled in for {} pixels".format(count))


def processEntityLowResToFilledInEnglandAndWales(entityName, forceOverwrite=False):
    processEntityLowResToFilledIn(entityName, forceOverwrite, SOURCE_OF_TRUTH_ENGLAND_WALES)


if __name__ == '__main__':
    for filename in os.listdir(FILE_LOCATIONS[FileType.XYZ_LOW_RES]):
        entityName = os.path.splitext(filename)[0]
        _, filepath_out = getFilepaths(entityName, FileType.XYZ_LOW_RES, FileType.XYZ_FILLED_IN)

        if os.path.exists(filepath_out) and not FORCE_OVERWRITE:
            continue

        processEntityLowResToFilledIn(entityName, FORCE_OVERWRITE)
