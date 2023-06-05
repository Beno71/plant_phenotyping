import os
import pandas as pd
import glob
import time


DATA_DIR = os.path.join('..', 'data')
IMG_FILES = os.listdir(DATA_DIR)
# while checking all folders, collect data in overall table if not yet saved there
timestr = time.strftime("%Y%m%d_%H%M%S")
OVERALL_TABLE_PATH = os.path.join('..', 'combined_data', f'combined_data_{timestr}.csv')
if os.path.isfile(OVERALL_TABLE_PATH):
    overall_df = pd.read_csv(OVERALL_TABLE_PATH)
else:
    overall_df = pd.DataFrame(columns=['file_id', 'plant_id', 'cell_area_cm2'])


for file in IMG_FILES:
    acdc_basename = file.split('.')[0]
    acdc_img_path = os.path.join('..', 'acdc_data', acdc_basename, 'Position_1', 'Images')
    if os.path.isdir(acdc_img_path):
        print(f'Appending data from {acdc_basename}.')
        acdc_output_search = glob.glob(os.path.join(acdc_img_path, '*_acdc_output.csv'))
        if len(acdc_output_search) == 1:
            acdc_output_path = acdc_output_search[0]
        elif len(acdc_output_search) == 0:
            print(f'No output file existing for {acdc_basename}. Skipping File')
        else:
            print(f'Found multiple output files for {acdc_basename}. Skipping File')
            continue
        acdc_output = pd.read_csv(acdc_output_path).loc[:,['Cell_ID', 'cell_area_cm2']]
        acdc_output['file_id'] = acdc_basename
        overall_df = pd.concat([overall_df, acdc_output], ignore_index=True)
    else:
        continue


overall_df.to_csv(OVERALL_TABLE_PATH, index=False)
