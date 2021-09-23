from osgeo import osr, ogr, gdal
import pandas as pd
import tkinter
from tkinter import filedialog
from tkinter.filedialog import askopenfilename

def world_to_pixel(geo_matrix, x, y):
    """
    Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
    the pixel location of a geospatial coordinate
    """
    ul_x= geo_matrix[0] # up left_X of image
    ul_y = geo_matrix[3] # up left y of image
    x_dist = geo_matrix[1] # size x of pixel (resolution of image)
    y_dist = geo_matrix[5] # size y of pixel (resolution of image)
    col = int((x - ul_x) / x_dist)
    row = -int((ul_y - y) / y_dist)
    return col, row


# Extract target reference from the tiff file
Root = tkinter.Tk() # Create a Tkinter.Tk() instance    Root.withdraw() # Hide the Tkinter.Tk() instance
Root.withdraw() # Hide the Tkinter.Tk() instance
img_path = askopenfilename(title=u'Open image file', filetypes=[("TIF", ".tif")])
ds = gdal.Open(img_path)
target = osr.SpatialReference(wkt=ds.GetProjection()) # get projection from image

source = osr.SpatialReference()
source.ImportFromEPSG(4326) # EPSG(4326) for WGS84
transform = osr.CoordinateTransformation(source, target)

point = ogr.Geometry(ogr.wkbPoint)
point.AddPoint(99.87550402,19.15297745) # add tung point
point.Transform(transform)

x, y = world_to_pixel(ds.GetGeoTransform(), point.GetX(), point.GetY())
print(x, y)
""" where: ds.GetGeoTransform() = geo_matrix  in world_to_pixel function above
         point.GetX() = x    in  world_to_pixel function
        point.GetY() = y   in  world_to_pixel function"""


#
# GPS_path = filedialog.askopenfilename(title=u'Open XY excel file', filetypes=[("Excel files", ".xlsx .xls")])
# dataGPS = pd.read_excel(GPS_path)
# Lat = dataGPS[['Lat']].values
# Long = dataGPS[['Long']].values
# point = ogr.Geometry(ogr.wkbPoint)
# point.AddPoint(Lat, Long)
# point.Transform(transform)
