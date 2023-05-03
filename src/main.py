import os
import pandas as pd
import numpy as np
import skimage
from skimage.color import label2rgb, rgb2gray
from skimage.measure import label, regionprops_table, regionprops
from skimage.segmentation import expand_labels
import matplotlib.pyplot as plt
from skimage.util import img_as_ubyte
from tifffile import imread, imwrite

from plant_seg import plant_segmentation

DATA_DIR = os.path.join('..', 'data')
PURE_GREEN = [0,255,0]
IMG_FILES = os.listdir(DATA_DIR)


for file in IMG_FILES:
    acdc_basename = file.split('.')[0]
    acdc_img_path = os.path.join('..', 'acdc_data', acdc_basename, 'Position_1', 'Images')
    if os.path.isdir(acdc_img_path):
        print(f'ACDC data already existing for {acdc_basename}. Not overwriting, skipping Image')
        pass
    else:
        print(f'Performing plant phenotyping for file {acdc_basename}.')
        # read image
        img = skimage.io.imread(os.path.join(DATA_DIR, file))
        print('Calculating initial binary segmentation')
        binary_seg = plant_segmentation(img, ref_color=PURE_GREEN)

        # merge segmented objects based on their expanded label
        print('Labeling plant objects and removing fragments')
        labeled = label(binary_seg)
        labeled = skimage.morphology.remove_small_objects(labeled, min_size=500) # after merging remove small objects
        expanded = expand_labels(binary_seg, distance=20)
        expanded_labeled = label(expanded)

        new_labeled = np.zeros(labeled.shape)
        for l_id in np.unique(labeled):
            if l_id>0:
                l_id_exp_ids = expanded_labeled[labeled==l_id]
                # expanded contains old objects, so there is only one new id for each old id
                assert len(np.unique(l_id_exp_ids))==1
                new_l_id = l_id_exp_ids[0]
                new_labeled[labeled==l_id] = new_l_id
        new_labeled = new_labeled.astype(int)
        new_labeled = skimage.morphology.remove_small_objects(new_labeled, min_size=1500)
        
        print('Calculating areas for segmented plants.')
        rp_table = regionprops_table(new_labeled, properties=['label', 'centroid', 'area', 'axis_major_length', 'axis_minor_length'])
        result_df = pd.DataFrame(rp_table)
        result_df['filename'] = file
        result_df['elongation'] = result_df.axis_major_length / result_df.axis_minor_length

        # eliminate elongated "plants"
        remove_labels = result_df[result_df.elongation>4].label
        for rl in remove_labels:
            new_labeled[new_labeled==rl] = 0

        os.mkdir(os.path.join('..', 'acdc_data', acdc_basename))
        os.mkdir(os.path.join('..', 'acdc_data', acdc_basename, 'Position_1'))
        os.mkdir(acdc_img_path)
        imwrite(os.path.join(acdc_img_path, f'{acdc_basename}_grayscale.tif'), rgb2gray(img))
        metadata_df = pd.DataFrame({'Description':['basename'], 'values':[acdc_basename]}, index=None)
        metadata_df.to_csv(os.path.join(acdc_img_path, f'{acdc_basename}_metadata.csv'))
        np.savez_compressed(os.path.join(acdc_img_path, f'{acdc_basename}_segm.npz'), new_labeled)


        """
        fig, axs = plt.subplots(ncols=2, figsize=(12,6))
        axs[0].imshow(img)
        axs[0].set_title('Input Image')
        axs[1].imshow(label2rgb(new_labeled))
        axs[1].set_title('Plant Segmentation')
        plt.show()
        """


