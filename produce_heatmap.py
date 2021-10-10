import matplotlib.pyplot as plt
import pandas as pd
import fiona  # even though this isn't used is has to be imported prior to geopandas. why?
import geopandas as gpd
import numpy as np
import shapely
from shapely.geometry import Polygon
import re

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


def processMSOAEntityToHeatMap(entityName, forceOverwrite=False):
    filepath_in, filepath_out = getFilepaths(entityName, FileType.MSOA_SIMPLIFIED, FileType.HEATMAP, forceOverwrite)

    df = pd.read_csv(filepath_in)
    df['geometry'] = df['geometry'].apply(shapely.wkt.loads)

    log("Plotting")
    plot_uk(df)
    plt.axis("off")
    log("Saving figure")
    plt.savefig(filepath_out, bbox_inches='tight')


if __name__ == '__main__':
    # processEntityXYZToHeatMap('iceland', True)


    # TMP PLEASE DELETE THIS:
    def toDecimal(lat):
        print(lat)
        deg, minutes, seconds, direction = re.split('[°′″]', lat)
        return (float(deg) + float(minutes) / 60 + float(seconds) / (60 * 60)) * (-1 if direction in ['W', 'S'] else 1)


    longs = ["002°57′39″W", "0°17′19.32″W", "001°18′33″E", "002°12′01″W", "001°34′20″W", "000°06′31″W", "00°04′59.8″W",
             "002°57′59″W", "001°08′32″W", "0°0′59″W", "002°07′49″W", "002°17′29″W", "001°37′18″W", "001°23′28″W",
             "000°05′08″W", "000°11′28″W", "000°03′59″W", "2°13′49″W", "000°24′06″W", "001°53′05″W"]
    lats = ["53°25′51″N", "51°29′26.97″N", "52°37′20″N", "53°28′59″N", "53°46′40″N", "51°33′18″N", "50°51′42.56″N",
            "53°26′20″N", "52°37′13″N", "51°32′19″N", "52°35′25″N", "53°27′47″N", "54°58′32″N", "50°54′21″N",
            "51°23′54″N", "51°28′54″N", "51°36′17″N", "53°47′21″N", "51°39′00″N", "52°30′33″N"]

    results = []
    for i in range(20):
        results.append({'lat': float(toDecimal(lats[i])), 'lng': float(toDecimal(longs[i]))})

    df = pd.read_csv('./data/MSOAProcessing/SimplifiedGeoDF/FY2012TotalAnnualIncome.csv')
    df['geometry'] = df['geometry'].apply(shapely.wkt.loads)

    plot_uk(df)

    plt.scatter([x['lng'] for x in results], [x['lat'] for x in results], c='red')
    plt.show()


