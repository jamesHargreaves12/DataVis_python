import math
import os

from termcolor import colored
from enum import Enum


def noOverwriteOpen(filepath):
    if not os.path.isfile(filepath):
        return open(filepath, 'w+')
    raise Exception('File Already exists: {}'.format(filepath))


class LogLevel(Enum):
    INFO = 0,
    WARN = 1,
    ERROR = 2,


def log(str, level=LogLevel.INFO):
    color = 'green' if level == LogLevel.INFO else ('yellow' if level == LogLevel.WARN else 'red')
    print(colored(str, color))


def logInfo(val, *args):
    if args:
        val = (val,) + args
    log(val, LogLevel.INFO)


if __name__ == '__main__':
    log('info auto')
    log('info explicit', LogLevel.INFO)
    log('warn', LogLevel.WARN)
    log('error', LogLevel.ERROR)

FORCE_OVERWRITE = False


class FileType(Enum):
    TIF = 1,
    XYZ = 2,
    XYZ_LOW_RES = 3,
    XYZ_FILLED_IN = 4,
    OBJ = 5,
    VID = 6,
    POINT = 7,
    ZIP = 8,
    HEATMAP = 9,
    COMPRESSED = 10,
    MASKS = 11,
    POSTCODE = 12,
    MSOA_COMMON_FORM = 13,
    MSOA_GEO_DF = 14,
    MSOA_MERGED = 15,
    MSOA_SIMPLIFIED = 16


FILE_EXTENSIONS = {
    FileType.TIF: ".tif",
    FileType.XYZ: '.csv',
    FileType.XYZ_LOW_RES: ".csv",
    FileType.XYZ_FILLED_IN: ".csv",
    FileType.OBJ: '.obj',
    FileType.VID: '.mp4',
    FileType.POINT: '.json',
    FileType.COMPRESSED: '.obj.gz',
    FileType.HEATMAP: '.png',
    FileType.MASKS: '.csv',
    FileType.POSTCODE: '.csv',
    FileType.MSOA_COMMON_FORM: '.csv',
    FileType.MSOA_GEO_DF: '.csv',
    FileType.MSOA_MERGED: '.csv',
    FileType.MSOA_SIMPLIFIED: '.csv'
}
BASE_FILEPATH = '/Users/james_hargreaves/PycharmProjects/dataplay_a2'

FILE_LOCATIONS = {
    FileType.TIF: "data/tifs",
    FileType.XYZ: 'data/xyz/',
    FileType.XYZ_LOW_RES: "data/xyz_low_res",
    FileType.XYZ_FILLED_IN: "data/xyz_fill_in",
    FileType.OBJ: 'data/obj/',
    FileType.VID: 'data/vid/',
    FileType.POINT: 'data/points/',
    FileType.COMPRESSED: 'data/compressed/',
    FileType.HEATMAP: 'data/heatmaps/',
    FileType.MASKS: 'data/masks/',
    FileType.POSTCODE: 'data/postcode/',
    FileType.MSOA_COMMON_FORM: 'data/MSOAProcessing/CommonStartForm',
    FileType.MSOA_GEO_DF: 'data/MSOAProcessing/GeoDF',
    FileType.MSOA_MERGED: 'data/MSOAProcessing/MergedGeoDF',
    FileType.MSOA_SIMPLIFIED: 'data/MSOAProcessing/SimplifiedGeoDF'
}


def getFilepaths(entityName: str, inputType: type(FileType), outputType: type(FileType),
                 forceOverwrite: bool = True) -> (str, str):
    filepath_in = os.path.join(FILE_LOCATIONS[inputType], entityName + FILE_EXTENSIONS[inputType])
    filepath_out = os.path.join(FILE_LOCATIONS[outputType], entityName + FILE_EXTENSIONS[outputType])
    if not os.path.exists(filepath_in):
        raise Exception('input file doesnt exist for entity {} ({})'.format(entityName, filepath_in))
    if os.path.exists(filepath_out) and not forceOverwrite:
        raise Exception('Output file already exists for entity ' + entityName)
    return filepath_in, filepath_out


def get_rect_verts(x1, x2, y1, y2):
    return [(x1, y1), (x1, y2), (x2, y2), (x2, y1)]


def get_next_bounds(xs):
    if len(xs) < 1:
        raise Exception('To short array: [{}]'.format(','.join(xs)))
    differences = [xs[i] - xs[i - 1] for i in range(1, len(xs))]
    av_difference = sum(differences) / len(differences)
    next_bound = {}
    for i, x in enumerate(xs):
        limit = xs[i + 1] if i < len(xs) - 1 else 2 * x - xs[i - 1]
        # to handle the case where we have a big gap between points
        if limit - x > av_difference * 5:
            limit = x + av_difference
        next_bound[x] = limit
    return next_bound


# this also generalises to polygons
def verts_for_polygon(xys, z):
    verts_bottom = [(x, y, 0) for x, y in xys]
    verts_top = [(x, y, z) for x, y in xys]
    # To complete the polygon it prints the vertices twice
    return verts_bottom[:-1] + verts_top[:-1]


def scale_to_texture(value):
    # Justification for this method:
    # Since the textures are tiles the values at 0 and 1 are not correct since they are overlapped between the two
    return value * 0.99 + 0.005  # (0.005 - 0.995)


def scale_z(df, max_val=10):
    min_z = df['Z'].min()
    max_z = df['Z'].max()
    df['Z'] = (df['Z'] - min_z) / max_z * max_val
    return df


def get_mins_maxs_from_obj(obj_filename):
    xs = set()
    ys = set()
    with open(obj_filename, 'r') as fp:
        for line in fp.readlines():
            if line.startswith('#') or line.startswith('mtllib'):
                continue
            if not line.startswith('v '):
                break;
            vals = line.split(' ')
            xs.add(float(vals[1]))
            ys.add(float(vals[2]))
    return min(xs), max(xs), min(ys), max(ys)


def get_resolution_multiplier(xs, height_aim):
    differences = [xs[i] - xs[i - 1] for i in range(1, len(xs))]
    current_height = (xs.max() - xs.min()) / min(differences)
    return current_height // height_aim


def get_buckets(divisions, resolution):
    # we have assumed that divisions are sorted.
    differences = [divisions[i] - divisions[i - 1] for i in range(1, len(divisions))]
    min_limit, max_limit = divisions.min(), divisions.max()
    cur_pixel_size = min(differences)
    find_bucket = lambda x: int((x - min_limit) / cur_pixel_size / resolution)
    limits = [(min_limit + i * cur_pixel_size * resolution, min_limit + (i + 1) * cur_pixel_size * resolution) for i in
              range(math.floor((max_limit - min_limit) / cur_pixel_size / resolution) + 1)]
    return find_bucket, limits
