import os
import sys
import csv
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt


data_path = sys.argv[1]

os.chdir(os.path.dirname(os.path.abspath(__file__)))

ds = xr.open_dataset(data_path)
similarities = ds['similarities']
n_sets = len(similarities.s1)

labels = similarities.s1.values

def plot():
    sim_plot = similarities.copy()
    sim_plot.coords['s1'] = range(n_sets)
    sim_plot.coords['s2'] = range(n_sets)
    sim_plot.plot(x='s1', y='s2', vmin=0, vmax=1)
    ax = plt.gca()
    ax.set_xticks(range(n_sets))
    ax.set_yticks(range(n_sets))
    ax.set_xticklabels(labels, size=8, fontname='monospace',
                       rotation='vertical')
    ax.set_yticklabels(labels, size=8, fontname='monospace')
    ax.set_title('Searchlight similarity')
    ax.set_aspect('equal')
    plt.subplots_adjust(bottom=0.2, top=0.95, left=0.20, right=1)
    fig = plt.gcf()
    fig.set_size_inches(9, 9)
    return fig

fig = plot()
image_path = data_path.replace('.nc', '.png')
print "Writing", image_path
fig.savefig(image_path)
plt.close(fig)
