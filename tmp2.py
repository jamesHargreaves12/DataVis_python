import gzip
import os
import shutil

from tqdm import tqdm

dir = '/Users/james_hargreaves/WebstormProjects/data-visualisation/src/data/objFiles/populationDensity'
outDir = '/Users/james_hargreaves/WebstormProjects/data-visualisation/src/data/details/populationDensity'
todo = [x for x in os.listdir(dir)]

for filename in tqdm(todo):
    path = os.path.join(dir, filename)
    if ("gbr_pd_2020_1km_UNadj_ASCII_XYZ" in filename):
        continue
    with open(os.path.join(outDir, filename.split('.')[0])+'.json', 'w+') as f_out:
        gender = "Male" if "gbr_m" in filename else "Female"
        ageRangeStart = int(filename.split('_')[2])
        ageRange = str(ageRangeStart) + " - " + str(1 if ageRangeStart == 0 else (5 if ageRangeStart == 1 else ageRangeStart+5))
        title = gender + " " + ageRange
        f_out.write('''{{\n\t"idOverride": "{}",\n\t"title": "{}",\n\t"ageRange": "{}",\n\t"gender": "{}",\n\t"description": "TODO"\n}}\n'''
                    .format(title.replace(' ',''), title, ageRange, gender))
