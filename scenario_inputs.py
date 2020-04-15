# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 09:45:12 2020

@author: 03110850
"""

import pyreadr
import os
import pandas as pd
import matplotlib.pyplot as plt
from koordinaattimuunnos import koordGT
import numpy as np
from iotools import write_AsciiGrid

def create_inputs(fp_forcing,
                  fp_coords=r'scen_coords\coordinates_all.txt',
                  cf=[0.75, 0.65, 0.55, 0.45],
                  LAI_conif=[5.5, 3.5, 2., 1.5],
                  LAI_decid=[0., 0., 0., 0.],
                  hc=20.0, soil_id=2,
                  ditch_depth=0.5, ditch_spacing=40.0):

    # output directory
    fdir_output = '_'.join((os.path.basename(fp_forcing)).split('.')[:-1])
    os.makedirs(fdir_output, exist_ok=True)

    print('Inputs will be saved to ' + fdir_output)

    # read weather data
    data = pyreadr.read_r(fp_forcing)

    data = data['dat']

    data['PAR'] = data['PAR'] * 1e6 / (24*3600) / 4.56  # mol/m2/day to W/m2

    # rday is the day since 1980-01-01 (365 d calendar)
    year = 1980. + (data['rday'] - 1 - ((data['rday'] - 1) % 365))/365

    data['doy'] = (data['rday'] - 1) % 365 + 1

    data['date'] = pd.to_datetime(year * 1000 + data['doy'], format='%Y%j')

    coords_data = sorted(set(data['id']))

    coords = pd.read_csv(fp_coords, sep=',', header='infer', encoding = 'ISO-8859-1')

    inputs=coords[coords['ID'].isin(coords_data)]

    inputs['N'], inputs['E'] = koordGT(lev_aste=inputs['y'],
                                       pit_aste=inputs['x'],
                                       desimals=2)

    # plt.plot(inputs['E'], inputs['N'],'o')

    # write forcing file for each grid point
    fn = os.path.join(fdir_output,r'forcing\weather_id_[forcing_id].csv')
    os.makedirs(os.path.join(fdir_output, r'forcing'), exist_ok=True)
    for idx in inputs['ID']:
        print(idx)
        data[data['id']==idx][['date','doy','TAir','Precip','PAR', 'VPD']].to_csv(
            fn.replace('[forcing_id]',str(int(idx))), index=False)

    input_para = {}

    info = ['ncols         1\n',
            'nrows         50000\n',
            'xllcorner     0\n',
            'yllcorner     0\n',
            'cellsize      16\n',
            'NODATA_value  -9999\n']

    keys = ['Ncoord', 'Ecoord', 'forcing_id',
            'hc', 'ditch_depth', 'ditch_spacing', 'soil_id',
            'cf', 'LAI_conif', 'LAI_decid']

    imin = 0
    imax = len(inputs['E'])
    jmax = len(cf)

    for key in keys:
        input_para[key] = np.ones([imax,jmax])

    for j in range(jmax):
        input_para['Ncoord'][:,j] = inputs['N'].values[imin:imin+imax]
        input_para['Ecoord'][:,j] = inputs['E'].values[imin:imin+imax]
        input_para['forcing_id'][:,j] = inputs['ID'].values[imin:imin+imax]

    input_para['ditch_spacing'][:,:] = ditch_spacing
    input_para['ditch_depth'][:,:] = ditch_depth
    input_para['soil_id'][:,:] = soil_id
    input_para['hc'][:,:] = hc

    for j in range(jmax):
        input_para['cf'][:,j] = cf[j]
        input_para['LAI_conif'][:,j] = LAI_conif[j]
        input_para['LAI_decid'][:,j] = LAI_decid[j]

    fpath = os.path.join(fdir_output,r'parameters')
    os.makedirs(fpath, exist_ok=True)
    for key, value in input_para.items():
        if key in ['soil_id', 'forcing_id']:
            write_AsciiGrid(os.path.join(fpath, key + '.dat'), value, info, fmt='%d')
        else:
            write_AsciiGrid(os.path.join(fpath, key + '.dat'), value, info, fmt='%.2f')

if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', help='forcing data filepath', type=str)
    parser.add_argument('--coords', help='coordinates filepath', type=str)

    args = parser.parse_args()

    create_inputs(fp_forcing=args.filepath,fp_coords=args.coords)
