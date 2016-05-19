"Compute similarities for Nienke's T-cell FACS data."

import sys
import os
import time
import collections
import itertools
import re
import numpy as np
import xarray as xr
from searchlight import *

focus = np.array([0.61, 0.74, 0.63, 0.50, 0.73])
input_dirs = ['Normalized_Tcon', 'Normalized_Treg']

if len(sys.argv) < 1:
    print "Usage: compute_similarities_nienke_tcells.py [test]"
    sys.exit(1)

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

data = collections.OrderedDict()
start = time.time()
for p in paths:
    match = re.search(r'/Normalized_(\w+)/Export_CompNM39A1_(\w+?)_T', p)
    (cell_type, sample_name) = match.groups()
    key = '%s/%s' % (cell_type, sample_name)
    data[key] = np.loadtxt(p, delimiter=',', ndmin=2)
print 'Time to load data:', time.time() - start, 's'

n_sets = len(data)
keys = sorted(data.keys())
overlaps = xr.DataArray(np.zeros((n_sets,n_sets)), {'s1': keys, 's2': keys})

start = time.time()
for i2, s2 in enumerate(overlaps.coords['s2'].values):
    for i1, s1 in enumerate(overlaps.coords['s1'].values):
        if i1 >= i2:
            print '%s,%s (%d x %d)' % (s2, s1, len(data[s2]),
                                           len(data[s1]))
            overlaps.loc[s2, s1] = searchlight(data[s2], data[s1],
                                               focus)
        else:
            overlaps.loc[s2, s1] = overlaps.loc[s1, s2]
print 'Time to compute overlaps:', time.time() - start, 's'

similarities = overlaps.copy()
for i2, s2 in enumerate(overlaps.coords['s2'].values):
    for i1, s1 in enumerate(overlaps.coords['s1'].values):
        similarities.loc[s2, s1] = ((overlaps.loc[s1, s2] * overlaps.loc[s2, s1]) /
                                    (overlaps.loc[s1, s1] * overlaps.loc[s2, s2]))

ds = similarities.to_dataset(name='similarities')
output_path = 'OUTPUT/Nienke_tcells_flow/similarities_tcon_sample%s.nc' % testing_str
ds.to_netcdf(output_path, format='NETCDF4')
