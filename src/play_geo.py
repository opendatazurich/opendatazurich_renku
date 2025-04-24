# %%
import geojson
import geopandas as gpd
import io
import json
from owslib.wfs import WebFeatureService
import re
import requests
import xml.etree.ElementTree as ET


# %%
# Define helper functions
def identifier_from_url(url):
    """
    Extracts the identifier from the url.
    """
    # Extract the identifier from the url
    identifier = re.search(r"\/([^\/\?]+)\?", url).group(1)
    return identifier


def url_to_geoportal_url(url):
    """
    Converts the url to a geoportal url.
    """
    # Extract the identifier from the url
    identifier = identifier_from_url(url)
    # Create the geoportal url
    geoportal_url = f"https://www.ogd.stadt-zuerich.ch/wfs/geoportal/{identifier}"
    return geoportal_url


def geojson_layers_from_wfs(wfs):
    layers = list(wfs.contents.keys())
    return layers


def geojson_layers_from_url(geoportal_url):
    params = {"service": "WFS", "version": "1.1.0", "request": "GetCapabilities"}
    response = requests.get(geoportal_url, params=params)
    root = ET.fromstring(response.content)
    namespace = {"wfs": "http://www.opengis.net/wfs"}
    layers = [
        feature_type.find("wfs:Name", namespace).text
        for feature_type in root.findall(".//wfs:FeatureType", namespace)
    ]
    return layers


def read_geojson_from_wfs(wfs, layer):
    response = wfs.getfeature(typename=layer, outputFormat="application/json")
    return response.read()


def read_geojson_from_url(geoportal_url, layer):
    params = dict(
        service="WFS",
        version="1.1.0",
        request="GetFeature",
        typename=layer,
        outputFormat="application/json",
    )
    r = requests.get(geoportal_url, params=params)
    return r.json()


# Specify the url for the backend.
# Here we are using data from Statistics Finland: https://www.stat.fi/org/avoindata/paikkatietoaineistot_en.html. (CC BY 4.0)
url = "https://www.stadt-zuerich.ch/geodaten/download/_GDP__Inventar_der_schuetzenswerten_Gaerten_und_Anlagen_von_kommunaler_Bedeutung_der_Stadt_Zuerich?format=geojson_link"
url_geoportal = url_to_geoportal_url(url)

# %% [markdown]
# ## Read in the dataframe as in the template
print("Getting available layers from:", url_geoportal)
requests_layers = geojson_layers_from_url(url_geoportal)
print("Available layers:", requests_layers)
print(
    "First layer is set as default. To chose another layer set it as typename in the get_dataset() function."
)
requests_gj = read_geojson_from_url(url_geoportal, requests_layers[0])
requests_gdf = gpd.read_file(json.dumps(requests_gj))
requests_gdf.head()

# %% [markdown]
# ## Read in the dataframe using the WFS service
wfs11 = WebFeatureService(url_geoportal, version="1.1.0")
wfs_layers = geojson_layers_from_wfs(wfs11)
print("Available layers:", wfs_layers)
print(
    "First layer is set as default. To chose another layer set it as typename in the get_dataset() function."
)
wfs_gj = read_geojson_from_wfs(wfs11, wfs_layers[0])
wfs_gdf = gpd.read_file(wfs_gj)
wfs_gdf.head()

# %%
requests_gdf.plot()

# %%
wfs_gdf.plot()

# %%
features_gdf = gpd.GeoDataFrame.from_features(
    geojson.load(io.BytesIO(wfs_gj)), crs="EPSG:3857"
)
features_gdf.head()
features_gdf.plot()

# %%
wfs_gdf.crs
# %%
features_gdf.crs

# %%
