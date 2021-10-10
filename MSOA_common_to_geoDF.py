
import fiona
from shapely.geometry import shape, point
import geopandas as gpd
import pandas as pd

from helpers import FileType, getFilepaths


def processMSOAEntityCommonToGeoDF(entityName, forceOverwrite=False):
    filepath_in, filepath_out = getFilepaths(entityName, FileType.MSOA_COMMON_FORM, FileType.MSOA_GEO_DF, forceOverwrite)

    # Could convert these to be lazy loaded?
    print('Read 1')
    boundariesDf = gpd.read_file("data/MSOAFiles/MSOA_2011_EW_BFC_shp/MSOA_2011_EW_BFC.shp")
    boundariesDf['geometry'] = boundariesDf['geometry'].to_crs('EPSG:4326')

    print('Read 2')
    populationPerMsoa = pd.read_csv('data/MSOAFiles/popPerMSOA.csv')
    populationPerMsoa['population'] = pd.to_numeric(populationPerMsoa['All Ages'].str.strip().str.replace(',',''))


    print('Read 3')
    df = pd.read_csv(filepath_in)

    print('Merging')
    df = df.merge(boundariesDf, left_on='MSOA code', right_on='MSOA11CD', how='left')
    df = df.merge(populationPerMsoa, on='MSOA code', how='left')

    print('saving')
    pds_poly = gpd.GeoDataFrame(df)
    pds_poly[['Z', 'geometry','population']].to_csv(filepath_out, index=False)


if __name__ == '__main__':
    processMSOAEntityCommonToGeoDF('FY2018NetAnnualIncome', True)