# /gpfs/home/yuk/anaconda3/envs/py36/bin/python3
# -*- coding: utf-8 -*-

# lai filepath r'/gpfs/home/yuk/LAI/out_inter/GLASS/month/1836resample'
# temp filepath r'/gpfs/home/yuk/dailymaxtemp/argomentmax/8day'
# outpath  r'/gpfs/home/yuk/LAI/out_inter/glass_gs/2000/optima/patch'
# study area filepath r'/gpfs/home/yuk/LAI/out_inter' + '/' + 'veg_GLASS_1800.tif'
import gdal
import numpy
import os
from osgeo import gdal, gdalconst
from osgeo import ogr, osr
import math
import datetime
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt
import copyreg
import types
import multiprocess
from multiprocess.pool import ThreadPool as TPool
from tqdm import tqdm

filepath5 = r'/1836resample' # LAI
ffile_list5 = os.listdir(filepath5)
ffile_list5.sort()

filepath6 = r'/8day' # TEMP
ffile_list6 = os.listdir(filepath6)
ffile_list6.sort()


outpath = r'/patch'

file_ex = r'/out_inter' + '/' + 'veg_GLASS_1800.tif' # study area
ex_data = gdal.Open(file_ex)
im_width1 = int(ex_data.RasterXSize)
im_height1 = int(ex_data.RasterYSize)
# im_temp = ex_data.ReadAsArray(0, 0, im_width1, im_height1)
im_geotrans1 = ex_data.GetGeoTransform()
im_proj1 = ex_data.GetProjection()

optima = numpy.full((im_height1, im_width1), numpy.nan, dtype='float16')
for i in range(0, im_height1):
    for j in range(0, im_width1):
        if ~numpy.isnan(im_temp[i, j]) and im_temp[i, j] > 0:
            select_lai = []
            select_temp = []
            name = list(range(2012, 2019))
            for date in name:
                yyy = 365
                if (int(date) % 4) == 0:
                    if (int(date) % 100) == 0:
                        if (int(date) % 400) == 0:
                            yyy = 366
                        else:
                            yyy = 365
                    else:
                        yyy = 366  #
                else:
                    yyy = 365
                ff5 = []
                day5 = []
                for f5 in ffile_list5:
                    if str(f5)[2:6] == str(date) and str(f5)[-1] == 'f':
                        maxtemp_data5 = gdal.Open(os.path.join(filepath5, f5))
                        l = float((maxtemp_data5.ReadAsArray(j, i, 1, 1))[0])
                        if ~numpy.isnan(l):
                            ff5.append(l)
                            day5.append(str(f5)[6:9])
                # maxtemp_data5_add = gdal.Open(os.path.join(filepath5, 're' + str(int(date)+1))+'001_lai_GLASS.tif')
                # ff5.append(maxtemp_data5_add.ReadAsArray(j, i, 1, 1))
                # day5.append(str(int(yyy+1)))
                ff6 = []
                day6 = []
                for f6 in ffile_list6:
                    if str(f6)[0:4] == str(date) and str(f6)[-1] == 'f':
                        # print(f1)
                        maxtemp_data6 = gdal.Open(os.path.join(filepath6, f6))
                        t = float((maxtemp_data6.ReadAsArray(j, i, 1, 1))[0])
                        if ~numpy.isnan(t):
                            ff6.append(t - 273.15)
                            day6.append((str(f6).split('-')[1])[0:3])
                if len(day5) >= 3 and len(day6) >= 3:
                    day5 = list(map(int, day5))
                    day6 = list(map(int, day6))
                    f_lai = interp1d(day5, ff5, kind='linear', fill_value='extrapolate')
                    f_temp = interp1d(day6, ff6, kind='linear', fill_value='extrapolate')
                    xx = numpy.linspace(1, 365, 46)
                    yy_lai = f_lai(xx)
                    yy_temp = f_temp(xx)
                    smoother_lai = list(savgol_filter(yy_lai, window_length=21, polyorder=4))
                    smoother_temp = list(savgol_filter(yy_temp, window_length=21, polyorder=4))
                    select_lai = select_lai + smoother_lai
                    select_temp = select_temp + smoother_temp
                else:
                    continue
            if len(select_lai) >= 2 and len(select_temp) >= 2:
                select_temp_1 = []
                select_lai_1 = []
                for de_i in range(0,len(select_temp)):
                    if select_temp[de_i] >0 and select_lai[de_i] >= 0.1:
                        select_temp_1.append(select_temp[de_i])
                        select_lai_1.append(select_lai[de_i])
                if len(select_lai_1)>2:
                    mmax = float(numpy.nanmax(select_temp_1))
                    mmin = float(numpy.nanmin(select_temp_1))
                    aa = list(numpy.arange(mmin, mmax, 0.5))
                    temp_new = []
                    lai_new = []
                    for a in aa:
                        lai_zhong = []
                        temp_zhong = []
                        for tt in select_temp_1:
                            if a <= tt < a + 0.5:
                                lai_zhong.append(select_lai_1[select_temp_1.index(tt)])
                                temp_zhong.append(tt)
                        if len(lai_zhong) > 3:
                            lai_zhong1 = lai_zhong
                            lai_zhong.sort()
                            lai_new.append(lai_zhong[int(round((len(lai_zhong) - 1) * 0.85))])
                            temp_new.append(temp_zhong[lai_zhong1.index(lai_zhong[int(round((len(lai_zhong) - 1) * 0.85))])])
                            # aaa.write(bb, 1, temp_zhong[math.floor((len(temp_zhong) - 1) * 0.95)])
                    if len(lai_new)>2:
                        lai_new[0] = numpy.nanmean(lai_new[0:1])
                        lai_new[-1] = numpy.nanmean(lai_new[-2:])
                        for ln in range(1,len(lai_new)-1):
                            lai_new[ln] = numpy.nanmean(lai_new[ln-1:ln+2])
                        f_lai_inter = interp1d(temp_new, lai_new, kind='linear', fill_value='extrapolate')
                        temp_yy_min = float(numpy.min(temp_new))
                        temp_yy_max = float(numpy.max(temp_new))
                        xx2_temp = numpy.linspace(temp_yy_min, temp_yy_max, int((temp_yy_max - temp_yy_min + 1) * 40))
                        yy2_lai = f_lai_inter(xx2_temp)
                        smoother_lai_result = list(savgol_filter(yy2_lai, window_length=21, polyorder=4))
                        # print(len(smoother_lai_result))
                        # print(len(xx2_temp))
                        result_max = numpy.nanmax(smoother_lai_result)
                        if 0 < list(smoother_lai_result).index(result_max) < len(smoother_lai_result) - 1:
                            optima[i, j] = xx2_temp[list(smoother_lai_result).index(result_max)]
                            # ccc.write(0, lie, xx2_temp[list(smoother_lai_result).index(result_max)])
                            # lie = lie + 2
                        else:
                            continue
                    else:
                        continue
                else:
                    continue

            else:
                continue
    print(i)
driver = gdal.GetDriverByName('Gtiff')
outRaster = driver.Create(outpath + '/' + '2012-2019-optima.tif', im_width1, im_height1, 1, gdal.GDT_Float32)
outRaster.SetGeoTransform(im_geotrans1)
outband = outRaster.GetRasterBand(1)
outband.WriteArray(optima, 0, 0)
outRaster.SetProjection(im_proj1)
outRaster.FlushCache()

