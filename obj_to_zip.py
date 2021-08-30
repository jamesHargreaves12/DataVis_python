import gzip
import os
import shutil

from tqdm import tqdm

from helpers import getFilepaths, FileType


def processEntityObjToZip(entityName, forceOverwrite=False):
    filepath_in, filepath_out = getFilepaths(entityName, FileType.OBJ, FileType.COMPRESSED, forceOverwrite)
    with open(filepath_in, 'rb') as f_in:
        with gzip.open(filepath_out, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


# dir = '/Users/james_hargreaves/WebstormProjects/data-visualisation/src/data/objFiles/distanceTo'
# outDir = '/Users/james_hargreaves/WebstormProjects/data-visualisation/src/data/objFilesCompressed/distanceTo'
# todo = [x for x in os.listdir(dir) if not x.endswith('.gz')]
#
# for filename in tqdm(todo):
#     path = os.path.join(dir, filename)
#     with open(path, 'rb') as f_in:
#         with gzip.open(os.path.join(outDir, filename)+'.gz', 'wb') as f_out:
#             shutil.copyfileobj(f_in, f_out)