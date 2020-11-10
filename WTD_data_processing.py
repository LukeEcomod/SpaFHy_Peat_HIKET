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

eps = np.finfo(float).eps  # machine epsilon

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

def plot_xy(x, y, slope=None, return_para=False, plot=True, line=True, color='b'):


    idx = np.isfinite(x) & np.isfinite(y)

    if slope==None:
        p = np.polyfit(x[idx], y[idx], 1)
    else:
        p = [slope, np.mean(slope * y[idx] - x[idx])]

    if plot:
        plt.scatter(x, y, marker='o', color=color)
        residuals = y[idx] - (p[0]*x[idx] + p[1])
        R2 = 1 - sum(residuals**2)/(sum((y[idx]-np.mean(y[idx]))**2) + eps)
        # plt.annotate("y = %.2fx%+.2f\nR$^2$ = %.2f" % (p[0], p[1], R2), (max(x[idx]),max(y[idx])),
        #             ha='left', va='center', fontsize=9, color=color)
        lim = [min(min(y[idx]), min(x[idx]))-1000, max(max(y[idx]), max(x[idx]))+1000]
        lim2 = [min(min(y[idx]), min(x[idx])), max(max(y[idx]), max(x[idx]))]
        add = (lim2[1] - lim2[0]) * 0.1
        lim2[0] = lim2[0] - add
        lim2[1] = lim2[1] + add
        if line:
            plt.plot(lim, lim, 'k:', linewidth=1)
            plt.plot(lim, [p[0]*lim[0] + p[1], p[0]*lim[1] + p[1]], color=color, linewidth=1)
            plt.ylim(lim2)
            plt.xlim(lim2)
        else:
            plt.plot([min(x[idx]),max(x[idx])],
                     [p[0]*min(x[idx]) + p[1], p[0]*max(x[idx]) + p[1]], color=color, linewidth=1)
        plt.annotate("R$^2$ = %.2f" % (R2), (0.05, 0.85), xycoords='axes fraction',
                     fontsize=9, color=color)

    if return_para:
        return p

def run(save=False, fn='sompa_data/wtd_obs.csv', loggers=False, slope=None):
    if loggers:
        loggerdata = gather_data(dir_path='O:/Projects/SOMPAsites/WTD_data/', substring='loggeridatat')
        # loggerdata = gather_data(dir_path='C:/Users/03110850/Desktop/sompa temp/SOMPAsites/WTD_data/', substring='loggeridatat')
        loggerdata = loggerdata.rename(columns={'date_time':'date'})
        loggerdata.index = pd.to_datetime(loggerdata['date'], yearfirst=True)
    manualdata = gather_data(dir_path='O:/Projects/SOMPAsites/WTD_data/', substring='manuaalidatat')
    # manualdata = gather_data(dir_path='C:/Users/03110850/Desktop/sompa temp/SOMPAsites/WTD_data/', substring='manuaalidatat')
    manualdata['date'] = pd.to_datetime(manualdata['date'], yearfirst=True)
    manualdata['year'] = pd.to_datetime(manualdata['date'].values).year

    # datan tsekkaus
    site = 'Vaarajoki'
    ix = (manualdata['site']==site)
    # plt.figure(figsize=(12,round(len(set(manualdata[ix]['plot']))/2)*2))
    # for plot in set(manualdata[ix]['plot']):
    #     ixx = ix & (manualdata['plot'] == plot)
    #     plt.subplot(round(len(set(manualdata[ix]['plot']))/2),2,plot)
    #     plt.title(site + ' ' + str(plot))
    #     for pipe in range(9):
    #         plt.plot(manualdata[ixx & (manualdata['pipe_no']==pipe+1)]['date'],
    #                   manualdata[ixx & (manualdata['pipe_no']==pipe+1)]['water_depth_korj'],'-o',
    #                   color=pal[pipe])
    #     plt.gca().invert_yaxis()

    # plt.figure(figsize=(12,round(len(set(manualdata[ix]['plot']))/2)*2))
    # for plot in set(manualdata[ix]['plot']):
    #     ixx = ix & (manualdata['plot'] == plot)
    #     plt.subplot(round(len(set(manualdata[ix]['plot']))/2),2,plot)
    #     plt.title(site + ' ' + str(plot))
    #     for pipe in range(9):
    #         plt.plot(manualdata[ixx & (manualdata['pipe_no']==pipe+1)]['date'],
    #                   manualdata[ixx & (manualdata['pipe_no']==pipe+1)]['pipe_above_ground_cm'],'-o',
    #                   color=pal[pipe], label=pipe+1)
    #     plt.gca().invert_yaxis()
    # plt.legend()

    # pipe_above_ground_cm measured in 2018 to 2017
    for plot in set(manualdata[ix]['plot']):
        ixx = ix & (manualdata['plot'] == plot)
        for pipe in range(9):
            manualdata.loc[ixx & (manualdata['pipe_no']==pipe+1)
                    & (manualdata['year']==2017),'pipe_above_ground_cm'] = (
                    manualdata.loc[ixx & (manualdata['pipe_no']==pipe+1)
                    & (manualdata['year']==2018),'pipe_above_ground_cm'].mean())

    # Plot 2 & pipe 6
    manualdata.loc[ix & (manualdata['plot'] == 2) & (manualdata['pipe_no']==6)
            & (manualdata['year']>=2017),'pipe_above_ground_cm'] = (
            manualdata.loc[ix & (manualdata['plot'] == 2) & (manualdata['pipe_no']==6)
            & (manualdata['year']==2016),'pipe_above_ground_cm'].mean())

    # Plot 6 & pipe 5
    manualdata.loc[ix & (manualdata['plot'] == 6) & (manualdata['pipe_no']==5)
            & (manualdata['year']>=2017),'pipe_above_ground_cm'] = (
            manualdata.loc[ix & (manualdata['plot'] == 6) & (manualdata['pipe_no']==5)
            & (manualdata['year']==2016),'pipe_above_ground_cm'].mean())

    # Plot 1 & pipe 1 much higher than rest
    manualdata.loc[((manualdata['site']=='Vaarajoki')
                    & (manualdata['plot']==1)
                    & (manualdata['pipe_no']==1)),'water_depth_cm']=np.nan

    # plt.figure(figsize=(12,round(len(set(manualdata[ix]['plot']))/2)*2))
    # for plot in set(manualdata[ix]['plot']):
    #     ixx = ix & (manualdata['plot'] == plot)
    #     plt.subplot(round(len(set(manualdata[ix]['plot']))/2),2,plot)
    #     plt.title(site + ' ' + str(plot))
    #     for pipe in range(9):
    #         plt.plot(manualdata[ixx & (manualdata['pipe_no']==pipe+1)]['date'],
    #                   manualdata[ixx & (manualdata['pipe_no']==pipe+1)]['water_depth_cm'],'-o',
    #                   color=pal[pipe], label=pipe+1)
    #     plt.gca().invert_yaxis()
    # plt.legend()

    # apparently dry pipes
    manualdata.loc[(ix & (manualdata['plot']==2)
                    & (manualdata['date']>='7.1.2019')),'water_depth_cm']=np.nan
    manualdata.loc[(ix & (manualdata['plot']==3) & (manualdata['pipe_no']==1)
                    & (manualdata['date']>='7.1.2019')),'water_depth_cm']=np.nan
    manualdata.loc[(ix & (manualdata['plot']==3) & (manualdata['pipe_no']==7)
                    & (manualdata['date']>='7.15.2019')),'water_depth_cm']=np.nan
    manualdata.loc[(ix & (manualdata['plot']==3) & (manualdata['pipe_no']==5)
                    & (manualdata['date']>='7.31.2019')),'water_depth_cm']=np.nan
    manualdata.loc[(ix & (manualdata['plot']==1)
                    & (manualdata['water_depth_cm']>=116)),'water_depth_cm']=np.nan
    manualdata.loc[(ix & (manualdata['plot']==4) & (manualdata['pipe_no']==6)
                    & (manualdata['water_depth_cm']>=110)),'water_depth_cm']=np.nan
    manualdata.loc[(ix & (manualdata['plot']==4) & (manualdata['pipe_no']==1)
                    & (manualdata['water_depth_cm']>=120)),'water_depth_cm']=np.nan

    manualdata.loc[ix,'water_depth_korj'] = (
        manualdata.loc[ix,'water_depth_cm'] - manualdata.loc[ix,'pipe_above_ground_cm'])

    site = 'Havusuo'
    ix = (manualdata['site']==site)
    # plt.figure(figsize=(12,round(len(set(manualdata[ix]['plot']))/2)*2))
    # for plot in set(manualdata[ix]['plot']):
    #     ixx = ix & (manualdata['plot'] == plot)
    #     plt.subplot(round(len(set(manualdata[ix]['plot']))/2),2,plot)
    #     plt.title(site + ' ' + str(plot))
    #     print(set(manualdata[ixx]['pipe_no']))
    #     for pipe in range(9):
    #         plt.plot(manualdata[ixx & (manualdata['pipe_no']==pipe+1)]['date'],
    #                   manualdata[ixx & (manualdata['pipe_no']==pipe+1)]['water_depth_korj'],'-o',
    #                   color=pal[pipe], label=pipe+1)
    #     plt.gca().invert_yaxis()
    # plt.legend()

    # apparently dry pipes
    manualdata.loc[(ix & (manualdata['plot']==4) & (manualdata['pipe_no']==4)
                    & (manualdata['water_depth_korj']>=45)),'water_depth_korj']=np.nan
    manualdata.loc[(ix & (manualdata['plot']==4) & (manualdata['pipe_no']==6)
                    & (manualdata['water_depth_korj']>=46)),'water_depth_korj']=np.nan
    manualdata.loc[(ix & (manualdata['plot']==1) & (manualdata['pipe_no']==7)
                    & (manualdata['water_depth_korj']>=42)),'water_depth_korj']=np.nan
    manualdata.loc[(ix & (manualdata['plot']==1) & (manualdata['pipe_no']==9)
                    & (manualdata['water_depth_korj']>=57)),'water_depth_korj']=np.nan

    site = 'Lintupirtti'
    ix = (manualdata['site']==site)
    # koealanumerointi Linttupirtti: (Lohko -1)*4 + Koeala
    manualdata.loc[ix,'plot']=(
            manualdata[ix]['experiment']-1)*4+manualdata[ix]['plot']

    # kun kaivo täynnä wtd=0
    manualdata.loc[(ix & (manualdata['water_depth_cm']<=0)),'water_depth_cm']=np.nan

    # apparently dry pipes
    manualdata.loc[(ix & (manualdata['water_depth_cm']>=110)),'water_depth_cm']=np.nan

    # pipe_above_ground_cm measured in 2019 for plot 14 somehow wrong
    ixx = ix & (manualdata['plot'] == 14)
    for pipe in range(9):
        manualdata.loc[ixx & (manualdata['pipe_no']==pipe+1)
                & (manualdata['date']>'07-01-2019'),'pipe_above_ground_cm'] = (
                manualdata.loc[ixx & (manualdata['pipe_no']==pipe+1)
                & (manualdata['year']==2018),'pipe_above_ground_cm'].mean())

    manualdata.loc[ix,'water_depth_korj']=(
            manualdata[ix]['water_depth_cm']-manualdata[ix]['pipe_above_ground_cm'])

    # values < 0
    manualdata.loc[(ix & (manualdata['water_depth_korj']<=0)),'water_depth_korj']=np.nan

    manualdata.loc[(ix & (manualdata['plot']==14) & (manualdata['date']=='6-5-2015')),'water_depth_korj']=np.nan

    # plt.figure(figsize=(12,round(len(set(manualdata[ix]['plot']))/2)*2))
    # for plot in set(manualdata[ix]['plot']):
    #     ixx = ix & (manualdata['plot'] == plot)
    #     plt.subplot(round(len(set(manualdata[ix]['plot']))/2),2,plot)
    #     plt.title(site + ' ' + str(plot))
    #     for pipe in range(9):
    #         plt.plot(manualdata[ixx & (manualdata['pipe_no']==pipe+1)]['date'],
    #                   manualdata[ixx & (manualdata['pipe_no']==pipe+1)]['pipe_above_ground_cm'],'-o',
    #                   color=pal[pipe], label=pipe+1)
    #     plt.gca().invert_yaxis()
    # plt.legend()

    # plt.figure(figsize=(12,round(len(set(manualdata[ix]['plot']))/2)*2))
    # for plot in set(manualdata[ix]['plot']):
    #     ixx = ix & (manualdata['plot'] == plot)
    #     plt.subplot(round(len(set(manualdata[ix]['plot']))/2),2,plot)
    #     plt.title(site + ' ' + str(plot))
    #     for pipe in range(9):
    #         plt.plot(manualdata[ixx & (manualdata['pipe_no']==pipe+1)]['date'],
    #                   manualdata[ixx & (manualdata['pipe_no']==pipe+1)]['water_depth_cm'],'-o',
    #                   color=pal[pipe], label=pipe+1)
    #     plt.gca().invert_yaxis()
    # plt.legend()

    # plt.figure(figsize=(12,round(len(set(manualdata[ix]['plot']))/2)*2))
    # for plot in set(manualdata[ix]['plot']):
    #     ixx = ix & (manualdata['plot'] == plot)
    #     plt.subplot(round(len(set(manualdata[ix]['plot']))/2),2,plot)
    #     plt.title(site + ' ' + str(plot))
    #     for pipe in range(9):
    #         plt.plot(manualdata[ixx & (manualdata['pipe_no']==pipe+1)]['date'],
    #                   manualdata[ixx & (manualdata['pipe_no']==pipe+1)]['water_depth_korj'],'-o',
    #                   color=pal[pipe], label=pipe+1)
    #     plt.gca().invert_yaxis()
    # plt.legend()

    # kontrollikoealat ja hakkuun ajankohta
    info = {'Rouvanlehto':{'harvest':'3-1-2017', # mm-dd-yyy
                            'control_plots':[1,6],
                            'logger_start':'6-7-2017',
                            'logger_min':-10,
                            'logger_max':60},
            'Sinilammenneva':{'harvest':'3-1-2018', # mm-dd-yyy
                            'control_plots':[2,5,8],
                            'logger_start':'5-25-2018',
                            'logger_min':-10,
                            'logger_max':100},
            'Vaarajoki':{'harvest':'3-1-2017', # mm-dd-yyy
                            'control_plots':[2,5],
                            'logger_start':'6-10-2017',
                            'logger_min':-10,
                            'logger_max':72},
            'Paroninkorpi':{'harvest':'3-1-2017', # mm-dd-yyy
                            'control_plots':[3,6,9,10,15],
                            'logger_start':'5-1-2016',
                            'logger_min':-10,
                            'logger_max':100},
            'Havusuo':{'harvest':'4-1-2016', # mm-dd-yyy
                            'control_plots':[1,4],
                            'logger_start':'9-20-2015',
                            'logger_min':6,
                            'logger_max':200},
            'Lintupirtti':{'harvest':'6-20-2015', # mm-dd-yyy
                            'control_plots':[1,5,9,13]}  #
            }

    if loggers:
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

    # plt.figure()
    # i=1
    # for site in set(manualdata['site']):
    #     print(site)
    #     plt.subplot(len(set(manualdata['site'])),1,i)
    #     plt.title(site)
    #     if site in set(loggerdata['site']):
    #         for plot in set(loggerdata[loggerdata['site']==site]['plot']):
    #             plt.plot(loggerdata[(loggerdata['site']==site) & (loggerdata['plot']==plot)].index,
    #                      loggerdata[(loggerdata['site']==site) & (loggerdata['plot']==plot)]['water_depth_cm'],
    #                      label=plot,color=pal[plot-1])
    #             plt.plot(loggerdata[(loggerdata['site']==site) & (loggerdata['plot']==plot)].index,
    #                     loggerdata[(loggerdata['site']==site) & (loggerdata['plot']==plot)]['logger_raw'],
    #                     ':k')
    #     # for plot in set(manualdata[manualdata['site']==site]['plot']):
    #     #     plt.plot(manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)].index,
    #     #             manualdata[(manualdata['site']==site) & (manualdata['plot']==plot)]['water_depth_korj'],
    #     #             'o',linestyle='',color=pal[plot-1],label=plot)
    #     # plt.legend(ncol=2)
    #     plt.gca().invert_yaxis()
    #     i+=1

    # comparing pipes
    # site = 'Rouvanlehto'
    # ix = (manualdata['site']==site)
    # for plot in set(manualdata[ix]['plot']):
    #     plt.figure(figsize=(12,12))
    #     ixx = ix & (manualdata['plot'] == plot)
    #     for i in range(9):
    #         for j in range(9):
    #             plt.subplot(9,9,i+1+9*j)
    #             plot_xy(manualdata[ixx & (manualdata['pipe_no']==i+1)]['water_depth_korj'].values,
    #                     manualdata[ixx & (manualdata['pipe_no']==j+1)]['water_depth_korj'].values)

    # plotwise dataframe for all data
    wtd = manualdata.groupby(['date','site','plot']).agg({'water_depth_korj':['min', 'max', 'median','count']})
    wtd.columns = wtd.columns.droplevel(0)

    wtd.loc[(wtd['count']<=3), 'median'] = np.nan

    wtd = wtd.rename(columns={'min':'manual_min',
                              'max':'manual_max',
                              'median':'manual_median'})

    if loggers:
        loggerdaily =loggerdata.groupby(['site','plot']).resample('D').mean()
        loggerdaily = loggerdaily['logger_raw']
        loggerdaily = loggerdaily.reorder_levels(['date', 'site', 'plot'])

        wtd = wtd.merge(loggerdaily,how='outer',left_index=True, right_index=True)

    wtd.reset_index(inplace=True,level=[1,2])

    if loggers:
        wtd['logger_corrected'] = np.nan
        wtd['logger_pred_min'] = np.nan
        wtd['logger_pred_max'] = np.nan
        wtd['logger_pred_mean'] = np.nan

    wtd['manual_pred_min'] = np.nan
    wtd['manual_pred_max'] = np.nan
    wtd['manual_pred_mean'] = np.nan

    for site in set(wtd['site']):
        ix = (wtd['site'] == site)

        if loggers:
            # correct raw logger data against manual measurements
            if any(np.isfinite(wtd[ix]['logger_raw'])):
                # plt.figure(figsize=(2*len(set(wtd[ix]['plot']))/2,4))
                for plot in set(wtd[ix]['plot']):
                    # plt.subplot(2,round(len(set(wtd[ix]['plot']))/2),plot)
                    # plt.title(site)
                    ixx=(ix & (wtd['plot'] == plot))
                    p = plot_xy(wtd[ixx]['logger_raw'],
                                wtd[ixx]['manual_median'],
                                return_para=True, plot=False)
                    wtd.loc[ixx,'logger_corrected'] = (
                        p[0]*wtd.loc[ixx,'logger_raw'] + p[1])
                plt.tight_layout()

        # predicted control for all plots based on all control plots of site
        plt.figure(figsize=(0.5+1.5*len(info[site]['control_plots']),1.5*len(set(wtd[ix]['plot']))))
        calib_data=wtd[ix & (wtd.index < info[site]['harvest'])]
        i=1
        for plot1 in set(wtd[ix]['plot']):
            pred_control = []
            pred_control_log = []
            ixx = ix & (wtd['plot'] == plot1)
            for plot2 in info[site]['control_plots']:
                if i==1:
                    ax=plt.subplot(len(set(wtd[ix]['plot'])),len(info[site]['control_plots']),i)
                    if plot1 in info[site]['control_plots']:
                        ax.set_facecolor('lightgrey')
                else:
                    axx=plt.subplot(len(set(wtd[ix]['plot'])),len(info[site]['control_plots']),i, sharex=ax, sharey=ax)
                    if plot1 in info[site]['control_plots']:
                        axx.set_facecolor('lightgrey')
                if site == 'Lintupirttiiii':
                    pred_control.append(
                        wtd.loc[ix & (wtd['plot'] == plot2),'manual_median'].values)
                else:
                    p = plot_xy(calib_data[calib_data['plot'] == plot2]['manual_median'],
                            calib_data[calib_data['plot'] == plot1]['manual_median'],
                            return_para=True, slope=slope)
                    if plot2 != plot1:
                        pred_control.append(
                            p[0] * wtd.loc[ix & (wtd['plot'] == plot2),'manual_median'].values + p[1])
                if plot1 == len(set(wtd[ix]['plot'])):
                    plt.xlabel(plot2)
                else:
                    plt.setp(plt.gca().axes.get_xticklabels(), visible=False)
                if plot2 == info[site]['control_plots'][0]:
                    plt.ylabel(plot1)
                else:
                    plt.setp(plt.gca().axes.get_yticklabels(), visible=False)
                if loggers:
                    # logger prediction with same relation
                    if plot2 != plot1:
                        pred_control_log.append(
                            p[0]*wtd.loc[ix & (wtd['plot'] == plot2),'logger_corrected'].values + p[1])
                i+=1
            wtd.loc[ixx,'manual_pred_mean'] = np.nanmean(pred_control,axis=0)
            wtd.loc[ixx,'manual_pred_max'] = np.nanmax(pred_control,axis=0)
            wtd.loc[ixx,'manual_pred_min'] = np.nanmin(pred_control,axis=0)
            if loggers:
                wtd.loc[ixx,'logger_pred_mean'] = np.nanmean(pred_control_log,axis=0)
                wtd.loc[ixx,'logger_pred_max'] = np.nanmax(pred_control_log,axis=0)
                wtd.loc[ixx,'logger_pred_min'] = np.nanmin(pred_control_log,axis=0)
        plt.ylim([0,max(wtd[ix]['manual_median'])])
        plt.xlim([0,max(wtd[ix]['manual_median'])])
        plt.tight_layout()

        # Plot wtd for each plot of site with predicted control and range of measurements
        plt.figure(figsize=(12,round(len(set(wtd[ix]['plot']))/2)*2))
        for plot in set(wtd[ix]['plot']):
            ixx = ix & (wtd['plot'] == plot)
            if plot == 1:
                ax = plt.subplot(round(len(set(wtd[ix]['plot']))/2),2,plot)
                if  plot in info[site]['control_plots']:
                    ax.set_facecolor('lightgrey')
            else:
                axx=plt.subplot(round(len(set(wtd[ix]['plot']))/2),2,plot,sharex=ax,sharey=ax)
                if  plot in info[site]['control_plots']:
                    axx.set_facecolor('lightgrey')
            plt.title(site + ' ' + str(plot))
            if loggers:
                if any(np.isfinite(wtd[ixx]['logger_raw'])):
                    plt.fill_between(wtd[ixx].index, wtd[ixx]['logger_pred_min'], wtd[ixx]['logger_pred_max'],
                                     facecolor='k', alpha=0.3)
                    plt.plot(wtd[ixx].index, wtd[ixx]['logger_pred_mean'],':k')
                    plt.plot(wtd[ixx].index, wtd[ixx]['logger_corrected'],'-k')
            plt.errorbar(wtd[ixx].index, wtd[ixx]['manual_pred_mean'],
                         yerr=[-wtd[ixx]['manual_pred_min']+wtd[ixx]['manual_pred_mean'],
                               wtd[ixx]['manual_pred_max']-wtd[ixx]['manual_pred_mean']],
                               color='k',label=plot, ecolor='k', marker='x', linestyle='', capsize=2)
            plt.errorbar(wtd[ixx].index, wtd[ixx]['manual_median'],
                         yerr=[-wtd[ixx]['manual_min']+wtd[ixx]['manual_median'],
                                wtd[ixx]['manual_max']-wtd[ixx]['manual_median']],
                                color='r',label=plot, ecolor='r', marker='o', linestyle='', capsize=2)
            plt.plot([pd.to_datetime(info[site]['harvest']),pd.to_datetime(info[site]['harvest'])], [150,0],'--k')
            # select =((manualdata['site']==site) & (manualdata['plot']==plot) &
            #          ((manualdata['pipe_no']==2) | (manualdata['pipe_no']==5) | (manualdata['pipe_no']==8)))
            # plt.plot(manualdata[select]['date'], manualdata[select]['water_depth_korj'],
            #         's',linestyle='',color='k')
            if plot < (len(set(wtd[ix]['plot']))) - 1:
                plt.setp(plt.gca().axes.get_xticklabels(), visible=False)
            if (plot % 2) == 0:
                plt.setp(plt.gca().axes.get_yticklabels(), visible=False)
            else:
                plt.ylabel('WTD (cm)')
        plt.ylim([0,max(wtd[ix]['manual_pred_max'])+2])
        plt.gca().invert_yaxis()
        plt.tight_layout()

    cols = ['manual_min', 'manual_max', 'manual_median','manual_pred_min', 'manual_pred_max','manual_pred_mean']
    if loggers:
        cols= cols + ['logger_raw', 'logger_corrected', 'logger_pred_min', 'logger_pred_max',
           'logger_pred_mean']

    for col in cols:
        wtd[col]=wtd[col]/100

    cols = ['site','plot'] + cols

    # save to file
    if save:
        wtd[cols].to_csv(fn)
    else:
        return wtd[cols]