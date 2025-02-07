# %%
# A script to just try things out

# %%
import pandas as pd
from opendata import OpenDataZH
from IPython.display import display, HTML, Markdown

odz = OpenDataZH()

# %%
package = odz.get_package(name="bau_hae_lima_zuordnung_adr_quartier_bzo16_bzo99_od5143")

# %%
dataset = package.dataset(0)

# %%
dataset.display_metadata()

# %%
df = dataset.df
df.head()

# %%
odz.csv_package_list.head()
# %%
