import numpy as np
from skimage.filters import threshold_minimum

def plant_segmentation(img, ref_color=[0,255,0]):
    pure_green = np.array([[ref_color]])
    dist_to_green = np.abs(img - pure_green).sum(axis=-1)
    thres = threshold_minimum(dist_to_green)
    return dist_to_green < thres