import urllib.request
from zipfile import ZipFile

url = 'ftp://ftp.worldpop.org/GIS/Population_Density/Global_2000_2020_1km_UNadj/2020/GBR/gbr_pd_2020_1km_UNadj_ASCII_XYZ.zip'
zip_loc = 'data/zips/gbr_pd_2020_1km_UNadj_ASCII_XYZ.zip'
save_loc = 'data/xyz'
r = urllib.request.urlopen(url)

open(zip_loc, 'wb').write(r.read())
with ZipFile(zip_loc, 'r') as zipObj:
    zipObj.extractall(save_loc)

