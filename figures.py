# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 16:36:48 2020

@author: 03110850
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import math

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color']

def timeseries_comparison(results, wtd,
                          labels=['Lintupirtti','Vaarajoki','Havusuo','Rouvanlehto','Sinilammenneva','Paroninkorpi']):

    # Time series
    for i in range(len(labels)):
        site=labels[i]
        ix = (wtd['site'] == site)
        if len(set(wtd[ix]['plot'])) < 10:
            m=math.ceil(len(set(wtd[ix]['plot']))/2)
            n=2
        else:
            m=math.ceil(len(set(wtd[ix]['plot']))/3)
            n=3
        plt.figure(figsize=(6*n,m*2))
        for plot in set(wtd[ix]['plot']):
            ixx = ix & (wtd['plot'] == plot)
            if plot==1:
                ax=plt.subplot(m,n,plot)
            else:
                plt.subplot(m,n,plot, sharex=ax, sharey=ax)
            if any(np.isfinite(wtd[ixx]['logger_raw'])):
                plt.fill_between(wtd[ixx].index, wtd[ixx]['logger_pred_min'], wtd[ixx]['logger_pred_max'],
                                  facecolor='k', alpha=0.3)
                plt.plot(wtd[ixx].index, wtd[ixx]['logger_pred_mean'],':k')
                plt.plot(wtd[ixx].index, wtd[ixx]['logger_corrected'],':r', label=plot)
            plt.errorbar(wtd[ixx].index, wtd[ixx]['manual_pred_mean'],
                          yerr=[-wtd[ixx]['manual_pred_min']+wtd[ixx]['manual_pred_mean'],
                                wtd[ixx]['manual_pred_max']-wtd[ixx]['manual_pred_mean']],
                                color='k',label=plot, ecolor='k', marker='x', linestyle='', capsize=2)
            plt.errorbar(wtd[ixx].index, wtd[ixx]['manual_median'],
                          yerr=[-wtd[ixx]['manual_min']+wtd[ixx]['manual_median'],
                                wtd[ixx]['manual_max']-wtd[ixx]['manual_median']],
                                color='r',label=plot, ecolor='r', marker='o', linestyle='', capsize=2)
            results['soil_ground_water_level'][:,plot-1,2*i+1].plot.line(x='date', color='r')
            results['soil_ground_water_level'][:,plot-1,2*i].plot.line(x='date', color='k')
            plt.title(site + ' ' + str(plot))
            if plot < max(wtd[ix]['plot'])+1-n:
                plt.setp(plt.gca().axes.get_xticklabels(), visible=False)
            plt.xlabel('')
            plt.ylabel('WTD [m]')
        plt.gca().invert_yaxis()
        plt.tight_layout()

def yearly_comparison(results, wtd):

    wtd_manual = wtd[np.isfinite(wtd['manual_median'])]
    wtd_manual = wtd_manual[['date','site', 'plot', 'manual_min', 'manual_max', 'manual_median',
                             'manual_pred_min', 'manual_pred_max','manual_pred_mean']]
    wtd_manual['id'] = np.arange(len(wtd_manual))

    # kontrollikoealat ja hakkuun ajankohta
    info = {'Lintupirtti':{'harvest':2015, # first year after harvest
                            'control_plots':[1,5,9,13],
                            'id':0},
            'Vaarajoki':{'harvest':2017,
                            'control_plots':[2,5],
                            'id':1},
            'Havusuo':{'harvest':2016,
                            'control_plots':[1,4],
                            'id':2},
            'Rouvanlehto':{'harvest':2017,
                            'control_plots':[1,6],
                            'id':3},
            'Sinilammenneva':{'harvest':2018,
                            'control_plots':[2,5,8],
                            'id':4},
            'Paroninkorpi':{'harvest':2017,
                            'control_plots':[3,6,9,10,15],
                            'id':5}
            }

    wtd_manual['mod_treated']=np.nan
    wtd_manual['mod_control']=np.nan
    for index, row in wtd_manual.iterrows():
        # print(row['plot'],row['site'],labels[info[row['site']]['id']])
        wtd_manual.loc[(wtd_manual['id'] == row['id']),'mod_control'] = (
            results['soil_ground_water_level'][:,row['plot']-1,2*info[row['site']]['id']][results.date==np.datetime64(row['date'])])
        wtd_manual.loc[(wtd_manual['id'] == row['id']),'mod_treated'] = (
            results['soil_ground_water_level'][:,row['plot']-1,2*info[row['site']]['id']+1][results.date==np.datetime64(row['date'])])

    wtd_yearly = wtd_manual[(wtd_manual.index.month>=6) & (wtd_manual.index.month<=9)].groupby(['site','plot']).resample('Y').mean()
    wtd_yearly = wtd_yearly.drop(columns=['plot'])
    wtd_yearly = wtd_yearly.reset_index(level=[0,1])
    wtd_yearly.index=wtd_yearly.index.year

    marker = ['+','x','^','s','D','o']
    years = list(set(wtd_yearly.index))
    years.sort()

    plt.figure(figsize=(13,4))
    plt.subplot(1,3,1)
    plt.plot([0,2],[0,2],':k')
    for key, value in info.items():
        ix = (wtd_yearly['site'] == key)
        for plot in set(wtd_yearly[ix]['plot']):
            if plot not in value['control_plots']:
                for year in years:
                    ixx = (ix & (wtd_yearly['plot'] == plot) & (wtd_yearly.index == year) & (wtd_yearly.index < value['harvest']))
                    plt.plot(wtd_yearly[ixx]['manual_median'],wtd_yearly[ixx]['mod_control'],
                             marker=marker[year-min(years)], color=colors[value['id']])
            else:
                for year in years:
                    ixx = (ix & (wtd_yearly['plot'] == plot) & (wtd_yearly.index == year))
                    plt.plot(wtd_yearly[ixx]['manual_median'],wtd_yearly[ixx]['mod_control'],
                             marker=marker[year-min(years)], color=colors[value['id']])
    plt.xlabel('Measured')
    plt.ylabel('Modelled')
    plt.ylim([0,1.2])
    plt.xlim([0,1.2])
    plt.title('Pre-harvest and reference site WTD')
    plt.subplot(1,3,2)
    plt.plot([0,2],[0,2],':k')
    for key, value in info.items():
        ix = (wtd_yearly['site'] == key)
        for plot in set(wtd_yearly[ix]['plot']):
            if plot not in value['control_plots']:
                for year in years:
                    ixx = (ix & (wtd_yearly['plot'] == plot) & (wtd_yearly.index == year) & (wtd_yearly.index >= value['harvest']))
                    plt.plot(wtd_yearly[ixx]['manual_median'],wtd_yearly[ixx]['mod_treated'],
                             marker=marker[year-min(years)], color=colors[value['id']])
    plt.xlabel('Measured')
    plt.ylim([0,1.2])
    plt.xlim([0,1.2])
    plt.title('Post-harvest WTD')
    plt.subplot(1,3,3)
    plt.plot([-1,1],[-1,1],':k')
    for key, value in info.items():
        ix = (wtd_yearly['site'] == key)
        for plot in set(wtd_yearly[ix]['plot']):
            if plot not in value['control_plots']:
                for year in years:
                    ixx = (ix & (wtd_yearly['plot'] == plot) & (wtd_yearly.index == year) & (wtd_yearly.index >= value['harvest']))
                    plt.plot(wtd_yearly[ixx]['manual_pred_mean'] - wtd_yearly[ixx]['manual_median'],
                             wtd_yearly[ixx]['mod_control'] - wtd_yearly[ixx]['mod_treated'],
                             marker=marker[year-min(years)], color=colors[value['id']])
        plt.annotate(key,(1.05, 0.85-(value['id']*0.07)), color=colors[value['id']], xycoords='axes fraction', weight='bold')
    for i in range(len(marker)):
        plt.plot([-1],[-1],marker[i],color='grey',label=years[i])
    plt.legend(bbox_to_anchor=(1.,0.26), loc="center left", frameon=False, borderpad=0.0)
    plt.xlabel('Measured')
    plt.ylim([-0.1,0.6])
    plt.xlim([-0.1,0.6])
    plt.title('WTD response to harvest')
    plt.tight_layout()