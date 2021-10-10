import json
import math
import os
from time import time

from MSOA_common_to_geoDF import processMSOAEntityCommonToGeoDF
from MSOA_geoDF_to_merged import ProcessMSOAEntityGeoDfToMerged
from MSOA_merged_to_simplified import processMSOAEntityMergedToSimplified
from helpers import log
from obj_to_zip import processEntityObjToZip
from points_to_distance_xyz import processEntityPointToDistance
from postcodeToAverageXyz import processPostcodeToMedianXYZLowRes, processPostcodeToMeanXYZLowRes
from produce_heatmap import processEntityXYZToHeatMap, processMSOAEntityToHeatMap
from skip_filling_in import skipLowResToFilledIn
from xyz_filled_in_to_obj import processEntityFilledInToObj, processMSOASimplifiedEntityInToObj
from xyz_low_res_to_xyz_filled_in import processEntityLowResToFilledIn, processEntityLowResToFilledInEnglandAndWales
from xyz_to_xyz_low_res import processEntityXyzToXyzLowRes, processEntityXyzToXyzLowResWithResolution, \
    processEntityXyzToXyzLowResEngWales

POINTS_ALL_STEPS = [processEntityPointToDistance, processEntityXyzToXyzLowRes, processEntityLowResToFilledIn,
                    processEntityFilledInToObj, processEntityXYZToHeatMap,
                    processEntityObjToZip]
XYZ_ALL_STEPS = [processEntityXyzToXyzLowRes, processEntityLowResToFilledIn, processEntityFilledInToObj,
                 processEntityFilledInToObj, processEntityXYZToHeatMap, processEntityObjToZip]
forceOverwrite = True
PRED_RUN_TIMES_FILEPATH: str = 'infoFiles/pred_run_times.json'


class PredLoadTimes:
    pred_run_times = {}
    alpha = 0.5

    def __init__(self):
        if not os.path.exists(PRED_RUN_TIMES_FILEPATH):
            return
        obj = json.load(open(PRED_RUN_TIMES_FILEPATH, 'r'))
        for key in obj.keys():
            self.pred_run_times[key] = obj[key]

    def save(self):
        json.dump(self.pred_run_times, open(PRED_RUN_TIMES_FILEPATH, 'w+'))

    def update(self, name, value):
        if name in self.pred_run_times:
            self.pred_run_times[name] = self.pred_run_times[name] * (1 - self.alpha) + value * self.alpha
        else:
            self.pred_run_times[name] = value
        self.save()

    def __getitem__(self, item):
        if item in self.pred_run_times:
            val = self.pred_run_times[item]
            return math.floor(val / 60), round(val % 60)
        else:
            return math.nan, math.nan

FULL_MSOA = [processEntityObjToZip]
entityStepsToRun = {
    # 'FY2016NetIncomeBeforeHousing': FULL_MSOA,
    # 'FY2016NetIncomeAfterHousing': FULL_MSOA,
    # 'FY2016NetAnnualIncome': FULL_MSOA,
    # 'FY2016TotalIncome': FULL_MSOA,
    # 'FY2018NetIncomeBeforeHousing': FULL_MSOA,
    # 'FY2018NetIncomeAfterHousing': FULL_MSOA,
    # 'FY2018NetAnnualIncome': FULL_MSOA,
    # 'FY2018TotalIncome': FULL_MSOA,
    'med_price_paid_97-99': [processEntityLowResToFilledInEnglandAndWales, processEntityFilledInToObj, processEntityXYZToHeatMap, processEntityObjToZip],
    'med_price_paid_00-02': [processEntityLowResToFilledInEnglandAndWales, processEntityFilledInToObj, processEntityXYZToHeatMap, processEntityObjToZip],
    'med_price_paid_03-05': [processEntityLowResToFilledInEnglandAndWales, processEntityFilledInToObj, processEntityXYZToHeatMap, processEntityObjToZip],
    'med_price_paid_06-08': [processEntityLowResToFilledInEnglandAndWales, processEntityFilledInToObj, processEntityXYZToHeatMap, processEntityObjToZip],
    'med_price_paid_09-11': [processEntityLowResToFilledInEnglandAndWales, processEntityFilledInToObj, processEntityXYZToHeatMap, processEntityObjToZip],
    'med_price_paid_12-14': [processEntityLowResToFilledInEnglandAndWales, processEntityFilledInToObj, processEntityXYZToHeatMap, processEntityObjToZip],
    'med_price_paid_15-17': [processEntityLowResToFilledInEnglandAndWales, processEntityFilledInToObj, processEntityXYZToHeatMap, processEntityObjToZip],
    'med_price_paid_18-20': [processEntityLowResToFilledInEnglandAndWales, processEntityFilledInToObj, processEntityXYZToHeatMap, processEntityObjToZip],

    'mean_price_paid_97-99': [processEntityLowResToFilledInEnglandAndWales, processEntityFilledInToObj, processEntityXYZToHeatMap, processEntityObjToZip],
    'mean_price_paid_00-02': [processEntityLowResToFilledInEnglandAndWales, processEntityFilledInToObj, processEntityXYZToHeatMap, processEntityObjToZip],
    'mean_price_paid_03-05': [processEntityLowResToFilledInEnglandAndWales, processEntityFilledInToObj, processEntityXYZToHeatMap, processEntityObjToZip],
    'mean_price_paid_06-08': [processEntityLowResToFilledInEnglandAndWales, processEntityFilledInToObj, processEntityXYZToHeatMap, processEntityObjToZip],
    'mean_price_paid_09-11': [processEntityLowResToFilledInEnglandAndWales, processEntityFilledInToObj, processEntityXYZToHeatMap, processEntityObjToZip],
    'mean_price_paid_12-14': [processEntityLowResToFilledInEnglandAndWales, processEntityFilledInToObj, processEntityXYZToHeatMap, processEntityObjToZip],
    'mean_price_paid_15-17': [processEntityLowResToFilledInEnglandAndWales, processEntityFilledInToObj, processEntityXYZToHeatMap, processEntityObjToZip],
    'mean_price_paid_18-20': [processEntityLowResToFilledInEnglandAndWales, processEntityFilledInToObj, processEntityXYZToHeatMap, processEntityObjToZip]
    # 'gbr_pd_2020_1km_UNadj_ASCII_XYZ': [processEntityFilledInToObj]
}

pred_run_times = PredLoadTimes()
for entity in entityStepsToRun.keys():
    for step in entityStepsToRun[entity]:
        expect_mins, expect_seconds = pred_run_times[step.__name__]
        expectedRunTimeStr = '{}m {}s'.format(expect_mins, expect_seconds) if expect_mins > 1 else '{}s'.format(
            expect_seconds)
        log('------ Running Step: {} for {} ({})------'.format(step.__name__, entity, expectedRunTimeStr))
        start = time()
        step(entity, forceOverwrite)
        pred_run_times.update(step.__name__, time() - start)
