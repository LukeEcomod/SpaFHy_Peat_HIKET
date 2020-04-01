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

data = pyreadr.read_r(
    r'C:\Users\03110850\Desktop\sompa temp\SOMPAsites\Forcing\from_Mikko\CanESM2.rcp26.rdata')

data = data['dat']

data = data[data['rday'] <= 10950]

data['PAR'] = data['PAR'] * 1e6 / (24*3600)
data['Rg'] = data['PAR'] / 4.56 / 0.45

year = 1980. + (data['rday'] - 1 - ((data['rday'] - 1) % 365))/365

data['doy'] = (data['rday'] - 1) % 365 + 1

data['date'] = pd.to_datetime(year * 1000 + data['doy'], format='%Y%j')

coords_data = sorted(set(data['id']))

coords = pd.read_csv(
    r'C:\Users\03110850\Desktop\sompa temp\SOMPAsites\Forcing\from_Mikko\coordinates_FI.txt',
    sep=',', header='infer', encoding = 'ISO-8859-1')

inputs=coords[coords['ID'].isin(coords_data)]

inputs['N'], inputs['E'] = koordGT(lev_aste=inputs['y'],
                                   pit_aste=inputs['x'],
                                   desimals=2)

plt.plot(inputs['E'], inputs['N'],'o')

# fn = r'scenario_data2/forcing/weather_id_[forcing_id].csv'
# for idx in inputs['ID']:
#     data[data['id']==idx][['date','doy','TAir','Precip','PAR','Rg','VPD']].to_csv(
#         fn.replace('[forcing_id]',str(int(idx))), index=False)

from iotools import write_AsciiGrid

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
jmax = 4

for key in keys:
    input_para[key] = np.ones([imax,jmax])

for j in range(jmax):
    input_para['Ncoord'][:,j] = inputs['N'].values[imin:imin+imax]
    input_para['Ecoord'][:,j] = inputs['E'].values[imin:imin+imax]
    input_para['forcing_id'][:,j] = inputs['ID'].values[imin:imin+imax]

input_para['ditch_spacing'][:,:] = 40.0
input_para['ditch_depth'][:,:] = 0.5
input_para['soil_id'][:,:] = 2
input_para['hc'][:,:] = 20.0

cf = [0.75, 0.65, 0.55, 0.45]
LAI_conif = [5.5, 3.5, 2., 1.5]
LAI_decid = [0., 0., 0., 0.]

for j in range(jmax):
    input_para['cf'][:,j] = cf[j]
    input_para['LAI_conif'][:,j] = LAI_conif[j]
    input_para['LAI_decid'][:,j] = LAI_decid[j]

fpath = r'scenario_data2\parameters'
for key, value in input_para.items():
    if key in ['soil_id', 'forcing_id']:
        write_AsciiGrid(os.path.join(fpath, key + '.dat'), value, info, fmt='%d')
    else:
        write_AsciiGrid(os.path.join(fpath, key + '.dat'), value, info, fmt='%.2f')
