# /gpfs/home/yuk/anaconda3/envs/py36/bin/python3
# coding=utf-8

# filepath: r'/gpfs/home/yuk/LAI/out_inter/1-year-avhrr' LAI data
# global grid data : r'/gpfs/home/yuk/merged/globe1.tif'
import gdal
import numpy
import os
import statsmodels.api
import math
import copyreg
import types
import multiprocess
from multiprocess.pool import ThreadPool as TPool
from tqdm import tqdm

numpy.set_printoptions(suppress=True)

# input LAI
filepath = r'/1-year-avhrr'
ffile_list = os.listdir(filepath)
ffile_list.sort()
image = numpy.zeros((3600, 7200, 37), dtype='float32')
for ff in ffile_list:
    if str(ff).split('.')[-1] == 'tif':
        globe_data = gdal.Open(os.path.join(filepath, ff))
        im_width0 = globe_data.RasterXSize  # 栅格矩阵的列数
        im_height0 = globe_data.RasterYSize  # 栅格矩阵的行数
        image[:, :, ffile_list.index(ff)] = globe_data.ReadAsArray(0, 0, im_width0, im_height0)  # 获取esvf数据
    else:
        continue
outpath = r'/result'

globe = r'/merged/globe1.tif' # study area
globe_data = gdal.Open(globe)
im_width0 = int(globe_data.RasterXSize)  # column
im_height0 = int(globe_data.RasterYSize)  # row
im_geotrans0 = globe_data.GetGeoTransform()  # Get the affine matrix information
im_proj0 = globe_data.GetProjection()  # Get projection information

para = numpy.zeros((im_height0, im_width0, 6), dtype='float32')  #
para_BP1 = numpy.zeros((im_height0, im_width0, 10), dtype='float32')
para_TP = numpy.zeros((im_height0, im_width0, 8), dtype='float32')
result = numpy.zeros((im_height0, im_width0, 8), dtype='float32')

loca = []
T = []
L = []

for i in range(0, im_height0):
    for j in range(0, im_width0):
        a = image[i, j, :]
        L.append((a[~numpy.isnan(a)]).tolist())
        b = list(list(numpy.where(~numpy.isnan(a)))[0])
        # c = [cc + 1981 for cc in b]
        T.append(b)
        loca.append([i, j])

for ia in range(0, len(loca)):
    if len(L[ia]) < 10:
        result[int((loca[ia])[0]), int((loca[ia])[1]), 0] = numpy.nan
        result[int((loca[ia])[0]), int((loca[ia])[1]), 1] = numpy.nan
        result[int((loca[ia])[0]), int((loca[ia])[1]), 2] = numpy.nan
        result[int((loca[ia])[0]), int((loca[ia])[1]), 3] = numpy.nan
        result[int((loca[ia])[0]), int((loca[ia])[1]), 4] = numpy.nan
        result[int((loca[ia])[0]), int((loca[ia])[1]), 5] = numpy.nan
        result[int((loca[ia])[0]), int((loca[ia])[1]), 6] = numpy.nan
        result[int((loca[ia])[0]), int((loca[ia])[1]), 7] = numpy.nan
    else:
        # ----------------------------------------Linear fitting of the pixels-----------------------------------------------------------
        mm = numpy.mean(L[ia])
        std = numpy.std(L[ia])
        s1 = mm - 2 * std
        s2 = mm + 2 * std
        # vv1 = [i1-s1 for i1 in lai]
        # vv2 = [s2-i2 for i2 in lai]
        for iic in range(0, len(L[ia])):
            if (L[ia])[iic] > s2 or (L[ia])[iic] < s1:
                if 2 <= iic <= len(L[ia]) - 3:
                    aa = [(L[ia])[jjc] for jjc in range(iic - 2, iic + 3) if s1 <= (L[ia])[jjc] <= s2]
                    (L[ia])[iic] = numpy.mean(aa)
                elif iic == 0:
                    bb = [(L[ia])[jjc] for jjc in range(0, 3) if s1 <= (L[ia])[jjc] <= s2]
                    (L[ia])[iic] = numpy.mean(bb)
                elif iic == 1:
                    cc = [(L[ia])[jjc] for jjc in range(0, 4) if s1 <= (L[ia])[jjc] <= s2]
                    (L[ia])[iic] = numpy.mean(cc)
                elif iic == len(L[ia]) - 2:
                    dd = [(L[ia])[jjc] for jjc in range(len(L[ia]) - 4, len(L[ia])) if s1 <= (L[ia])[jjc] <= s2]
                    (L[ia])[iic] = numpy.mean(dd)
                elif iic == len(L[ia]) - 1:
                    ee = [(L[ia])[jjc] for jjc in range(len(L[ia]) - 3, len(L[ia])) if s1 <= (L[ia])[jjc] <= s2]
                    (L[ia])[iic] = numpy.mean(ee)
                else:
                    continue
            else:
                continue

        time1 = statsmodels.api.add_constant(T[ia])
        est = statsmodels.api.OLS(L[ia], time1)
        est = est.fit()
        # fitting the whole time series with linear model =======================================
        para[int((loca[ia])[0]), int((loca[ia])[1]), 0] = est.params[1]  # slope
        para[int((loca[ia])[0]), int((loca[ia])[1]), 1] = est.params[1]  # slope
        # para[i,j,2] = std_err   # standard deviation
        para[int((loca[ia])[0]), int((loca[ia])[1]), 2] = 0  # turning point
        para[int((loca[ia])[0]), int((loca[ia])[1]), 3] = est.f_pvalue  # p
        para[int((loca[ia])[0]), int((loca[ia])[1]), 4] = est.f_pvalue  # p
        para[int((loca[ia])[0]), int((loca[ia])[1]), 5] = est.aic  # AIC


        # ----------------------------------------------monitoring break points-------------------------------------------------------------
        beta = numpy.zeros((len(T[ia]) - 9, 10), dtype='float32')
        stdd1 = []
        stdd2 = []
        # moniter break points from the 5th data point
        for p in range(5, len(T[ia]) - 4):
            time_seg1 = numpy.array((T[ia])[0:p + 1]).transpose()
            lai_seg1 = numpy.array((L[ia])[0:p + 1]).transpose()
            time_seg2 = numpy.array((T[ia])[p:]).transpose()
            lai_seg2 = numpy.array((L[ia])[p:]).transpose()

            # before point
            time_seg1 = statsmodels.api.add_constant(time_seg1)
            est1 = statsmodels.api.OLS(lai_seg1, time_seg1)
            est1 = est1.fit()
            stdd1.append(est1.params[1]) # fitting-slope
            # after point
            time_seg2 = statsmodels.api.add_constant(time_seg2)
            est2 = statsmodels.api.OLS(lai_seg2, time_seg2)
            est2 = est2.fit()
            stdd2.append(est2.params[1]) # fitting-slope

            # evaluate significance level
            if float(as_num(est1.pvalues[1])) <= 0.05 and float(as_num(est2.pvalues[1])) <= 0.05:
                beta[p - 5, 0] = est1.params[1]  # slope before point
                beta[p - 5, 1] = est1.rsquared  # R2 before point
                beta[p - 5, 2] = est1.pvalues[1]  # p before point
                # beta[p, 3] = std_err1
                beta[p - 5, 3] = est2.params[1]  # slope after point
                beta[p - 5, 4] = est2.rsquared  # R2 after point
                beta[p - 5, 5] = est2.pvalues[1]  # p after point
                # beta[p, 7] = std_err2
                beta[p - 5, 6] = (T[ia])[p] + 1982  # time of break point
                beta[p - 5, 7] = sum([ie ** 2 for ie in est1.resid]) + sum([je ** 2 for je in est2.resid])
                beta[p - 5, 8] = len(T[ia]) * (math.log(beta[p - 5, 7] / len(T[ia]))) + 2 * 4 + (
                            (2 * 4 * (4 + 1)) / (len(T[ia]) - 4 - 1))  # AIC
                yymean = numpy.nanmean(L[ia])
                beta[p - 5, 9] = 1 - (beta[p - 5, 7] / (sum([(laij - yymean) ** 2 for laij in L[ia]])))  # R2
            else:
                continue

        beta = beta[beta[:, 9] != 0]  # delete 0 rows
        if beta.shape[0] > 0:
            beta_de = beta[numpy.argsort(beta[:, 9])]
            beta_de = beta_de[-5:, :]  # higher R2
            lloo = list((numpy.where(beta_de == numpy.max(beta_de[:, 9])))[0])

            # para_BP1[i, j, 1] = intercept1
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 0] = beta_de[zz, 0]  # slope before point
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 1] = beta_de[zz, 1]  # R2 before point
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 2] = beta_de[zz, 2]  # p before point
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 3] = beta_de[zz, 6]  # time of turning point
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 4] = beta_de[zz, 3]  # slope after point
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 5] = beta_de[zz, 4]  # R2 after point
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 6] = beta_de[zz, 5]  # p after point
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 7] = beta_de[zz, 8]  # AIC
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 8] = numpy.std(stdd1)
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 9] = numpy.std(stdd2)
        else:
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 0] = numpy.nan
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 1] = numpy.nan
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 2] = numpy.nan
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 3] = numpy.nan
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 4] = numpy.nan
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 5] = numpy.nan
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 6] = numpy.nan
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 7] = numpy.nan
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 8] = numpy.nan
            para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 9] = numpy.nan

        # ----------------------------------------------monitoring turning points-----------------------------------------------------------
        beta2 = numpy.zeros((len(T[ia]) - 9, 9), dtype='float32')
        sttd1_tp = []
        sttd2_tp = []
        for p in range(5, len(T[ia]) - 4):
            time_seg11 = numpy.array((T[ia])[0:p + 1]).transpose()
            lai_seg11 = numpy.array((L[ia])[0:p + 1]).transpose()
            time_seg22 = numpy.array((T[ia])[p:]).transpose()
            lai_seg22 = numpy.array((L[ia])[p:]).transpose()

            time_seg111 = statsmodels.api.add_constant(time_seg11)
            est3 = statsmodels.api.OLS(lai_seg11, time_seg111)
            est3 = est3.fit()
            sttd1_tp.append(est3.params[1])

            y2 = func(time_seg22, est3.params[0], est3.params[1])
            y_dif = (numpy.array(lai_seg22) - numpy.array(y2)).transpose()
            x2 = numpy.array(list(x - p for x in (T[ia])[p:])).transpose()
            est4 = statsmodels.api.OLS(y_dif, x2)
            est4 = est4.fit()
            y22 = func(time_seg22, est3.params[0], est3.params[1]) + est4.params[0] * (time_seg22 - p)
            rreess = (sum([je ** 2 for je in (numpy.array(lai_seg22) - numpy.array(y22))]))
            y2mean = numpy.mean(lai_seg22)
            r2 = (1 - (rreess / (sum([(laij - y2mean) ** 2 for laij in (L[ia])[p:]]))))

            sttd2_tp.append(est3.params[1] + est4.params[0])

            if float(as_num(est3.pvalues[1])) <= 0.05 and float(as_num(est4.pvalues[0])) <= 0.05:
                beta2[p - 5, 0] = est3.params[1]  # slope1
                beta2[p - 5, 1] = r2  # R2 after turning point
                beta2[p - 5, 2] = est3.params[1] + est4.params[0]  # slope2
                beta2[p - 5, 3] = (T[ia])[p] + 1982  # the time of turning point
                beta2[p - 5, 4] = sum([je ** 2 for je in (numpy.array(lai_seg11) - numpy.array(est3.fittedvalues))]) + sum([je ** 2 for je in (numpy.array(lai_seg22) - numpy.array(y22))])  # Residuals
                beta2[p - 5, 5] = len(T[ia]) * (math.log(beta2[p - 5, 4] / len(T[ia]))) + 2 * 5 + ((2 * 5 * (5 + 1)) / (len(T[ia]) - 5 - 1))  # AIC
                yymean = numpy.nanmean(L[ia])
                beta2[p - 5, 6] = 1 - (beta2[p - 5, 4] / (sum([(laij - yymean) ** 2 for laij in L[ia]])))
                beta2[p - 5, 7] = est3.pvalues[1]  # significance of slopes
                beta2[p - 5, 8] = est4.pvalues[0]  # significance of slope difference
            else:
                continue
            del y2
            del y_dif
            del x2
            del y22
            del rreess
            del r2
            del y2mean
        beta2 = beta2[beta2[:, 6] != 0]  # delete 0 rows
        if beta2.shape[0] > 0:
            beta2_de = beta2[numpy.argsort(beta2[:, 1])]  # higher R2
            beta2_de = beta2_de[-5:, :]
            # z = int((numpy.where(beta2_de == numpy.min(beta2_de[:, 4])))[0])
            lloo2 = list((numpy.where(beta2_de == numpy.max(beta2_de[:, 6])))[0])

            para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 0] = beta2_de[z, 0]  # slope before turning point
            para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 1] = beta2_de[z, 2]  # slope after turning point
            para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 2] = beta2_de[z, 3]  # turning point
            para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 3] = beta2_de[z, 5]  # AIC
            para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 4] = beta2_de[z, 7]  # # significance of slopes
            para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 5] = beta2_de[z, 8]  # significance of slope difference
            para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 6] = numpy.std(sttd1_tp)
            para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 7] = numpy.std(sttd2_tp)
        else:
            para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 0] = numpy.nan
            para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 1] = numpy.nan
            para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 2] = numpy.nan
            para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 3] = numpy.nan
            para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 4] = numpy.nan
            para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 5] = numpy.nan
            para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 6] = numpy.nan
            para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 7] = numpy.nan


        # ----------------------------------------------compare AIC--------------------------------------------------

        if numpy.isnan(para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 7]) and numpy.isnan(
                para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 3]):
            result[int((loca[ia])[0]), int((loca[ia])[1]), 0] = 0
            result[int((loca[ia])[0]), int((loca[ia])[1]), 1] = para[int((loca[ia])[0]), int((loca[ia])[1]), 0]
            result[int((loca[ia])[0]), int((loca[ia])[1]), 2] = para[int((loca[ia])[0]), int((loca[ia])[1]), 1]
            result[int((loca[ia])[0]), int((loca[ia])[1]), 3] = para[int((loca[ia])[0]), int((loca[ia])[1]), 2]
            result[int((loca[ia])[0]), int((loca[ia])[1]), 4] = para[int((loca[ia])[0]), int((loca[ia])[1]), 3]
            result[int((loca[ia])[0]), int((loca[ia])[1]), 5] = para[int((loca[ia])[0]), int((loca[ia])[1]), 4]
            result[int((loca[ia])[0]), int((loca[ia])[1]), 6] = 0
            result[int((loca[ia])[0]), int((loca[ia])[1]), 7] = 0
        else:
            AIC1 = para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 7] - para[
                int((loca[ia])[0]), int((loca[ia])[1]), 5]  #
            AIC2 = para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 3] - para[
                int((loca[ia])[0]), int((loca[ia])[1]), 5]  #
            if str(AIC1) == 'nan' and str(AIC2) != 'nan':
                if para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 3] < para[
                    int((loca[ia])[0]), int((loca[ia])[1]), 5] and \
                        para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 3] != 0:
                    if abs(AIC2) > 2:
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 0] = 2
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 1] = para_TP[
                            int((loca[ia])[0]), int((loca[ia])[1]), 0]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 2] = para_TP[
                            int((loca[ia])[0]), int((loca[ia])[1]), 1]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 3] = para_TP[
                            int((loca[ia])[0]), int((loca[ia])[1]), 2]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 4] = para_TP[
                            int((loca[ia])[0]), int((loca[ia])[1]), 4]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 5] = para_TP[
                            int((loca[ia])[0]), int((loca[ia])[1]), 5]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 6] = para_TP[
                            int((loca[ia])[0]), int((loca[ia])[1]), 6]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 7] = para_TP[
                            int((loca[ia])[0]), int((loca[ia])[1]), 7]
                    else:
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 0] = 0
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 1] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 0]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 2] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 1]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 3] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 2]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 4] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 3]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 5] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 4]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 6] = 0
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 7] = 0
                else:
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 0] = 0
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 1] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 0]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 2] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 1]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 3] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 2]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 4] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 3]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 5] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 4]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 6] = 0
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 7] = 0
            elif str(AIC1) != 'nan' and str(AIC2) == 'nan':
                if para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 7] < para[
                    int((loca[ia])[0]), int((loca[ia])[1]), 5] and \
                        para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 7] != 0:
                    if abs(AIC1) > 2:
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 0] = 1
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 1] = para_BP1[
                            int((loca[ia])[0]), int((loca[ia])[1]), 0]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 2] = para_BP1[
                            int((loca[ia])[0]), int((loca[ia])[1]), 4]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 3] = para_BP1[
                            int((loca[ia])[0]), int((loca[ia])[1]), 3]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 4] = para_BP1[
                            int((loca[ia])[0]), int((loca[ia])[1]), 2]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 5] = para_BP1[
                            int((loca[ia])[0]), int((loca[ia])[1]), 6]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 6] = para_BP1[
                            int((loca[ia])[0]), int((loca[ia])[1]), 8]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 7] = para_BP1[
                            int((loca[ia])[0]), int((loca[ia])[1]), 9]
                    else:
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 0] = 0
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 1] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 0]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 2] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 1]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 3] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 2]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 4] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 3]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 5] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 4]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 6] = 0
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 7] = 0
                else:
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 0] = 0
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 1] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 0]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 2] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 1]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 3] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 2]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 4] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 3]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 5] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 4]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 6] = 0
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 7] = 0
            #
            else:
                if para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 7] < para_TP[
                    int((loca[ia])[0]), int((loca[ia])[1]), 3] != 0 and \
                        para_BP1[int((loca[ia])[0]), int((loca[ia])[1]), 7] < para[
                    int((loca[ia])[0]), int((loca[ia])[1]), 5] and \
                        para_BP1[
                            int((loca[ia])[0]), int((loca[ia])[1]), 7] != 0:
                    if abs(AIC1) > 2:
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 0] = 1
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 1] = para_BP1[
                            int((loca[ia])[0]), int((loca[ia])[1]), 0]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 2] = para_BP1[
                            int((loca[ia])[0]), int((loca[ia])[1]), 4]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 3] = para_BP1[
                            int((loca[ia])[0]), int((loca[ia])[1]), 3]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 4] = para_BP1[
                            int((loca[ia])[0]), int((loca[ia])[1]), 2]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 5] = para_BP1[
                            int((loca[ia])[0]), int((loca[ia])[1]), 6]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 6] = para_BP1[
                            int((loca[ia])[0]), int((loca[ia])[1]), 8]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 7] = para_BP1[
                            int((loca[ia])[0]), int((loca[ia])[1]), 9]
                    else:
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 0] = 0
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 1] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 0]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 2] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 1]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 3] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 2]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 4] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 3]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 5] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 4]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 6] = 0
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 7] = 0
                elif para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 3] < para_BP1[
                    int((loca[ia])[0]), int((loca[ia])[1]), 7] != 0 and para_TP[
                    int((loca[ia])[0]), int((loca[ia])[1]), 3] < \
                        para[int((loca[ia])[0]), int((loca[ia])[1]), 5] and para_TP[
                    int((loca[ia])[0]), int((loca[ia])[1]), 3] != 0:
                    if abs(AIC2) > 2:
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 0] = 2
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 1] = para_TP[
                            int((loca[ia])[0]), int((loca[ia])[1]), 0]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 2] = para_TP[
                            int((loca[ia])[0]), int((loca[ia])[1]), 1]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 3] = para_TP[
                            int((loca[ia])[0]), int((loca[ia])[1]), 2]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 4] = para_TP[
                            int((loca[ia])[0]), int((loca[ia])[1]), 4]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 5] = para_TP[
                            int((loca[ia])[0]), int((loca[ia])[1]), 5]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 6] = para_TP[
                            int((loca[ia])[0]), int((loca[ia])[1]), 6]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 7] = para_TP[
                            int((loca[ia])[0]), int((loca[ia])[1]), 7]
                    else:
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 0] = 0
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 1] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 0]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 2] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 1]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 3] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 2]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 4] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 3]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 5] = para[
                            int((loca[ia])[0]), int((loca[ia])[1]), 4]
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 6] = 0
                        result[int((loca[ia])[0]), int((loca[ia])[1]), 7] = 0
                elif para[int((loca[ia])[0]), int((loca[ia])[1]), 5] < para_BP1[
                    int((loca[ia])[0]), int((loca[ia])[1]), 7] and para[int((loca[ia])[0]), int((loca[ia])[1]), 5] < \
                        para_TP[int((loca[ia])[0]), int((loca[ia])[1]), 3]:
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 0] = 0
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 1] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 0]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 2] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 1]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 3] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 2]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 4] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 3]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 5] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 4]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 6] = 0
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 7] = 0
                else:
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 0] = 0
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 1] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 0]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 2] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 1]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 3] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 2]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 4] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 3]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 5] = para[
                        int((loca[ia])[0]), int((loca[ia])[1]), 4]
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 6] = 0
                    result[int((loca[ia])[0]), int((loca[ia])[1]), 7] = 0

 # 输出文件

driver = gdal.GetDriverByName('Gtiff')
outRaster = driver.Create(outpath + '/' + 'yearfiting_avhrr_0.05' + '.tif', im_width0, im_height0, 8,
                          gdal.GDT_Float32)
outRaster.SetGeoTransform(im_geotrans0)  # 参数2,6为水平垂直分辨率，参数3,5表示图片是指北的
outband1 = outRaster.GetRasterBand(1)
outband1.WriteArray(result[:, :, 0], 0, 0)
outband2 = outRaster.GetRasterBand(2)
outband2.WriteArray(result[:, :, 1], 0, 0)
outband3 = outRaster.GetRasterBand(3)
outband3.WriteArray(result[:, :, 2], 0, 0)
outband4 = outRaster.GetRasterBand(4)
outband4.WriteArray(result[:, :, 3], 0, 0)
outband5 = outRaster.GetRasterBand(5)
outband5.WriteArray(result[:, :, 4], 0, 0)
outband6 = outRaster.GetRasterBand(6)
outband6.WriteArray(result[:, :, 5], 0, 0)
outband5 = outRaster.GetRasterBand(7)
outband5.WriteArray(result[:, :, 6], 0, 0)
outband6 = outRaster.GetRasterBand(8)
outband6.WriteArray(result[:, :, 7], 0, 0)
outRaster.SetProjection(im_proj0)  #
outRaster.FlushCache()

