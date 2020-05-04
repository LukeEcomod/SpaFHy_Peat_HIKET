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

def pF_fig():
    """
    Water retention curves fitted to measurements of peat water
    retention by Päivänen.

    Ref: Päivänen, J. (1973), Hydraulic conductivity and water
    retention in peat soils, Acta For. Fenn., 129, 1–70.
    """

    from scipy.optimize import curve_fit
    from matplotlib.ticker import ScalarFormatter, FormatStrFormatter

    def fit_pF(head, watcont, fig=False, color='lightgrey', nolabel=False):
        """
        Fits vanGenuchten-Mualem soil water retention model to given
        head and water content data.
        Args:
            head (list): pressure head [m] (as positive values)
            watcont (list in list): volumetric water content
                correstponding to head [%]
        Returns:
            pF (list in list): water retention parameters for watcont
                0. 'ThetaS' saturated water content [m\ :sup:`3` m\ :sup:`-3`\ ]
                1. 'ThetaR' residual water content [m\ :sup:`3` m\ :sup:`-3`\ ]
                2. 'alpha' air entry suction [cm\ :sup:`-1`]
                3. 'n' pore size distribution [-]
        """

        head = np.array(head)
        head = head * 10  # kPa -> cm
        vg_ini = (0.88, 0.09, 0.03, 1.3)
        van_g = lambda h, *p:   p[1] + (p[0] - p[1]) / (1. + (p[2] * h) **p[3]) **(1. - 1. / p[3])
        vgen_all = []
        alpha_all = []

        for k in range(0, len(watcont)):
            Wcont = np.array(watcont[k])
            ix = np.where(Wcont >= 0)
            Wcont[ix] = Wcont[ix] / 100  # % -> fraction
            try:
                vgen, _ = curve_fit(van_g, head[ix], Wcont[ix], p0=vg_ini)
                if nolabel:
                    label='_nolegend_'
                else:
                    label=r'$\theta_s$=%.2f, $\theta_r$=%.3f, $\alpha$=%.2f, $\beta$=%.2f' % tuple(vgen)
            except RuntimeError:
                vgen = [-1, -1, -1, -1]
                label='No fit!'
            vgen_all.append(vgen)
            alpha_all.append(vgen[2])
            if fig:
                if nolabel:
                    plt.semilogy(Wcont[ix], head[ix] / 100, '.',color = color)
                xx = np.logspace(0, 4.2, 100)
                plt.semilogy(van_g(xx, *vgen), xx / 100., '-',color = color,
                             label=label,linewidth=2.0)

        if fig:
            plt.xlabel(r'Moisture content (m$^3$ m$^{-3}$)')
            plt.ylabel('Pressure head (m)', labelpad=-5)
            plt.ylim(xx[0] / 100, xx[-1] / 100)
            plt.gcf().axes[0].yaxis.set_major_formatter(FormatStrFormatter('$-$%.3g'))
            plt.xlim(0.0, 1.0)
            plt.legend(loc = "lower left",frameon=False, borderpad=0.0)

        return vgen_all

    # heads [kPa]
    head = [0.0001, 1, 3.2, 10, 20, 60, 100, 200, 500, 1000, 1500]

    # volumetric water content measurements corresponding to heads for different peat types [%]
    watcont_sphagnum = [[93.3, 73, 43.4, 25.4, 22.3, 19.9, 17.1, 13.7, 10.8, 8.3, -999],
               [94.5, 59.8, 42.4, 27.1, 24.7, 23.2, 19.4, 17.2, 13.8, 10.4, -999],
               [92.9, 70, 47.9, 31.5, 27.2, 21.9, 21.4, 20.4, 14.6, 12.9, -999],
               [94.6, 77.8, 53.9, 34.5, 25.3, 21.3, 18.3, 15.3, 13.4, 9.4, -999],
               [92.7, 89.4, 66.2, 45.3, 35.2, 26.4, 24, 23.2, 18.5, 18.7, -999],
               [92, 75, 53.7, 40.8, 37.3, -999, 29.5, 27.1, -999, 18, -999],
               [94, 91.3, 66.1, 44.8, 31.2, 28.4, 25.2, -999, 20.8, 18, -999],
               [94.3, 91.4, 80, 48.5, -999, 33.1, 24.5, 23, -999, 12.8, 9.5],
               [92, 65.6, 50.4, 36.4, 34.9, 28.5, 25.4, 22.4, 16.4, 15.4, -999],
               [93.9, 87.2, 74.5, 53.4, -999, 29.5, 25.7, 21.1, -999, 15.4, 11.9],
               [92.2, 76.8, 50.7, 32.1, 31.4, 28.5, 25.9, 22, 17.6, 14.1, -999],
               [90.9, 80.4, 62, 44.1, 38.2, 28.1, 26.5, 23.7, 22.9, 15.5, -999],
               [91.6, 87.4, 76.4, 53.2, -999, 32.9, 29.9, 26.1, -999, 14.9, 13.5],
               [92.9, 82.2, 62, 45.4, -999, 25.6, 23.4, 19.6, -999, 13.7, 11.2],
               [89.7, 86.4, 69.2, 51.6, 45.8, 37.7, 36.1, -999, 30.1, 27.5, -999],
               [91.6, 89.4, 78.5, 54.6, 38.3, 30.7, 28, 24.7, 20.6, 17.5, -999],
               [90.1, 80.1, 61.3, 41.6, -999, 27.2, 24.6, 20.7, -999, 13.1, 11.3],
               [90.4, 76.5, 61.6, 46.4, 40.8, 33.2, 29.6, 27, 23.1, 17.5, -999],
               [90, 88.6, 75, 63.3, -999, 38.7, 32.3, 29.1, 21, 19, -999],
               [90.7, 84.8, 73.7, 60.5, -999, 38.4, 32.9, 28.4, -999, 20.4, 17.2],
               [91.1, 88.2, 77.8, 61.6, -999, 35, 30.4, 30.2, -999, 20.5, 17.9],
               [89.3, 84, 71, 55.4, 49.2, 38.7, 31.4, 27.7, 25.7, 24.1, -999],
               [90, 89.6, 83.7, 64.2, 52.1, 39.3, 29.8, 26.6, 23.6, 20.3, -999],
               [89.3, 86.4, 77, 65.8, 56, 41.3, 29, 25.1, 20.5, 17.6, -999],
               [89.2, 87.5, 81, 70.8, -999, 37.3, 31.1, 30.8, -999, 16.2, 14.8],
               [85.5, 84.9, 79.8, 68.4, -999, 46.6, 40.9, 35.1, -999, 25.4, 20.2]]

    watcont_sedge = [[94.3, 68, 47.9, 35.5, 22, 18.4, 16.7, 12.6, 7.9, 6.3, -999],
               [91.7, 82.9, 61.8, 35.9, 31.7, 25.2, 23.4, 19.2, 17.3, 14.4, -999],
               [90.6, 86.2, 56.4, 36.4, 33.4, 29.8, 26.8, 23.5, 20.2, 16.4, -999],
               [89.7, 85, 74.5, 53.4, 36, 29, 24.7, 22.1, 17.6, 14.7, -999],
               [87.3, 85.4, 77.8, 64, 41.4, 28.8, 23.4, 22.7, 21.9, 17, -999],
               [89.3, 86.5, 80.7, 52.5, 45.6, 35.4, 32, 25.1, 20.6, 18.4, -999],
               [91, 89.9, 84.7, 60, -999, 33.8, 27.2, 29.3, -999, 17.2, 12.9],
               [89.3, 87.2, 79.2, 59.8, 53.8, 46.3, 41.5, 36.1, 32, 28.6, -999],
               [87.2, 77.7, 76.2, 56.4, -999, 33.3, 31.6, 28.8, -999, 17.3, 15.7],
               [84.2, 83.7, 76, 56.6, 44.2, 41.2, 37.4, -999, 36.3, 32.6, -999],
               [83.9, 80.7, 78.8, 67.1, 54.7, 41, 37.4, 35.2, 29.3, 27, -999],
               [87.2, 84.3, 81.6, 71.7, 55.1, 43.4, 36.8, 33.4, 29, 27.3, -999],
               [82.4, 81.8, 70.5, 57.5, 50.1, 48.2, 44.2, 42.5, 41.9, 32.4, -999],
               [81.8, 77.7, 75.1, 64.7, 56.8, 43.4, 40, 32.6, 27.1, 27, -999]]

    watcont_woody = [[90.3, 79.4, 69.8, 54.6, 42.4, -999, 29.8, 27.1, -999, 23.3, -999],
               [90.5, 80.4, 65.8, 47.8, 36.3, 33.2, 27.8, 26.2, 21.4, 21.3, -999],
               [88.4, 82, 69.6, 53.9, 43.3, 35.3, 31.9, 27.8, 24, 23.4, -999],
               [86.7, 83.1, 69.6, 57.9, 49.3, 45.2, 43.6, -999, 36.4, 31.5, -999],
               [84.6, 82.1, 76, 58.3, 49.4, 39.9, 36.2, 30.7, 26, 26.3, -999],
               [83.3, 80, 70.8, 59.9, 50.9, -999, 40.5, 33.4, 30.3, 29.4, -999],
               [82.2, 81.3, 79.4, 65.5, -999, 44.6, 42.6, 38.7, -999, 25.7, 21.3]]

    plt.figure()
    fit_pF(head, watcont_sphagnum, fig=True, nolabel=True)
    fit_pF(head, [watcont_sphagnum[1]], fig=True, color='blue')
    fit_pF(head, [np.average(watcont_sphagnum, axis=0, weights=~np.isin(watcont_sphagnum, -999)*1)],
           fig=True, color='red')
    plt.title('Sphagnum')

    head2=head[:-1]
    watcont_sedge2 = [watcont_s[:-1] for watcont_s in watcont_sedge]

    plt.figure()
    fit_pF(head, watcont_sedge, fig=True, nolabel=True)
    fit_pF(head, [watcont_sedge[0]], fig=True, color='blue')
    fit_pF(head2, [np.average(watcont_sedge2, axis=0, weights=~np.isin(watcont_sedge2, -999)*1)],
           fig=True, color='red')
    plt.title('Carex')

    plt.figure()
    fit_pF(head, watcont_woody, fig=True, nolabel=True)
    fit_pF(head, [watcont_woody[1]], fig=True, color='blue')
    fit_pF(head, [np.average(watcont_woody, axis=0, weights=~np.isin(watcont_woody, -999)*1)],
           fig=True, color='red')
    plt.title('Woody')

def modmeas_comparison(results, wtd):

    from mpl_toolkits.axes_grid1.inset_locator import inset_axes

    wtd_manual = wtd_manual = wtd[(np.isfinite(wtd['manual_pred_mean'])) & (np.isfinite(wtd['manual_median']))]
    wtd_manual = wtd_manual[['date','site', 'plot', 'manual_min', 'manual_max', 'manual_median',
                             'manual_pred_min', 'manual_pred_max','manual_pred_mean']]
    wtd_manual['id'] = np.arange(len(wtd_manual))

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

    marker = ['*','P','^','s','D','o']
    cmap=plt.cm.get_cmap('viridis')
    years = list(set(wtd_yearly.index))
    years.sort()

# %%
    pos = (-0.25,1.02)
    # plt.figure(figsize=(13,8))
    fig, axes = plt.subplots(3, 4, figsize=(13,8))
    ax = plt.subplot(3,4,1)
    plt.plot([0,2],[0,2],':k')
    for key, value in info.items():
        ix = ((wtd_yearly['site'] == key) & (wtd_yearly['plot'].isin(value['control_plots'])))
        plt.plot(wtd_yearly[ix]['manual_median'].mean(),wtd_yearly[ix]['mod_control'].mean(),
                 marker=marker[value['id']], color='k', linestyle='')
    plt.setp(plt.gca().axes.get_xticklabels(), visible=False)
    plt.ylim([0,1.1])
    plt.xlim([0,1.1])
    plt.annotate('(a)', pos, xycoords='axes fraction', fontsize=12, fontweight='bold')
    plt.title('Reference plots\nWTD (m) all years')
    plt.ylabel('Modelled')
    plt.subplot(3,4,2, sharex=ax, sharey=ax)
    plt.plot([0,2],[0,2],':k')
    for key, value in info.items():
        ix = ((wtd_yearly['site'] == key) & ~(wtd_yearly['plot'].isin(value['control_plots'])) & (wtd_yearly.index < value['harvest']))
        plt.plot(wtd_yearly[ix]['manual_median'].mean(),wtd_yearly[ix]['mod_control'].mean(),
                 marker=marker[value['id']], color='k', linestyle='')
    plt.setp(plt.gca().axes.get_xticklabels(), visible=False)
    plt.setp(plt.gca().axes.get_yticklabels(), visible=False)
    plt.title('Treated plots\nPre-harvest WTD (m)')
    plt.subplot(3,4,3, sharex=ax, sharey=ax)
    plt.plot([0,2],[0,2],':k')
    for key, value in info.items():
        ix = ((wtd_yearly['site'] == key) & ~(wtd_yearly['plot'].isin(value['control_plots'])) & (wtd_yearly.index >= value['harvest']))
        plt.plot(wtd_yearly[ix]['manual_median'].mean(),wtd_yearly[ix]['mod_treated'].mean(),
                 marker=marker[value['id']], color='k', linestyle='')
    plt.setp(plt.gca().axes.get_xticklabels(), visible=False)
    plt.setp(plt.gca().axes.get_yticklabels(), visible=False)
    plt.title('Treated plots\nPost-harvest WTD (m)')
    ax2 = plt.subplot(3,4,4)
    plt.plot([-1,2],[-1,2],':k')
    for key, value in info.items():
        ix = ((wtd_yearly['site'] == key) & ~(wtd_yearly['plot'].isin(value['control_plots'])) & (wtd_yearly.index >= value['harvest']))
        plt.plot(wtd_yearly[ix]['manual_pred_mean'].mean() - wtd_yearly[ix]['manual_median'].mean(),
                 wtd_yearly[ix]['mod_control'].mean() - wtd_yearly[ix]['mod_treated'].mean(),
                 marker=marker[value['id']], color='k', linestyle='', label=key)
    plt.setp(plt.gca().axes.get_xticklabels(), visible=False)
    plt.ylim([-0.1,0.6])
    plt.xlim([-0.1,0.6])
    plt.xticks([0,.2,.4,.6])
    plt.yticks([0,.2,.4,.6])
    plt.title('Treated plots\nWTD response (m)')
    plt.legend(bbox_to_anchor=(1.,0.5), loc="center left", frameon=False, borderpad=0.0)

    plt.subplot(3,4,5, sharex=ax, sharey=ax)
    plt.annotate('(b)', pos, xycoords='axes fraction', fontsize=12, fontweight='bold')
    plt.plot([0,2],[0,2],':k')
    for key, value in info.items():
        for year in years:
            ix = ((wtd_yearly['site'] == key) & (wtd_yearly['plot'].isin(value['control_plots'])) & (wtd_yearly.index == year))
            plt.plot(wtd_yearly[ix]['manual_median'].mean(),wtd_yearly[ix]['mod_control'].mean(),
                     marker=marker[value['id']], color=cmap((year-min(years))/5), linestyle='')
    plt.setp(plt.gca().axes.get_xticklabels(), visible=False)
    plt.ylabel('Modelled')
    plt.subplot(3,4,6, sharex=ax, sharey=ax)
    plt.plot([0,2],[0,2],':k')
    for key, value in info.items():
        for year in years:
            ix = ((wtd_yearly['site'] == key) & ~(wtd_yearly['plot'].isin(value['control_plots'])) & (wtd_yearly.index == year) & (wtd_yearly.index < value['harvest']))
            plt.plot(wtd_yearly[ix]['manual_median'].mean(),wtd_yearly[ix]['mod_control'].mean(),
                     marker=marker[value['id']], color=cmap((year-min(years))/5), linestyle='')
    plt.setp(plt.gca().axes.get_xticklabels(), visible=False)
    plt.setp(plt.gca().axes.get_yticklabels(), visible=False)
    plt.subplot(3,4,7, sharex=ax, sharey=ax)
    plt.plot([0,2],[0,2],':k')
    for key, value in info.items():
        for year in years:
            ix = ((wtd_yearly['site'] == key) & ~(wtd_yearly['plot'].isin(value['control_plots'])) & (wtd_yearly.index == year) & (wtd_yearly.index >= value['harvest']))
            plt.plot(wtd_yearly[ix]['manual_median'].mean(),wtd_yearly[ix]['mod_treated'].mean(),
                     marker=marker[value['id']], color=cmap((year-min(years))/5), linestyle='')
    plt.setp(plt.gca().axes.get_xticklabels(), visible=False)
    plt.setp(plt.gca().axes.get_yticklabels(), visible=False)
    axx=plt.subplot(3,4,8, sharex=ax2, sharey=ax2)
    plt.plot([-1,2],[-1,2],':k')
    for key, value in info.items():
        for year in years:
            ix = ((wtd_yearly['site'] == key) & ~(wtd_yearly['plot'].isin(value['control_plots'])) & (wtd_yearly.index == year) & (wtd_yearly.index >= value['harvest']))
            plt.plot(wtd_yearly[ix]['manual_pred_mean'].mean() - wtd_yearly[ix]['manual_median'].mean(),
                     wtd_yearly[ix]['mod_control'].mean() - wtd_yearly[ix]['mod_treated'].mean(),
                     marker=marker[value['id']], color=cmap((year-min(years))/5), linestyle='')
    plt.setp(plt.gca().axes.get_xticklabels(), visible=False)
    plt.scatter([-1,-1],[-1,-1],c=[-1,-1],cmap=plt.cm.get_cmap('viridis', 6),vmin=2014,vmax=2019)
    axins = inset_axes(axx,
                       width="5%", height="100%",
                       loc='lower left',
                       bbox_to_anchor=(1.07, 0., 1, 1),
                       bbox_transform=axx.transAxes,
                       borderpad=0)
    plt.colorbar(cax=axins)
    plt.clim(2013.5, 2019.5)

    plt.subplot(3,4,9, sharex=ax, sharey=ax)
    plt.annotate('(c)', pos, xycoords='axes fraction', fontsize=12, fontweight='bold')
    plt.plot([0,2],[0,2],':k')
    for key, value in info.items():
        for plot in set(wtd_yearly[wtd_yearly['site'] == key]['plot']):
            if plot in value['control_plots']:
                ix = ((wtd_yearly['site'] == key) & (wtd_yearly['plot'] == plot))
                plt.plot(wtd_yearly[ix]['manual_median'].mean(),wtd_yearly[ix]['mod_control'].mean(),
                         marker=marker[value['id']], color=cmap(value['ba'][plot-1]/30), linestyle='')
    plt.ylabel('Modelled')
    plt.xlabel('Measured')
    plt.subplot(3,4,10, sharex=ax, sharey=ax)
    plt.plot([0,2],[0,2],':k')
    for key, value in info.items():
        for plot in set(wtd_yearly[wtd_yearly['site'] == key]['plot']):
            if plot not in value['control_plots']:
                ix = ((wtd_yearly['site'] == key) & (wtd_yearly['plot'] == plot) & (wtd_yearly.index < value['harvest']))
                plt.plot(wtd_yearly[ix]['manual_median'].mean(),wtd_yearly[ix]['mod_control'].mean(),
                         marker=marker[value['id']], color=cmap(value['ba_old'][plot-1]/30), linestyle='')
    plt.setp(plt.gca().axes.get_yticklabels(), visible=False)
    plt.xlabel('Measured')
    plt.subplot(3,4,11, sharex=ax, sharey=ax)
    plt.plot([0,2],[0,2],':k')
    for key, value in info.items():
        for plot in set(wtd_yearly[wtd_yearly['site'] == key]['plot']):
            if plot not in value['control_plots']:
                ix = ((wtd_yearly['site'] == key) & (wtd_yearly['plot'] == plot) & (wtd_yearly.index >= value['harvest']))
                plt.plot(wtd_yearly[ix]['manual_median'].mean(),wtd_yearly[ix]['mod_treated'].mean(),
                         marker=marker[value['id']], color=cmap(value['ba'][plot-1]/30), linestyle='')
    plt.setp(plt.gca().axes.get_yticklabels(), visible=False)
    plt.xlabel('Measured')
    axx = plt.subplot(3,4,12, sharex=ax2, sharey=ax2)
    plt.plot([-1,2],[-1,2],':k')
    for key, value in info.items():
        for plot in set(wtd_yearly[wtd_yearly['site'] == key]['plot']):
            if plot not in value['control_plots']:
                ix = ((wtd_yearly['site'] == key) & (wtd_yearly['plot'] == plot) & (wtd_yearly.index >= value['harvest']))
                plt.plot(wtd_yearly[ix]['manual_pred_mean'].mean() - wtd_yearly[ix]['manual_median'].mean(),
                         wtd_yearly[ix]['mod_control'].mean() - wtd_yearly[ix]['mod_treated'].mean(),
                         marker=marker[value['id']], color=cmap(value['ba'][plot-1]/30), linestyle='')
    plt.xlabel('Measured')
    plt.scatter([-1,-1],[-1,-1],c=[-1,-1],vmin=0,vmax=30)
    axins = inset_axes(axx,
                   width="5%", height="100%",
                   loc='lower left',
                   bbox_to_anchor=(1.07, 0., 1, 1),
                   bbox_transform=axx.transAxes,
                   borderpad=0)
    plt.colorbar(cax=axins,label='Basal area (m$^2$ ha$^{-1}$)', extend='max')
    plt.tight_layout(w_pad=1)
