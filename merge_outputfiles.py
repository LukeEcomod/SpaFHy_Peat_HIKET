# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 11:15:57 2020

@author: 03110850
"""
import xarray as xr
import os
import pandas as pd

def to_montly_merge(outputfiles, merged_outputfile):

    results = []
    names = []

    for outputfile in outputfiles:
        print(outputfile)
        ds = xr.open_dataset(outputfile)
        # My workaround: this does not add the time dimension to the timeless variables
        ds_withtime = ds.drop([ var for var in ds.variables if not 'date' in ds[var].dims ])
        ds_timeless = ds.drop([ var for var in ds.variables if 'date' in ds[var].dims ])
        ds = xr.merge([ds_timeless, ds_withtime.resample(date='1M').mean()])
        results.append(ds)
        names.append((os.path.basename(outputfile)).split('.')[0])

    results = xr.concat([result for result in results], pd.Index(names,name='scenario'))

    results.to_netcdf(merged_outputfile)

if __name__ == '__main__':

    outputfiles=[
        'results/CanESM2_rcp26_1981-2010.nc',
        'results/CanESM2_rcp26_2070-2099.nc',
        'results/CanESM2_rcp45_1981-2010.nc',
        'results/CanESM2_rcp45_2070-2099.nc',
        'results/CanESM2_rcp85_1981-2010.nc',
        'results/CanESM2_rcp85_2070-2099.nc',
        'results/CNRM_rcp26_1981-2010.nc',
        'results/CNRM_rcp26_2070-2099.nc',
        'results/CNRM_rcp45_1981-2010.nc',
        'results/CNRM_rcp45_2070-2099.nc',
        'results/CNRM_rcp85_1981-2010.nc',
        'results/CNRM_rcp85_2070-2099.nc',
        'results/GFDL_rcp26_1981-2010.nc',
        'results/GFDL_rcp26_2070-2099.nc',
        'results/GFDL_rcp45_1981-2010.nc',
        'results/GFDL_rcp45_2070-2099.nc',
        'results/GFDL_rcp85_1981-2010.nc',
        'results/GFDL_rcp85_2070-2099.nc',
        'results/HadGEM2_rcp26_1981-2010.nc',
        'results/HadGEM2_rcp26_2070-2099.nc',
        'results/HadGEM2_rcp45_1981-2010.nc',
        'results/HadGEM2_rcp45_2070-2099.nc',
        'results/HadGEM2_rcp85_1981-2010.nc',
        'results/HadGEM2_rcp85_2070-2099.nc',
        'results/MIROC_rcp26_1981-2010.nc',
        'results/MIROC_rcp26_2070-2099.nc',
        'results/MIROC_rcp45_1981-2010.nc',
        'results/MIROC_rcp45_2070-2099.nc',
        'results/MIROC_rcp85_1981-2010.nc',
        'results/MIROC_rcp85_2070-2099.nc',
        ]

    outputs = ['1981-2010', 'rcp26_2070-2099', 'rcp45_2070-2099', 'rcp85_2070-2099']

    for out in outputs:
        outfiles = [i for i in outputfiles if out in i]
        to_montly_merge(outfiles, 'results/monthly_' + out + '.nc')


