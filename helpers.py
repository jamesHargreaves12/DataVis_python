import math
from enum import Enum
# This isn't working right now - seems to be some issue with fiona will solve in the future since currently only used to plot the heat maps.
# import fiona
# import geopandas as gpd

FORCE_OVERWRITE = False


class FileType(Enum):
    TIF = 1,
    XYZ = 2,
    XYZ_LOW_RES = 3,
    XYZ_FILLED_IN = 4,
    OBJ = 5,
    VID = 6


FILE_LOCATIONS = {
    FileType.TIF: "data/tifs",
    FileType.XYZ: 'data/xyz/',
    FileType.XYZ_LOW_RES: "data/xyz_low_res",
    FileType.XYZ_FILLED_IN: "data/xyz_fill_in",
    FileType.OBJ: 'data/obj/',
    FileType.VID: 'data/vid/'
}


# def plot_uk(df):
#     pds_poly = gpd.GeoDataFrame(df)
#     pds_poly = pds_poly.set_crs('EPSG:4326')
#     pds_poly.plot(column='Z', legend=True)


def get_rect_verts(x1, x2, y1, y2):
    return [(x1, y1), (x1, y2), (x2, y2), (x2, y1)]


def get_next_bounds(xs):
    differences = [xs[i] - xs[i - 1] for i in range(1, len(xs))]
    av_difference = sum(differences) / len(differences)
    next_bound = {}
    for i, x in enumerate(xs):
        limit = xs[i + 1] if i < len(xs) - 1 else 2 * x - xs[i - 1]
        # to handle the case where we have a big gap between points
        if limit - x > av_difference * 3:
            limit = x + av_difference
        next_bound[x] = limit
    return next_bound


def verts_for_cuboid(xys, z):
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
