import json
import math
import os
from time import time

from helpers import log
from obj_to_zip import processEntityObjToZip
from points_to_distance_xyz import processEntityPointToDistance
from postcodeToAverageXyz import processPostcodeToMedianXYZLowRes
from produce_heatmap import processEntityXYZToHeatMap
from skip_filling_in import skipLowResToFilledIn
from xyz_filled_in_to_obj import processEntityFilledInToObj
from xyz_low_res_to_xyz_filled_in import processEntityLowResToFilledIn, processEntityLowResToFilledInEnglandAndWales
from xyz_to_xyz_low_res import processEntityXyzToXyzLowRes

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


entityStepsToRun = {
    'med_price_paid_18-20': [processPostcodeToMedianXYZLowRes, processEntityLowResToFilledInEnglandAndWales,
                         processEntityFilledInToObj, processEntityXYZToHeatMap,
                         processEntityObjToZip],
    'med_price_paid_15-17': [processPostcodeToMedianXYZLowRes, processEntityLowResToFilledInEnglandAndWales,
                         processEntityFilledInToObj, processEntityXYZToHeatMap,
                         processEntityObjToZip],
    'med_price_paid_12-14': [processPostcodeToMedianXYZLowRes, processEntityLowResToFilledInEnglandAndWales,
                         processEntityFilledInToObj, processEntityXYZToHeatMap,
                         processEntityObjToZip],
    'med_price_paid_09-11': [processPostcodeToMedianXYZLowRes, processEntityLowResToFilledInEnglandAndWales,
                         processEntityFilledInToObj, processEntityXYZToHeatMap,
                         processEntityObjToZip],
    'med_price_paid_06-08': [processPostcodeToMedianXYZLowRes, processEntityLowResToFilledInEnglandAndWales,
                         processEntityFilledInToObj, processEntityXYZToHeatMap,
                         processEntityObjToZip],
    'med_price_paid_03-05': [processPostcodeToMedianXYZLowRes, processEntityLowResToFilledInEnglandAndWales,
                         processEntityFilledInToObj, processEntityXYZToHeatMap,
                         processEntityObjToZip],
    'med_price_paid_00-02': [processPostcodeToMedianXYZLowRes, processEntityLowResToFilledInEnglandAndWales,
                         processEntityFilledInToObj, processEntityXYZToHeatMap,
                         processEntityObjToZip],
    'med_price_paid_97-99': [processPostcodeToMedianXYZLowRes, processEntityLowResToFilledInEnglandAndWales,
                         processEntityFilledInToObj, processEntityXYZToHeatMap,
                         processEntityObjToZip],
}

entityStepsToRun = {
    # "coop": [processEntityFilledInToObj, processEntityObjToZip],
    # "england": [processEntityFilledInToObj, processEntityObjToZip],
    # "englandWales": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_f_0_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_f_10_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_f_15_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_f_1_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_f_20_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_f_25_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_f_30_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_f_35_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_f_40_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_f_45_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_f_50_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_f_55_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_f_5_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_f_60_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_f_65_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_f_70_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_f_75_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_f_80_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_m_0_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_m_10_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_m_15_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_m_1_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_m_20_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_m_25_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_m_30_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_m_35_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_m_40_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_m_45_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_m_50_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_m_55_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_m_5_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_m_60_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_m_65_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_m_70_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_m_75_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_m_80_2020_constrained_UNadj": [processEntityFilledInToObj, processEntityObjToZip],
    "gbr_pd_2020_1km_UNadj_ASCII_XYZ": [processEntityFilledInToObj, processEntityObjToZip],
    "iceland": [processEntityFilledInToObj, processEntityObjToZip],
    "inverted_coop": [processEntityFilledInToObj, processEntityObjToZip],
    "inverted_iceland": [processEntityFilledInToObj, processEntityObjToZip],
    "inverted_mands": [processEntityFilledInToObj, processEntityObjToZip],
    "inverted_mcdonalds": [processEntityFilledInToObj, processEntityObjToZip],
    "inverted_morisons": [processEntityFilledInToObj, processEntityObjToZip],
    "inverted_sainsburys": [processEntityFilledInToObj, processEntityObjToZip],
    "inverted_tesco": [processEntityFilledInToObj, processEntityObjToZip],
    "mands": [processEntityFilledInToObj, processEntityObjToZip],
    "mcdonalds": [processEntityFilledInToObj, processEntityObjToZip],
    "morisons": [processEntityFilledInToObj, processEntityObjToZip],
    "pricePaid18-20": [processEntityFilledInToObj, processEntityObjToZip],
    "price_paid_00-02": [processEntityFilledInToObj, processEntityObjToZip],
    "price_paid_03-05": [processEntityFilledInToObj, processEntityObjToZip],
    "price_paid_06-08": [processEntityFilledInToObj, processEntityObjToZip],
    "price_paid_09-11": [processEntityFilledInToObj, processEntityObjToZip],
    "price_paid_12-14": [processEntityFilledInToObj, processEntityObjToZip],
    "price_paid_15-17": [processEntityFilledInToObj, processEntityObjToZip],
    "price_paid_18-20": [processEntityFilledInToObj, processEntityObjToZip],
    "price_paid_97-99": [processEntityFilledInToObj, processEntityObjToZip],
    "med_price_paid_00-02": [processEntityFilledInToObj, processEntityObjToZip],
    "med_price_paid_03-05": [processEntityFilledInToObj, processEntityObjToZip],
    "med_price_paid_06-08": [processEntityFilledInToObj, processEntityObjToZip],
    "med_price_paid_09-11": [processEntityFilledInToObj, processEntityObjToZip],
    "med_price_paid_12-14": [processEntityFilledInToObj, processEntityObjToZip],
    "med_price_paid_15-17": [processEntityFilledInToObj, processEntityObjToZip],
    "med_price_paid_18-20": [processEntityFilledInToObj, processEntityObjToZip],
    "med_price_paid_97-99": [processEntityFilledInToObj, processEntityObjToZip],

    "price_paid_2020": [processEntityFilledInToObj, processEntityObjToZip],
    "sainsburys": [processEntityFilledInToObj, processEntityObjToZip],
    "tesco": [processEntityFilledInToObj, processEntityObjToZip],
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
