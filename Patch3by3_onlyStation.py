

import numpy as np
from osgeo import gdal
import pandas as pd
from numpy import load, save, concatenate
import tkinter
from tkinter import filedialog
from tkinter.filedialog import askopenfilename


window_size = 3

# STEP 1: LOAD DATA image and XY file

Root = tkinter.Tk()  # Create a Tkinter.Tk() instance
Root.withdraw()  # Hide the Tkinter.Tk() instance

GPS_path = filedialog.askopenfilename(title=u'Open XY excel file', filetypes=[("Excel files", ".xlsx .xls")])
dataXY = pd.read_excel(GPS_path)
img_path = askopenfilename(title=u'Open image file', filetypes=[("TIF", ".tif")])
data_img = gdal.Open(img_path).ReadAsArray()
n_bands, n_row, n_col = data_img.shape

# STEP 2: SELECT THE INSITU MEET THE REQUIREMENT OF AN AREA OF 3*3 WITHOUT VALUE OF 0
def selected_samples(data_img, dataXY):
    [z, x, y] = data_img.shape # z is the depth of image (number of bands)
    xy_img = dataXY[['X_img', 'Y_img']].values # read only 2 columns X_img and Y_img

    n_samples = xy_img.shape[0] # number of samples/stations
    # Trong Python, khi tạo một array rỗng 3D thì depth luôn phải trên đầu, thứ tự: depth, width, height
    sample_4D = np.zeros([n_samples, z, 3, 3])  # create a sample 4 dimensions
    sel_samples = []   # create list of select samples
    m = 0
    for i in range(n_samples):
        a1 = xy_img[i][0] - 1  #[0] is first column (X_img)
        a2 = xy_img[i][0] + 2
        b1 = xy_img[i][1] - 1  # [1] is Y_img column
        b2 = xy_img[i][1] + 2
        for j in range(z):
            sample_4D[i][j] = data_img[j, b1:b2, a1:a2] # including pixels have 0 value
        if 0 in sample_4D[i]:
            m = m
        else:
            m = m + 1
            sel_samples += [i]
    # THE LOCATION OF THE SELECTED INSITU SAMPLES WILL BE STORED IN THE SEL_SAMPLES
    # THE SAMPLE_4D CONTAIN THE INFORMATION OF AN AREA OF 3*3 OF ALL INSITU SAMPLE
    return z, m, sel_samples, sample_4D


z, m, sel_samples, sample_4D = selected_samples(data_img, dataXY)


#STEP 3: EXTRACT ONLY THE INFORMATION (TOA/Rrs) OF THE SELECTED INSITU SAMPLE without 0 value
def extract(z, m, sel_samples, sample_4D):
    patches_4D = np.zeros([m, z, 3, 3])
    for k in range(m):
        patches_4D[k] = sample_4D[sel_samples[k]]
    #patches_4D IS 4D TOA/Rrs DATA OF THE SELECTED INSITU SAMPLES
    return patches_4D


patches_4D = extract(z, m, sel_samples, sample_4D)


# CAREFULLY CHECK BEFORE SAVE DATA


path_save = tkinter.filedialog.asksaveasfilename(title=u'Save npy file', filetypes=[("NPY", ".npy")])
save(path_save, patches_4D)
