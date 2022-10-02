# LAIcode

This zipped code file contains the five key code files used in this study.

1. fit_lai_BP_TP.py 
This code was utilized to fit LAI time series pixel by pixel from 1982 to 2018 to extract break point/turning points (BP/TP) through the statsmodel module in python 3.6 (Fig.  S2-S6) (Chen et al., 2014, RSE). 
In time series of LAI, we fit trends of two stages before and after BP/TP and selected better BP/TP if both the significance levels of two trends are lower than 0.05. Then R2 was used to find best BP and TP, respectively. We also fit the trend in the whole time series using simple linear model. Finally, through AIC value we can determine the best model to describe LAI trend from BP, TP and linear models. 
Output: BP, TP, trends before and after points, AIC, significance level.

2. optima-temperature-extract.py
This code was utilized to calculate the optima air temperature in growing season using the relationship between air temperature and LAI in python 3.6. (Fig. S10)(Huang et al., 2019, Nature Ecology & Evolution) 
In each pixel, we split the temperature time series from 1982 to 2018 into different bins with the step of 0.5℃, then put the corresponding LAI into them and selected the LAI value at 85% percentage. Through maximum LAI we can determine the optimum temperature. If the maximum LAI occur at the start and end points, we assumed that this pixel did not have optimum temperature.
Output: optimum temperature at each pixel

3. extract growingseason.py
This code was utilized to extract growing season in each plant pixel in python 3.6. (Zhu et al., 2016, Nature Clim. Change) (Fig.  S10)
In the time series of LAI in one year, if the LAI is greater than 0.1 and increased by 15% of amplitude of LAI, the date was regarded as the start of growing season; Symmetrically, if the LAI is lower than 0.1 and decreased by 85% of amplitude, the date was regarded as the end of growing season. Noting that the growing season of broadleaf evergreen forests in equatorial regions was directly regarded as 365 days. 
Output: the start and the end of growing season, as well as the time span. 

4. pigture_trendvegtype.py
This code was utilized to depict trend slope of LAI before and after BP/TP for different PFT all over the world in python 3.6. (Fig.  S5-S6)  
Output: the picture about trend slope of LAI before and after BP/TP for different PFT.

5. slop_hist_frequency.py
This code was utilized to depict probability density distribution of T_opt^eco  ,〖 T〗_air^afterCPand 〖 T〗_air^(max,gs) in python 3.6 (Fig. S10 (b)).
Output: the picture about probability density distribution of T_opt^eco  ,〖 T〗_air^afterCPand 〖 T〗_air^(max,gs)

Reference
Chen, B. et al. Changes in vegetation photosynthetic activity trends across the Asia–Pacific region over the last three decades. Remote Sens. Environ. 144, 28–41 (2014).
Huang, M. et al. Air temperature optima of vegetation productivity across global biomes. Nat. Ecol. Evol. 3, 772–779 (2019).
Zhu, Z. et al. Greening of the Earth and its drivers. Nat. Clim. Change 6, 791–795 (2016).
