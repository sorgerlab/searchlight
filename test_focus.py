"Test a single value of focus_factor and save results to disk."

import sys
import os
import time
import collections
import itertools
import numpy as np
import xarray as xr
from searchlight import *


if len(sys.argv) < 2:
    print "Usage: test3.py <focus_factor> [test]"
    sys.exit(1)
else:
    # Take exact string for use in filenames, etc.
    ff_str = sys.argv[1]
    # Convert to float for numeric use.
    focus_factor = float(sys.argv[1])

# If non-zero, only run 4 (1) samples or 20 (2) samples, to allow a short
# runtime for testing.
testing_mode = 0
if len(sys.argv) == 3 and sys.argv[2] in ('1', '2'):
    testing_mode = int(sys.argv[2])
    ff_str += '_test'

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# List of columns (cell feature dimensions) directly from Adam's code. Subtract
# 1 to convert from 1-based to 0-based indexing.
cols = np.array([
        6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
        33, 34, 35, 36, 37, 38, 39, 40, 41, 42]) - 1

well_cols = range(2, 12)
well_rows_treated = 'CDEFG'
if testing_mode == 1:
    well_cols = well_cols[:2]
    well_rows_treated = well_rows_treated[:1]
elif testing_mode == 2:
    well_rows_treated = well_rows_treated[:1]

untreated_wells = ['B%02d' % i for i in well_cols]
treated_wells = ['%s%02d' % t for t in
                 itertools.product(well_rows_treated, well_cols)]

print 'Untreated wells:', untreated_wells
print 'Treated wells:', treated_wells

plate_data = {}
start = time.time()
for well in untreated_wells + treated_wells:
    plate_data[well] = np.loadtxt('INPUT/INPUT HOECHST ON/%s.csv' % well,
                                  delimiter=',', skiprows=1, usecols=cols)
untreated_std = np.vstack([plate_data[w] for w in untreated_wells]).std(axis=0)
focus = untreated_std * focus_factor
print 'Time to load data:', time.time() - start, 's'

set_names = untreated_wells + treated_wells
n_sets = len(plate_data)
overlaps = xr.DataArray(np.zeros((n_sets,n_sets)),
                        {'s1': set_names, 's2': set_names})

start = time.time()
for i2, s2 in enumerate(overlaps.coords['s2'].values):
    for i1, s1 in enumerate(overlaps.coords['s1'].values):
        if i1 >= i2:
            print '%s,%s (%d x %d)' % (s2, s1, len(plate_data[s2]),
                                           len(plate_data[s1]))
            overlaps.loc[s2, s1] = searchlight(plate_data[s2], plate_data[s1],
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
ds.to_netcdf('OUTPUT/test_focus_%s_similarities.nc' % ff_str, format='NETCDF4')
