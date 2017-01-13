import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

os.chdir(os.path.dirname(os.path.abspath(__file__)))

data_path = 'OUTPUT/Nienke_tcells_flow/similarities.nc'
ds = xr.open_dataset(data_path)
s = ds['similarities']

#s = s.fillna(-1)


def plot():
    s.plot()
    ax = plt.gca()
    ax.set_title('Searchlight similarity')
    ax.set_aspect('equal')
    plt.subplots_adjust(bottom=0.2, top=0.95, left=0.20, right=1)
    fig = plt.gcf()
    fig.set_size_inches(9, 9)
    return fig

def reset_dims(da, dims=None):
    da = da.copy()
    if dims is None:
        dims = da.dims
    for dim in dims:
        da[dim] = range(len(da[dim]))
    return da

fig = plot()
image_path = data_path.replace('.nc', '.png')
print "Writing", image_path
fig.savefig(image_path)
plt.close(fig)
