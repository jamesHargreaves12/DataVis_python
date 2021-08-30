import csv
import json
import math
import os

from tqdm import tqdm

from helpers import FILE_LOCATIONS, FileType, FORCE_OVERWRITE, getFilepaths, log


def processEntityPointToDistance(entityName, forceOverwrite=False):
    filepath_in, filepath_out = getFilepaths(entityName, FileType.POINT, FileType.XYZ, forceOverwrite)
    [folder, filename] = os.path.split(filepath_out)
    filepath_out_inverted = os.path.join(folder, "inverted_" + filename)

    points = json.load(open(filepath_in, 'r'))
    lng_lat_points = [(float(point['lng']), float(point['lat'])) for point in points]
    lng_lat_points = [x for x in set(lng_lat_points)]
    example_filename = os.path.join(FILE_LOCATIONS[FileType.XYZ], 'gbr_pd_2020_1km_UNadj_ASCII_XYZ.csv')

    xyz_example = csv.reader(open(example_filename))
    xyz_example = [x for x in xyz_example]  # make it a list so we have total count for tqdm
    xyz_example = xyz_example[1:]  # skip the headers

    xyz_result = []
    max_z = 0
    log('calculating distance for each pixel')
    for x, y, z in tqdm(xyz_example):
        min_sq_distance = math.inf
        x = float(x)
        y = float(y)
        dx = 0
        dy = 0
        for lng, lat in lng_lat_points:  # This could be made much much faster but hey its quick enough for now - takes like 3mins for high def
            dx = x - lng
            dy = y - lat
            distance_sq = dx * dx + dy * dy
            min_sq_distance = min(min_sq_distance, distance_sq)
        min_distance = math.sqrt(min_sq_distance)
        max_z = max(max_z, min_distance)
        xyz_result.append((x, y, min_distance))

    log('writing result to {} and {}'.format(filepath_out, filepath_out_inverted))
    if not os.path.exists(filepath_out) or forceOverwrite:
        out_template = "{},{},{}\n"
        with open(filepath_out, 'w') as out_fp:
            out_fp.write(out_template.format("X", "Y", "Z"))
            for x, y, z in tqdm(xyz_result):
                out_fp.write(out_template.format(x, y, z))

    if not os.path.exists(filepath_out_inverted) or forceOverwrite:
        out_template = "{},{},{}\n"
        with open(filepath_out_inverted, 'w') as out_fp:
            out_fp.write(out_template.format("X", "Y", "Z"))
            for x, y, z in tqdm(xyz_result):
                out_fp.write(out_template.format(x, y, max_z - z))


if __name__ == '__main__':
    for filename in os.listdir(FILE_LOCATIONS[FileType.POINT]):
        entityName = os.path.splitext(filename)[0]
        _, filepath_out = getFilepaths(entityName, FileType.POINT, FileType.XYZ, True)

        if os.path.exists(filepath_out) and not FORCE_OVERWRITE:
            continue

        processEntityPointToDistance(entityName, FORCE_OVERWRITE)
