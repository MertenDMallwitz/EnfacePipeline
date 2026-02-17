# -*- coding: utf-8 -*-
"""
Created on Thu Dec  4 17:02:04 2025

@author: 50126825
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Dec  4 13:41:41 2025

@author: 50126825
"""
def e2e_to_xml_final_pip(e2e_path, output_directory):

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

    # Import HEYEX E2E export
    from eyepy.data import load
    struc_ev = ep.import_heyex_e2e(e2e_path)
    out_dir = Path(output_directory)
    img = struc_ev.localizer.data
    plt.imshow(img, cmap='gray', origin='upper')
    # Ensure output directory exists before writing files
    out_dir.mkdir(parents=True, exist_ok=True)


    # 1. Extract scale_* variables and define coordinate system
    # IR image is 9mm × 9mm or 768 × 768 pixels or 30° × 30°
    IR_SIZE_MM = 9.0  # IR image size in mm
    IR_SIZE_PIXELS = 768  # IR image size in pixels
    IR_FOV_DEGREES = 30.0  # IR field of view in degrees
    BSCAN_FOV_DEGREES = 25.0  # B-scan field of view in degrees
    NUM_BSCANS = 241  # Number of B-scans

    # Calculate ScaleX and ScaleY in µm/pixel
    # IR is 9mm (9000 µm) across 768 pixels
    scale_x_for_str=round(9000.0 / IR_SIZE_PIXELS/1000.0, 4)
    scale_x = str(scale_x_for_str)  # µm/pixel ≈ 11.72
    scale_y = str(9000.0 / IR_SIZE_PIXELS/1000.0)  # µm/pixel ≈ 11.72
    # Wenn, dann scale_z in  0.3 mm/degree (30° = 9mm) -> µm/pixel
    scale_z = str(IR_SIZE_MM*BSCAN_FOV_DEGREES/IR_FOV_DEGREES/ NUM_BSCANS)
    scale_unit = str(struc_ev.meta["scale_unit"])
    laterality = str(struc_ev.meta["laterality"])
    visit_date = str(struc_ev.meta["visit_date"])
    exam_time = "01.01.1970"  # Placeholder if not available
    patient= "not defined"
    firstname = 'Unknown'
    lastname = 'Unknown'
    dob = '1900-01-01'
    pid = '0000000'
    patient_id = '0000000'


    # Calculate Y positions for B-scans
    # 25° FOV centered in 30° IR: starts at 27.5° and goes to 2.5°
    # Convert degrees to mm: 30° = 9mm, so 1° = 0.3mm
    DEGREES_TO_MM = IR_SIZE_MM / IR_FOV_DEGREES  # 0.3 mm/degree

    # Generate 241 equally spaced Y positions from 27.5° to 2.5°
    start_angle_deg = 27.5
    end_angle_deg = 2.5
    y_angles = np.linspace(start_angle_deg, end_angle_deg, NUM_BSCANS)
    y_positions_mm = y_angles * DEGREES_TO_MM  # Convert to mm

    print(f'scale_z: {scale_z}, scale_x: {scale_x}, scale_y: {scale_y}, scale_unit: {scale_unit}')

    laterality=laterality[-2:]
    if laterality=="OD":
        laterality="R"
    else:
        laterality="L"
    # Immer gleiche Werte eintragen
    HEDX = ET.Element('HEDX')
    body = ET.SubElement(HEDX, 'BODY')

    sub1 = ET.SubElement(body, 'ExportType')
    sub1.text = 'Data'

    sub2 = ET.SubElement(body, 'SWVersion')


    name = ET.SubElement(sub2, 'Name')
    name.text = 'Spectralis Viewing Module'

    version = ET.SubElement(sub2, 'Version')
    version.text = 'LUXIS'

    #Ab hier variabele Werte eintragen
    sub3 = ET.SubElement(body, 'Patient')
    sub3.text =''
    patient_uid_list = ET.SubElement(sub3, 'PatientUIDList')
    patient_uid_list.text =''
    NumUIDs = ET.SubElement(patient_uid_list, 'NumUIDs')
    NumUIDs.text = '1'
    patient_uid=ET.SubElement(patient_uid_list, 'PatientUID')
    patient_uid.text = ''
    Source=ET.SubElement(patient_uid, 'Source')
    Source.text='LOC15468318'
    UID=ET.SubElement(patient_uid, 'UID')
    UID.text='LOC15468318.1.3.6.1.4.1.33437.10.7.14690379.13188926265.4273.7'
    ID = ET.SubElement(patient_uid, 'ID')
    ID.text= patient_id
    LastName=ET.SubElement(patient_uid_list, 'LastName')
    LastName.text= lastname
    FirstNames=ET.SubElement(patient_uid_list, 'FirstNames')
    FirstNames.text= firstname
    Birthdate=ET.SubElement(sub3, 'Birthdate')
    Birthdate.text=''
    Date=ET.SubElement(Birthdate, 'Date')
    Date.text=''
    Year=ET.SubElement(Date, 'Year')
    Year.text='1900'
    Month=ET.SubElement(Date, 'Month')
    Month.text='01'
    Day=ET.SubElement(Date, 'Day')
    Day.text='01'
    Sex=ET.SubElement(sub3, 'Sex')
    Sex.text='F'

    Study=ET.SubElement(sub3, 'Study')
    Study.text=''
    StudyUID=ET.SubElement(Study, 'StudyUID')
    StudyUID.text='LOC15468318.1.3.6.1.4.1.33437.10.8.14690379.13188926254.4272.8'
    ID_2=ET.SubElement(Study, 'ID')
    ID_2.text=patient_id
    StudyDate=ET.SubElement(Study, 'StudyDate')
    StudyDate.text=''
    Year_2=ET.SubElement(StudyDate, 'Year')
    Year_2.text=exam_time[0:4]
    Month_2=ET.SubElement(StudyDate, 'Month')
    Month_2.text=exam_time[5:7]
    Day_2=ET.SubElement(StudyDate, 'Day')
    Day_2.text=exam_time[8:10]
    Operator=ET.SubElement(Study, 'Day')
    Operator.text='LUXIS'
    ReferringPhysician=ET.SubElement(Study, 'ReferringPhysician')
    ReferringPhysician.text=''
    Series=ET.SubElement(Study, 'Series')
    Series.text=''
    SeriesUID=ET.SubElement(Series, 'SeriesUID')
    SeriesUID.text='LOC2989778.1.3.6.1.4.1.33437.10.9.10192895.13289492176.11502.9'
    ID_3=ET.SubElement(Series, 'ID')
    ID_3.text=patient_id
    Examined_Structure=ET.SubElement(Series, 'ExaminedStructure')
    Examined_Structure.text='Retina'
    Modality=ET.SubElement(Series, 'Modality')
    Modality.text='OCT'
    ModalityProcedure=ET.SubElement(Series, 'ModalityProcedure')
    ModalityProcedure.text='IR_OCT'
    Type=ET.SubElement(Series, 'Type')
    Type.text='Volume'
    Laterality=ET.SubElement(Series, 'Laterality')
    Laterality.text=laterality
    GeneralEquipment=ET.SubElement(Series, 'GeneralEquipment')
    GeneralEquipment.text='Heidelberg Engineering'
    ManufacturerModelName=ET.SubElement(GeneralEquipment, 'ManufacturerModelName')
    ManufacturerModelName.text='Spectralis'
    AQMVersion=ET.SubElement(GeneralEquipment, 'AQMVersion')
    AQMVersion.text=''
    Name=ET.SubElement(AQMVersion, 'Name')
    Name.text='Spectralis Acquisition Module'
    Version=ET.SubElement(AQMVersion, 'Version')
    Version.text='TBD'
    OCTFieldSize=ET.SubElement(Series, 'OCTFieldSize')
    OCTFieldSize.text=''
    Width=ET.SubElement(OCTFieldSize, 'Width')
    Width.text='30'
    Height=ET.SubElement(OCTFieldSize, 'Height')
    Height.text='25'
    ThicknessGrid=ET.SubElement(Series, 'ThicknessGrid')
    ThicknessGrid.text=''
    ThicknessGrid2=ET.SubElement(Series, 'ThicknessGrid')
    ThicknessGrid2.text=''
    NumImages=ET.SubElement(Series, 'NumImages')
    NumImages.text=str(NUM_BSCANS+1)

    Image0=ET.SubElement(Series, 'Image')
    Image0.text=''
    ID_4=ET.SubElement(Image0, 'ID')
    ID_4.text='0'
    ImageNumber=ET.SubElement(Image0, 'ImageNumber')
    ImageNumber.text='0'
    Laterality_0=ET.SubElement(Image0, 'Laterality')
    Laterality_0.text=laterality
    AcquisitionTime=ET.SubElement(Image0, 'AcquisitionTime')
    AcquisitionTime.text=''
    Time=ET.SubElement(AcquisitionTime, 'Time')
    Time.text=''
    Hour=ET.SubElement(Time, 'Hour')
    Hour.text=struc_ev.localizer.meta["visit_date"]
    Minute=ET.SubElement(Time, 'Minute')
    Minute.text=''
    Second=ET.SubElement(Time, 'Second')
    Second.text=''
    UTCBias=ET.SubElement(Time, 'UTCBias')
    UTCBias.text=''
    ImageType=ET.SubElement(Image0, 'ImageType')
    ImageType.text=''
    Type=ET.SubElement(ImageType, 'Type')
    Type.text='LOCALIZER'
    LightSource=ET.SubElement(ImageType, 'LightSource')
    LightSource.text='IR'

    OphthalmicAcquisitionContext=ET.SubElement(Image0, 'OphthalmicAcquisitionContext')
    OphthalmicAcquisitionContext.text=''
    Width_2=ET.SubElement(OphthalmicAcquisitionContext, 'Width')
    Width_2.text=str(struc_ev.localizer.size_x)
    Height_2=ET.SubElement(OphthalmicAcquisitionContext, 'Height')
    Height_2.text=str(struc_ev.localizer.size_y)
    ScaleX=ET.SubElement(OphthalmicAcquisitionContext, 'ScaleX')
    ScaleX.text=scale_x
    ScaleY=ET.SubElement(OphthalmicAcquisitionContext, 'ScaleY')
    ScaleY.text=scale_y
    #Focus=ET.SubElement(OphthalmicAcquisitionContext, 'Focus')
    #Focus.text=struc_ev.localizer.scan_focus
    ImageData0=ET.SubElement(Image0, 'ImageData')
    ImageData0.text=''
    Extension0=ET.SubElement(ImageData0, 'Extension')
    Extension0.text='TIF'
    ExamURL=ET.SubElement(ImageData0, 'ExamURL')
    ExamURL.text='localizer.tif'
    # Put out Localizer Image
    localizer = struc_ev.localizer            # EyeBscan object
    out_localizer = out_dir / f"localizer.tif"
    img=localizer.data
    rgb = np.stack([img, img, img], axis=-1)
    tifffile.imwrite(out_localizer, rgb, photometric="rgb")

    #Bscan Loop ET and TIFF export
    for idx, bscan in enumerate(struc_ev):
        img=bscan.data
        out_bscan = out_dir / f"{idx}.tif"
        # Create RGB image with equal channels
        rgb = np.stack([img, img, img], axis=-1)  # shape -> (H, W, 3)

        # Convert to uint8 if needed (recommended for TIFF viewers)
        if not np.issubdtype(rgb.dtype, np.uint8):
            rgb = img_as_ubyte(rgb)  # scales floats in [0,1] or clips/normalizes other dtypes
        tifffile.imwrite(out_bscan, rgb, photometric='rgb')
        exec(f"BImage{idx} = ET.SubElement(Series, 'Image')")
        exec(f"BImage{idx}.text = ''")
        exec(f"BID_{idx} = ET.SubElement(BImage{idx}, 'ID')")
        exec(f"BID_{idx}.text = '{idx+1}'")
        exec(f"BImageNumber_{idx} = ET.SubElement(BImage{idx}, 'ImageNumber')")
        exec(f"BImageNumber_{idx}.text = '{idx+1}'")
        exec(f"BLaterality_{idx} = ET.SubElement(BImage{idx}, 'Laterality')")
        exec(f"BLaterality_{idx}.text = laterality")
        exec(f"BAcquisitionTime_{idx} = ET.SubElement(BImage{idx}, 'AcquisitionTime')")
        exec(f"BAcquisitionTime_{idx}.text = ''")
        exec(f"BTime_{idx} = ET.SubElement(BAcquisitionTime_{idx}, 'Time')")
        exec(f"BTime_{idx}.text = ''")
        exec(f"BHour_{idx} = ET.SubElement(BTime_{idx}, 'Hour')")
        exec(f"BHour_{idx}.text = ''")
        exec(f"BMinute_{idx} = ET.SubElement(BTime_{idx}, 'Minute')")
        exec(f"BMinute_{idx}.text = ''")
        exec(f"BSecond_{idx} = ET.SubElement(BTime_{idx}, 'Second')")
        exec(f"BSecond_{idx}.text = ''")
        exec(f"BUTCBias_{idx} = ET.SubElement(BTime_{idx}, 'UTCBias')")
        exec(f"BUTCBias_{idx}.text = ''")
        exec(f"BImageType_{idx} = ET.SubElement(BImage{idx}, 'ImageType')")
        exec(f"BImageType_{idx}.text = ''")
        exec(f"BType_{idx} = ET.SubElement(BImageType_{idx}, 'Type')")
        exec(f"BType_{idx}.text = 'OCT'")
        exec(f"BOphthalmicAcquisitionContext_{idx} = ET.SubElement(BImage{idx}, 'OphthalmicAcquisitionContext')")
        exec(f"BOphthalmicAcquisitionContext_{idx}.text = ''")
        exec(f"BWidth_{idx} = ET.SubElement(BOphthalmicAcquisitionContext_{idx}, 'Width')")
        exec(f"BWidth_{idx}.text = str(bscan.data.shape[1])")
        exec(f"BHeight_{idx} = ET.SubElement(BOphthalmicAcquisitionContext_{idx}, 'Height')")
        exec(f"BHeight_{idx}.text = str(bscan.data.shape[0])")
        exec(f"BScaleX_{idx} = ET.SubElement(BOphthalmicAcquisitionContext_{idx}, 'ScaleX')")
        exec(f"BScaleX_{idx}.text = str(scale_x)")
        exec(f"BScaleY_{idx} = ET.SubElement(BOphthalmicAcquisitionContext_{idx}, 'ScaleY')")
        exec(f"BScaleY_{idx}.text = str(scale_y)")
        exec(f"BResolution_{idx} = ET.SubElement(BOphthalmicAcquisitionContext_{idx}, 'Resolution')")
        exec(f"BResolution_{idx}.text = ''")
        exec(f"BStart_{idx} = ET.SubElement(BOphthalmicAcquisitionContext_{idx}, 'Start')")
        exec(f"BStart_{idx}.text = ''")
        exec(f"BCoord_{idx} = ET.SubElement(BStart_{idx}, 'Coord')")
        exec(f"BCoord_{idx}.text = ''")
        exec(f"BX_{idx} = ET.SubElement(BCoord_{idx}, 'X')")
        # X coordinates: always 0 to 9.0 mm (full IR width)
        exec(f"BX_{idx}.text = '0.000'")
        exec(f"BY_{idx} = ET.SubElement(BCoord_{idx}, 'Y')")
        # Y coordinate: same for start and end of a single B-scan
        exec(f"BY_{idx}.text = str(round(y_positions_mm[idx], 6))")
        exec(f"BEnd_{idx} = ET.SubElement(BOphthalmicAcquisitionContext_{idx}, 'End')")
        exec(f"BEnd_{idx}.text = ''")
        exec(f"BCoordEnd_{idx} = ET.SubElement(BEnd_{idx}, 'Coord')")
        exec(f"BCoordEnd_{idx}.text = ''")
        exec(f"BXEnd_{idx} = ET.SubElement(BCoordEnd_{idx}, 'X')")
        # X end: full width of IR image
        exec(f"BXEnd_{idx}.text = '{IR_SIZE_MM-0.015}'")
        exec(f"BYEnd_{idx} = ET.SubElement(BCoordEnd_{idx}, 'Y')")
        # Y end: same as Y start for this B-scan
        exec(f"BYEnd_{idx}.text = str(round(y_positions_mm[idx], 6))")
        exec(f"BImageData_{idx} = ET.SubElement(BImage{idx}, 'ImageData')")
        exec(f"BImageData_{idx}.text = ''")
        exec(f"BExtension_{idx} = ET.SubElement(BImageData_{idx}, 'Extension')")
        exec(f"BExtension_{idx}.text = 'TIF'")
        exec(f"BExamURL_{idx} = ET.SubElement(BImageData_{idx}, 'ExamURL')")
        exec(f"BExamURL_{idx}.text = f'{idx}.tif'")

    # Save to file
    tree = ET.ElementTree(HEDX)

    tree.write(str(out_dir / 'output.xml'), encoding="utf-8", xml_declaration=True)