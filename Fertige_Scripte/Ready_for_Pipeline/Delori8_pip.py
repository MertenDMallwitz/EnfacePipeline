import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, Rectangle
import pandas as pd
import tifffile as tiff
from pathlib import Path
from datetime import datetime
import os

def compute_segment_stats(FD, X, Y, img, img_path):
    # Parameters
    radii_pix = [0.90*FD, 0.68*FD, 0.46*FD]    # Outer, Middle, Inner rings
    thickness_pix = 0.2*FD
    min_theta = [r - 0.5*thickness_pix for r in radii_pix]
    max_theta = [r + 0.5*thickness_pix for r in radii_pix]                    # Segment thickness
    segment_angle = 40                         # Angle per segment (degrees)
    gap = 5                                    # Angle gap between segments (degrees)
    n_segments = int(360 / (segment_angle + gap))
    fovea_radius = 0.1*FD                      # Central circle
    # Visual field degrees corresponding to FD=315 pixels, for reference
    degrees_map = {0.90*FD: "11.1°", 0.68*FD: "8.4°", 0.46*FD: "5.7°", 0.1*FD: "1.2°", 0.2*FD: "2.5°"}

    def segment_mask(shape, center, r_in, r_out, theta_start, theta_end):
        Y, X = np.ogrid[:shape[0], :shape[1]]
        cx, cy = center
        rr = np.sqrt((X-cx)**2 + (Y-cy)**2)
        angle = (np.rad2deg(np.arctan2(Y-cy, X-cx)) + 360) % 360
        mask_rad = (rr >= r_in) & (rr <= r_out)
        if theta_end > theta_start:
            mask_ang = (angle >= theta_start) & (angle <= theta_end)
        else:
            mask_ang = (angle >= theta_start) | (angle <= theta_end)
        return mask_rad & mask_ang

    stats_list = []
    for idx in range(len(radii_pix)):
        r_outer = max_theta[idx]
        r_inner = min_theta[idx]
        for i in range(n_segments):
            start_angle = (-20 + i*(segment_angle + gap)) % 360
            end_angle = (start_angle + segment_angle) % 360
            mask = segment_mask(img.shape, (X, Y), r_inner, r_outer, start_angle, end_angle)
            segment_pixels = img[mask]
            if segment_pixels.size > 0:
                stats = {
                    'segment_index': idx*n_segments + i,
                    'ring_idx': idx,
                    'i': i,
                    'r_inner': r_inner,
                    'r_outer': r_outer,
                    'start_angle': start_angle,
                    'end_angle': end_angle,
                    'min': float(np.min(segment_pixels)),
                    'max': float(np.max(segment_pixels)),
                    'mean': float(np.mean(segment_pixels)),
                    'std': float(np.std(segment_pixels)),
                    'n': int(segment_pixels.size)
                }
            else:
                stats = {
                    'segment_index': idx*n_segments + i,
                    'ring_idx': idx,
                    'i': i,
                    'start_angle': start_angle,
                    'end_angle': end_angle,
                    'min': None,
                    'max': None,
                    'mean': None,
                    'std': None,
                    'n': 0
                }
            stats_list.append(stats)

    # You can print summary or convert to DataFrame for further analysis:
    import pandas as pd
    df = pd.DataFrame(stats_list)
    df[['mean','std', 'r_inner', 'r_outer']] = df[['mean','std', 'r_inner', 'r_outer']].astype('float32').round(2)
    p = Path(img_path)
    img_stem = p.stem           # filename without extension
    print("Image:", img_stem)
    img_dir = p.parent          # directory path

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_name = f"{img_stem}_segment_stats_{ts}.csv"
    out_path = img_dir / out_name

    df.to_csv(out_path, index=False, sep=';')
    print("Saved:", out_path)
    # Draw fovea (central small circle)
    #ax.add_patch(Circle((X,Y), fovea_radius, color="none", ec="b", lw=2))
    #ax.text(0, 0, "+", color='k', fontsize=16, ha='center', va='center', weight='bold')


    # Parameters draw blue séctors of qaf8 grid
    radii_pix = [0.90*FD, 0.68*FD, 0.46*FD]    # Outer, Middle, Inner rings
    thickness_pix = 0.2*FD
    min_theta = [r - 0.5*thickness_pix for r in radii_pix]
    max_theta = [r + 0.5*thickness_pix for r in radii_pix]                    # Segment thickness
    segment_angle = 40                         # Angle per segment (degrees)
    gap = 5                                    # Angle gap between segments (degrees)
    n_segments = int(360 / (segment_angle + gap))
    fovea_radius = 0.1*FD                      # Central circle
    # Visual field degrees corresponding to FD=315 pixels, for reference
    degrees_map = {0.90*FD: "11.1°", 0.68*FD: "8.4°", 0.46*FD: "5.7°", 0.1*FD: "1.2°", 0.2*FD: "2.5°"}

    fig, ax = plt.subplots(figsize=(8,8))
    ax.set_aspect('equal', 'box')
    plt.imshow(img)

def find_fovea_disk_files(root_dir, suffix="FoveaAndDiskEdge.csv"):
    matches = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith(suffix):
                matches.append(os.path.join(dirpath, fname))
    return matches
def find_map_files(root_dir, suffixes=("map_768x768.tif", "map_768x768.tiff")):
    matches = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.lower().endswith(suffixes):
                matches.append(os.path.join(dirpath, fname))
    return matches



def Delori8_pip(root):
    matches = find_fovea_disk_files(root)
    # Find all FoveaAndDiskEdge.csv files
    print(f"Found {len(matches)} file(s):")
    for p in matches:
        print(p)
    df2=pd.read_csv(p, sep='\t')
    # assume df2 exists and has a column literally named 'SEP=;'
    parts = df2['SEP=;'].astype(str).str.rstrip(';').str.split(';', expand=True)

    # name the new columns (adjust names/count to match your data)
    parts.columns = ['FoveaX','FoveaY','DiscEdgeX','DiscEdgeY']

    # convert to numeric if desired
    parts = parts.apply(pd.to_numeric, errors='coerce')

    # replace the original column or join back into df2
    df2 = df2.drop(columns=['SEP=;']).join(parts)
    df2=df2.dropna()
    FD=int(df2["FoveaX"] - df2["DiscEdgeX"])  # FoveaX-discX
    X=int(df2["FoveaX"])     # FoveaX
    Y=int(df2["FoveaY"])     # FoveaY
    # Now find all map files
    map_files = find_map_files(root)
    print(f"Found {len(map_files)} map file(s):")

    # Process each map file
    for mf in map_files:
        img = tiff.imread(mf)
        df=compute_segment_stats(FD, X, Y, img, mf)