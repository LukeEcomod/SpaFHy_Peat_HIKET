# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 12:58:54 2018

@author: khaahti
"""
import numpy as np
eps = np.finfo(float).eps
from scipy.interpolate import interp1d

apply_vectorized = np.vectorize(lambda f, x: f(x))

class SoilGrid(object):
    """
    Soil profile model for gridded uses (inputs as arrays)
    Simulates moss/organic layer with interception and evaporation,
    soil water storage, drainage to ditches and pond storage on top of soil.
    """
    def __init__(self, spara):
        """
        Initializes SoilProfile:
        Args:
            spara (dict):
                # scipy interpolation functions describing soil behavior
                'wtso_to_gwl'
                'gwl_to_wsto'
                'gwl_to_Ksat'
                # organic (moss) layer
                'org_depth': depth of organic top layer (m)
                'org_poros': porosity (-)
                'org_fc': field capacity (-)
                'org_rw': critical vol. moisture content (-) for decreasing phase in Ef
                'pond_storage_max': maximum pond depth [m]
                # drainage parameters
                'ditch_depth':ditch depth [m]
                'ditch_spacing': ditch spacing [m]
                'ditch_width': ditch width [m]
                # initial states
                'ground_water_level': groundwater depth [m]
                'org_sat': organic top layer saturation ratio (-)
                'pond_storage': initial pond depth at surface [m]
        """
        # top layer is interception storage, which capacity is depends on its depth [m]
        # and field capacity
        self.dz_top = spara['org_depth']  # depth, m3 m-3
        self.poros_top = spara['org_poros']  # porosity, m3 m-3
        self.fc_top = spara['org_fc']  # field capacity m3 m-3
        self.rw_top = spara['org_rw']  # ree parameter m3 m-3
        self.Wsto_top_max = self.fc_top * self.dz_top  # maximum storage m
        self.soiltype = spara['soiltype']

        # pond storage
        self.h_pond_max = spara['pond_storage_max']

        # interpolated functions for soil column ground water dpeth vs. water storage
        self.wsto_to_gwl = spara['wtso_to_gwl']
        self.gwl_to_wsto = spara['gwl_to_wsto']
        self.gwl_to_Ksat = spara['gwl_to_Ksat']

        self.Wsto_max = np.full_like(self.h_pond_max,0.0)
        for key, value in self.gwl_to_wsto.items():
            self.Wsto_max[self.soiltype == key] = value(0.0)

        self.gwl_to_rootmoist = spara['gwl_to_rootmoist']

        # drainage parameters
        self.ditch_depth = spara['ditch_depth']
        self.ditch_spacing = spara['ditch_spacing']
        self.depth_id = spara['depth_id']
        self.Ksat = np.full_like(self.h_pond_max, 0.0)

        # initialize state
        # soil profile
        self.gwl = spara['ground_water_level']
        self.Wsto = np.full_like(self.gwl, 0.0)
        self.rootmoist = np.full_like(self.gwl, 0.0)
        self.root_fc0 = np.full_like(self.gwl, 0.0)
        self.root_fc1 = np.full_like(self.gwl, 0.0)
        self.root_wp = np.full_like(self.gwl, 0.0)
        for key, value in self.gwl_to_wsto.items():
            self.Wsto[self.soiltype == key] = value(self.gwl[self.soiltype == key])
        for key, value in self.gwl_to_rootmoist.items():
            self.rootmoist[self.soiltype == key] = value(self.gwl[self.soiltype == key])
            self.root_fc0[self.soiltype == key] = value(-0.7 - 0.1)
            self.root_fc1[self.soiltype == key] = value(-1.2 - 0.1)
            self.root_wp[self.soiltype == key] = value(-150.0 - 0.1)

        self.Rew = 1.0

        # toplayer storage and relative conductance for evaporation
        self.Wsto_top = self.Wsto_top_max * spara['org_sat']

        self.Wliq_top = self.poros_top * self.Wsto_top / self.Wsto_top_max
        self.Ree = np.maximum(0.0, np.minimum(
                0.98*self.Wliq_top / self.rw_top, 1.0)) # relative evaporation rate (-)
        # pond storage
        self.h_pond = spara['pond_storage']

    def watbal(self, dt=1, rr=0.0, tr=0.0, evap=0.0):

        r""" Solves soil water storage in column assuming hydrostatic equilibrium.

        Args:
            dt (float): solution timestep [s]
            rr (float/array): potential infiltration [m]
            tr (float/array): transpiration from root zone [m]
            evap (float/array): evaporation from top layer [m]
        Returns:
            results (dict)

        """

        state0 = self.Wsto + self.Wsto_top + self.h_pond + rr
        rr += self.h_pond
        self.h_pond = 0.0

        # top layer interception & water balance
        interc = np.maximum(0.0, (self.Wsto_top_max - self.Wsto_top))\
                    * (1.0 - np.exp(-(rr / self.Wsto_top_max)))
        rr -= interc  # to soil profile
        self.Wsto_top += interc
        evap = np.minimum(evap, self.Wsto_top)
        self.Wsto_top -= evap

        # drainage [m]
        for i in range(len(self.gwl_to_Ksat)):
            self.Ksat[self.depth_id == i] = self.gwl_to_Ksat[i](self.gwl[self.depth_id == i])  # [m s-1]
        Hdr = np.minimum(np.maximum(0, self.gwl + self.ditch_depth), self.ditch_depth)
        drain = 4 * self.Ksat * Hdr**2 / (self.ditch_spacing**2) * dt  # [m]

        """ soil column water balance """
        # net flow to soil profile during dt
        Qin = rr - drain - tr
        # airvolume available in soil profile after previous time step
        Airvol = np.maximum(0.0, self.Wsto_max - self.Wsto)

        Qin = np.minimum(Qin, Airvol)
        self.Wsto += Qin

        infiltration = Qin + drain + tr

        # inflow excess
        exfil = rr - infiltration
        # first fill top layer
        # water that can fit in top layer
        to_top_layer = np.minimum(exfil, self.Wsto_top_max - self.Wsto_top)
        self.Wsto_top += to_top_layer
        # then pond storage
        to_pond = np.minimum(exfil - to_top_layer, self.h_pond_max - self.h_pond)
        self.h_pond += to_pond
        # and route remaining to surface runoff
        surface_runoff = exfil - to_top_layer - to_pond

        """ update state """
        # soil profile
        # ground water depth corresponding to Wsto
        for key, value in self.wsto_to_gwl.items():
            self.gwl[self.soiltype == key] = value(self.Wsto[self.soiltype == key])

        # organic top layer; maximum that can be hold is Fc
        self.Wliq_top = self.fc_top * self.Wsto_top / self.Wsto_top_max
        self.Ree = np.maximum(0.0, np.minimum(0.98*self.Wliq_top / self.rw_top, 1.0))

        for key, value in self.gwl_to_rootmoist.items():
            self.rootmoist[self.soiltype == key] = value(self.gwl[self.soiltype == key])

        # Koivusalo et al. 2008 HESS without wet side limit
        self.Rew = np.where(self.rootmoist > self.root_fc1,
                            np.minimum(1.0, 0.5*(1 + (self.rootmoist - self.root_fc1)/(self.root_fc0 - self.root_fc1))),
                            np.maximum(0.0, 0.5*(self.rootmoist - self.root_wp)/(self.root_fc1 - self.root_wp))
                            )

        # mass balance error [m]
        mbe = (state0  - self.Wsto_top - self.Wsto - self.h_pond -
               drain - tr - surface_runoff - evap)

        results = {
                'pond_storage': self.h_pond,  # [m]
                'ground_water_level': self.gwl,  # [m]
                'infiltration': infiltration * 1e3,  # [mm d-1]
                'surface_runoff': surface_runoff * 1e3,  # [mm d-1]
                'evaporation': evap * 1e3,  # [mm d-1]
                'drainage': drain * 1e3,  # [mm d-1]
                'moisture_top': self.Wliq_top,  # [m3 m-3]
                'water_closure':  mbe,  # [mm d-1]
                'transpiration_limitation': self.Rew,  # [-]
                'rootzone_moisture': self.rootmoist,  # [m3 m-3]
                }

        return results

def gwl_Wsto(z, pF, grid_step=0.01, root=False):
    r""" Forms interpolated function for soil column ground water dpeth, < 0 [m], as a
    function of water storage [m] and vice versa

    Args:
        pF (dict of arrays):
            'ThetaS' saturated water content [m\ :sup:`3` m\ :sup:`-3`\ ]
            'ThetaR' residual water content [m\ :sup:`3` m\ :sup:`-3`\ ]
            'alpha' air entry suction [cm\ :sup:`-1`]
            'n' pore size distribution [-]
        dz (np.arrays): soil conpartment thichness, node in center [m]
    Returns:
        (dict):
            'to_gwl': interpolated function for gwl(Wsto)
            'to_wsto': interpolated function for Wsto(gwl)
    """
    # finer grid (J-P's code)
    z_fine= np.arange(0, min(z), -grid_step)
    dz_fine = z_fine*0.0 + grid_step
    z_mid_fine = dz_fine / 2 - np.cumsum(dz_fine)

    # pF parameter arrays for finer grid
    ix = np.zeros(len(z_fine))
    for depth in z:
        # below makes sure floating point precision doesnt mess with the ix
        ix += np.where((z_fine < depth) & ~np.isclose(z_fine, depth, atol=1e-9), 1, 0)
    pF_fine={}
    for key in pF.keys():
        pp = []
        for i in range(len(z_fine)):
            pp.append(pF[key][int(ix[i])])
        pF_fine.update({key: np.array(pp)})

    # --------- connection between gwl and water storage------------
    # gwl from ground surface gwl = 0 to gwl = -5
    gwl = np.arange(0.0, -5, -grid_step)
    gwl[-1] = -150.
    # solve water storage corresponding to gwls
    Wsto = [sum(h_to_cellmoist(pF_fine, g - z_mid_fine, dz_fine) * dz_fine) for g in gwl]

    if root:
        Wsto = Wsto/sum(dz_fine)

    # interpolate functions
    WstoToGwl = interp1d(np.array(Wsto), np.array(gwl), fill_value='extrapolate')
    GwlToWsto = interp1d(np.array(gwl), np.array(Wsto), fill_value='extrapolate')

    del gwl, Wsto

    if root:
        return {'to_rootmoist': GwlToWsto}
    else:
        return {'to_gwl': WstoToGwl, 'to_wsto': GwlToWsto}


def h_to_cellmoist(pF, h, dz):
    r""" Cell moisture based on vanGenuchten-Mualem soil water retention model.
    Partly saturated cells calculated as thickness weigthed average of
    saturated and unsaturated parts.

    Args:
        pF (dict):
            'ThetaS' (array): saturated water content [m\ :sup:`3` m\ :sup:`-3`\ ]
            'ThetaR' (array): residual water content [m\ :sup:`3` m\ :sup:`-3`\ ]
            'alpha' (array): air entry suction [cm\ :sup:`-1`]
            'n' (array): pore size distribution [-]
        h (array): pressure head [m]
        dz (array): soil conpartment thichness, node in center [m]
    Returns:
        theta (array): volumetric water content of cell [m\ :sup:`3` m\ :sup:`-3`\ ]

    Kersti Haahti, Luke 8/1/2018
    """

    # water retention parameters
    Ts = np.array(pF['ThetaS'])
    Tr = np.array(pF['ThetaR'])
    alfa = np.array(pF['alpha'])
    n = np.array(pF['n'])
    m = 1.0 - np.divide(1.0, n)

    # moisture based on cell center head
    x = np.minimum(h, 0)
    theta = Tr + (Ts - Tr) / (1 + abs(alfa * 100 * x)**n)**m

    # correct moisture of partly saturated cells
    ix = np.where(abs(h) < dz/2)
    if len(Ts) == 1:
        ixx = 0
    else:
        ixx = ix
    # moisture of unsaturated part
    x[ix] = -(dz[ix]/2 - h[ix]) / 2
    theta[ix] = Tr[ixx] + (Ts[ixx] - Tr[ixx]) / (1 + abs(alfa[ixx] * 100 * x[ix])**n[ixx])**m[ixx]
    # total moisture as weighted average
    theta[ix] = (theta[ix] * (dz[ix]/2 - h[ix]) + Ts[ixx] * (dz[ix]/2 + h[ix])) / (dz[ix])

    return theta

def gwl_Ksat(z, Ksat, DitchDepth, grid_step=0.01):
    r""" Forms interpolated function for hydraulic conductivity of saturated layer 
    above ditch bottom vs gwl
    """
    # gwl from soil surface gwl = 0 to gwl = -150 (finer resolution until ditch bottom)
    gwl = np.arange(0.0, - DitchDepth - 0.1, - grid_step)
    gwl[-1] = -150

    # solve water storage corresponding to gwls
    Ka = [Ksat_layer(z, Ksat, g, DitchDepth) for g in gwl]

    # interpolate functions
    GwlToKsat = interp1d(np.array(gwl), np.array(Ka), fill_value='extrapolate')

    return GwlToKsat

def Ksat_layer(z, Ksat, gwl, DitchDepth):
    r""" Calculates hydraulic conductivity of saturated layer 
    above ditch bottom.

    Args:
       dz (array): soil layer thichnesses, node in center [m]
       Ksat (array): horizontal saturated hydr. cond. of soil layers [m s-1]
       gwl (float): ground water level below soil surface, <0 [m]
       DitchDepth (float): depth of drainage ditch bottom, >0 [m]

    Returns:
       Ka (array): hydraulic conductivity of saturated layer above ditch bottom [m s-1]
    """
    z = np.array(z)
    dz = abs(z)
    dz[1:] = z[:-1] - z[1:]

    # each layers thickness above ditch bottom [m] (zero when layer completely below ditch bottom)
    dz_dd = np.minimum(dz, np.maximum(DitchDepth + z + dz, 0))
    # each layers saturated thickness above ditch bottom [m]
    dz_sat = np.minimum(np.maximum(gwl - np.maximum(-DitchDepth, z), 0), dz_dd)
    if sum(dz_sat) > 0:
        # transmissivity of layers  [m2 s-1]
        Trans = Ksat * dz_sat
        # effective hydraulic conductivity ms-1
        Ka = sum(Trans) / sum(dz_sat) 
    else:
        Ka = 0.0

    return Ka

nan_function = interp1d(np.array([np.nan, np.nan]),
                        np.array([np.nan, np.nan]),
                        fill_value='extrapolate')