# -*- coding: utf-8 -*-
"""
PARAMETERS

@author: slauniai & khaahti
"""
import pathlib
import time

def parameters(folder=''):

    pgen = {'description': 'testcase',  # description written in result file
            'start_date': '1995-01-01',
            'end_date': '2025-12-31',
            'spinup_end': '1995-12-31',
            'dt': 86400.0,
            'spatial_cpy': True,  # if False uses parameters from cpy['state']
            # else needs cf.dat, hc.dat, LAI_decid.dat, LAI_spruce.dat, LAI_pine.dat, (cmask.dat)
            'spatial_soil': True,  # if False uses soil_id, ditch_depth, ditch_spacing from psp
            # else needs soil_id.dat, ditch_depth.dat, ditch_spacing.dat
            'spatial_forcing': True,  # if False uses forcing from forcing file with pgen['forcing_id'] and cpy['loc']
            # else needs Ncoord.dat, Ecoord.dat, forcing_id.dat
            'stand_development': False,  # if True stand characteristics change annually accoording to input,
            # give input (cf.dat, hc.dat, LAI_decid.dat, LAI_spruce.dat, LAI_pine.dat) for each year in columns
            'gis_folder': str(pathlib.Path(folder+r'/parameters')),
            'forcing_file': str(pathlib.Path(folder+r'/forcing/Weather_id_[forcing_id].csv')),
            'forcing_id': 0,  # used if spatial_forcing == False
            #'ncf_file': folder + time.strftime('%Y%m%d%H%M') + r'.nc',
            'ncf_file': str(pathlib.Path(folder+r'/results/')) + time.strftime('%Y%m%d%H%M') + r'.nc',
            'results_folder': str(pathlib.Path(folder+r'/results/')),
            'save_interval': 366, # interval for writing results to file (decreases need for memory during computation)
            'variables':[ # list of output variables (rows can be commented out if not all variables are of interest)
                    ['parameters_lai_conif', 'leaf area index of conifers [m2 m-2]'],
                    ['parameters_lai_decid_max', 'leaf area index of decidious trees [m2 m-2]'],
                    # ['parameters_hc', 'canopy height [m]'],
                    ['parameters_cf', 'canopy closure [-]'],
                    # ['parameters_soil_id', 'soil class index'],
                    ['parameters_ditch_depth', 'ditch depth [m]'],
                    ['parameters_ditch_spacing', 'ditch spacing [m]'],
                    ['parameters_lat', 'latitude [deg]'],
                    ['parameters_lon', 'longitude [deg]'],
                    #['forcing_air_temperature', 'air temperature [degC]'],
                    #['forcing_precipitation', 'precipitation [mm d-1]'],
                    #['forcing_vapor_pressure_deficit', 'vapor pressure deficit [kPa]'],
                    #['forcing_global_radiation', 'global radiation [Wm-2]'],
                    #['forcing_CO2', 'CO2 mixing ratio [ppm]'],
                    # ['forcing_wind_speed','wind speed [m s-1]'],
                    # ['forcing_snow_depth', 'snow depth [cm]'],
                    # ['soil_pond_storage', 'pond storage [m]'],
                    ['soil_ground_water_level', 'ground water level [m]'],
                    # ['soil_infiltration', 'infiltration [mm d-1]'],
                    # ['soil_surface_runoff', 'surface runoff [mm d-1]'],
                    #['soil_evaporation', 'evaporation from soil surface [mm d-1]'],
                    # ['soil_drainage', 'subsurface drainage [mm d-1]'],
                    # ['soil_moisture_top', 'volumetric water content of moss layer [m3 m-3]'],
                    # ['soil_rootzone_moisture', 'volumetric water content of rootzone [m3 m-3]'],
                    # ['soil_water_closure', 'soil water balance error [mm d-1]'],
                    # ['soil_transpiration_limitation', 'transpiration limitation [-]'],
                    # ['canopy_interception', 'canopy interception [mm d-1]'],
                    #['canopy_evaporation', 'evaporation from interception storage [mm d-1]'],
                    #['canopy_transpiration','transpiration [mm d-1]'],
                    # ['canopy_stomatal_conductance','stomatal conductance [m s-1]'],
                    # ['canopy_gs_raw','stomatal conductance [m s-1]'],
                    # ['canopy_throughfall', 'throughfall to moss or snow [mm d-1]'],
                    #['canopy_snow_water_equivalent', 'snow water equivalent [mm]'],
                    # ['canopy_water_closure', 'canopy water balance error [mm d-1]'],
                    # ['canopy_phenostate', 'canopy phenological state [-]'],
                    #['canopy_leaf_area_index', 'canopy leaf area index [m2 m-2]'],
                    #['canopy_degree_day_sum', 'sum of degree days [degC]'],
                    ]
             }

    # canopygrid
    pcpy = {'flow' : {  # flow field
                     'zmeas': 2.0,
                     'zground': 0.5,
                     'zo_ground': 0.01
                     },
            'interc': {  # interception
                        'wmax': 1.5,  # storage capacity for rain (mm/LAI)
                        'wmaxsnow': 4.5,  # storage capacity for snow (mm/LAI)
                        'c_snow': 1.0,  #correctioon for snow fall (-)
                        'Tmin': 0.0,  # temperature below which all is snow [degC]
                        'Tmax': 2.0,  # temperature above which all is water [degC]- Koivusalo & Kokkonen 2002
                        },
            'snow': {  # degree-day snow model
                    'kmelt': 2.5,  # melt coefficient in open (mm/d)
                    'kfreeze': 0.5,  # freezing coefficient (mm/d)
                    'r': 0.05  # maximum fraction of liquid in snow (-)
                    },
            'physpara': {
                        # canopy conductance
                        'amax': 10.0, # maximum photosynthetic rate (umolm-2(leaf)s-1)
                        'g1_conif': 2.1, # stomatal parameter, conifers
                        'g1_decid': 3.5, # stomatal parameter, deciduous
                        'q50': 50.0, # light response parameter (Wm-2)
                        'kp': 0.6, # light attenuation parameter (-)
                        # soil evaporation
                        'gsoil': 1e-2 # soil surface conductance if soil is fully wet (m/s)
                        },
            'phenopara': {
                        # seasonal cycle of physiology: smax [degC], tau[d], xo[degC],fmin[-](residual photocapasity)
                        'smax': 18.5, # degC
                        'tau': 13.0, # days
                        'xo': -4.0, # degC
                        'fmin': 0.05, # minimum photosynthetic capacity in winter (-)
                        # deciduos phenology
                        'lai_decid_min': 0.1, # minimum relative LAI (-)
                        'ddo': 45.0, # degree-days for bud-burst (5degC threshold)
                        'ddur': 23.0, # duration of leaf development (days)
                        'sdl': 9.0, # daylength for senescence start (h)
                        'sdur': 30.0, # duration of leaf senescence (days),
                         },
            'state': {  # following properties are used if spatial_cpy == False
                       'lai_conif': 3.5, # conifer 1-sided LAI (m2 m-2)
                       'lai_decid_max': 0.5, # maximum annual deciduous 1-sided LAI (m2 m-2)
                       'hc': 16.0, # canopy height (m)
                       'cf': 0.6, # canopy closure fraction (-)
                       #initial state of canopy storage [mm] and snow water equivalent [mm]
                       'w': 0.0, # canopy storage mm
                       'swe': 0.0, # snow water equivalent mm
                       },
            'loc': {  # following coordinates used if spatial_forcing == False
                    'lat': 61.4,  # decimal degrees
                    'lon': 23.4
                    }
            }

    # soil profile
    psp = {
            # soil profile, following properties are used if spatial_soil = False
            'soil_id': 2.0,
            # drainage parameters, following properties are used if spatial_soil = False
            'ditch_depth': 1.0,  # ditch depth [m]
            'ditch_spacing': 45.0,  # ditch spacing [m]
            'ditch_width': 1.0,  # ditch width [m]
            # organic (moss) layer
            'org_depth': 0.04, # depth of organic top layer (m)
            'org_poros': 0.9, # porosity (-)
            'org_fc': 0.3, # field capacity (-)
            'org_rw': 0.24, # critical vol. moisture content (-) for decreasing phase in Ef
            'pond_storage_max': 0.05,  # maximum pond depth [m]
            # initial states
            'ground_water_level': -0.2,  # groundwater depth [m]
            'org_sat': 1.0, # organic top layer saturation ratio (-)
            'pond_storage': 0.0  # initial pond depth at surface [m]
            }

    return pgen, pcpy, psp

def peat_soilprofiles():
    """
    Properties of soil profiles (Estonia + Latvia).
    Note z is elevation of lower boundary of layer (soil surface at 0.0),
    e.g. z = [-0.05, -0.15] means first layer thickness is 5 cm and second 10 cm.
    """
    peatp = {'soil_1': {'soil_id': 1,
            'z': [-0.3, -0.6, -1.2, -3.0],
            'soil_types': ['Peat1', 'Peat2', 'Coarse', 'Coarse'],
            'pF': {'ThetaS': [0.8969999999999999, 0.874, 0.41, 0.41],
                   'ThetaR': [0.13266666666666668, 0.19800000000000004, 0.05, 0.05],
                   'alpha': [0.08733333333333333, 0.03, 0.039, 0.039],
                   'n': [1.4436666666666664, 1.4910000000000003, 1.4, 1.4]},
            'saturated_conductivity': [0.0007800000000000002, 9.2e-06, 0.0001, 0.0001]},
 'soil_2': {'soil_id': 2,
            'z': [-0.3, -0.6, -1.2, -3.0],
            'soil_types': ['Peat1', 'Peat2', 'Peat3', 'Peat4'],
            'pF': {'ThetaS': [0.8969999999999999, 0.874, 0.874, 0.874],
                   'ThetaR': [0.13266666666666668, 0.19800000000000004, 0.198, 0.198],
                   'alpha': [0.08733333333333333, 0.03, 0.03, 0.03],
                   'n': [1.4436666666666664, 1.4910000000000003, 1.491, 1.491]},
            'saturated_conductivity': [0.0007800000000000002,
                                       9.2e-06,
                                       2.097e-06,
                                       1.8850000000000003e-07]},
 'soil_3': {'soil_id': 3,
            'z': [-0.3, -0.6, -1.2, -3.0],
            'soil_types': ['Peat1', 'Peat2', 'Fine', 'Fine'],
            'pF': {'ThetaS': [0.8969999999999999, 0.874, 0.5, 0.5],
                   'ThetaR': [0.13266666666666668, 0.19800000000000004, 0.07, 0.07],
                   'alpha': [0.08733333333333333, 0.03, 0.018, 0.018],
                   'n': [1.4436666666666664, 1.4910000000000003, 1.16, 1.16]},
            'saturated_conductivity': [0.0007800000000000002, 9.2e-06, 1e-06, 1e-06]},
 'soil_4': {'soil_id': 4,
            'z': [-0.3, -0.6, -1.2, -3.0],
            'soil_types': ['Coarse', 'Medium', 'Medium', 'Medium'],
            'pF': {'ThetaS': [0.41, 0.43, 0.43, 0.43],
                   'ThetaR': [0.05, 0.05, 0.05, 0.05],
                   'alpha': [0.039, 0.024, 0.024, 0.024],
                   'n': [1.4, 1.2, 1.2, 1.2]},
            'saturated_conductivity': [0.0001, 1e-05, 1e-05, 1e-05]},
 'soil_5': {'soil_id': 5,
            'z': [-0.3, -0.6, -1.2, -3.0],
            'soil_types': ['Medium', 'Medium', 'Medium', 'Medium'],
            'pF': {'ThetaS': [0.43, 0.43, 0.43, 0.43],
                   'ThetaR': [0.05, 0.05, 0.05, 0.05],
                   'alpha': [0.024, 0.024, 0.024, 0.024],
                   'n': [1.2, 1.2, 1.2, 1.2]},
            'saturated_conductivity': [1e-05, 1e-05, 1e-05, 1e-05]},
 'soil_6': {'soil_id': 6,
            'z': [-0.3, -0.6, -1.2, -3.0],
            'soil_types': ['Coarse', 'Coarse', 'Coarse', 'Coarse'],
            'pF': {'ThetaS': [0.41, 0.41, 0.41, 0.41],
                   'ThetaR': [0.05, 0.05, 0.05, 0.05],
                   'alpha': [0.039, 0.039, 0.039, 0.039],
                   'n': [1.4, 1.4, 1.4, 1.4]},
            'saturated_conductivity': [0.0001, 0.0001, 0.0001, 0.0001]},
 'soil_7': {'soil_id': 7,
            'z': [-0.3, -0.6, -1.2, -3.0],
            'soil_types': ['Coarse', 'Coarse', 'Medium', 'Medium'],
            'pF': {'ThetaS': [0.41, 0.41, 0.43, 0.43],
                   'ThetaR': [0.05, 0.05, 0.05, 0.05],
                   'alpha': [0.039, 0.039, 0.024, 0.024],
                   'n': [1.4, 1.4, 1.2, 1.2]},
            'saturated_conductivity': [0.0001, 0.0001, 1e-05, 1e-05]},
 'soil_8': {'soil_id': 8,
            'z': [-0.3, -0.6, -1.2, -3.0],
            'soil_types': ['Peat1', 'Peat2', 'Medium', 'Medium'],
            'pF': {'ThetaS': [0.8969999999999999, 0.874, 0.43, 0.43],
                   'ThetaR': [0.13266666666666668, 0.19800000000000004, 0.05, 0.05],
                   'alpha': [0.08733333333333333, 0.03, 0.024, 0.024],
                   'n': [1.4436666666666664, 1.4910000000000003, 1.2, 1.2]},
            'saturated_conductivity': [0.0007800000000000002, 9.2e-06, 1e-05, 1e-05]},
 'soil_9': {'soil_id': 9,
            'z': [-0.3, -0.6, -1.2, -3.0],
            'soil_types': ['Peat1', 'Coarse', 'Coarse', 'Coarse'],
            'pF': {'ThetaS': [0.8969999999999999, 0.41, 0.41, 0.41],
                   'ThetaR': [0.13266666666666668, 0.05, 0.05, 0.05],
                   'alpha': [0.08733333333333333, 0.039, 0.039, 0.039],
                   'n': [1.4436666666666664, 1.4, 1.4, 1.4]},
            'saturated_conductivity': [0.0007800000000000002, 0.0001, 0.0001, 0.0001]},
 'soil_10': {'soil_id': 10,
             'z': [-0.3, -0.6, -1.2, -3.0],
             'soil_types': ['Coarse', 'Coarse', 'Coarse', 'Medium'],
             'pF': {'ThetaS': [0.41, 0.41, 0.41, 0.43],
                    'ThetaR': [0.05, 0.05, 0.05, 0.05],
                    'alpha': [0.039, 0.039, 0.039, 0.024],
                    'n': [1.4, 1.4, 1.4, 1.2]},
             'saturated_conductivity': [0.0001, 0.0001, 0.0001, 1e-05]},
 'soil_11': {'soil_id': 11,
             'z': [-0.3, -0.6, -1.2, -3.0],
             'soil_types': ['Fine', 'Fine', 'Fine', 'Fine'],
             'pF': {'ThetaS': [0.5, 0.5, 0.5, 0.5],
                    'ThetaR': [0.07, 0.07, 0.07, 0.07],
                    'alpha': [0.018, 0.018, 0.018, 0.018],
                    'n': [1.16, 1.16, 1.16, 1.16]},
             'saturated_conductivity': [1e-06, 1e-06, 1e-06, 1e-06]},
 'soil_21': {'soil_id': 21,
             'z': [-0.3, -0.6, -1.2, -3.0],
             'soil_types': ['Peat1', 'Peat2', 'Peat3', 'Peat4'],
             'pF': {'ThetaS': [0.8969999999999999, 0.874, 0.874, 0.874],
                    'ThetaR': [0.13266666666666668, 0.19800000000000004, 0.198, 0.198],
                    'alpha': [0.08733333333333333, 0.03, 0.03, 0.03],
                    'n': [1.4436666666666664, 1.4910000000000003, 1.491, 1.491]},
             'saturated_conductivity': [0.0007800000000000002,
                                        9.2e-06,
                                        2.097e-06,
                                        1.8850000000000003e-07]},
 'soil_22': {'soil_id': 22,
             'z': [-0.3, -0.6, -1.2, -3.0],
             'soil_types': ['Peat1', 'Peat2', 'Peat3', 'Medium'],
             'pF': {'ThetaS': [0.8969999999999999, 0.874, 0.874, 0.43],
                    'ThetaR': [0.13266666666666668, 0.19800000000000004, 0.198, 0.05],
                    'alpha': [0.08733333333333333, 0.03, 0.03, 0.024],
                    'n': [1.4436666666666664, 1.4910000000000003, 1.491, 1.2]},
             'saturated_conductivity': [0.0007800000000000002, 9.2e-06, 2.097e-06, 1e-05]},
 'soil_23': {'soil_id': 23,
             'z': [-0.3, -0.6, -1.2, -3.0],
             'soil_types': ['Peat1', 'Peat2', 'Medium', 'Medium'],
             'pF': {'ThetaS': [0.8969999999999999, 0.874, 0.43, 0.43],
                    'ThetaR': [0.13266666666666668, 0.19800000000000004, 0.05, 0.05],
                    'alpha': [0.08733333333333333, 0.03, 0.024, 0.024],
                    'n': [1.4436666666666664, 1.4910000000000003, 1.2, 1.2]},
             'saturated_conductivity': [0.0007800000000000002, 9.2e-06, 1e-05, 1e-05]},
 'soil_24': {'soil_id': 24,
             'z': [-0.3, -0.6, -1.2, -3.0],
             'soil_types': ['Peat1', 'Peat2', 'Coarse', 'Coarse'],
             'pF': {'ThetaS': [0.8969999999999999, 0.874, 0.41, 0.41],
                    'ThetaR': [0.13266666666666668, 0.19800000000000004, 0.05, 0.05],
                    'alpha': [0.08733333333333333, 0.03, 0.039, 0.039],
                    'n': [1.4436666666666664, 1.4910000000000003, 1.4, 1.4]},
             'saturated_conductivity': [0.0007800000000000002, 9.2e-06, 0.0001, 0.0001]},
 'soil_25': {'soil_id': 25,
             'z': [-0.3, -0.6, -1.2, -3.0],
             'soil_types': ['Coarse', 'Coarse', 'Coarse', 'Coarse'],
             'pF': {'ThetaS': [0.41, 0.41, 0.41, 0.41],
                    'ThetaR': [0.05, 0.05, 0.05, 0.05],
                    'alpha': [0.039, 0.039, 0.039, 0.039],
                    'n': [1.4, 1.4, 1.4, 1.4]},
             'saturated_conductivity': [0.0001, 0.0001, 0.0001, 0.0001]},
 'soil_26': {'soil_id': 26,
             'z': [-0.3, -0.6, -1.2, -3.0],
             'soil_types': ['Peat1', 'Medium', 'Medium', 'Medium'],
             'pF': {'ThetaS': [0.8969999999999999, 0.43, 0.43, 0.43],
                    'ThetaR': [0.13266666666666668, 0.05, 0.05, 0.05],
                    'alpha': [0.08733333333333333, 0.024, 0.024, 0.024],
                    'n': [1.4436666666666664, 1.2, 1.2, 1.2]},
             'saturated_conductivity': [0.0007800000000000002, 1e-05, 1e-05, 1e-05]},
 'soil_27': {'soil_id': 27,
             'z': [-0.3, -0.6, -1.2, -3.0],
             'soil_types': ['Medium', 'Medium', 'Medium', 'Medium'],
             'pF': {'ThetaS': [0.43, 0.43, 0.43, 0.43],
                    'ThetaR': [0.05, 0.05, 0.05, 0.05],
                    'alpha': [0.024, 0.024, 0.024, 0.024],
                    'n': [1.2, 1.2, 1.2, 1.2]},
             'saturated_conductivity': [1e-05, 1e-05, 1e-05, 1e-05]}}
    return peatp
