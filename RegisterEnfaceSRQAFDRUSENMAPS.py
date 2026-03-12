import cv2
import numpy as np
import pandas as pd
from pathlib import Path

# Load QAFF.tiff
qaff = cv2.imread('QAFF.tiff', cv2.IMREAD_UNCHANGED)
print(f"QAFF shape: {qaff.shape}")

# Load images from GeenaStandardRetinaAge folder
standard_retina_folder = Path('GeenaStandardRetinaAge')
standard_retina_images = []
for img_file in sorted(standard_retina_folder.glob('*')):
    img = cv2.imread(str(img_file), cv2.IMREAD_UNCHANGED)
    if img is not None:
        standard_retina_images.append(img)
        print(f"Loaded {img_file.name}: {img.shape}")

# Load fovea and disc edge data
fovea_data = pd.read_csv('FoveaandDiscedge.csv')
fovea_x = fovea_data['FoveaX'].values[0]
fovea_y = fovea_data['FoveaY'].values[0]
print(f"Fovea coordinates: ({fovea_x}, {fovea_y})")

# Align: center QAFF (768x768) on the fovea
# Calculate offset to center fovea in the image
qaff_center = 768 / 2
offset_x = qaff_center - fovea_x
offset_y = qaff_center - fovea_y

# Create transformation matrix for translation
M = np.float32([[1, 0, offset_x], [0, 1, offset_y]])
qaff_aligned = cv2.warpAffine(qaff, M, (768, 768))

print(f"QAFF aligned with fovea centered at ({qaff_center}, {qaff_center})")