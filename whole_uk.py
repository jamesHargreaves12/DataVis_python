import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# To be fixed
# from helpers import get_next_bounds, get_rect_verts, plot_uk
from helpers import get_next_bounds, get_rect_verts
from shapely.geometry import Polygon


def inclusion(val, start_ends):
    return any(filter(lambda x: x[0] <= val <= x[1], start_ends))


def get_closest(x, sorted_xs):
    distance = abs(sorted_xs[0] - x)
    closest = sorted_xs[0]
    for test_x in sorted_xs:
        new_dist = abs(test_x - x)
        if new_dist > distance:
            return closest
        else:
            distance = new_dist
            closest = test_x

def get_all_within_threshold(x, sorted_xs, thresh):
    return filter(lambda val: -thresh < x-val < 0, sorted_xs)


class UkLandmass:
    def __init__(self, source_of_truth_filepath, x_resolution):
        df = pd.read_csv(source_of_truth_filepath)
        x_vals = np.sort(df['X'].unique())
        y_vals = np.sort(df['Y'].unique())
        next_bound_x = get_next_bounds(x_vals)
        self.possible_ys = y_vals
        self.y_to_blocks = {}
        for y in y_vals:
            blocks = []
            xs = list(df[df['Y'] == y]['X'])
            start = xs[0]
            prev = xs[0]
            for i in range(1, len(xs)):
                if xs[i] != next_bound_x[prev]:
                    blocks.append((start, prev))
                    start = xs[i]
                prev = xs[i]
            blocks.append((start, prev))
            self.y_to_blocks[y] = blocks
        self.apply_x_resolution(x_resolution)

    def apply_x_resolution(self, x_resolution):
        # There could be a better way to do this however for now this is how we will do it.
        for y in self.possible_ys:
            blocks = self.y_to_blocks[y]
            new_blocks = []
            # remove any gaps that are smaller than threshold.
            cur_start, cur_end = blocks[0]
            for start,end in blocks[1:]:
                if start- cur_end > x_resolution:
                    new_blocks.append((cur_start,cur_end))
                    cur_start = start
                    cur_end = end
                else:
                    cur_end = end
            new_blocks.append((cur_start, cur_end))
            self.y_to_blocks[y] = new_blocks



    def is_included(self, x, y):
        return inclusion(x, self.y_to_blocks[get_closest(y, self.possible_ys)])

    def filter_included(self, sorted_xs, y, y_threshold):
        closest_y = get_closest(y, self.possible_ys)
        if abs(y-closest_y) > y_threshold:
            print(y)
            return []

        blocks = self.y_to_blocks[closest_y]
        included = []
        cur_block_index = 0
        in_block = False
        next_checkpoint = blocks[cur_block_index][0]
        for x in sorted_xs:
            while x >= next_checkpoint:
                if in_block:
                    cur_block_index += 1
                    if len(blocks) <= cur_block_index:
                        break
                    next_checkpoint = blocks[cur_block_index][0]
                    in_block = False
                else:
                    next_checkpoint = blocks[cur_block_index][1]
                    in_block = True
            if len(blocks) <= cur_block_index:
                break

            if in_block:
                included.append(x)

        return included

    def filter_included_all_y(self, sorted_xs, y, y_threshold, x_threshold):
        included = set()
        for close_y in get_all_within_threshold(y, self.possible_ys, y_threshold):
            blocks = self.y_to_blocks[close_y]
            cur_block_index = 0
            in_block = False
            next_checkpoint = blocks[cur_block_index][0]
            for x in sorted_xs:
                while x >= next_checkpoint + (-x_threshold if not in_block else 0):
                    if in_block:
                        cur_block_index += 1
                        if len(blocks) <= cur_block_index:
                            break
                        next_checkpoint = blocks[cur_block_index][0]
                        in_block = False
                    else:
                        next_checkpoint = blocks[cur_block_index][1]
                        in_block = True
                if len(blocks) <= cur_block_index:
                    break

                if in_block:
                    included.add(x)
        return included

    # def plot_template(self):
    #     df_dict_landmass = {'Z': [], 'geometry': []}
    #     next_bound_y = get_next_bounds(self.possible_ys)
    #     for y in self.possible_ys:
    #         for x0, x1 in self.y_to_blocks[y]:
    #             df_dict_landmass['Z'].append(0)
    #             df_dict_landmass['geometry'].append(Polygon(get_rect_verts(x0, x1, y, next_bound_y[y])))
    #     df_uk = pd.DataFrame.from_dict(df_dict_landmass)
    #     plot_uk(df_uk)
    #     plt.show()



if __name__ == "__main__":
    x_resolution = 0 # max res
    uk_landmass = UkLandmass('data/xyz/gbr_pd_2020_1km_UNadj_ASCII_XYZ.csv', x_resolution)
    uk_landmass.plot_template()
    print(uk_landmass.is_included(-1, 60))
