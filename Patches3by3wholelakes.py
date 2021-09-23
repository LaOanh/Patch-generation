


import numpy as np
from osgeo import gdal
from numpy import load, save, concatenate
import tkinter
from tkinter import filedialog
from tkinter.filedialog import askopenfilename


window_size = 3

# STEP 1: LOAD DATA
def load_data():
## TOA_3 angles image
## or AOT image
## or iCOR image
    Root = tkinter.Tk() # Create a Tkinter.Tk() instance    Root.withdraw() # Hide the Tkinter.Tk() instance
    Root.withdraw() # Hide the Tkinter.Tk() instance
    img_path = askopenfilename(title=u'Open image file', filetypes=[("TIF", ".tif")])
    data_img = gdal.Open(img_path).ReadAsArray()
    n_bands, n_row, n_col = data_img.shape
    return data_img, n_bands, n_row, n_col

data_img, n_bands, n_row, n_col = load_data()

# STEP 2: SEARCHING ROW_I AND COL_J OF GOOD PIXELS
# (INCLUDING all PIXELS) HAVE NO VALUES OF 0 and negative IN AREA OF 3*3
def good_pixels(n_bands, n_row, n_col, data_img):
    good_pix = np.zeros([n_bands, 3, 3])
    m = 0
    sel_pix_row_i = []
    sel_pix_col_j = []
    for i in range(1, (n_row-2)):
        for j in range(1, (n_col-2)):
            a1 = i - 1
            a2 = i + 2
            b1 = j - 1
            b2 = j + 2
            for z in range(n_bands):
                good_pix[z, ...] = data_img[z, a1:a2, b1:b2]
            if 0 in good_pix :
                m = m
            else:
                m = m + 1
                sel_pix_row_i += [i]
                sel_pix_col_j += [j]
    # m: NUMBER OF GOOD PIXELS
    # sel_pix_row_i: ROW I OF GOOD PIXEL
    # sel_pix_col_j: COL J OF GOOD PIXEL
    return good_pix, sel_pix_row_i, sel_pix_col_j, m


[good_pixels, sel_pix_row_i, sel_pix_col_j, m] = good_pixels(n_bands, n_row, n_col, data_img)



def extract_patches(sel_pix_row_i,sel_pix_col_j, n_bands, data_img):
    sel_pix_row_i = np.asarray(sel_pix_row_i)
    sel_pix_col_j = np.asarray(sel_pix_col_j)
    n_patch = sel_pix_row_i.shape[0]  # Number of patches
    patches_4D = np.zeros([n_patch, n_bands, 3, 3]) # patches in 4 dimensions (n_patch, n_band, 3, 3)
    for i in range(n_patch):
        a1 = sel_pix_row_i[i] - 1
        a2 = sel_pix_row_i[i] + 2
        b1 = sel_pix_col_j[i] - 1
        b2 = sel_pix_col_j[i] + 2
        for z in range(n_bands):
            patches_4D[i, z, ...] = data_img[z, a1:a2, b1:b2]
    return patches_4D, n_patch


[patches_4D, n_patch] = extract_patches(sel_pix_row_i, sel_pix_col_j, n_bands, data_img)

# 3.SAVE INTO NPY
## save for TOA
path_save = tkinter.filedialog.asksaveasfilename(title=u'Save npy file', filetypes=[("NPY", ".npy")])
save(path_save, patches_4D)


'''Note: if the n_patches_4D of TOA and iCOR are different in one lake. 
    Run TOA image to get the location of sel_pix_col and sel_pix_row.
    Then run iCOR image again and run extract patches to get patches4D from sel_pix_col, sel_pix_row'''