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
loggerdata = loggerdata.rename(columns={'date_time':'date'})
loggerdata.index = pd.to_datetime(loggerdata['date'], yearfirst=True)
manualdata = gather_data(dir_path='O:/Projects/SOMPAsites/WTD_data/', substring='manuaalidatat')
manualdata['date'] = pd.to_datetime(manualdata['date'], yearfirst=True).values

# koealanumerointi Linttupirtti: (Lohko -1)*4 + Koeala
manualdata.loc[(manualdata['site']=='Lintupirtti'),'plot']=(
        manualdata[(manualdata['site']=='Lintupirtti')]['experiment']-1)*4+manualdata[(manualdata['site']=='Lintupirtti')]['plot']

# kun kaivo täynnä wtd=0
manualdata.loc[((manualdata['site']=='Lintupirtti') & (manualdata['water_depth_cm']<=0)),'water_depth_cm']=np.nan

manualdata.loc[(manualdata['site']=='Lintupirtti'),'water_depth_korj']=(
        manualdata[(manualdata['site']=='Lintupirtti')]['water_depth_cm']-manualdata[(manualdata['site']=='Lintupirtti')]['pipe_above_ground_cm'])

# site='Lintupirtti'
# plt.figure()
# ax=plt.subplot(8,2,1)
# for plot in set(manualdata[manualdata['site']==site]['plot']):
#     plt.subplot(8,2,plot,sharey=ax)
#     plt.title(plot)
#     for i in range (9):
#         plt.plot(manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)& (manualdata['pipe_no']==i+1)].index,
#             manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)& (manualdata['pipe_no']==i+1)]['pipe_above_ground_cm'],
#             '-o')
# plt.figure()
# ax=plt.subplot(8,2,1)
# for plot in set(manualdata[manualdata['site']==site]['plot']):
#     plt.subplot(8,2,plot,sharey=ax)
#     plt.title(plot)
#     for i in range (9):
#         plt.plot(manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)& (manualdata['pipe_no']==i+1)].index,
#             manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)& (manualdata['pipe_no']==i+1)]['water_depth_cm'],
#             '-o')
# ax.invert_yaxis()
# plt.figure()
# ax=plt.subplot(8,2,1)
# for plot in set(manualdata[manualdata['site']==site]['plot']):
#     plt.subplot(8,2,plot,sharey=ax)
#     plt.title(plot)
#     for i in range (9):
#         plt.plot(manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)& (manualdata['pipe_no']==i+1)].index,
#             manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)& (manualdata['pipe_no']==i+1)]['water_depth_korj'],
#             '-o')
# ax.invert_yaxis()

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

# loggerdata karsinta
loggerdata['logger_raw'] = loggerdata['water_depth_cm'].copy()

for site in set(loggerdata['site']):
    for plot in set(loggerdata[loggerdata['site']==site]['plot']):
        loggerdata.loc[((loggerdata.index < info[site]['logger_start']) &
                        (loggerdata['site']==site) &
                        (loggerdata['plot']==plot)),'logger_raw']=np.nan
        loggerdata.loc[((loggerdata['water_depth_cm'] > info[site]['logger_max']) &
                        (loggerdata['site']==site) &
                        (loggerdata['plot']==plot)),'logger_raw']=np.nan
        loggerdata.loc[((loggerdata['water_depth_cm'] < info[site]['logger_min']) &
                        (loggerdata['site']==site) &
                        (loggerdata['plot']==plot)),'logger_raw']=np.nan

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
                    loggerdata[(loggerdata['site']==site) & (loggerdata['plot']==plot)]['logger_raw'],
                    ':k')
    # for plot in set(manualdata[manualdata['site']==site]['plot']):
    #     plt.plot(manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)].index,
    #             manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)]['water_depth_korj'],
    #             'o',linestyle='',color=pal[plot-1],label=plot)
    # plt.legend(ncol=2)
    plt.gca().invert_yaxis()
    i+=1

# plotwise dataframe for all data
wtd = manualdata.groupby(['date','site','plot']).agg({'water_depth_korj':['min', 'max', 'median']})
wtd.columns = wtd.columns.droplevel(0)

wtd = wtd.rename(columns={'min':'manual_min',
                          'max':'manual_max',
                          'median':'manual_median'})

loggerdaily =loggerdata.groupby(['site','plot']).resample('D').mean()
loggerdaily = loggerdaily['logger_raw']
loggerdaily = loggerdaily.reorder_levels(['date', 'site', 'plot'])

wtd = wtd.merge(loggerdaily,how='outer',left_index=True, right_index=True)
wtd.reset_index(inplace=True,level=[1,2])

wtd['logger_corrected'] = np.nan
wtd['logger_pred_min'] = np.nan
wtd['logger_pred_max'] = np.nan
wtd['logger_pred_mean'] = np.nan
wtd['manual_pred_min'] = np.nan
wtd['manual_pred_max'] = np.nan
wtd['manual_pred_mean'] = np.nan

for site in set(wtd['site']):
    ix = (wtd['site'] == site)

    # correct raw logger data against manual measurements
    if any(np.isfinite(wtd[ix]['logger_raw'])):
        plt.figure(figsize=(2*len(set(wtd[ix]['plot']))/2,4))
        for plot in set(wtd[ix]['plot']):
            plt.subplot(2,round(len(set(wtd[ix]['plot']))/2),plot)
            plt.title(site)
            ixx=(ix & (wtd['plot'] == plot))
            p = plot_xy(wtd[ixx]['logger_raw'],
                        wtd[ixx]['manual_median'],
                        return_para=True)
            wtd.loc[ixx,'logger_corrected'] = (
                p[0]*wtd.loc[ixx,'logger_raw'] + p[1])
        plt.tight_layout()

    # predicted control for all plots based on all control plots of site
    plt.figure(figsize=(2*len(info[site]['control_plots']),2*len(set(wtd[ix]['plot']))))
    calib_data=wtd[ix & (wtd.index < info[site]['harvest'])]
    i=1
    for plot1 in set(wtd[ix]['plot']):
        pred_control = []
        pred_control_log = []
        ixx = ix & (wtd['plot'] == plot1)
        for plot2 in info[site]['control_plots']:
            plt.subplot(len(set(wtd[ix]['plot'])),len(info[site]['control_plots']),i)
            p = plot_xy(calib_data[calib_data['plot'] == plot2]['manual_median'],
                        calib_data[calib_data['plot'] == plot1]['manual_median'],
                        return_para=True, slope=1)  # SLOPE??
            plt.xlabel(plot2)
            plt.ylabel(plot1)
            pred_control.append(
                p[0] * wtd.loc[ix & (wtd['plot'] == plot2),'manual_median'].values + p[1])
            # logger prediction with same relation
            pred_control_log.append(
                p[0]*wtd.loc[ix & (wtd['plot'] == plot2),'logger_corrected'].values + p[1])
            i+=1
        wtd.loc[ixx,'manual_pred_mean'] = np.nanmean(pred_control,axis=0)
        wtd.loc[ixx,'manual_pred_max'] = np.nanmax(pred_control,axis=0)
        wtd.loc[ixx,'manual_pred_min'] = np.nanmin(pred_control,axis=0)
        wtd.loc[ixx,'logger_pred_mean'] = np.nanmean(pred_control_log,axis=0)
        wtd.loc[ixx,'logger_pred_max'] = np.nanmax(pred_control_log,axis=0)
        wtd.loc[ixx,'logger_pred_min'] = np.nanmin(pred_control_log,axis=0)

    # Plot wtd for each plot of site with predicted control and range of measurements
    plt.figure(figsize=(12,round(len(set(wtd[ix]['plot']))/2)*2))
    for plot in set(wtd[ix]['plot']):
        ixx = ix & (wtd['plot'] == plot)
        plt.subplot(round(len(set(wtd[ix]['plot']))/2),2,plot)
        plt.title(site + ' ' + str(plot))
        if any(np.isfinite(wtd[ixx]['logger_raw'])):
            plt.fill_between(wtd[ixx].index, wtd[ixx]['logger_pred_min'], wtd[ixx]['logger_pred_max'],
                             facecolor='k', alpha=0.3)
            plt.plot(wtd[ixx].index, wtd[ixx]['logger_pred_mean'],':k')
            plt.plot(wtd[ixx].index, wtd[ixx]['logger_corrected'],
                     label=plot,color=pal[plot-1])
        plt.errorbar(wtd[ixx].index, wtd[ixx]['manual_pred_mean'],
                     yerr=[-wtd[ixx]['manual_pred_min']+wtd[ixx]['manual_pred_mean'],
                           wtd[ixx]['manual_pred_max']-wtd[ixx]['manual_pred_mean']],
                           color='k',label=plot, ecolor='k', marker='x', linestyle='', capsize=2)
        plt.errorbar(wtd[ixx].index, wtd[ixx]['manual_median'],
                     yerr=[-wtd[ixx]['manual_min']+wtd[ixx]['manual_median'],
                            wtd[ixx]['manual_max']-wtd[ixx]['manual_median']],
                            color=pal[plot-1],label=plot, ecolor=pal[plot-1], marker='o', linestyle='', capsize=2)
        plt.gca().invert_yaxis()
    plt.tight_layout()

cols = ['manual_min', 'manual_max', 'manual_median',
       'logger_raw', 'logger_corrected', 'logger_pred_min', 'logger_pred_max',
       'logger_pred_mean', 'manual_pred_min', 'manual_pred_max','manual_pred_mean']

for col in cols:
    wtd[col]=wtd[col]/100

# save to file
wtd.to_csv('sompa_data/wtd_obs.csv')