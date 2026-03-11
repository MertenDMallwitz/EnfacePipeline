import subprocess
import argparse
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import eyepy as ep
import tifffile
import pprint
import re
import pandas as pd
import ast
import xml.etree.ElementTree as ET
from skimage.util import img_as_ubyte
from pathlib import Path
import glob
from scipy import ndimage

ev=ep.EyeVolume.load(r"E:\data_export\images\015\0001\V1-SCR\sdoct_cslo_spectralis\MACUSTAR-313-015-0001-V1-Spectralis_SDOCT_cSLO\processed\processed\OUTPUT.eye")
rpe_names = [l for l in ev.layers if "RPE_" in l]
bm_names = [l for l in ev.layers if "BM_" in l]

drsn = ep.drusen(ev.layers[rpe_names[0]], ev.layers[bm_names[0]], ev.shape, minimum_height=5)
drusen_depth_map_values = drsn.sum(axis=1)[::-1, :]

target_shape = (650, 768)
zoom_y = target_shape[0] / drusen_depth_map_values.shape[0]
zoom_x = target_shape[1] / drusen_depth_map_values.shape[1]
resized_drusen_depth_map_values = ndimage.zoom(drusen_depth_map_values, (zoom_y, zoom_x), order=0)
resized_drusen_boolean_map_values = resized_drusen_depth_map_values.astype(bool)


# Now create padded versions to 768x768
out_dir = r"E:\data_export\images\015\0001\V1-SCR\sdoct_cslo_spectralis\MACUSTAR-313-015-0001-V1-Spectralis_SDOCT_cSLO\processed\processed"
os.makedirs(out_dir, exist_ok=True)

h, w = resized_drusen_depth_map_values.shape
pad_top = 64
pad_bottom = 768 - pad_top - h
# If source is taller than available middle region, crop from the bottom
if pad_bottom == 64:
    crop = -pad_bottom
    src_depth = resized_drusen_depth_map_values[: h - crop, :]
    pad_bottom = 0
else:
    src_depth = resized_drusen_depth_map_values

# Prepare depth TIFF dtype (avoid overflow)
# Save depth counts as float32, rounded to 2 decimal places, and pad to 768x768
src_depth_f = np.round(src_depth.astype(np.float32), 2)

out_depth = np.zeros((768, w), dtype=np.float32)
out_depth[pad_top: pad_top + src_depth_f.shape[0], :] = src_depth_f
edge_cols = 50
n_edge = min(edge_cols, w // 2)
if n_edge > 0:
    out_depth[:, :n_edge] = 0
    out_depth[:, -n_edge:] = 0
tifffile.imwrite(os.path.join(out_dir, "drusen_depth_map_768x768.tif"), out_depth)

# Boolean map -> 0 or 255, pad similarly
src_bool = resized_drusen_boolean_map_values.astype(bool)
if src_bool.shape[0] > (768 - pad_top):
    src_bool = src_bool[:(768 - pad_top), :]
out_bool = np.zeros((768, w), dtype=np.uint8)
out_bool[pad_top: pad_top + src_bool.shape[0], :] = (src_bool.astype(np.uint8) * 255)
if n_edge > 0:
    out_bool[:, :n_edge] = 0
    out_bool[:, -n_edge:] = 0
tifffile.imwrite(os.path.join(out_dir, "drusen_boolean_map_768x768.tif"), out_bool)
