# -*- coding: utf-8 -*-
"""
Created on Thu Mar 19 09:45:12 2020

@author: 03110850
"""

import pyreadr
import pandas as pd
import matplotlib.pyplot as plt
from koordinaattimuunnos import koordGT

data = pyreadr.read_r(
    r'C:\Users\03110850\Desktop\sompa temp\SOMPAsites\Forcing\from_Mikko\CurrClim.rdata')

data = data['dat']

data['PAR'] = data['PAR'] * 1e6 / (24*3600)
data['Rg'] = data['PAR'] / 4.56 / 0.45

year = 1980. + (data['rday'] - 1 - ((data['rday'] - 1) % 365))/365

data['doy'] = (data['rday'] - 1) % 365 + 1

data['date'] = pd.to_datetime(year * 1000 + data['doy'], format='%Y%j')

coords_data = sorted(set(data['id']))

coords = pd.read_csv(
    r'C:\Users\03110850\Desktop\sompa temp\SOMPAsites\Forcing\from_Mikko\coordinates.txt',
    sep=',', header='infer', encoding = 'ISO-8859-1')

inputs=coords[coords['ID'].isin(coords_data)]

inputs['N'], inputs['E'] = koordGT(lev_aste=inputs['y'],
                                   pit_aste=inputs['x'],
                                   desimals=2)

plt.plot(inputs['E'], inputs['N'],'o')

fn = r'scenario_data/forcing/weather_id_[forcing_id].csv'
for idx in inputs['ID']:
    data[data['id']==idx][['date','doy','TAir','Precip','PAR','Rg','VPD']].to_csv(
        fn.replace('[forcing_id]',str(int(idx))), index=False)
