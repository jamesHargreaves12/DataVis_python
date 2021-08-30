import shutil

from helpers import FileType, getFilepaths


def skipLowResToFilledIn(entityName, forceOverwrite=False):
    filepath_in, filepath_out = getFilepaths(entityName, FileType.XYZ_LOW_RES, FileType.XYZ_FILLED_IN, forceOverwrite)
    shutil.copyfile(filepath_in, filepath_out)
