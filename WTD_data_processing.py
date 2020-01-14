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

def plot_xy(x, y, slope=None, return_para=False):

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
    if return_para:
        return p

loggerdata = gather_data(dir_path='O:/Projects/SOMPAsites/WTD_data/', substring='loggeridatat')
loggerdata.index = pd.to_datetime(loggerdata['date_time'], yearfirst=True)
manualdata = gather_data(dir_path='O:/Projects/SOMPAsites/WTD_data/', substring='manuaalidatat')
manualdata.index = pd.to_datetime(manualdata['date'], yearfirst=True)

# Lintupirtin mittaukset suoraan maanpinnasta? pipe_above_ground_cm on usein nan..
manualdata['water_depth_korj2'] = np.where(manualdata['site']=='Lintupirtti',
                                           manualdata['water_depth_cm'],
                                           manualdata['water_depth_cm']-manualdata['pipe_above_ground_cm'])

# koealanumerointi Linttupirtti
a = np.tile(np.repeat(np.arange(1,17),9),int(len(manualdata[(manualdata['site']=='Lintupirtti')])/(4*9*4)))
manualdata.loc[(manualdata['site']=='Lintupirtti'),'plot']=a

# kontrollikoealat ja hakkuun ajankohta
info = {'Rouvanlehto':{'harvest':'1-1-2017', # mm-dd-yyy
                        'control_plots':[1,6],
                        'logger_start':'6-7-2017',
                        'logger_min':-10,
                        'logger_max':60},
        'Sinilammenneva':{'harvest':'3-1-2018', # mm-dd-yyy
                        'control_plots':[2,5,8],
                        'logger_start':'5-25-2018',
                        'logger_min':-10,
                        'logger_max':100},
        'Vaarajoki':{'harvest':'1-1-2017', # mm-dd-yyy
                        'control_plots':[2,5],
                        'logger_start':'6-10-2017',
                        'logger_min':-10,
                        'logger_max':72},
        'Paroninkorpi':{'harvest':'4-1-2017', # mm-dd-yyy
                        'control_plots':[3,6,9,10,15],
                        'logger_start':'5-1-2016',
                        'logger_min':-10,
                        'logger_max':100},
        'Havusuo':{'harvest':'1-1-2016', # mm-dd-yyy
                        'control_plots':[1,4],
                        'logger_start':'9-20-2015',
                        'logger_min':6,
                        'logger_max':200},
        'Lintupirtti':{'harvest':'1-1-2015', # mm-dd-yyy
                        'control_plots':[1,5,9,13]}
        }

loggerdata['water_depth_karsittu_cm'] = loggerdata['water_depth_cm'].copy()

for site in set(loggerdata['site']):
    for plot in set(loggerdata[loggerdata['site']==site]['plot']):
        loggerdata.loc[((loggerdata.index < info[site]['logger_start']) &
                        (loggerdata['site']==site) &
                        (loggerdata['plot']==plot)),'water_depth_karsittu_cm']=np.nan
        loggerdata.loc[((loggerdata['water_depth_cm'] > info[site]['logger_max']) &
                        (loggerdata['site']==site) &
                        (loggerdata['plot']==plot)),'water_depth_karsittu_cm']=np.nan
        loggerdata.loc[((loggerdata['water_depth_cm'] < info[site]['logger_min']) &
                        (loggerdata['site']==site) &
                        (loggerdata['plot']==plot)),'water_depth_karsittu_cm']=np.nan

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
            plt.plot(loggerdata[(loggerdata['site']==site) & (loggerdata['plot']==plot)].index,
                     loggerdata[(loggerdata['site']==site) & (loggerdata['plot']==plot)]['water_depth_karsittu_cm'],
                     ':k')
    for plot in set(manualdata[manualdata['site']==site]['plot']):
        plt.plot(manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)].index,
                 manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)]['water_depth_korj2'],
                 'o',linestyle='',color=pal[plot-1],label=plot)
#    plt.legend(ncol=2)
    plt.gca().invert_yaxis()
    i+=1
#plt.tight_layout()

#for site in set(manualdata['site']):
#    plt.figure()
#    print(site)
#    for plot in set(manualdata[manualdata['site']==site]['plot']):
#        plt.subplot(len(set(manualdata[manualdata['site']==site]['plot'])),1,plot)
#        plt.title(site)
#        plt.plot(manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)]['pipe_no'],
#                 manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)]['pipe_above_ground_cm'],
#                 'o')

# site='Lintupirtti' # Lintupirtti 25.8.2015, 2 -> 4
#for i in range (9):
#    plt.figure()
#    colors=['k','k','k','k','b','b','b','b','r','r','r','r','g','g','g','g']
#    for plot in set(manualdata[manualdata['site']==site]['plot']):
#        plt.plot(manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)& (manualdata['pipe_no']==i+1)].index,
#                 manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)& (manualdata['pipe_no']==i+1)]['pipe_above_ground_cm'],
#                 '-o',color=colors[plot-1])

loggerdata['water_depth_korj_cm'] = np.nan

for site in set(manualdata['site']):

    site_dat = manualdata[manualdata['site']==site].groupby(['date','plot']).agg({'water_depth_korj2':['min', 'max', 'median']})
    site_dat = site_dat.unstack()
    site_dat.index=pd.to_datetime(site_dat.index, yearfirst=True)

    if site in set(loggerdata['site']):
        loggerdaily=loggerdata[loggerdata['site']==site].groupby(['plot']).resample('D').mean()
        loggerdaily=loggerdaily['water_depth_karsittu_cm']
        loggerdaily=loggerdaily.reorder_levels(['date_time', 'plot'])
        loggerdaily=loggerdaily.unstack()
        ddd=site_dat.merge(loggerdaily,how='outer',left_index=True, right_index=True)

        plt.figure()
        for plot in site_dat.columns.levels[2]:
            plt.subplot(2,round(max(site_dat.columns.levels[2])/2),plot)
            plt.title(site)
            p = plot_xy(ddd[plot],ddd[('water_depth_korj2','median',plot)], return_para=True)
            loggerdata.loc[((loggerdata['site']==site) & (loggerdata['plot']==plot)),'water_depth_korj_cm']=(
                    p[0]*loggerdata.loc[((loggerdata['site']==site) & (loggerdata['plot']==plot)), 'water_depth_karsittu_cm'] + p[1])

        # calib against control sites
        loggerdaily=loggerdata[loggerdata['site']==site].groupby(['plot']).resample('D').mean()
        loggerdaily=loggerdaily['water_depth_korj_cm']
        loggerdaily=loggerdaily.reorder_levels(['date_time', 'plot'])
        loggerdaily=loggerdaily.unstack()
#        plt.figure(figsize=(2*len(info[site]['control_plots']),2*len(site_dat.columns.levels[2])))
#        i=1
#        loggerdaily_calib=loggerdaily[loggerdaily.index < info[site]['harvest']]
#        for plot1 in site_dat.columns.levels[2]:
#            for plot2 in info[site]['control_plots']:
#                plt.subplot(len(site_dat.columns.levels[2]),len(info[site]['control_plots']),i)
#                p = plot_xy(loggerdaily_calib[plot2],
#                            loggerdaily_calib[plot1],
#                            return_para=True)
#                plt.xlabel(plot2)
#                plt.ylabel(plot1)
#                loggerdaily[str(plot1) + '_pred_control'+str(plot2)]=(
#                        p[0]*loggerdaily[plot2] + p[1])
#                i+=1

    plt.figure(figsize=(2*len(info[site]['control_plots']),2*len(site_dat.columns.levels[2])))
    i=1
    site_dat_calib=site_dat[site_dat.index < info[site]['harvest']]
    for plot1 in site_dat.columns.levels[2]:
        mean = 0.0
        for plot2 in info[site]['control_plots']:
            plt.subplot(len(site_dat.columns.levels[2]),len(info[site]['control_plots']),i)
            p = plot_xy(site_dat_calib['water_depth_korj2']['median'][plot2],
                        site_dat_calib['water_depth_korj2']['median'][plot1],
                        return_para=True)
            plt.xlabel(plot2)
            plt.ylabel(plot1)
            site_dat['water_depth_korj2','pred_control'+str(plot2),plot1]=(
                p[0]*site_dat['water_depth_korj2']['median'][plot2] + p[1])
            mean += (p[0]*site_dat['water_depth_korj2']['median'][plot2] + p[1])
            if site in set(loggerdata['site']):
                loggerdaily[str(plot1) + '_pred_control'+str(plot2)]=(
                    p[0]*loggerdaily[plot2] + p[1])
            i+=1
        site_dat['water_depth_korj2','pred_control_mean',plot1]=mean/len(info[site]['control_plots'])
        if site in set(loggerdata['site']):
            loggerdaily[str(plot1) + '_pred_control_median']=loggerdaily[
                [str(plot1) + '_pred_control'+str(plot2) for plot2 in info[site]['control_plots']]].median(axis=1)

    plt.figure(figsize=(12,round(max(site_dat.columns.levels[2])/2)*2))
    if site in set(loggerdata['site']):
        for plot in set(loggerdata[loggerdata['site']==site]['plot']):
            plt.subplot(round(max(site_dat.columns.levels[2])/2),2,plot)
            for plot2 in info[site]['control_plots']:
                plt.plot(loggerdaily.index,
                     loggerdaily[str(plot) + '_pred_control'+str(plot2)],':',color='lightgrey')
            plt.plot(loggerdaily.index,
                     loggerdaily[str(plot) + '_pred_control_median'],':k')
#            plt.plot(loggerdata[(loggerdata['site']==site) & (loggerdata['plot']==plot)].index,
#                     loggerdata[(loggerdata['site']==site) & (loggerdata['plot']==plot)]['water_depth_cm'],
#                     label=plot,color=pal[plot-1], linestyle=':')
            plt.plot(loggerdata[(loggerdata['site']==site) & (loggerdata['plot']==plot)].index,
                     loggerdata[(loggerdata['site']==site) & (loggerdata['plot']==plot)]['water_depth_korj_cm'],
                     label=plot,color=pal[plot-1])
    for plot in site_dat.columns.levels[2]:
        plt.subplot(round(max(site_dat.columns.levels[2])/2),2,plot)
        plt.title(site + ' ' +str(plot))
        for plot2 in info[site]['control_plots']:
            plt.plot(site_dat.index,site_dat['water_depth_korj2']['pred_control'+str(plot2)][plot],'x', color='lightgrey')
        plt.plot(site_dat.index,site_dat['water_depth_korj2']['pred_control_mean'][plot],'xk')
        plt.errorbar(site_dat.index,
                     site_dat['water_depth_korj2']['median'][plot],
                     yerr=[-site_dat['water_depth_korj2']['min'][plot]+site_dat['water_depth_korj2']['median'][plot],
                           site_dat['water_depth_korj2']['max'][plot]-site_dat['water_depth_korj2']['median'][plot]],
                           color=pal[plot-1],label=plot,ecolor='k', marker='o', linestyle='', capsize=2)
        plt.gca().invert_yaxis()
    plt.tight_layout()

    if site in set(loggerdata['site']):
        WTD_junaug = loggerdaily[(loggerdaily.index.month >= 7) & (loggerdaily.index.month <= 7)].resample('Y').mean()
        for plot in set(loggerdata[loggerdata['site']==site]['plot']):
            WTD_junaug[str(plot) + '_WTD_dif_cm']=WTD_junaug[str(plot) + '_pred_control_median']-WTD_junaug[plot]
        WTD_junaug.index=WTD_junaug.index.year
        WTD_junaug.to_csv(path_or_buf="results/sompa/" + site + ".csv", sep=',', na_rep='NaN', index=True)