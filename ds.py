from osgeo import gdal
gdal.UseExceptions()

IMAGE_HEIGHT = 23040
IMAGE_WIDTH = 46080

ds: gdal.Dataset = gdal.Open("./mola_data.tif")

band: gdal.Band = ds.GetRasterBand(1)

minimum, maximum, mean, stddev = band.GetStatistics(True, True)
