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

def WTD_diff_analysis():

    # measured wtd
    wtd = pd.read_csv('sompa_data/wtd_obs_nologgers.csv', sep=',', header='infer', encoding = 'ISO-8859-1')
    wtd.index = pd.to_datetime(wtd['date'], yearfirst=True)

    # kontrollikoealat ja hakkuun ajankohta
    info = {
            'Lintupirtti':{'harvest':2015, # first year after harvest
                            'control_plots':[1,5,9,13],
                            'ba_old':[21.25,23.33,26.17,23.29,30.04,26.37,32.01,27.31,27.59,24.73,27.65,26.93,20.91,22.23,24.86,23.73],
                            'ba': [21.25,8.82,12.49,16.43,30.04,8.26,12.92,14.47,27.59,9.04,12.59,16.34,20.91,9.39,13.22,16.54],
                            'id':0},
            'Vaarajoki':{'harvest':2017,
                            'control_plots':[2,5],
                            'ba_old':[23.92,21.96,19.32,24.5,20.15,29.3],
                            'ba': [17.01,21.96,16.08,12.39,20.15,11.28],
                            'id':1},
            'Havusuo':{'harvest':2016,
                            'control_plots':[1,4],
                            'ba_old':[25.5,29.54,31.4,28.05],
                            'ba': [25.5,13.55,13.5,28.05],
                            'id':2},
            'Rouvanlehto':{'harvest':2017,
                            'control_plots':[1,6],
                            'ba_old':[22.91,22.12,21.67,24.3,21.25,22.1],
                            'ba': [22.91,12.2,11.57,17.2,17.06,22.1],
                            'id':3},
            'Sinilammenneva':{'harvest':2018,
                            'control_plots':[2,5,8],
                            'ba_old':[27.43,38.16,21,22.2,29.43,24.28,26.03,28.26],
                            'ba': [7.29,38.16,5.51,6.54,29.43,0,0,28.26],
                            'id':4},
            'Paroninkorpi':{'harvest':2017,
                            'control_plots':[3,6,9,10,15],
                            'ba_old':[24.87,25.68,26.83,25.31,24.72,23.56,24.08,21.99,22.77,24.28,21.89,24.85,31.25,26.65,29.74],
                            'ba': [16.86,13.16,26.83,16.32,11.59,23.56,16.92,13.06,22.77,24.28,17.63,12.95,12.06,16.85,29.74],
                            'id':5}
            }

    wtd_yearly = wtd[np.isfinite(wtd['manual_pred_mean']) & np.isfinite(wtd['manual_median']) &
                     (wtd.index.month>=6) & (wtd.index.month<=9)
                     ].groupby(['site','plot']).resample('Y').mean()
    wtd_yearly = wtd_yearly.drop(columns=['plot'])
    wtd_yearly = wtd_yearly.reset_index(level=[0,1])
    wtd_yearly.index = wtd_yearly.index.year

    wtd_yearly['ba_old'] = np.nan
    wtd_yearly['ba'] = np.nan
    wtd_yearly['id'] = np.nan
    wtd_yearly['control'] = np.nan
    wtd_yearly['post-harvest'] = np.nan

    for key, value in info.items():
        for plot in set(wtd_yearly[(wtd_yearly['site'] == key)]['plot']):
            ix = ((wtd_yearly['site'] == key) & (wtd_yearly['plot'] == plot))
            # print(key, len(value['ba_old']), plot)
            wtd_yearly.loc[ix,'ba_old'] = value['ba_old'][plot-1]
            wtd_yearly.loc[ix,'ba'] = np.where(
                (wtd_yearly[ix].index < value['harvest']),value['ba_old'][plot-1],value['ba'][plot-1])
            wtd_yearly.loc[ix,'post-harvest'] = np.where(
                (wtd_yearly[ix].index < value['harvest']),0,1)
            wtd_yearly.loc[ix,'control'] = np.where(wtd_yearly[ix]['plot'].isin(value['control_plots']),1,0)
        wtd_yearly.loc[(wtd_yearly['site'] == key),'id'] = value['id']

    wtd_yearly['ba_removed-%'] = (wtd_yearly['ba_old']-wtd_yearly['ba'])/wtd_yearly['ba_old']

    from statsmodels.api import OLS
    cmap=plt.cm.get_cmap('viridis')

    def plot_lines(p,ax=None):
        ba = np.linspace(0,1,6)
        x = np.linspace(0,1,2)
        for b in ba:
            # y = p[0] + p[1] * b * x
            y = p[0] * b * x
            if ax is None:
                plt.plot(x,y,'-', color=cmap(b), zorder=1)
            else:
                ax.plot(x,y,'-', color=cmap(b), zorder=1)

    # Sites in subplots
    fig, axes = plt.subplots(2, 3, sharex=True, sharey=True,figsize=(11,7))
    for idx in range(6):
        ax = axes.flat[idx]
        ix = ((wtd_yearly['control'] == 0) & (wtd_yearly['id'] == idx) & (wtd_yearly['post-harvest'] == 1) &
              np.isfinite(wtd_yearly['manual_pred_mean']) & np.isfinite(wtd_yearly['manual_median']))
        im = ax.scatter(wtd_yearly[ix]['manual_pred_mean'], wtd_yearly[ix]['manual_pred_mean']-wtd_yearly[ix]['manual_median'],
                c=wtd_yearly[ix]['ba_removed-%'],vmin=0, vmax=1, zorder=2)
        ax.set_title(wtd_yearly[ix]['site'].values[0], fontweight='bold')
        model = OLS(wtd_yearly[ix]['manual_pred_mean'].values - wtd_yearly[ix]['manual_median'].values,
                    pd.DataFrame({#'constant': wtd_yearly[ix]['manual_pred_mean']*0.0+1,
                                  'WTD_ctrl * ba-%': wtd_yearly[ix]['manual_pred_mean'] * wtd_yearly[ix]['ba_removed-%']}))
                                  # 'ba-%': wtd_yearly[ix]['ba_removed-%']}))
        result = model.fit()
        plot_lines(result.params, ax)
        print('id = ' + str(idx))
        print(result.summary())
        ax.annotate("$WTD_{diff} = $%.2f $WTD_{pred} * BA_{frac}$ \n$R^2 = $%.2f"
                      % (result.params[0], result.rsquared), (0.03, 0.82), xycoords='axes fraction')
    # set labels
    plt.setp(axes[-1, :], xlabel='Predicted reference $WTD_{pred}$ (m)')
    plt.setp(axes[:, 0], ylabel='Response to harvest, $WTD_{diff}$ (m)')

    plt.ylim([-0.1,0.5])
    plt.xlim([0,1])
    plt.tight_layout()
    fig.subplots_adjust(right=0.9)
    cbar_ax = fig.add_axes([0.92, 0.2, 0.02, 0.6])
    fig.colorbar(im, cax=cbar_ax,
                 label="Removed basal area as fraction, $BA_{frac}$ (-)")

    # All except Lintupirtti in same plot
    plt.figure(figsize=(5,4))
    ix = ((wtd_yearly['control'] == 0) & (wtd_yearly['id'] >= 1) & (wtd_yearly['post-harvest'] == 1) &
          np.isfinite(wtd_yearly['manual_pred_mean']) & np.isfinite(wtd_yearly['manual_median']))
    model = OLS(wtd_yearly[ix]['manual_pred_mean'].values - wtd_yearly[ix]['manual_median'].values,
                pd.DataFrame({#'constant': wtd_yearly[ix]['manual_pred_mean']*0.0+1,
                              'WTD_ctrl * ba-%': wtd_yearly[ix]['manual_pred_mean'] * wtd_yearly[ix]['ba_removed-%']}))
                              # 'ba-%': wtd_yearly[ix]['ba_removed-%']}))
    result = model.fit()
    plot_lines(result.params)
    print(result.summary())
    plt.scatter(wtd_yearly[ix]['manual_pred_mean'], wtd_yearly[ix]['manual_pred_mean']-wtd_yearly[ix]['manual_median'],
            c=wtd_yearly[ix]['ba_removed-%'],vmin=0, vmax=1, zorder=2)
    plt.annotate("$WTD_{diff} = $%.2f $WTD_{pred} * BA_{frac}$ \n$R^2 = $%.2f"
                  % (result.params[0], result.rsquared), (0.03, 0.83), xycoords='axes fraction')
    plt.ylim([-0.1,0.5])
    plt.xlim([0,1])
    plt.xlabel('Predicted reference $WTD_{pred}$ (m)')
    plt.ylabel('Response to harvest, $WTD_{diff}$ (m)')
    # plt.title('All except Lintupirtti')
    plt.colorbar(label="Removed basal area as fraction, $BA_{frac}$ (-)")
    plt.tight_layout()

    # def plot_lines(p):
    #     ba = np.linspace(0,1,6)
    #     x = np.linspace(0,1,2)
    #     for b in ba:
    #         y = p[0] + p[1] * x + p[2] * b * x
    #         # y = p[0] * x + p[1] * b * x
    #         plt.plot(x,y,'-', color=cmap(b), zorder=1)

    # plt.figure()
    # ix = ((wtd_yearly['control'] == 0) & (wtd_yearly['id'] >= 1)  &
    #       np.isfinite(wtd_yearly['manual_pred_mean']) & np.isfinite(wtd_yearly['manual_median']))
    # plt.scatter(wtd_yearly[ix]['manual_pred_mean'], wtd_yearly[ix]['manual_median'],
    #             c=wtd_yearly[ix]['ba_removed-%'],vmin=0, vmax=1, zorder=2)
    # model = OLS(wtd_yearly[ix]['manual_median'].values,
    #             pd.DataFrame({'constant': wtd_yearly[ix]['manual_pred_mean']*0.0+1,
    #                           'WTD_ctrl': wtd_yearly[ix]['manual_pred_mean'],
    #                           'WTD_ctrl * ba-%': wtd_yearly[ix]['manual_pred_mean'] * wtd_yearly[ix]['ba_removed-%']}))
    #                           # 'ba-%': wtd_yearly[ix]['ba_removed-%']}))
    # result = model.fit()
    # plot_lines(result.params)
    # print(result.summary())
    # plt.annotate("$WTD = $%.2f$WTD_{pred} $%+.2f $WTD_{pred} * BA$%+.2f\n$R^2 = $%.2f"
    #              % (result.params[1], result.params[2], result.params[0], result.rsquared), (0.02, 0.85), xycoords='axes fraction')
    # plt.ylim([0,1])
    # plt.xlim([0,1])
    # plt.colorbar()

    # plt.figure(figsize=(12,8))
    # for idx in range(6):
    #     if idx == 0:
    #         ax=plt.subplot(2,3,idx+1)
    #     else:
    #         plt.subplot(2,3,idx+1,sharex=ax,sharey=ax)
    #     ix = ((wtd_yearly['control'] == 0) & (wtd_yearly['id'] == idx) &
    #           np.isfinite(wtd_yearly['manual_pred_mean']) & np.isfinite(wtd_yearly['manual_median']))
    #     plt.title(wtd_yearly[ix]['site'].values[0])
    #     model = OLS(wtd_yearly[ix]['manual_median'].values,
    #                 pd.DataFrame({'constant': wtd_yearly[ix]['manual_pred_mean']*0.0+1,
    #                               'WTD_ctrl': wtd_yearly[ix]['manual_pred_mean'],
    #                               'WTD_ctrl * ba-%': wtd_yearly[ix]['manual_pred_mean'] * wtd_yearly[ix]['ba_removed-%']}))
    #                               # 'ba-%': wtd_yearly[ix]['ba_removed-%']}))
    #     result = model.fit()
    #     plot_lines(result.params)
    #     print('id = ' + str(idx))
    #     print(result.summary())
    #     plt.scatter(wtd_yearly[ix]['manual_pred_mean'], wtd_yearly[ix]['manual_median'],
    #             c=wtd_yearly[ix]['ba_removed-%'],vmin=0, vmax=1, zorder=2)
    #     plt.annotate("$WTD = $%.2f$WTD_{pred} $%+.2f $WTD_{pred} * BA$%+.2f\n$R^2 = $%.2f"
    #                   % (result.params[1], result.params[2], result.params[0], result.rsquared), (0.02, 0.85), xycoords='axes fraction')
    # # plt.colorbar()
    # plt.ylim([0,1])
    # plt.xlim([0,1])
    # plt.tight_layout()