import matplotlib.pyplot as plt
import pandas as pd
import fiona  # even though this isn't used is has to be imported prior to geopandas. why?
import geopandas as gpd
import numpy as np
from shapely.geometry import Polygon

from helpers import FileType, get_rect_verts, get_next_bounds, getFilepaths, log


def plot_uk(df):
    pds_poly = gpd.GeoDataFrame(df)
    pds_poly = pds_poly.set_crs('EPSG:4326')
    pds_poly.plot(column='Z', cmap='viridis')


def processEntityXYZToHeatMap(entityName, forceOverwrite=False):
    filepath_in, filepath_out = getFilepaths(entityName, FileType.XYZ_FILLED_IN, FileType.HEATMAP, forceOverwrite)
    # filepath_in = 'data/tmp/low_res.csv'
    df = pd.read_csv(filepath_in)
    xs = np.sort(df['X'].unique())
    ys = np.sort(df['Y'].unique())
    next_bound_x = get_next_bounds(xs)
    next_bound_y = get_next_bounds(ys)
    df['geometry'] = df.apply(
        lambda row: Polygon(get_rect_verts(row.X, next_bound_x[row.X], row.Y, next_bound_y[row.Y])), axis=1)
    log("Plotting")
    plot_uk(df)
    plt.axis('off')
    log("Saving figure")
    plt.savefig(filepath_out, bbox_inches='tight')


if __name__ == '__main__':
    processEntityXYZToHeatMap('iceland', True)
