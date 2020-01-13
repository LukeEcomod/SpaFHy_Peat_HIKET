# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 10:09:27 2020

@author: L1656
"""

import numpy as np
import pandas as pd
from os import listdir
import matplotlib.pyplot as plt
prop_cycle = plt.rcParams['axes.prop_cycle']
pal = prop_cycle.by_key()['color']
pal=pal+pal

def gather_data(dir_path='O:/Projects/SOMPAsites/WTD_data/', substring='loggeridatat',cols=None):
    """
    Collect files in one directory to one file.
    """

    filenames = listdir(dir_path)

    frames = []

    for fn in filenames:
        if substring in fn:
            print(fn)
            dat = pd.read_csv(dir_path + fn, sep=',', header='infer', encoding = 'ISO-8859-1')
            if cols is not None:
                frames.append(dat[cols])
            else:
                frames.append(dat)

    data = pd.concat(frames, ignore_index=True, sort=False)

#    data.to_csv(path_or_buf=dir_path + 'concat.csv', sep=',', na_rep='NaN', index=False)
    return data

def plot_xy(x, y, slope=None):

    plt.scatter(x, y, marker='o')
    idx = np.isfinite(x) & np.isfinite(y)

    if slope==None:
        p = np.polyfit(x[idx], y[idx], 1)
    else:
        p = [slope, np.mean(slope * y[idx] - x[idx])]

    residuals = y[idx] - (p[0]*x[idx] + p[1])
    R2 = 1 - sum(residuals**2)/sum((y[idx]-np.mean(y[idx]))**2)
    plt.annotate("y = %.2fx%+.2f\nR$^2$ = %.2f" % (p[0], p[1], R2), (0.45, 0.85),
                 xycoords='axes fraction', ha='center', va='center', fontsize=9)

    lim = [min(min(y[idx]), min(x[idx]))-1000, max(max(y[idx]), max(x[idx]))+1000]
    lim2 = [min(min(y[idx]), min(x[idx])), max(max(y[idx]), max(x[idx]))]
    add = (lim2[1] - lim2[0]) * 0.1
    lim2[0] = lim2[0] - add
    lim2[1] = lim2[1] + add
    plt.plot(lim, lim, 'k:', linewidth=1)
    plt.plot(lim, [p[0]*lim[0] + p[1], p[0]*lim[1] + p[1]], 'k', linewidth=1)
    plt.ylim(lim2)
    plt.xlim(lim2)

loggerdata = gather_data(dir_path='O:/Projects/SOMPAsites/WTD_data/', substring='loggeridatat')
loggerdata.index = pd.to_datetime(loggerdata['date_time'], yearfirst=True)
manualdata = gather_data(dir_path='O:/Projects/SOMPAsites/WTD_data/', substring='manuaalidatat')
manualdata.index = pd.to_datetime(manualdata['date'], yearfirst=True)
manualdata['water_depth_korj2'] = manualdata['water_depth_cm']-manualdata['pipe_above_ground_cm']

# koealanumerointi Linttupirtti
a = np.tile(np.repeat(np.arange(1,17),9),int(len(manualdata[(manualdata['site']=='Lintupirtti')])/(4*9*4)))
manualdata.loc[(manualdata['site']=='Lintupirtti'),'plot']=a

plt.figure()
i=1
for site in set(manualdata['site']):
    print(site)
    plt.subplot(len(set(manualdata['site'])),1,i)
    plt.title(site)
    if site in set(loggerdata['site']):
        for plot in set(loggerdata[loggerdata['site']==site]['plot']):
            plt.plot(loggerdata[(loggerdata['site']==site) & (loggerdata['plot']==plot)].index,
                     loggerdata[(loggerdata['site']==site) & (loggerdata['plot']==plot)]['water_depth_cm'],
                     label=plot,color=pal[plot-1])
    for plot in set(manualdata[manualdata['site']==site]['plot']):
        plt.plot(manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)].index,
                 manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)]['water_depth_cm'],
                 'o',linestyle='',color=pal[plot-1],label=plot)
    plt.legend(ncol=2)
    plt.gca().invert_yaxis()
    i+=1
plt.tight_layout()

plt.figure()
i=1
for site in set(manualdata['site']):
    print(site)
    plt.subplot(len(set(manualdata['site'])),1,i)
    plt.title(site)
    for plot in set(manualdata[manualdata['site']==site]['plot']):
        plt.plot(manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)]['pipe_no'],
                 manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)]['pipe_above_ground_cm'],
                 '-o')
    i+=1

#for i in range (9):  # 25.8.2015, 2 -> 4
#    plt.figure()
#    colors=['k','k','k','k','b','b','b','b','r','r','r','r','g','g','g','g']
#    for plot in set(manualdata[manualdata['site']=='Lintupirtti']['plot']):
#        plt.plot(manualdata[(manualdata['site']=='Lintupirtti') & (manualdata['plot']==plot)& (manualdata['pipe_no']==i+1)].index,
#                 manualdata[(manualdata['site']=='Lintupirtti') & (manualdata['plot']==plot)& (manualdata['pipe_no']==i+1)]['pipe_above_ground_cm'],
#                 '-o',color=colors[plot-1])

plt.figure()
site ='Paroninkorpi'
site_dat = manualdata[manualdata['site']==site].groupby(['date','plot']).agg({'water_depth_korj2':['min', 'max', 'median']})
site_dat = site_dat.unstack()
site_dat.index=pd.to_datetime(site_dat.index, yearfirst=True)
if site in set(loggerdata['site']):
    for plot in set(loggerdata[loggerdata['site']==site]['plot']):
        plt.subplot(round(max(site_dat.columns.levels[2])/2),2,plot)
        plt.plot(loggerdata[(loggerdata['site']==site) & (loggerdata['plot']==plot)].index,
                 loggerdata[(loggerdata['site']==site) & (loggerdata['plot']==plot)]['water_depth_cm'],
                 label=plot,color=pal[plot-1])
for plot in site_dat.columns.levels[2]:
    plt.subplot(round(max(site_dat.columns.levels[2])/2),2,plot)
    plt.errorbar(site_dat.index,
                 site_dat['water_depth_korj2']['median'][plot],
                 yerr=[-site_dat['water_depth_korj2']['min'][plot]+site_dat['water_depth_korj2']['median'][plot],
                       site_dat['water_depth_korj2']['max'][plot]-site_dat['water_depth_korj2']['median'][plot]],
                       color=pal[plot-1],label=plot,ecolor='k', marker='o', linestyle='', capsize=2)
    plt.legend(ncol=2)
    plt.gca().invert_yaxis()

loggerdaily=loggerdata[loggerdata['site']==site].groupby(['plot']).resample('D').mean()
loggerdaily=loggerdaily['water_depth_cm']
loggerdaily=loggerdaily.reorder_levels(['date_time', 'plot'])
dd=loggerdaily.unstack()
ddd=site_dat.merge(dd,how='outer',left_index=True, right_index=True)

plt.figure()
for plot in site_dat.columns.levels[2]:
    plt.subplot(2,round(max(site_dat.columns.levels[2])/2),plot)
    plot_xy(ddd[('water_depth_korj2','median',plot)],ddd[plot])