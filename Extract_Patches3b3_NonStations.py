import numpy as np
import pandas as pd
from osgeo import gdal
from numpy import load, save, concatenate

window_size = 3
'''
Created on 14 April 2020 by Manh Nguyen 
Purposes: 
1. Extracting the 3x3 area (no values of 0) of the non-station pixels 
2. Excluding the stations pixels from all pixels above
'''


# STEP 1: LOAD DATA
def load_data():
    # data_img = gdal.Open(r"D:\ACProgramML\InputforANN\fromENVI\TOAref_WestLake_13Aug19_final.tif").ReadAsArray()
    # insituXY = pd.read_excel(r"D:\ACProgramML\InsituStation\WestLake_13Aug2019.xlsx")
    # data_img = gdal.Open(r"E:\ACProgramML\InputforANN\fromENVI\TOAref_26June2019_ThuLe.tif").ReadAsArray()
    # insituXY = pd.read_excel(r"E:\ACProgramML\InsituStation\LakeThuLe_26June2019.xlsx")
    # data_img = gdal.Open(r"E:\ACProgramML\InputforANN\fromENVI\TOAref_26June2019_VanQuan.tif").ReadAsArray()
    # insituXY = pd.read_excel(r"E:\ACProgramML\InsituStation\LakeVanQuan_26June2019.xlsx")
    ##iCOR_Rrs output load
    # data_img = gdal.Open(r"E:\ACProgramML\InputforANN\fromICORouput\iCORoutput\iCOR_fitwithpptMay2020\Westlake_Rrs_13Aug19_iCOR.tif").ReadAsArray()
    # insituXY = pd.read_excel(r"E:\ACProgramML\InsituStation\WestLake_13Aug2019.xlsx")
    # data_img = gdal.Open(r"E:\ACProgramML\InputforANN\fromICORouput\iCORoutput\iCOR_fitwithpptMay2020\ThuLe_Rrs_26Jun19_iCOR.tif").ReadAsArray()
    # insituXY = pd.read_excel(r"E:\ACProgramML\InsituStation\LakeThuLe_26June2019.xlsx")
    data_img = gdal.Open(r"E:\ACProgramML\InputforANN\fromICORouput\iCORoutput\iCOR_fitwithpptMay2020\VanQuan_Rrs_26June19_iCOR.tif").ReadAsArray()
    insituXY = pd.read_excel(r"E:\ACProgramML\InsituStation\LakeVanQuan_26June2019.xlsx")
    n_bands, n_row, n_col = data_img.shape
    xy_img = insituXY[['X_img', 'Y_img']].values  # In situ samples
    return data_img,  insituXY, xy_img, n_bands, n_row, n_col

data_img, insituXY, xy_img, n_bands, n_row, n_col = load_data()
# STEP 2: SEARCHING ROW_I AND COL_J OF GOOD PIXELS
# (INCLUDING STATION AND NON-STATION PIXELS) HAVE NO VALUES OF 0 IN AREA OF 3*3
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

#STEP 3: GET LOCATION OF IN-SITU SAMPLES AMONG THE GOOD PIXELS TO REMOVE IT.
def locat_insitu_in_good_pixels(m, sel_pix_col_j, sel_pix_row_i, xy_img, insituXY):
    test = 0
    n_insitu_samples = insituXY.shape[0]
    exclud = []
    for i in range (m):
        for j in range(n_insitu_samples):
            if sel_pix_col_j[i] == xy_img[j, 0]  and sel_pix_row_i[i] == xy_img[j, 1]:
                test = test + 1
                exclud += [i]
    #TEST SHOULD BE EQUAL TO NUMBER OF INSITU SAMPLES
    #EXCLUD: THE LOCATION OF THE PIXELS ARE INSITU SAMPLES AMONG GOOD PIXELS
    return test, exclud


test, exclud = locat_insitu_in_good_pixels(m, sel_pix_col_j, sel_pix_row_i, xy_img, insituXY)

# STEP 4:
def remove_insitu(sel_pix_row_i, sel_pix_col_j, exclud):
    exclud = np.asarray(exclud)
    n_remove = exclud.shape[0] # number of samples must be removed
    sel_non_sta_i = sel_pix_row_i.copy() #SEL_NON_STA_I: ROW OF GOOD PIXELS EXCLUDE INSITU PIXELS
    sel_non_sta_j = sel_pix_col_j.copy() #SEL_NON_STA_J: COL OF GOOD PIXELS EXCLUDE INSITU PIXELS
    for e in range(n_remove):
        so = exclud[e] # VAR "SO" WILL BE A VALUE WHICH REPRESENT LOCATION OF INSITU
        sel_non_sta_i[so] = 0 #ASSIGN IT TO ZERO AND THEN DO FILTER TO REMOVE IT
        sel_non_sta_j[so] = 0 #ASSIGN IT TO ZERO AND THEN DO FILTER TO REMOVE IT
    # sel_non_sta_i = sel_non_sta_i.tolist()
    # sel_non_sta_j = sel_non_sta_j.tolist()
    r_i = list(filter((0).__ne__, sel_non_sta_i)) #r_i: row i  filter all 0 value and remove them in row i
    c_j = list(filter((0).__ne__, sel_non_sta_j)) #c_j: col j filter all 0 value and remove them in column j
    return r_i, c_j, sel_non_sta_i, sel_non_sta_j


r_i, c_j, sel_non_sta_i, sel_non_sta_j = remove_insitu(sel_pix_row_i, sel_pix_col_j, exclud)

# STEP 5:
def extrt_patches_nonstation(r_i, c_j, n_bands, data_img):
    r_i= np.asarray(r_i)
    n0_non_sample = r_i.shape[0] #n0_non_sample: Number of non-station samples
    non_sample_4D = np.zeros([n0_non_sample, n_bands, 3, 3])
    for i in range(n0_non_sample):
        a1 = r_i[i] - 1
        a2 = r_i[i] + 2
        b1 = c_j[i] - 1
        b2 = c_j[i] + 2
        for z in range(n_bands):
            non_sample_4D[i, z, ...] = data_img[z, a1:a2, b1:b2]
    return non_sample_4D, n0_non_sample


non_sample_4D, n0_non_sample = extrt_patches_nonstation(r_i, c_j, n_bands, data_img)

## save for TOA
# path_save = "E:\\ACProgramML\\InputforANN\\fromENVI\\Patches_nonStation\\"
# save(path_save + 'WL_4D_nonsta_13Aug19.npy', non_sample_4D)

# path_save = "E:\\ACProgramML\\InputforANN\\fromENVI\\Patches_nonStation\\"
# save(path_save + 'ThuLe_4D_nonsta_26June19.npy', non_sample_4D)

# path_save = "E:\\ACProgramML\\InputforANN\\fromENVI\\Patches_nonStation\\"
# save(path_save + 'VanQuan_4D_nonsta_26June19.npy', non_sample_4D)
#

## save for iCOR
# path_save = "E:\\ACProgramML\\InputforANN\\fromICORouput\\Patches_nonStation\\"
# save(path_save + 'WL_4D_nonsta_iCOR_Rrs_13Aug19.npy', non_sample_4D)

# path_save = "E:\\ACProgramML\\InputforANN\\fromICORouput\\Patches_nonStation\\"
# save(path_save + 'ThuLe_4D_nonsta_iCOR_Rrs_26June19.npy', non_sample_4D)
#
path_save = "E:\\ACProgramML\\InputforANN\\fromICORouput\\Patches_nonStation\\"
save(path_save + 'VanQuan_4D_nonsta_iCOR_Rrs_26June19.npy', non_sample_4D)