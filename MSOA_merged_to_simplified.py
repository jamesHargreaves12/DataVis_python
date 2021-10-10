import csv
import os
import re
import sys
from collections import defaultdict
from math import inf

import fiona
import shapely.wkt
from shapely.geometry import Polygon, LineString, Point
from shapely.validation import explain_validity
from tqdm import tqdm
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

from helpers import getFilepaths, FileType

csv.field_size_limit(sys.maxsize)

withPlot = True
smoothness_coef = 0.03


def plot(filepath):
    df = pd.read_csv(filepath)
    df['geometry'] = df['geometry'].apply(shapely.wkt.loads)

    pds_poly = gpd.GeoDataFrame(df)
    pds_poly = pds_poly.set_crs('EPSG:4326')
    pds_poly.plot(column='Z', cmap='viridis')
    plt.axis("off")
    # plt.grid()
    plt.show()


def simplifyLine(verts, indecies):
    threshold = smoothness_coef
    if len(verts) == 2:
        return verts, indecies
    line = LineString([verts[0], verts[-1]])
    maxDistance = 0
    furthest_i = 0
    for i, v in enumerate(verts):
        dist = line.distance(Point(v))
        if dist > maxDistance:
            maxDistance = dist
            furthest_i = i

    if maxDistance < threshold:
        return [verts[0], verts[-1]], [indecies[0], indecies[-1]]
    else:
        left_v, left_i = simplifyLine(verts[:furthest_i + 1], indecies[:furthest_i + 1])
        right_v, right_i = simplifyLine(verts[furthest_i:], indecies[furthest_i:])
        return [left_v + right_v[1:], left_i + right_i[1:]]


def roundAndRemoveInvalidPoints(polygon):
    coords = [(x, y) for x, y in polygon.exterior.coords]
    coords = [(round(x, 8), round(y, 8)) for x, y in coords]
    retPoly = Polygon(coords)
    if retPoly.is_valid:
        return retPoly
    explanation = explain_validity(retPoly)
    match = re.match('Self-intersection\[(?P<first>-?\d+\.\d+) (?P<sec>-?\d+\.\d+)\]', explanation)
    if not match:
        print(explain_validity(retPoly))
        assert False

    errorx, errory = float(match.group(1)), float(match.group(2))
    closestD = inf
    closestP = None
    for px, py in retPoly.exterior.coords:
        d = (px - errorx) ** 2 + (py - errory) ** 2
        if d < closestD:
            closestD = d
            closestP = (px, py)
    retPoly = Polygon([(x, y) for x, y in list(retPoly.exterior.coords) if (x, y) != closestP])
    if retPoly.is_valid:
        return retPoly
    print(explain_validity(retPoly))
    assert False


def processMSOAEntityMergedToSimplified(entityName, forceOverwrite=False):
    filepath_in, filepath_out = getFilepaths(entityName, FileType.MSOA_MERGED, FileType.MSOA_SIMPLIFIED, forceOverwrite)

    print('reading and loading data structures')
    zs = {}
    polys = {}
    v_to_key = defaultdict(set)
    key_to_vs = defaultdict(list)
    key = 0
    with open(filepath_in, 'r') as fp:
        reader = csv.reader(fp)
        next(reader)  # skip headers
        for i, (z, p) in tqdm(enumerate(reader)):
            loaded = shapely.wkt.loads(p)
            ps = [loaded] if p.startswith('POLYGON') else list(loaded)
            for poly in ps:
                zs[key] = z
                poly = roundAndRemoveInvalidPoints(poly)
                polys[key] = poly
                for v in poly.exterior.coords:
                    key_to_vs[key].append(v)
                    v_to_key[v].add(key)
                key += 1
    maxKey = key

    key = None  # to get run time errors if it is read again
    print('calculating simplified lines between neighbours')
    poly_to_borders = defaultdict(list)
    poly_to_replaced_indecies = defaultdict(list)

    for k in tqdm(range(maxKey)):
        verts = key_to_vs[k]
        neighbours = set()
        for v in verts:
            neighbours = neighbours.union(v_to_key[v])
        for nKey in neighbours:
            if nKey < k or nKey == k:
                continue  # will be handled during other iteration
            commonVerts = set(verts).intersection(key_to_vs[nKey])
            # need a way to detect if they are multiple lines
            start = None
            end = None
            prev_included = False
            start_i, end_i, commonVerts_ids = None, None, []
            for i, v in enumerate(verts):
                if v in commonVerts:
                    commonVerts_ids.append(i)

                    if verts[(i + 1) % len(verts)] not in commonVerts:
                        end = v
                        end_i = i

                    if verts[i - 1] not in commonVerts:
                        start = v
                        start_i = i

            if start_i > end_i:
                b_indecies = list(range(start_i, len(verts))) + list(range(end_i + 1))
                boundaryPoints = verts[start_i:] + verts[:end_i + 1]
            else:
                b_indecies = list(range(start_i, end_i + 1))
                boundaryPoints = verts[start_i:end_i + 1]

            for i in b_indecies:
                assert (i in commonVerts_ids)
            # this only works if the do not cross the start point but if they don't then I assume that the "if not
            # closeEnough" statement will fire. If this statement returns true this means that the points between the
            # start and end point are not a continuous sequence of points on the perimeter of the polygon. There are
            # two reasons that this can happen the first is that there is a slight difference between some non significant
            # bit between the two neighbouring polygons (for this case we just proceed). The second case is where
            # there is two edges between the two polygons this case hasn't been encountered yet and so it is not handled.
            if len(commonVerts_ids) != len(b_indecies):
                print(len(commonVerts_ids), len(b_indecies))
                print([x for x in commonVerts_ids if x + 1 not in commonVerts_ids])
                # check all points closer than epsilon to the existing points which are in the range and if they are just
                # take the start and end this method runs the risk of ruining the corner of the next polygon along, if
                # this happens we should just remove some of the verts so that they wont be common but I think this will
                # be fine
                smallest = min(commonVerts_ids)
                largest = max(commonVerts_ids)
                threshold = 0.01
                for i in range(smallest, largest):
                    pointx, pointy = verts[i]
                    closeEnough = False
                    for commonx, commony in commonVerts:
                        dist = (pointx - commonx) ** 2 + (pointy - commony) ** 2
                        if dist < threshold:
                            closeEnough = True
                            break
                    if not closeEnough:
                        print(i, pointx, pointy)
                        assert False
                print('Happy that close enough')
                start_i = smallest
                end_i = largest
                b_indecies = list(range(start_i, end_i + 1))
                boundaryPoints = verts[start_i:end_i + 1]

            simplifiedBoundary_v, simplifyBoundary_i = simplifyLine(boundaryPoints, b_indecies)
            for i in range(len(simplifiedBoundary_v) - 1):
                start = simplifiedBoundary_v[i]
                start_i = simplifyBoundary_i[i]
                end = simplifiedBoundary_v[i + 1]
                end_i = simplifyBoundary_i[i + 1]
                mid_i = (
                                start_i + end_i) // 2 if start_i < end_i else 0  # mid point is needed to check if it wraps around the start point
                while mid_i not in commonVerts_ids:  # due to an error in a non significant bit
                    mid_i += 1
                poly_to_borders[k].append((start, end, verts[mid_i]))
                poly_to_borders[nKey].append((start, end, verts[mid_i]))

    print('writing out and simplifying map edges')
    template = "{},\"{}\"\n"
    with open(filepath_out, 'w+') as fp:
        fp.write("Z,geometry\n")
        # From this point On I will assume that the start / end points are contiguous
        for k in tqdm(range(maxKey)):
            neighbourBorderPoints = poly_to_borders[k]
            points = key_to_vs[k]
            # get the indecies of the start and end points
            neighbourBorderPointsIndecies = defaultdict(lambda: [inf, inf, inf])
            for pi, p in enumerate(points):
                for ni, (start, end, mid) in enumerate(neighbourBorderPoints):
                    if p == start:
                        neighbourBorderPointsIndecies[ni][0] = pi
                    if p == end:
                        neighbourBorderPointsIndecies[ni][1] = pi
                    if p == mid:
                        neighbourBorderPointsIndecies[ni][2] = pi

            for (start_i, end, mid) in neighbourBorderPointsIndecies.values():
                assert (start is not inf)
                assert (mid is not inf)
                assert (end is not inf)

            # work out if one edge wraps around start point
            doesWrap = False
            for start, end, mid in neighbourBorderPointsIndecies.values():
                smallest = min(start, end)
                largest = max(start, end)
                doesWrap |= not (smallest < mid < largest) and mid != inf

            onEdge = doesWrap
            outPoints = []
            remaining_indecies = sorted(
                [x for x, y, z in neighbourBorderPointsIndecies.values()] + [y for x, y, z in
                                                                             neighbourBorderPointsIndecies.values()])
            # print(k, doesWrap, neighbourBorderPointsIndecies.values())
            next_index = remaining_indecies.pop(0) if remaining_indecies else inf
            nonEdgePoints = []
            current_nonEdge = []
            for pi, p in enumerate(points):
                if pi == next_index:
                    if current_nonEdge:
                        current_nonEdge.append(p)
                        nonEdgePoints.append(current_nonEdge)
                        current_nonEdge = []
                    outPoints.append(p)
                    next_index = remaining_indecies.pop(0) if remaining_indecies else inf
                    if pi == next_index:  # ie end of one and start of another
                        next_index = remaining_indecies.pop(0) if remaining_indecies else inf
                    else:
                        onEdge = not onEdge
                        if not onEdge:
                            current_nonEdge.append(p)
                    continue
                elif not onEdge:
                    current_nonEdge.append(p)
            # wrap around non edge
            if not onEdge and current_nonEdge:
                if nonEdgePoints:
                    nonEdgePoints[0] = current_nonEdge + nonEdgePoints[0]
                else:
                    nonEdgePoints.append(current_nonEdge)

            for nonBoundary in nonEdgePoints:
                simplifiedBoundary_v, simplifyBoundary_i = simplifyLine(nonBoundary,
                                                                        [i for i, _ in enumerate(nonBoundary)])
                simplifiedLine = []
                simplifiedPoints = []
                for i in range(len(simplifiedBoundary_v) - 1):
                    start = simplifiedBoundary_v[i]
                    end = simplifiedBoundary_v[i + 1]
                    simplifiedPoints.append(start)
                    simplifiedLine.append((start, end))
                insertIndex = outPoints.index(end) if outPoints else 0
                outPoints = outPoints[:insertIndex] + simplifiedPoints + outPoints[insertIndex:]

            outPolygon = Polygon(outPoints)
            fp.write(template.format(zs[k], outPolygon))

    if withPlot:
        print('Plotting')
        plot(filepath_out)

    print('Finished')


if __name__ == '__main__':
    # processMSOAEntityMergedToSimplified('FY2018NetAnnualIncome', True)
    plot('/Users/james_hargreaves/PycharmProjects/dataplay_a2/data/MSOAProcessing/SimplifiedGeoDF/FY2016NetAnnualIncome.csv')
