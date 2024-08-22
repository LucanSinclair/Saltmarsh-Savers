import os
import datacube
import numpy as np
import pandas as pd
import xarray as xr
import datetime as dt
import matplotlib.pyplot as plt

import sys
sys.path.insert(1, '../Tools/')
from dea_tools.temporal import xr_phenology, temporal_statistics
from dea_tools.datahandling import load_ard
from dea_tools.bandindices import calculate_indices
from dea_tools.plotting import display_map, rgb
from dea_tools.dask import create_local_dask_cluster

import os
import datacube
import numpy as np
import pandas as pd
import xarray as xr
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns


import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Create local dask cluster to improve data load time
client = create_local_dask_cluster(return_client=True)

dc = datacube.Datacube(app='Vegetation_phenology')

# Define area of interest
lat_min, lat_max = -16.864381, -16.864535
lon_min, lon_max = 145.757198, 145.757532

# Set the range of dates for the analysis
time_range = ('2016-04-19', '2023-05-13')

# Set the vegetation proxy to use
veg_proxy = 'NDVI'



display_map(x=(lon_min, lon_max), y=(lat_min, lat_max))


# Create a reusable query
query = {
    'x': (lon_min, lon_max),
    'y': (lat_min, lat_max),
    'time': time_range,
    'measurements': ['nbart_red', 'nbart_green', 'nbart_blue', 'nbart_nir_1'],
    'resolution': (-20, 20),
    'output_crs': 'epsg:6933',
    'group_by':'solar_day'
}

# Load available data from Sentinel-2
ds = load_ard(
    dc=dc,
    products=['ga_s2am_ard_3', 'ga_s2bm_ard_3'],
    cloud_mask='s2cloudless',
    min_gooddata=0.9,
    **query,
)

# Shut down Dask client now that we have loaded the data we need
client.close()

# Preview data
ds


# Calculate the chosen vegetation proxy index and add it to the loaded data set
ds = calculate_indices(ds, index=veg_proxy, collection='ga_s2_3')


ds.NDVI.median(['x', 'y']).plot.line('b-^', figsize=(11,4))
plt.title('Zonal median of vegetation timeseries');


resample_period='1M'
window=4

veg_smooth=ds[veg_proxy].resample(time=resample_period).median().rolling(time=window, min_periods=1).mean()



veg_smooth_1D = veg_smooth.mean(['x', 'y'])
veg_smooth_1D.plot.line('b-^', figsize=(15,5))
_max=veg_smooth_1D.max()
_min=veg_smooth_1D.min()

for year in range(2016, 2024):
    plt.vlines(np.datetime64(str(year)+'-01-01'), ymin=_min, ymax=_max)

plt.title(veg_proxy+' time-series, year start/ends marked with vertical lines')
plt.ylabel(veg_proxy)




# Create local dask cluster to improve data load time
client = create_local_dask_cluster(return_client=True)
dc = datacube.Datacube(app='Vegetation_phenology')
# Define area of interest
lat_min, lat_max = -16.830871, -16.830720
lon_min, lon_max = 145.732532, 145.732577

# Set the range of dates for the analysis
time_range = ('2016-04-19', '2023-04-19')

# Set the vegetation proxy to use
veg_proxy = 'NDVI'
display_map(x=(lon_min, lon_max), y=(lat_min, lat_max))
# Create a reusable query
query = {
    'x': (lon_min, lon_max),
    'y': (lat_min, lat_max),
    'time': time_range,
    'measurements': ['nbart_red', 'nbart_green', 'nbart_blue', 'nbart_nir_1'],
    'resolution': (-20, 20),
    'output_crs': 'epsg:6933',
    'group_by':'solar_day'
}

# Load available data from Sentinel-2
ds = load_ard(
    dc=dc,
    products=['ga_s2am_ard_3', 'ga_s2bm_ard_3'],
    cloud_mask='s2cloudless',
    min_gooddata=0.9,
    **query,
)

# Shut down Dask client now that we have loaded the data we need
client.close()

# Preview data
ds

# Calculate the chosen vegetation proxy index and add it to the loaded data set
ds = calculate_indices(ds, index=veg_proxy, collection='ga_s2_3')

# Convert the xarray dataset to a pandas dataframe
df = ds[veg_proxy].to_dataframe().reset_index()

# Add a year column to the dataframe
df['year'] = pd.DatetimeIndex(df['time']).year

# Plot the annual trend line with seaborn
sns.set_style('whitegrid')
sns.lmplot(x='year', y=veg_proxy, data=df, height=6, aspect=2, ci=None)

# Add a title and labels to the plot
plt.title('Zonal median of vegetation timeseries with annual trend line')
plt.xlabel('Year')
plt.ylabel('NDVI')

# Save the plot as a .jpg file
plt.savefig('veg_timeseries.jpg')

# Save zonal median vegetation timeseries data to a CSV file
df = ds.NDVI.median(['x', 'y']).to_dataframe(name='NDVI')
df.to_csv('zonal_median_vegetation_timeseries.csv')



# Save zonal median vegetation timeseries data to a CSV file
df = ds.NDVI.median(['x', 'y']).to_dataframe(name='NDVI')
df.to_csv('zonal_median_vegetation_timeseries.csv')