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
manualdata.index = pd.to_datetime(manualdata['date'], yearfirst=True).values

# koealanumerointi Linttupirtti: (Lohko -1)*4 + Koeala
manualdata.loc[(manualdata['site']=='Lintupirtti'),'plot']=(
        manualdata[(manualdata['site']=='Lintupirtti')]['experiment']-1)*4+manualdata[(manualdata['site']=='Lintupirtti')]['plot']

# kun kaivo täynnä wtd=0
manualdata.loc[((manualdata['site']=='Lintupirtti') & (manualdata['water_depth_cm']<=0)),'water_depth_cm']=np.nan

manualdata.loc[(manualdata['site']=='Lintupirtti'),'water_depth_korj']=(
        manualdata[(manualdata['site']=='Lintupirtti')]['water_depth_cm']-manualdata[(manualdata['site']=='Lintupirtti')]['pipe_above_ground_cm'])

#site='Lintupirtti'
#plt.figure()
#ax=plt.subplot(8,2,1)
#for plot in set(manualdata[manualdata['site']==site]['plot']):
#    plt.subplot(8,2,plot,sharey=ax)
#    plt.title(plot)
#    for i in range (9):
#        plt.plot(manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)& (manualdata['pipe_no']==i+1)].index,
#             manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)& (manualdata['pipe_no']==i+1)]['pipe_above_ground_cm'],
#             '-o')
#
#plt.figure()
#ax=plt.subplot(8,2,1)
#for plot in set(manualdata[manualdata['site']==site]['plot']):
#    plt.subplot(8,2,plot,sharey=ax)
#    plt.title(plot)
#    for i in range (9):
#        plt.plot(manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)& (manualdata['pipe_no']==i+1)].index,
#             manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)& (manualdata['pipe_no']==i+1)]['water_depth_cm'],
#             '-o')
#ax.invert_yaxis()
#
#plt.figure()
#ax=plt.subplot(8,2,1)
#for plot in set(manualdata[manualdata['site']==site]['plot']):
#    plt.subplot(8,2,plot,sharey=ax)
#    plt.title(plot)
#    for i in range (9):
#        plt.plot(manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)& (manualdata['pipe_no']==i+1)].index,
#             manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)& (manualdata['pipe_no']==i+1)]['water_depth_korj'],
#             '-o')
#ax.invert_yaxis()

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
#            plt.plot(loggerdata[(loggerdata['site']==site) & (loggerdata['plot']==plot)].index,
#                     loggerdata[(loggerdata['site']==site) & (loggerdata['plot']==plot)]['water_depth_karsittu_cm'],
#                     ':k')
#    for plot in set(manualdata[manualdata['site']==site]['plot']):
#        plt.plot(manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)].index,
#                 manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)]['water_depth_korj'],
#                 'o',linestyle='',color=pal[plot-1],label=plot)
#    plt.legend(ncol=2)
    plt.gca().invert_yaxis()
    i+=1
#plt.tight_layout()


loggerdata['water_depth_korj_cm'] = np.nan

for site in set(manualdata['site']):

    site_dat = manualdata[manualdata['site']==site].groupby(['date','plot']).agg({'water_depth_korj':['min', 'max', 'median']})
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
            p = plot_xy(ddd[plot],ddd[('water_depth_korj','median',plot)], return_para=True)
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
            p = plot_xy(site_dat_calib['water_depth_korj']['median'][plot2],
                        site_dat_calib['water_depth_korj']['median'][plot1],
                        return_para=True, slope=1)
            plt.xlabel(plot2)
            plt.ylabel(plot1)
            site_dat['water_depth_korj','pred_control'+str(plot2),plot1]=(
                p[0]*site_dat['water_depth_korj']['median'][plot2] + p[1])
            mean += (p[0]*site_dat['water_depth_korj']['median'][plot2] + p[1])
            if site in set(loggerdata['site']):
                loggerdaily['pred_control'+str(plot2) + '_' + str(plot1)]=(
                    p[0]*loggerdaily[plot2] + p[1])
            i+=1
        site_dat['water_depth_korj','pred_control_mean',plot1]=mean/len(info[site]['control_plots'])
        if site in set(loggerdata['site']):
            loggerdaily['pred_control_median_' + str(plot1)]=loggerdaily[
                ['pred_control'+str(plot2) + '_' + str(plot1) for plot2 in info[site]['control_plots']]].median(axis=1)

    plt.figure(figsize=(12,round(max(site_dat.columns.levels[2])/2)*2))
    if site in set(loggerdata['site']):
        for plot in set(loggerdata[loggerdata['site']==site]['plot']):
            plt.subplot(round(max(site_dat.columns.levels[2])/2),2,plot)
            for plot2 in info[site]['control_plots']:
                plt.plot(loggerdaily.index,
                     loggerdaily['pred_control'+str(plot2)+ '_'+ str(plot)],':',color='lightgrey')
            plt.plot(loggerdaily.index,
                     loggerdaily['pred_control_median_'+ str(plot)],':k')
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
            plt.plot(site_dat.index,site_dat['water_depth_korj']['pred_control'+str(plot2)][plot],'x', color='lightgrey')
        plt.plot(site_dat.index,site_dat['water_depth_korj']['pred_control_mean'][plot],'xk')
        plt.errorbar(site_dat.index,
                     site_dat['water_depth_korj']['median'][plot],
                     yerr=[-site_dat['water_depth_korj']['min'][plot]+site_dat['water_depth_korj']['median'][plot],
                           site_dat['water_depth_korj']['max'][plot]-site_dat['water_depth_korj']['median'][plot]],
                           color=pal[plot-1],label=plot,ecolor='k', marker='o', linestyle='', capsize=2)
        plt.gca().invert_yaxis()
    plt.tight_layout()
#
#    if site in set(loggerdata['site']):
#        WTD_junaug = loggerdaily[(loggerdaily.index.month >= 7) & (loggerdaily.index.month <= 8)].resample('Y').mean()
#        for plot in set(loggerdata[loggerdata['site']==site]['plot']):
#            WTD_junaug = WTD_junaug.rename(columns={plot: 'median_'+str(plot)})
#        WTD_junaug.columns=WTD_junaug.columns.str.rsplit('_', 1, expand=True)
#        WTD_junaug.index=WTD_junaug.index.year
#        WTD_junaug = WTD_junaug[['median','pred_control_median']]
#        WTD_junaug.columns.set_levels([int(i) for i in WTD_junaug.columns.levels[1]],level=1,inplace=True)
#        WTD_junaug = WTD_junaug.stack()
#        WTD_junaug['WTD_dif_cm']=WTD_junaug['pred_control_median']-WTD_junaug['median']
#        WTD_junaug = WTD_junaug.unstack()
#        WTD_junaug.to_csv(path_or_buf="results/sompa/" + site + "_logger.csv", sep=',', na_rep='NaN', index=True)
#
#    WTD_junaug = site_dat[(site_dat.index.month >= 7) & (site_dat.index.month <= 8)].resample('Y').mean()
#    WTD_junaug = WTD_junaug['water_depth_korj'][['median','pred_control_mean']]
#    WTD_junaug.index=WTD_junaug.index.year
#    WTD_junaug = WTD_junaug.stack()
#    WTD_junaug['WTD_dif_cm']=WTD_junaug['pred_control_mean']-WTD_junaug['median']
#    WTD_junaug = WTD_junaug.unstack()
#    WTD_junaug.to_csv(path_or_buf="results/sompa/" + site + "_manu.csv", sep=',', na_rep='NaN', index=True)
