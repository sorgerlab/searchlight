import os
import re
import collections
import numpy as np
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt

def reset_dims(da):
    da = da.copy()
    for dim in da.dims:
        da[dim] = range(len(da[dim]))
    return da

os.chdir(os.path.dirname(os.path.abspath(__file__)))

design = pd.read_csv('INPUT/TconTreg_Platemap_Jeremy.csv', dtype={'Plate': str})
design = design.rename(columns={'Experiment': 'experiment', 'Plate': 'plate',
                                'WellFlow': 'well'})
design.experiment = design.experiment.str.replace('_', '')
d_byconc = design[design.Compound == '10079;Torin1'].sort_values('Concentration')
torin1_concentrations = d_byconc.Concentration.unique()
wanted = d_byconc[['experiment', 'plate', 'well']]
wanted_tuples = list(wanted.itertuples(index=False, name=None))
wanted_keys = ['Treg/%s_Plate%s_%s' % t for t in wanted_tuples]

data_path = 'OUTPUT/Nienke_tcells_flow/complete/similarities-torin1_treg_1d.nc'
data2_path = 'OUTPUT/Nienke_tcells_flow/complete/similarities.nc'
sim = xr.open_dataset(data_path).similarities
full_sim = xr.open_dataset(data2_path).similarities

fs_treg = full_sim[0,full_sim.cell_type_x=='Treg']

for channel in sim.channel.values:

    strip_data = sim.loc[channel,wanted_keys,:].values.reshape(3,2,-1).mean(1)
    strip = xr.DataArray(
        strip_data,
        dims=['torin1_concentration', 'x'],
        coords=collections.OrderedDict([
            ('torin1_concentration', torin1_concentrations),
            ('compound_hmslid', fs_treg['compound_hmslid_x']),
            ('compound_name', fs_treg['compound_name_x']),
            ('compound_concentration', fs_treg['compound_concentration_x']),
        ]),
    )
    order = np.argsort(strip.sel(torin1_concentration=10.0).fillna(-1))
    strip_sorted = strip[:,order]

    ss_plot = reset_dims(strip_sorted.clip(max=1))
    fig = plt.figure()
    ax = plt.gca()
    ss_plot.plot(vmin=0, vmax=1)
    ax.set_xlabel('')
    ax.set_xticks([])
    ax.set_yticks(range(len(torin1_concentrations)))
    ax.set_yticklabels(['%.1f' % c for c in torin1_concentrations], size=20)
    plt.subplots_adjust(bottom=0.05, top=0.95, left=0.04, right=1.14)
    fig.set_size_inches(30, 4)

    png_path = data_path.replace('.nc', '_%s.png' % channel)
    print "Writing", png_path
    fig.savefig(png_path)
    pdf_path = png_path.replace('.png', '.pdf')
    print "Writing", pdf_path
    fig.savefig(pdf_path)
    plt.close(fig)

    table = strip_sorted[0,:].drop('torin1_concentration').to_dataframe('dummy')
    table = table.drop('dummy', axis=1)
    for c in strip_sorted.torin1_concentration.values:
        key = 'similarity_at_%.1f' % c
        table[key] = strip_sorted.sel(torin1_concentration=c)
    csv_path = png_path.replace('.png', '.csv')
    print "Writing", csv_path
    table.to_csv(csv_path, index=False)
