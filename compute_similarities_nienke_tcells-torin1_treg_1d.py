"""Compute similarities for Nienke's T-cell FACS data, one channel at a time.

Usage: compute_similarities_nienke_tcells-torin1_treg_1d.py [test]
"""

import sys
import os
import time
import collections
import itertools
import re
import numpy as np
import xarray as xr
import pandas as pd
from searchlight import *

CHANNELS = ['CD69', 'CD25', 'ICOS', 'GARP', 'TIGIT']

focus = np.array([0.61, 0.74, 0.63, 0.50, 0.73])
input_dirs = ['Normalized_Treg']

# If non-zero, only run 4 (1) samples or 20 (2) samples, to allow a short
# runtime for testing.
testing_mode = 0
testing_str = ''
if len(sys.argv) == 2 and sys.argv[1] in ('1', '2'):
    testing_mode = int(sys.argv[1])
    testing_str = '_test'

os.chdir(os.path.dirname(os.path.abspath(__file__)))

dirs = [os.path.join('INPUT', d) for d in input_dirs]
paths = [os.path.join(d, f) for d in dirs for f in os.listdir(d)
         if f.endswith('.csv')]

if testing_mode:
    num_samples = 4 if testing_mode == 1 else 20
    paths = sorted(paths)[:num_samples]
    paths.append('INPUT/Normalized_Treg/Export_CompNM39A1_NM54_Plate2_D10_Treg_Logicle_Transposed.csv')
    paths.append('INPUT/Normalized_Treg/Export_CompNM39A1_NM54_Plate2_D12_Treg_Logicle_Transposed.csv')
    
def path_to_key(path):
    match = re.search(r'/Normalized_(\w+)/Export_CompNM39A1_(\w+?)_T', path)
    (cell_type, sample_name) = match.groups()
    key = '%s/%s' % (cell_type, sample_name)
    return key

data = {}
start = time.time()
for p in paths:
    key = path_to_key(p)
    d = np.loadtxt(p, delimiter=',', ndmin=2)
    assert (d.shape[1] == len(CHANNELS) or d.shape[0] == 0), \
        'Wrong number of columns in %s' % p
    # We'll be processing single columns, so swapping the order here avoids a
    # copy in the main loop below.
    data[key] = d.copy('F')
print 'Time to load data:', time.time() - start, 's'

design = pd.read_csv('INPUT/TconTreg_Platemap_Jeremy.csv', dtype={'Plate': str})
design = design.rename(columns={'Experiment': 'experiment', 'Plate': 'plate',
                                'WellFlow': 'well'})
design.experiment = design.experiment.str.replace('_', '')
wanted = design[design.Compound == '10079;Torin1']
wanted = wanted[['experiment', 'plate', 'well']]
wanted_tuples = set(wanted.itertuples(index=False, name=None))
key_design_re = re.compile(r'/(NM\d\d)_Plate(\d)_([A-Z]\d\d)')

n_sets = len(data)
n_channels = len(CHANNELS)
keys = sorted(data.keys())
wanted_keys = set(k for k in keys
                  if key_design_re.search(k).groups() in wanted_tuples)

overlaps = xr.DataArray(np.zeros((n_channels, n_sets, n_sets)),
                        (('channel', CHANNELS), ('s2', keys), ('s1', keys)))
overlaps[:] = np.nan

start = time.time()
for c, cname in enumerate(overlaps.channel.values):
    for i2, s2 in enumerate(overlaps.coords['s2'].values):
        for i1, s1 in enumerate(overlaps.coords['s1'].values):
            # Only compute diagonal, and rows corresponding to wanted_keys.
            if i1 == i2 or s2 in wanted_keys:
                print '%s - %s,%s (%d x %d)' % (
                    cname, s2, s1, len(data[s2]), len(data[s1])
                )
                # The data arrays are in column-major order, so these slices are
                # contiguous which is required by searchlight. Otherwise we
                # would need to copy the data here, destroying performance.
                # expand_dims ensures we have a 2d array, also required by
                # searchlight.
                cc1 = np.expand_dims(data[s2][:,c], 1)
                cc2 = np.expand_dims(data[s1][:,c], 1)
                s = searchlight(cc1, cc2, focus[[c]])
                overlaps.loc[cname, s2, s1] = overlaps.loc[cname, s1, s2] = s
print 'Time to compute overlaps:', time.time() - start, 's'

similarities = xr.DataArray(np.empty_like(overlaps), coords=overlaps.coords)
similarities[:] = np.nan
for c in range(len(overlaps.channel)):
    diag = np.diag(overlaps[c, :, :])
    for y in range(len(overlaps.s2)):
        # This is a vectorized version of the similarity calculation that
        # computes an entire row at a time.
        similarities[c, y, :] = (
            (overlaps[c, y, :] * overlaps[c, :, y].values) /
            (diag * diag[y])
        )

ds = similarities.to_dataset(name='similarities')
output_path = ('OUTPUT/Nienke_tcells_flow/similarities-torin1_treg_1d%s.nc' %
               testing_str)
ds.to_netcdf(output_path, format='NETCDF4')
