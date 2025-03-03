"""
A helper module with some useful functions for
interacting with the Open Data Swiss API.

"""

import pandas as pd

import numpy as np
import requests
import json
import re
from datetime import datetime
import time
from tqdm import tqdm

from bs4 import BeautifulSoup as bs4

import warnings
from IPython.display import display, HTML, Markdown

warnings.simplefilter(action="ignore", category=FutureWarning)

# Defaults

# Set constants for data provider and data API.
PROVIDER = "opendata.zh"
PROVIDER_LINK = "https://data.stadt-zuerich.ch"
BASELINK_DATAPORTAL = "https://data.stadt-zuerich.ch/dataset/"
CKAN_API_LINK = "https://data.stadt-zuerich.ch/api/3/action"
LANGUAGE = "de"

# Sort markdown table by this feature.
SORT_TABLE_BY = "title"

# Select keys in metadata for dataset and distributions.
KEYS_DATASET = [
    "dateLastUpdated",
    "maintainer",
    "maintainer_email",
    "metadata_created",
    "metadata_modified",
    "organization.name",
]
KEYS_DISTRIBUTIONS = [
    "package_id",
    "description",
    "dateLastUpdated",
    "license_id",
]

# Select relevant column names to reduce dataset.
REDUCED_FEATURESET = [
    "author",
    "author_email",
    "dateLastUpdated",
    "id",
    "maintainer",
    "maintainer_email",
    "metadata_created",
    "metadata_modified",
    "resources",
    "groups",
    "name",
    "language",
    "modified",
    "url",
    "identifier",
    "display_name.fr",
    "display_name.de",
    "display_name.en",
    "display_name.it",
    "organization.name",
    "organization.title.fr",
    "organization.title.de",
    "organization.title.en",
    "organization.title.it",
    "title",
    # The following are added for the codebooks.
    "contact",
    "distributions",
    "distribution_links",
    "metadata",
]


# Utility functions
def has_csv_distribution(dists):
    """Iterate over package resources and keep only CSV entries in list"""
    csv_dists = [x for x in dists if x.get("format", "") == "CSV"]
    if csv_dists != []:
        return csv_dists
    else:
        return np.nan


def filter_csv(full_df):
    """Filter to datasets that have a CSV distribution"""
    df = full_df.copy()
    df.resources = df.resources.apply(has_csv_distribution)
    df.dropna(subset=["resources"], inplace=True)
    return df


def get_dataset(url):
    """
    Return pandas df if url is parquet or csv file. Return None if not.
    """
    extension = url.rsplit(".", 1)[-1]
    if extension == "parquet":
        data = pd.read_parquet(url)
    elif extension == "csv":
        data = pd.read_csv(
            url,
            sep=",",
            on_bad_lines="warn",
            encoding_errors="ignore",
            low_memory=False,
        )
        # if dataframe only has one column or less the data is not comma separated, use ";" instead
        if data.shape[1] <= 1:
            data = pd.read_csv(
                url,
                sep=";",
                on_bad_lines="warn",
                encoding_errors="ignore",
                low_memory=False,
            )
            if data.shape[1] <= 1:
                print(
                    "The data wasn't imported properly. Very likely the correct separator couldn't be found.\nPlease check the dataset manually and adjust the code."
                )
    else:
        print("Cannot load data! Please provide an url with csv or parquet extension.")
        data = None
    return data


# API
class OpenDataZH:
    def __init__(self):
        self.provider = PROVIDER
        self.provider_link = PROVIDER_LINK
        self.baselink_dataportal = BASELINK_DATAPORTAL
        self.ckan_api_link = CKAN_API_LINK
        self.language = LANGUAGE
        self.sort_table_by = SORT_TABLE_BY
        self.keys_dataset = KEYS_DATASET
        self.keys_distributions = KEYS_DISTRIBUTIONS
        self.reduced_featureset = REDUCED_FEATURESET

        self._full_package_list_df = None
        self._csv_package_list_df = None

    def _get_full_package_list(self, limit=500, sleep=2):
        """Get full package list from CKAN API"""
        offset = 0
        frames = []
        while True:
            df = self._get_package_list_page(limit, offset)
            if df is None:
                break
            frames.append(df)
            offset += limit
            time.sleep(sleep)
        df = pd.concat(frames)
        df = df.set_index("name", drop=False).sort_index()
        self._full_package_list_df = df
        return df

    def _get_package_list_page(self, limit=500, offset=0):
        """Get a page of packages from CKAN API"""
        url = f"{self.ckan_api_link}/current_package_list_with_resources?limit={limit}&offset={offset}"
        res = requests.get(url)
        data = json.loads(res.content)
        if data["result"] == []:
            print("0 packages retrieved.")
            return None
        num_results = len(data["result"])
        print(f"{num_results} packages retrieved.")
        df = pd.DataFrame(pd.json_normalize(data["result"]))
        return df

    @property
    def full_package_list_df(self):
        if self._full_package_list_df is None:
            self._get_full_package_list()
        return self._full_package_list_df

    @property
    def csv_package_list(self):
        if self._csv_package_list_df is None:
            if self._full_package_list_df is None:
                self._get_full_package_list()
            self._csv_package_list_df = filter_csv(self._full_package_list_df)
        return self._csv_package_list_df

    def get_package(self, id=None, name=None):
        """Get a package from CKAN API"""
        if id is None and name is None:
            print("Please provide either an id or a name.")
            return None
        url = (
            f"{self.ckan_api_link}/package_show?id={id}"
            if id is not None
            else f"{self.ckan_api_link}/package_show?id={name}"
        )
        res = requests.get(url)
        data = json.loads(res.content)
        if data["success"] == False:
            print(data.get("error", "No error message provided."))
            return None
        return OpenDataPackage(self, pd.json_normalize(data["result"]).iloc[0])


class OpenDataPackage:
    def __init__(self, odz, metadata):
        self.odz = odz
        self.metadata = metadata
        self.distributions = metadata.get("resources", [])
        self.distribution_links = [x.get("url") for x in self.distributions]

    def display_metadata(self):
        display(
            HTML(
                f"<h2>Open Government Data, provided by <i>{self.odz.provider}</i></h2>"
                + f"<i>Generated Python starter code for data set with identifier</i> <b>{self.metadata['name']}</b>"
            )
        )

        display(HTML(f"<h2>Dataset</h2>" + f"<b>{self.metadata['title']}</b>"))

        display(HTML(f"<h2>Description</h2>"))
        display(Markdown(self.metadata["notes"]))
        display(Markdown(self.metadata["sszBemerkungen"]))

        display(HTML(f"<h2>Data set links</h2>"))
        display(
            HTML(
                f"<a href='{BASELINK_DATAPORTAL}{self.metadata['name']}'>Direct link by OpenDataZurich for dataset</a>"
            )
        )
        url = self.metadata.resources[0]["url"]
        display(HTML(f"<a href='{url}'>{url}</a>"))

        display(HTML(f"<h2>Metadata</h2>"))
        display_name = self.metadata["groups"][0]["display_name"]
        display_tags = [t["display_name"] for t in self.metadata["tags"]]
        display(
            Markdown(
                f"* **Publisher** {self.metadata['author']}\n"
                + f"* **Maintainer** {self.metadata['maintainer']}\n"
                + f"* **Maintainer email** {self.metadata['maintainer_email']}\n"
                + f"* **Keywords** {display_name}\n"
                + f"* **Tags** {display_tags}\n"
                + f"* **Metadata created** {self.metadata['metadata_created']}\n"
                + f"* **Metadata modified** {self.metadata['metadata_modified']}\n"
            )
        )

    def dataset(self, index=0):
        return OpenDataDataset(self, index)


class OpenDataDataset:
    def __init__(self, package, index):
        self.package = package
        self.index = index
        self.metadata = package.metadata["resources"][index]
        self._df = None

    def display_metadata(self):
        display(
            Markdown(
                f"* **name** {self.metadata['name']}\n"
                f"* **filename** {self.metadata['filename']}\n"
                f"* **format** {self.metadata['format']}\n"
                f"* **url** {self.metadata['url']}\n"
                f"* **id** {self.metadata['id']}\n"
                f"* **resource_type** {self.metadata['resource_type']}\n"
                f"* **package_id** {self.metadata['package_id']}\n"
            )
        )

    @property
    def df(self):
        if self._df is None:
            self._df = get_dataset(self.metadata["url"])
        return self._df
