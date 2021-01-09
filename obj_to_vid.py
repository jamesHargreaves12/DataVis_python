import math
import os

import cv2
import numpy as np
import torch
from pytorch3d.io import load_objs_as_meshes
from pytorch3d.renderer import (
    look_at_view_transform,
    FoVPerspectiveCameras,
    PointLights,
    RasterizationSettings,
    MeshRenderer,
    MeshRasterizer,
    SoftPhongShader
)
from tqdm import tqdm

from helpers import get_mins_maxs_from_obj, FILE_LOCATIONS, FileType

print(os.path.basename(__file__))

IMG_QUALITY = 128

device = torch.device("cpu")
tmp_vid_filename = 'data/vid/tmp.mp4'


for filename in os.listdir(FILE_LOCATIONS[FileType.OBJ]):

    filepath_in = os.path.join(FILE_LOCATIONS[FileType.OBJ], filename)
    filepath_out = os.path.join(FILE_LOCATIONS[FileType.VID], os.path.splitext(filename)[0] + '.mp4')

    if os.path.exists(filepath_out) or filename.endswith('.mtl') or filename.endswith('.png'):
        continue

    mesh = load_objs_as_meshes([filepath_in], device=device)

    fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    # what does 20.0 mean?
    out = cv2.VideoWriter(tmp_vid_filename, fourcc, 20.0, (IMG_QUALITY, IMG_QUALITY))
    lights = PointLights(device=device, location=[[0.0, 0.0, 3.0]])
    R, T = look_at_view_transform(2.7, 0, 180, at=((-2, 55, -10),))
    cameras = FoVPerspectiveCameras(device=device, R=R, T=T)

    raster_settings = RasterizationSettings(
        image_size=IMG_QUALITY,
        blur_radius=0.0,
        faces_per_pixel=1,
    )
    renderer = MeshRenderer(
        rasterizer=MeshRasterizer(
            cameras=cameras,
            raster_settings=raster_settings
        ),
        shader=SoftPhongShader(
            device=device,
            cameras=cameras,
            lights=lights
        )
    )
    min_x, max_x, min_y, max_y = get_mins_maxs_from_obj(filepath_in)
    center = ((min_x + max_x) / 2, (min_y + max_y) / 2, 0)
    radius = -20
    camera_points = []
    for i in tqdm(range(180), position=0, leave=True):
        deg = i * 2
        camera_point = (center[0] + radius * math.sin(math.pi * deg / 180), center[1],
                        center[2] + radius * math.cos(math.pi * deg / 180))
        camera_points.append(camera_point)
        R, T = look_at_view_transform(2.7, 0, (180 + deg) % 360, device=device, at=(camera_point,))
        image = renderer(mesh, R=R, T=T)
        image = image[0, ..., :3].cpu().numpy()
        img_for_output = np.clip(image, 0.0, 1.0) * 255
        im_bgr = cv2.cvtColor(img_for_output.astype('uint8'), cv2.COLOR_RGB2BGR)
        out.write(im_bgr)
    out.release()
