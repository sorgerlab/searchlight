"Compute similarities for Nienke's T-cell FACS data."

import sys
import os
import time
import re
import numpy as np
import xarray as xr
from searchlight import *

# We have to compare 5037 files against 5037 other files. We want to break the
# 5037 x 5037 array up into 25 x 25 square pieces as this is the piece size
# that will require about 1 hour of runtime. 5037 / 25 rounded up is 202.
PIECE_SIZE = 202

focus = np.array([0.61, 0.74, 0.63, 0.50, 0.73])
input_dirs = ['Normalized_Tcon', 'Normalized_Treg']

if len(sys.argv) < 3:
    print "Usage: compute_similarities_nienke_tcells.py piece_x piece_y"
    sys.exit(1)
piece_x = int(sys.argv[1])
piece_y = int(sys.argv[2])

os.chdir(os.path.dirname(os.path.abspath(__file__)))

dirs = [os.path.join('INPUT', d) for d in input_dirs]
paths = sorted(os.path.join(d, f) for d in dirs for f in os.listdir(d)
               if f.endswith('.csv'))
base_x = piece_x * PIECE_SIZE
base_y = piece_y * PIECE_SIZE
paths_x = paths[base_x : base_x + PIECE_SIZE]
paths_y = paths[base_y : base_y + PIECE_SIZE]

def path_to_key(path):
    match = re.search(r'/Normalized_(\w+)/Export_CompNM39A1_(\w+?)_T', path)
    (cell_type, sample_name) = match.groups()
    key = '%s/%s' % (cell_type, sample_name)
    return key

data = {}
start = time.time()
for p in set(paths_x + paths_y):
    key = path_to_key(p)
    data[key] = np.loadtxt(p, delimiter=',', ndmin=2)
print 'Time to load data:', time.time() - start, 's'

keys_x = sorted(path_to_key(p) for p in paths_x)
keys_y = sorted(path_to_key(p) for p in paths_y)
overlaps = xr.DataArray(np.zeros((len(keys_y), len(keys_x)), int),
                        (('ky', keys_y), ('kx', keys_x)))

Start = time.time()
for y, ky in enumerate(overlaps.coords['ky'].values):
    for x, kx in enumerate(overlaps.coords['kx'].values):
        if x + base_x >= y + base_y:
            print '%s,%s (%d x %d)' % (ky, kx, len(data[ky]), len(data[kx]))
            overlaps.loc[ky, kx] = searchlight(data[ky], data[kx], focus)
print 'Time to compute overlaps:', time.time() - start, 's'

ds = overlaps.to_dataset(name='overlaps')
output_path = ('OUTPUT/Nienke_tcells_flow/pieces/overlaps_x%02d_y%02d.nc' %
               (piece_x, piece_y))
ds.to_netcdf(output_path, format='NETCDF4')
