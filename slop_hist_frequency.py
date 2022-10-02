# /gpfs/home/yuk/anaconda3/envs/py36/bin/python3
# -*- coding: utf-8 -*-

# tempmax filepath /gpfs/home/yuk/dailymaxtemp/cru/gs-temp/gs_temp_max
# landcover filepath /gpfs/home/yuk/LAI/out_inter

import numpy
import os
from osgeo import gdal, gdalconst
from osgeo import ogr, osr
import math
import xlrd
import xlwt
import pandas
import random
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.interpolate import make_interp_spline


plt.rc('font', family='Times New Roman')
plt.rcParams["font.weight"] = "bold"
plt.rcParams["axes.labelweight"] = "bold"

file = r'/gs_temp_max/1982-1988_summer_temMAX_mean_CRUbias40.tif'
lai_data1 = gdal.Open(file)
im_width1 = int(lai_data1.RasterXSize)
im_height1 = int(lai_data1.RasterYSize)
band1 = lai_data1.GetRasterBand(1)  # bestmodel
image1 = band1.ReadAsArray(0, 0, im_width1, im_height1)
im_geotrans0 = lai_data1.GetGeoTransform()
im_proj0 = lai_data1.GetProjection()

file2 = r'/gs_temp_max/1988-1994_summer_temMAX_mean_CRUbias40.tif'
lai_data2 = gdal.Open(file2)
image2 = lai_data2.ReadAsArray(0, 0, im_width1, im_height1)

file3 = r'/gs_temp_max/1994-2000_summer_temMAX_mean_CRUbias40.tif'
lai_data3 = gdal.Open(file3)
image3 = lai_data3.ReadAsArray(0, 0, im_width1, im_height1)

file4 = r'/gs_temp_max/2000-2006_summer_temMAX_mean_CRUbias40.tif'
lai_data4 = gdal.Open(file4)
image4 = lai_data4.ReadAsArray(0, 0, im_width1, im_height1)

file5 = r'/gs_temp_max/2006-2012_summer_temMAX_mean_CRUbias40.tif'
lai_data5 = gdal.Open(file5)
image5 = lai_data5.ReadAsArray(0, 0, im_width1, im_height1)

file6 = r'/gs_temp_max/2012-2018_summer_temMAX_mean_CRUbias40.tif'
lai_data6 = gdal.Open(file6)
image6 = lai_data6.ReadAsArray(0, 0, im_width1, im_height1)

fileopt = r'/gs_temp_max/optima_cru_mean82-18_nonan.tif'
lai_data7 = gdal.Open(fileopt)
image7 = lai_data7.ReadAsArray(0, 0, im_width1, im_height1)

filecp = r'/gs_temp_max/timenode_maxtemp_GS_CRU.tif'
lai_data8 = gdal.Open(filecp)
image8 = lai_data8.ReadAsArray(0, 0, im_width1, im_height1)

file_veg = r'/out_inter/veg_mean0.2_0.5du.tif'
globe_data = gdal.Open(file_veg)
veg = globe_data.ReadAsArray(0, 0, im_width1, im_height1)

t1 = []
t2 = []
t3 = []
t4 = []
t5 = []
t6 = []
t7 = []
t8 = []

for ii in range(0, im_height1):
    for jj in range(0, im_width1):
        if veg[ii, jj] > 0:
            if (~numpy.isnan(image1[ii, jj])) and 0<image1[ii, jj]<40:
                t1.append(image1[ii,jj])
            else:
                continue
for ii in range(0, im_height1):
    for jj in range(0, im_width1):
        if veg[ii, jj] > 0:
            if (~numpy.isnan(image2[ii, jj])) and 0<image2[ii, jj]<40:
                t2.append(image2[ii, jj])
            else:
                continue

for ii in range(0, im_height1):
    for jj in range(0, im_width1):
        if veg[ii, jj] > 0:
            if (~numpy.isnan(image3[ii, jj])) and 0<image3[ii, jj]<40:
                t3.append(image3[ii, jj])
            else:
                continue
for ii in range(0, im_height1):
    for jj in range(0, im_width1):
        if veg[ii, jj] > 0:
            if (~numpy.isnan(image4[ii, jj])) and 0<image4[ii, jj]<40:
                t4.append(image4[ii, jj])
            else:
                continue

for ii in range(0, im_height1):
    for jj in range(0, im_width1):
        if veg[ii, jj] > 0:
            if (~numpy.isnan(image5[ii, jj])) and 0<image5[ii, jj]<40:
                t5.append(image5[ii, jj])
            else:
                continue

for ii in range(0, im_height1):
    for jj in range(0, im_width1):
        if veg[ii, jj] > 0:
            if (~numpy.isnan(image6[ii, jj])) and 0<image6[ii, jj]<40:
                t6.append(image6[ii, jj])
            else:
                continue
for ii in range(0, im_height1):
    for jj in range(0, im_width1):
        if veg[ii, jj] > 0:
            if (~numpy.isnan(image7[ii, jj])) and 0<image7[ii, jj]<40:
                t7.append(image7[ii, jj])
            else:
                continue

for ii in range(0, im_height1):
    for jj in range(0, im_width1):
        if veg[ii, jj] > 0:
            if (~numpy.isnan(image8[ii, jj])) and 0<image8[ii, jj]<40:
                t8.append(image8[ii, jj])
            else:
                continue
cmap = plt.get_cmap("Oranges")
f, ax = plt.subplots(figsize=(10, 5))
plt.subplots_adjust(left = 0.1, bottom=0.2, top = 0.8, right=0.8)

sns.distplot(t1, bins = [0,10,20,30,40], hist = False, kde = True, kde_kws = {'lw':1.5},norm_hist = False,rug = False, vertical = False,
             color = cmap(1/ 6), label = '82-88')
ax.axvline(x=numpy.nanmean(t1), color=cmap(1/ 6),linestyle='-', linewidth=2)

sns.distplot(t2, bins = [0,10,20,30,40], hist = False, kde = True, kde_kws = {'lw':1.5},norm_hist = False,rug = False, vertical = False,
             color = cmap(2/ 6), label = '88-94')
ax.axvline(x=numpy.nanmean(t2), color=cmap(2/ 6),linestyle='-', linewidth=2)

sns.distplot(t3, bins = [0,10,20,30,40], hist = False, kde = True, kde_kws = {'lw':1.5},norm_hist = False,rug = False, vertical = False,
             color = cmap(3/ 6), label = '94-00')
ax.axvline(x=numpy.nanmean(t3), color=cmap(3/ 6),linestyle='-', linewidth=2)

sns.distplot(t4, bins = [0,10,20,30,40], hist = False, kde = True, kde_kws = {'lw':1.5},norm_hist = False,rug = False, vertical = False,
             color = cmap(4/ 6), label = '00-06')
ax.axvline(x=numpy.nanmean(t4), color=cmap(4/ 6),linestyle='-', linewidth=2)

sns.distplot(t5, bins = [0,10,20,30,40], hist = False, kde = True, kde_kws = {'lw':1.5},norm_hist = False,rug = False, vertical = False,
             color = cmap(5/ 6), label = '06-12')
ax.axvline(x=numpy.nanmean(t5), color=cmap(5/ 6),linestyle='-', linewidth=2)

sns.distplot(t6, bins = [0,10,20,30,40], hist = False, kde = True, kde_kws = {'lw':1.5},norm_hist = False,rug = False, vertical = False,
             color = cmap(6/ 6), label = '12-18')
ax.axvline(x=numpy.nanmean(t6), color=cmap(6/ 6),linestyle='-', linewidth=2)

sns.distplot(t7, bins = [0,10,20,30,40], hist = False, kde = True, kde_kws = {'linestyle':'-.','lw':2.5},norm_hist = False,rug = False, vertical = False,
             color = 'deeppink', label = 'opt')
ax.axvline(x=numpy.nanmean(t7), color='deeppink',linestyle='-.', linewidth=2.5)

sns.distplot(t8, bins = [0,10,20,30,40], hist = False, kde = True, kde_kws = {'linestyle':'-.','lw':2.5},norm_hist = False,rug = False, vertical = False,
             color = 'darkturquoise', label = 'timenode')
ax.axvline(x=numpy.nanmean(t8), color='darkturquoise',linestyle='-.', linewidth=2.5)


ax.legend(frameon=False)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)
# a = plt.axhline(y=0,ls="-",color=cm.binary(0.8), linewidth=3)
# a.set_zorder(0)
# sns.distplot(l2, bins = 20, hist = False, kde = True, kde_kws = {'color':'g', 'lw':2, 'linestyle':'--'},
#              norm_hist = False,rug = False, vertical = False,color = 'g', label = 'l1')
#ax.set_xlim([-0.1,0.1])
print(numpy.nanmean(t1))
print(numpy.nanmean(t2))
print(numpy.nanmean(t3))
print(numpy.nanmean(t4))
print(numpy.nanmean(t5))
print(numpy.nanmean(t6))
print(numpy.nanmean(t7))
print(numpy.nanmean(t8))

plt.show()
#
