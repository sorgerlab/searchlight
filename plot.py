import os
import csv
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt


os.chdir(os.path.dirname(__file__))

ds = xr.open_dataset('OUTPUT/similarities.nc')
similarities = ds['similarities']
n_sets = len(similarities.s1)

layout_file = open('INPUT/INPUT/saman_cycIF_20151128_well_locations.csv')
layout = {r[0]: r[1:] for r in csv.reader(layout_file)}
agents = [layout[c][0] for c in similarities.s1.values]
doses = [float(layout[c][1].split(' ')[0]) for c in similarities.s1.values]
dose_units = [layout[c][1].split(' ')[1] for c in similarities.s1.values]
labels = ['%s %4.1f %s' % x for x in zip(agents, doses, dose_units)]

idx = list(zip(*sorted(zip(map(str.upper,dose_units),
                           agents,
                           doses,
                           range(len(agents)))
                       ))[-1])
well_idx = similarities.s1[idx]
labels_ordered = [labels[i] for i in idx]

sim_plot = similarities.sel(s1=well_idx, s2=well_idx).copy()
sim_plot.coords['s1'] = range(n_sets)
sim_plot.coords['s2'] = range(n_sets)
sim_plot.plot(x='s1', y='s2', vmin=0, vmax=1)
ax = plt.gca()
ax.set_xticks(range(n_sets))
ax.set_yticks(range(n_sets))
ax.set_xticklabels(labels_ordered, size=8, fontname='monospace', rotation='vertical')
ax.set_yticklabels(labels_ordered, size=8, fontname='monospace')
ax.set_title('Searchlight similarity')
ax.set_aspect('equal')
plt.subplots_adjust(bottom=0.2, top=0.95, left=0.15, right=1)
plt.show()
