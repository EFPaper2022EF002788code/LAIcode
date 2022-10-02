# -*- coding: utf-8 -*-

import os
import pandas

import openpyxl
# import gdal
import numpy
import xlrd
import xlwt
import re
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.pyplot import MultipleLocator
from pylab import MaxNLocator
import matplotlib.font_manager as fm

matplotlib.rcParams['font.serif'] = ['Times New Roman']
sns.set_style('whitegrid')

file = r'F:\lai_year_fit\20210510\glass\veg\bp\combinebp.xls'
excel = xlrd.open_workbook(file)

tableBP = excel.sheet_by_index(0)
# tableBP2 = excel.sheet_by_index(4)
# tableBP3 = excel.sheet_by_index(10)

name1 = tableBP.col_values(0) # ENF
name2 = tableBP.col_values(3) # EBF
name3 = tableBP.col_values(6) # DNF
name4 = tableBP.col_values(9) # DBF
name5 = tableBP.col_values(12) # MF
name6 = tableBP.col_values(15) # CROP
name7 = tableBP.col_values(18) # GRASS
name8 = tableBP.col_values(21) # GRASS_QZGY
name9 = tableBP.col_values(24) # SHRUB
name10 = tableBP.col_values(27) # TUNDRA

# print(len(name1),len(name11),len(name111),len(name1111),len(name11111))
# name2 = tableBP2.col_values(0)
# name3 = tableBP3.col_values(0)
t11 = tableBP.col_values(1)
t21 = tableBP.col_values(4)
t31 = tableBP.col_values(7)
t41 = tableBP.col_values(10)
t51 = tableBP.col_values(13)
t61 = tableBP.col_values(16)
t71 = tableBP.col_values(19)
t81 = tableBP.col_values(22)
t91 = tableBP.col_values(25)
t101 = tableBP.col_values(28)
# t51 = tableBP.col_values(13)
# print(len(t1),len(t11),len(t111),len(t1111),len(t11111))
# t2 = tableBP2.col_values(1)
# t3 = tableBP3.col_values(1)
p12 = tableBP.col_values(2)
p22 = tableBP.col_values(5)
p32 = tableBP.col_values(8)
p42 = tableBP.col_values(11)
p52 = tableBP.col_values(14)
p62 = tableBP.col_values(17)
#p622 = tableBP.col_values(19)
p72 = tableBP.col_values(20)
# p722 = tableBP.col_values(23)
p82 = tableBP.col_values(23)
p92 = tableBP.col_values(26)
p102 = tableBP.col_values(29)
# p52 = tableBP.col_values(14)
# p2 = tableBP2.col_values(2)
# p3 = tableBP3.col_values(2)
# print(len(p1),len(p11),len(p111),len(p1111),len(p11111))
name1 = [i for i in name1 if i != '']
t11 = [j for j in t11 if j != '']
p12 = [k for k in p12 if k != '']
# print(len(name1), len(t11), len(p12))
name2 = [ii for ii in name2 if ii != '']
t21 = [jj for jj in t21 if jj != '']
p22 = [kk for kk in p22 if kk != '']
# print(len(name2), len(t21), len(p22))
name3 = [iii for iii in name3 if iii != '']
t31 = [jjj for jjj in t31 if jjj != '']
p32 = [kkk for kkk in p32 if kkk != '']
# print(len(name3), len(t31), len(p32))
name4 = [iiii for iiii in name4 if iiii != '']
t41 = [jjjj for jjjj in t41 if jjjj != '']
p42 = [kkkk for kkkk in p42 if kkkk != '']
# print(len(name4), len(t41), len(p42))
name5 = [iiiii for iiiii in name5 if iiiii != '']
t51 = [jjjjj for jjjjj in t51 if jjjjj != '']
p52 = [kkkkk for kkkkk in p52 if kkkkk != '']
# print(len(name5), len(t51), len(p52))
name6 = [iiiii for iiiii in name6 if iiiii != '']
t61 = [jjjjj for jjjjj in t61 if jjjjj != '']
p62 = [kkkkk for kkkkk in p62 if kkkkk != '']
# print(len(name6), len(t61), len(p62))
name7 = [iiiii for iiiii in name7 if iiiii != '']
t71 = [jjjjj for jjjjj in t71 if jjjjj != '']
p72 = [kkkkk for kkkkk in p72 if kkkkk != '']
# t711 = [jjjjj for jjjjj in t711 if jjjjj != '']
# p722 = [kkkkk for kkkkk in p722 if kkkkk != '']
# print(len(name7), len(t71), len(p72))
name8 = [iiiii for iiiii in name8 if iiiii != '']
t81 = [jjjjj for jjjjj in t81 if jjjjj != '']
p82 = [kkkkk for kkkkk in p82 if kkkkk != '']
# print(len(name8), len(t81), len(p82))
name9 = [iiiii for iiiii in name9 if iiiii != '']
t91 = [jjjjj for jjjjj in t91 if jjjjj != '']
p92 = [kkkkk for kkkkk in p92 if kkkkk != '']
# print(len(name9), len(t91), len(p92))
name10 = [iiiii for iiiii in name10 if iiiii != '']
t101 = [jjjjj for jjjjj in t101 if jjjjj != '']
p102 = [kkkkk for kkkkk in p102 if kkkkk != '']

name = name1 + name2 + name3 + name4 + name5 + name6 + name7 + name8 + name9 + name10
t = t11 + t21 + t31 + t41 + t51 + t61 + t71 + t81 + t91 + t101
p = p12 + p22 + p32 + p42 + p52 + p62 + p72 + p82 + p92 + p102
# print(len(name), len(t), len(p))
test = pandas.DataFrame({'name': name, 'trend': t, 'class': p})
# foo = pandas.DataFrame(columns =['name','trend','type'])
foo = test.explode('trend')
foo['trend'] = foo['trend'].astype('float')
x = ['ENF', 'EBF', 'DNF', 'DBF', 'MF', 'Crop','Grass', 'Grass_TB', 'Shrub', 'Tundra']


#time = [2001.8, 2001.5, 2003.2, 2001.8, 2002.1, 2003.1, 2002.9, 2003.6, 2002.7,2003.6]   # avhrrbp
#time = [1999.4, 1999.2, 2001.1, 2000.1, 1999.7, 2001.6, 1998.6, 2001, 2000,1999.9]  # avhrrtp

#time = [2001.5, 2000.5, 2001.2, 2001.9, 2002.4, 2002.7, 2002.5, 2002.4, 2002.5,2001.6]   # glassbp
#time = [1998, 2003.3, 1996.6, 1999.6, 1998.4, 2000.4, 1998.0, 1999, 2000.7,1997.2]  # glasstp

#time = [1999.4, 1999.1, 2000.1, 1999.0, 1999.7, 1999.5, 1999.2, 1999.2, 2000.4,2000.1]  # lai3gbp
#time = [1996.2, 1996.9, 1996.9, 1996.5, 1996.6, 1996.8, 1995.8, 1995.6, 1997.2,1998.3]  # lai3gtp


f, ax = plt.subplots(figsize=(13, 6))
#palette="Set3",
#cc = {'limegreen','orange'}
sns.boxplot(x='name', y='trend', hue='class', data=foo,
            showmeans=True, palette={'orange','limegreen'},width=0.7,
            # boxprops = {'color':'black','facecolor':'lightseagreen'},
            meanprops={'marker': 'D', 'markerfacecolor': 'red', 'markersize': 5},
            medianprops={'linestyle': '--', 'color': 'royalblue'},
            showfliers=False
            )
# 更改x轴和y轴标签
ax.set_ylim([-0.24, 0.22])
a = plt.axhline(y=0, ls="-.", color=cm.binary(0.8), linewidth=2)
a.set_zorder(0)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
# plt.grid(color='black',linestyle='-.',linewidth = 1)

plt.grid(False)
ax.spines['top'].set_color('black')  #
ax.spines['right'].set_color('black')  #
ax.spines['bottom'].set_color('black')  #
ax.spines['left'].set_color('black')  #
ax.spines['bottom'].set_linewidth(1)
ax.spines['left'].set_linewidth(1)
ax.spines['top'].set_linewidth(1)
ax.spines['right'].set_linewidth(1)

x_major_locator=MultipleLocator(1.5)

ax.xaxis.set_major_locator(x_major_locator)

color3 = cm.BuGn(0.9)
# ax2 = ax.twinx()
# ax2.plot(x, time, 'ro-', linewidth=2, markersize=8, label='Time')
# ax2.set_ylim([1994, 2008])

# r11 = list(map(lambda x: x[0]-x[1], zip(time, time1)))
# r12 = list(map(lambda x: x[0]+x[1], zip(time, time1)))
# # r21 = list(map(lambda x: x[0]-x[1], zip(y2, std2)))
# # r22 = list(map(lambda x: x[0]+x[1], zip(y2, std2)))
#
# ax2.fill_between(x, r11, r12, color='red', alpha=0.4, linewidth = 0)
# ax.fill_between(x, r21, r22, color=color2, alpha=0.3, linewidth = 0)

# ax2.spines['top'].set_color('black')
# ax2.spines['right'].set_color('black')
# ax2.spines['bottom'].set_color('black')
# ax2.spines['left'].set_color('black')  #
# ax2.spines['bottom'].set_linewidth(0)
# ax2.spines['left'].set_linewidth(0)
# ax2.spines['top'].set_linewidth(0)
# ax2.spines['right'].set_linewidth(0)

ax.legend(bbox_to_anchor=(0.5, -0.02), frameon=False, loc=4, fontsize=13)
# ax2.legend(bbox_to_anchor=(1.010, -0.02), frameon=False, loc=4, fontsize=13)

ax.set_xlabel('', fontsize=0)
ax.set_ylabel('Trend (LAI/y)', fontsize=13)
# ax2.set_ylabel('Year', fontsize=13)

plt.yticks(fontsize=13)
plt.grid(False)
plt.rc('font',family='Times New Roman',size=13)

plt.show()
