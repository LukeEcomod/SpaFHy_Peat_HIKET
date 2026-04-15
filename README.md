# SpaFHy-Peat
SpaFHy version for gridded simulation of drained peatland forests (Leppä et al. 2020):

 - Canopy and mosslayer as in SpaFHy (https://github.com/LukeEcomod/SpaFHy_v1, Launiainen et al. 2019)
 - Soil water storage based on equilibrium state and Hooghoudt's drainage equation.

## How to use

### 1. Set up the environment

Create and activate the conda environment from the provided [environment.yml](environment.yml):

```bash
conda env create -f environment.yml
conda activate spafhy-peat
```

### 2. Prepare input data

Each run requires a folder with two subdirectories:

- `parameters/` — GIS raster grids (`.dat` files) defining the spatial domain:
  - `cf.dat`, `hc.dat` — canopy closure and height
  - `LAI_conif.dat`, `LAI_decid.dat` — leaf area indices
  - `soil_id.dat`, `ditch_depth.dat`, `ditch_spacing.dat` — soil and drainage parameters
  - `latitude.dat`, `longitude.dat`, `forcing_id.dat` — location and forcing assignment
- `forcing/` — meteorological time series in CSV format (`Weather_id_[forcing_id].csv`)

Example input data are provided under [example_inputs/](example_inputs/).

### 3. Configure model parameters

Edit [parameters_example.py](parameters_example.py) to set the simulation period and point to your input data.

### 4. Run the model

Open [demo.ipynb](demo.ipynb) for a complete example. The notebook runs the model, reads the results, and plots ground water level and canopy transpiration

**Command line** — for batch/HPC runs:

```bash
python run_regions.py <region>
# e.g.: python run_regions.py ALappi
```

Results are saved as a NetCDF4 file (`.nc`) in the folder defined by `results_folder` in the parameter file.

### References:
Leppä, K., Hökkä, H., Laiho, R., Launiainen, S., Lehtonen, A., Peltoniemi, M., Mäkipää, R., M., Saarinen, Sarkkola, S., and Nieminen, M. (2020). Selection cuttings as a tool to control water table level in boreal drained peatland forests. Front. Earth Sci., 8: 576510. https://doi.org/10.3389/feart.2020.576510. 

Launiainen, S., Guan, M., Salmivaara, A., and Kieloaho, A.-J. (2019) Modeling boreal forest evapotranspiration and water balance at stand and catchment scales: a spatial approach, Hydrol. Earth Syst. Sci., 23, 3457–3480, https://doi.org/10.5194/hess-23-3457-2019.
