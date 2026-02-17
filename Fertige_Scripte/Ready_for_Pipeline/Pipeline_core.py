from logging import root
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
import Eyeseg_e2e_to_xml_final_pip
import Eyeseg_commands_pip
import eye_to_enface_maps_depth_binarized_pip
import Delori8_pip
import Distance_Map_pip
input_e2e_file = "C:\\Users\\50126825\\Desktop\\octa\\Drusen_algorithmus\\Datenexperimente\\MACUSTAR313-0_Retina_20191206_000.e2e"
output_directory = "C:\\Users\\50126825\\Desktop\\octa\\Drusen_algorithmus\\Fertige_Scripte\\Ready_for_Pipeline\\End"

def generator(input_e2e_file, output_directory, e2e_to_xml=True, eyeseg_commands=True, drusen_map=True, delori8=False, distance_map=True):
    if e2e_to_xml ==True:
        Eyeseg_e2e_to_xml_final_pip.e2e_to_xml_final_pip(input_e2e_file, output_directory)
        print("Output directory from e2e_to_xml_final_pip:", output_directory)
    if eyeseg_commands ==True:
        Eyeseg_commands_pip.eyeseg_commands_pip(output_directory)
        print("Eyeseg commands executed successfully.")
    if drusen_map ==True:
        drusen_map_dir = eye_to_enface_maps_depth_binarized_pip.eye_to_enface_maps_depth_binarized_pip(os.path.join(output_directory, "processed\\", "OUTPUT.eye"))
        print("Drusen maps generated successfully."+ drusen_map_dir)
    if delori8 ==True:  
        #Nur wenn Fovea und Disk Edge Dateien vorhanden sind
        Delori8_pip.Delori8_pip(output_directory)
        print("Delori8 processing completed successfully.")
    if distance_map ==True:
        Distance_Map_pip.Distance_Map(os.path.join(drusen_map_dir, "_boolean_map_768x768.tif"))
        print("Distance map computation completed successfully.")

def find_e2e_files(MACUSTAR_root):
    matches = []
    for dirpath, _, filenames in os.walk(MACUSTAR_root):
        for fn in filenames:
            if fn.lower().endswith(".e2e"):
                matches.append(os.path.join(dirpath, fn))
    return matches

list=find_e2e_files(r'C:\Users\50126825\Desktop\octa\Drusen_algorithmus\Datenexperimente\3130150007')
print("Found .e2e files:", list)
for i in list:
    output_dir=os.path.join(r'C:\Users\50126825\Desktop\octa\Drusen_algorithmus\Datenexperimente\MAC', i.split("\\")[-1].replace(".e2e",""))
    os.makedirs(output_dir, exist_ok=True)
    generator(i, output_dir, e2e_to_xml=True, eyeseg_commands=True, drusen_map=True, delori8=False, distance_map=True)