import time
import collections
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from searchlight import *


# The one parameter to the algorithm.
focus_factor = 1.5

# List of columns (cell feature dimensions) directly from Adam's code. Subtract
# 1 to convert from 1-based to 0-based indexing.
cols = np.array([
        6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
        33, 34, 35, 36, 37, 38, 39, 40, 41, 42]) - 1

untreated_wells = ['B%02d' % i for i in range(2,12)]
treated_wells = ['G02', 'G03']

plate_data = {}
start = time.time()
for well in untreated_wells + treated_wells:
    plate_data[well] = np.loadtxt('INPUT/%s.csv' % well, delimiter=',',
                                  skiprows=1, usecols=cols)
untreated_std = np.vstack([plate_data[w] for w in untreated_wells]).std(axis=0)
focus = untreated_std * focus_factor
print 'Time to load data:', time.time() - start, 's'

data = collections.OrderedDict()
data['u1'] = plate_data['B02']
data['u2'] = plate_data['B03']
data['t1'] = plate_data['G02']
data['t2'] = plate_data['G03']
n_sets = len(data)
overlaps = xr.DataArray(np.zeros((n_sets,n_sets)),
                        {'s1': data.keys(), 's2': data.keys()})

start = time.time()
for i2, s2 in enumerate(overlaps.coords['s2'].values):
    for i1, s1 in enumerate(overlaps.coords['s1'].values):
        if i1 >= i2:
            overlaps.loc[s2, s1] = searchlight(data[s2], data[s1], focus)
        else:
            overlaps.loc[s2, s1] = overlaps.loc[s1, s2]
print 'Time to compute overlaps:', time.time() - start, 's'

similarities = overlaps.copy()
for i2, s2 in enumerate(overlaps.coords['s2'].values):
    for i1, s1 in enumerate(overlaps.coords['s1'].values):
        similarities.loc[s2, s1] = ((overlaps.loc[s1, s2] * overlaps.loc[s2, s1]) /
                                    (overlaps.loc[s1, s1] * overlaps.loc[s2, s2]))

sim_plot = similarities.copy()
sim_plot.coords['s1'] = range(n_sets)
sim_plot.coords['s2'] = range(n_sets)
sim_plot.plot(x='s1', y='s2', vmin=0, vmax=1)
ax = plt.gca()
ax.set_xticks(range(n_sets))
ax.set_yticks(range(n_sets))
ax.set_xticklabels(similarities.coords['s1'].values)
ax.set_yticklabels(similarities.coords['s2'].values)
ax.set_title('Searchlight similarity')
plt.show()
