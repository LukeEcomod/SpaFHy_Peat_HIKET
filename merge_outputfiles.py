# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 11:15:57 2020

@author: 03110850
"""
import xarray as xr
import os
import pandas as pd

outputfiles = ['results/sompa_data_2014-2019.nc','results/sompa_data_2014-2020.nc']

merged_outputfile = 'results/test.nc'

def to_montly_merge(outputfiles, merged_outputfile):

    results = []
    names = []

    for outputfile in outputfiles:
        ds = xr.open_dataset(outputfile)
        # My workaround: this does not add the time dimension to the timeless variables
        ds_withtime = ds.drop([ var for var in ds.variables if not 'date' in ds[var].dims ])
        ds_timeless = ds.drop([ var for var in ds.variables if 'date' in ds[var].dims ])
        ds = xr.merge([ds_timeless, ds_withtime.resample(date='1M').mean()])
        results.append(ds)
        names.append((os.path.basename(outputfile)).split('.')[0])

    results = xr.concat([result for result in results], pd.Index(names,name='scenario'))

    results.to_netcdf(merged_outputfile)

to_montly_merge(outputfiles, merged_outputfile)