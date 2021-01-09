import os
import rioxarray as rxr
import rasterio as rio
from tqdm import tqdm
import numpy as np

from helpers import FileType, FILE_LOCATIONS

print(os.path.basename(__file__))

for filename in os.listdir(FILE_LOCATIONS[FileType.TIF]):
    filepath_in = os.path.join(FILE_LOCATIONS[FileType.TIF], filename)
    filepath_out = os.path.join(FILE_LOCATIONS[FileType.XYZ], os.path.splitext(filename)[0] + '.csv')

    if os.path.exists(filepath_out):
        continue

    print("Processing {}".format(filename))

    with rio.open(filepath_in) as src:
        data = src.read(1, masked=True)
    wrapped = rxr.open_rasterio(filepath_in, masked=True)

    out_f = open(filepath_out, 'w+')
    out_template = '{},{},{}\n'
    out_f.write(out_template.format('X', 'Y', 'Z'))
    for x in tqdm(range(data.shape[0]), position=0, leave=True):
        for y in np.where(data.mask[x] == False)[0]:
            X = round(float(wrapped[0][x][y].x.data), 5)
            Y = round(float(wrapped[0][x][y].y.data), 5)
            Z = round(float(data[x][y]), 5)
            out_f.write(out_template.format(X, Y, Z))
    out_f.close()
