import os
import glob
import re
import itertools
import numpy as np
import xarray as xr
import pandas as pd

os.chdir(os.path.dirname(os.path.abspath(__file__)))

paths = sorted(glob.glob('OUTPUT/Nienke_tcells_flow/pieces/*.nc'))
pieces = []
for p in paths:
    pieces.append(xr.open_dataset(p))

kx = sorted(set.union(*[set(ds.kx.values) for ds in pieces]))
ky = sorted(set.union(*[set(ds.ky.values) for ds in pieces]))
assert kx == ky
data = np.empty((len(ky), len(kx)))
data[:] = np.nan
overlaps = xr.DataArray(data, coords=(('ky', ky), ('kx', kx)))

# Insert pieces into master overlaps array.
for ds in pieces:
    overlaps.loc[{'kx': ds.kx, 'ky': ds.ky}] = ds.overlaps
# Mirror matrix to make it symmetric (only upper triangle was computed).
for y in range(len(overlaps.ky)):
    overlaps[y, :y] = overlaps[:y, y]

similarities = xr.DataArray(np.empty_like(overlaps), coords=overlaps.coords)
similarities[:] = np.nan
# Compute similarity score
diag = np.diag(overlaps)
for y in range(overlaps.shape[0]):
    # This is a vectorized version of the similarity calculation that computes
    # an entire row at a time.
    similarities[y, :] = ((overlaps[y, :] * overlaps[:, y].values) /
                          (diag * diag[y]))

# Extract experimental location attributes from sample keys.
key_re = re.compile(r'(T...)/(NM\d\d)_Plate(\d)_([A-Z]\d\d)')
location_tuples = [key_re.match(s).groups() for s in similarities.kx.values]
sample_columns = ('cell_type', 'experiment', 'plate', 'well')
index_columns = ['experiment', 'plate', 'well']
samples = pd.DataFrame(location_tuples, columns=sample_columns)

design = pd.read_csv('INPUT/TconTreg_Platemap_Jeremy.csv', dtype={'Plate': str})
design = design.rename(columns={'Experiment': 'experiment', 'Plate': 'plate',
                                'WellFlow': 'well'})
# Strip underscore from experiment names to match file naming convention.
design.experiment = design.experiment.map(lambda s: s.replace('_', ''))
# Assign index columns to match samples.
design = design.set_index(index_columns)
# Split compound HMSLID and name into separate columns.
compounds = design.Compound.str.split(';', n=2, expand=True)
compounds.columns = pd.Index(['compound_hmslid', 'compound_name'])
# Fix up DMSO rows which had no semicolon to split on.
compounds.loc[compounds.compound_hmslid == 'DMSO', :] = (None, 'DMSO')
compounds['compound_concentration'] = design.Concentration

# Join the sample info with the compound info to create one master table.
metadata_df = samples.join(compounds, on=index_columns)
metadata = xr.Dataset.from_dataframe(metadata_df)

# Swap out old kx and ky dims for integer-numbered x and y.
for old, new in ('kx', 'x'), ('ky', 'y'):
    similarities.coords[new] = ([old], range(len(similarities[old])))
    similarities = similarities.swap_dims({old: new})
for coord in 'kx', 'ky':
    del similarities[coord]
# Use the master metadata table to create identical _x and _y coords.
for dim in similarities.dims:
    coords = metadata.rename({'index': dim})
    name_dict = {v: '%s_%s' % (v, dim)
                 for v in coords.keys() if v not in similarities.dims}
    coords = coords.rename(name_dict)
    similarities.coords.update(coords)

# Clamp max to 1.
similarities.values[similarities.values > 1] = 1

ds = similarities.to_dataset(name='similarities')
output_path = 'OUTPUT/Nienke_tcells_flow/similarities.nc'
ds.to_netcdf(output_path, format='NETCDF4')
