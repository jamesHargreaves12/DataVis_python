import os

import numpy as np
import pandas as pd
from shapely.geometry import Polygon
from tqdm import tqdm

from helpers import get_next_bounds, get_rect_verts, scale_z, verts_for_cuboid, scale_to_texture, \
    FORCE_OVERWRITE, FILE_LOCATIONS, FileType

Z_SCALE = 10
MATERIAL_NAME = 'viridis'
WITH_NAIVE_Y_SCALE = True
UK_HEIGHT = 967
UK_WIDTH = 437


def dataframe_to_obj(df, filename='uk.obj', material_fname='master.mtl', material_name='viridis'):
    cuboid_faces = [[1, 2, 3, 4], [5, 6, 7, 8], [1, 2, 6, 5], [2, 3, 7, 6], [3, 4, 8, 7], [4, 1, 5, 8]]
    all_verts = []
    all_textures = []
    all_faces = []
    seen_verts = 0
    max_z = df['Z'].max()
    min_z = df['Z'].min()
    for index, row in tqdm(df.iterrows()):
        norm_z = (row['Z'] - min_z) / (max_z - min_z)
        verts = verts_for_cuboid(row['geometry'].exterior.coords, row['Z'])
        faces_to_plot = cuboid_faces if row['Z'] > 0 else cuboid_faces[:1]
        faces = [[x + seen_verts for x in face] for face in faces_to_plot]
        # this can be made more efficient
        all_textures.extend([scale_to_texture(norm_z) for _ in faces])
        all_verts.extend(verts)
        all_faces.extend(faces)
        seen_verts += len(verts)
    vert_format = 'v {} {} {}\n'
    texture_format = 'vt {} {}\n'
    face_format = 'f {}/{} {}/{} {}/{} {}/{}\n'
    with open(filename, 'w') as fp:
        fp.write('# UK population density\n')
        fp.write('mtllib {}\n'.format(material_fname))
        fp.write('# Verts\n')
        for x, y, z in tqdm(all_verts):
            fp.write(vert_format.format(x, y, z))
        for col in tqdm(all_textures):
            fp.write(texture_format.format(col, col))
        fp.write('# Faces\n')
        fp.write('usemtl {}\n'.format(material_name))
        for j, (a, b, c, d) in tqdm(enumerate(all_faces)):
            i = j + 1
            fp.write(face_format.format(a, i, b, i, c, i, d, i))


print(os.path.basename(__file__))

for filename in os.listdir(FILE_LOCATIONS[FileType.XYZ_FILLED_IN]):

    filepath_in = os.path.join(FILE_LOCATIONS[FileType.XYZ_FILLED_IN], filename)
    filepath_out = os.path.join(FILE_LOCATIONS[FileType.OBJ], os.path.splitext(filename)[0] + '.obj')

    if os.path.exists(filepath_out) and not FORCE_OVERWRITE:
        continue

    print("Processing {}".format(filepath_in))
    df = pd.read_csv(filepath_in)
    print("Shape {}".format(df.shape))
    xs = np.sort(df['X'].unique())
    ys = np.sort(df['Y'].unique())

    next_bound_x = get_next_bounds(xs)
    next_bound_y = get_next_bounds(ys)
    print('Setting geometry column')
    if WITH_NAIVE_Y_SCALE:
        df['geometry'] = [Polygon(get_rect_verts(row['X'], next_bound_x[row['X']], row['Y'] * UK_HEIGHT / UK_WIDTH,
                                                 next_bound_y[row['Y']] * UK_HEIGHT / UK_WIDTH))
                          for i, row in tqdm(df.iterrows())]
    else:
        df['geometry'] = [Polygon(get_rect_verts(row['X'], next_bound_x[row['X']], row['Y'], next_bound_y[row['Y']]))
                          for i, row in tqdm(df.iterrows())]

    print('Dataframe to obj')
    dataframe_to_obj(scale_z(df, Z_SCALE), filepath_out, material_name=MATERIAL_NAME)
    print("*" * 30)
