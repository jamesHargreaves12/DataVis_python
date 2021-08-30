import csv
import os

import fiona
from shapely.geometry import shape, point
from tqdm import tqdm
import rtree

from helpers import FILE_LOCATIONS, FileType

eng_data = fiona.open("/Users/james_hargreaves/PycharmProjects/dataplay_a2/data/nationalBoundaries/England_AL4-AL4.shp")
eng = next(iter(eng_data))
eng_geom = shape(eng['geometry'])
print(type(eng_geom))

wales_data = fiona.open("/Users/james_hargreaves/PycharmProjects/dataplay_a2/data/nationalBoundaries/Wales_AL4-AL4.shp")
wales = next(iter(wales_data))
wales_geom = shape(wales['geometry'])
print(type(wales_geom))

example_filename = os.path.join('/Users/james_hargreaves/PycharmProjects/dataplay_a2',
                                FILE_LOCATIONS[FileType.XYZ], 'gbr_pd_2020_1km_UNadj_ASCII_XYZ.csv')

eng_polys = list(eng_geom)
wales_polys = list(wales_geom)
all_polys = eng_polys + wales_polys
index = rtree.index.Index()

# populate the spatial index
for i, polygon in enumerate(all_polys):
    index.insert(i, polygon.bounds)

xyz_example = csv.reader(open(example_filename))
xyz_example = [x for x in xyz_example]  # make it a list so we have total count for tqdm
xyz_example = xyz_example[1:]  # skip the headers
with open(os.path.join('/Users/james_hargreaves/PycharmProjects/dataplay_a2',
                  FILE_LOCATIONS[FileType.MASKS], 'englandWales.csv'), "w+") as fpMask:
    with open(os.path.join('/Users/james_hargreaves/PycharmProjects/dataplay_a2',
                           FILE_LOCATIONS[FileType.XYZ_LOW_RES], 'englandWales.csv'), "w+") as fpComparison:
        out_template = '{},{},{}\n'
        fpMask.write(out_template.format("X", "Y", "Z"))
        fpComparison.write(out_template.format("X", "Y", "Z"))
        points = []
        for x, y, _ in tqdm(xyz_example):
            p = point.Point(float(x), float(y))
            geometry_buffered = p.buffer(0.0001)
            toCheck = index.intersection(geometry_buffered.bounds)
            z = 0
            for i in toCheck:
                if p.intersects(all_polys[i]):
                    z = 1

            fpComparison.write(out_template.format(x, y, z))
            if z == 1:
                fpMask.write(out_template.format(x, y, z))
