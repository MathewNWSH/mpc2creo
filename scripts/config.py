import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

import pystac
import yaml
from httpx import Client
from pystac_client import Client

LOCAL_CATALOGUE: pystac.Catalog = pystac.Catalog(
    id="mpc2creo",
    description="...",
    href="s3://eodata/auxdata/",
)


def modify_asset_hrefs(
    catalog: pystac.Catalog = LOCAL_CATALOGUE,
    new_base_s3_path: str = "s3://eodata/auxdata",
):
    """
    Example:
    An asset with href '.../IMG.tif' will be changed to
    's3://new-path/IMG_s2.tif'
    """
    # for i in [
    #     "Apache Software Foundation (ASF)",
    # ]:
    #     catalog.remove_child(i)
    for item in catalog.get_all_items():
        item.assets = {
            key: asset
            for key, asset in item.assets.items()
            if "visual" not in (asset.roles or [])
        }

        if "\\" in item.id:
            clear_id = item.id.replace("\\", "_")
            item.id = item.id.replace("\\", "/")
            for asset_data in item.assets.values():
                asset_data.href = asset_data.href.replace(item.id, clear_id)
            item.id = clear_id

        item.properties["auth:schemes"] = {
            "oidc": {
                "type": "openIdConnect",
                "openIdConnectUrl": "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/.well-known/openid-configuration",
            },
            "s3": {"type": "s3"},
        }

        item.properties["storage:schemas"] = {
            "cdse-s3": {
                "title": "Copernicus Data Space Ecosystem S3",
                "description": "This endpoint provides access to EO data which is stored on the object storage of both CloudFerro Cloud and OpenTelekom Cloud (OTC). See the [documentation](https://documentation.dataspace.copernicus.eu/APIs/S3.html) for more information, including how to get credentials.",
                "platform": "https://eodata.dataspace.copernicus.eu",
                "requester_pays": False,
                "type": "custom-s3",
            },
            "creodias-s3": {
                "title": "CREODIAS S3",
                "description": "Comprehensive Earth Observation Data (EODATA) archive offered by CREODIAS as a commercial part of CDSE, designed to provide users with access to a vast repository of satellite data without predefined quota limits.",
                "platform": "https://eodata.cloudferro.com",
                "requester_pays": True,
                "type": "custom-s3",
            },
        }

        item.stac_extensions.extend(
            [
                "https://stac-extensions.github.io/storage/v2.0.0/schema.json",
                "https://stac-extensions.github.io/authentication/v1.1.0/schema.json",
            ]
        )

        for asset_key, asset in item.assets.items():
            asset.extra_fields = {
                "storage:refs": ["cdse-s3", "creodias-s3"],
                "auth:refs": ["s3"],
            }

            new_href = new_base_s3_path + urlparse(asset.href).path
            asset.href = new_href


def save_with_empty_links(
    catalog: pystac.Catalog = LOCAL_CATALOGUE, dest_dir: str = "./results"
):
    os.makedirs(dest_dir, exist_ok=True)
    catalog.normalize_hrefs(dest_dir)  # Normalizujemy ścieżki do plików lokalnych

    for krotka in catalog.walk():
        for obj in krotka[1]:
            try:
                obj.keywords.append("IPCEI")
            except AttributeError:
                obj.keywords = ["IPCEI"]

            try:
                for i in obj.providers:
                    if "host" in i.roles:
                        i.roles.remove("host")
                        if len(i.roles) == 0:
                            obj.providers.remove(i)
            except TypeError:
                obj.providers = []

            obj.providers.append(
                pystac.Provider.from_dict(
                    {
                        "url": "https://cloudferro.com/",
                        "name": "CloudFerro",
                        "roles": ["host"],
                    }
                )
            )
            obj.extra_fields["auth:schemes"] = {
                "oidc": {
                    "type": "openIdConnect",
                    "openIdConnectUrl": "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/.well-known/openid-configuration",
                },
                "s3": {"type": "s3"},
            }

            obj.extra_fields["storage:schemas"] = {
                "cdse-s3": {
                    "title": "Copernicus Data Space Ecosystem S3",
                    "description": "This endpoint provides access to EO data which is stored on the object storage of both CloudFerro Cloud and OpenTelekom Cloud (OTC). See the [documentation](https://documentation.dataspace.copernicus.eu/APIs/S3.html) for more information, including how to get credentials.",
                    "platform": "https://eodata.dataspace.copernicus.eu",
                    "requester_pays": False,
                    "type": "custom-s3",
                },
                "creodias-s3": {
                    "title": "CREODIAS S3",
                    "description": "Comprehensive Earth Observation Data (EODATA) archive offered by CREODIAS as a commercial part of CDSE, designed to provide users with access to a vast repository of satellite data without predefined quota limits.",
                    "platform": "https://eodata.cloudferro.com",
                    "requester_pays": True,
                    "type": "custom-s3",
                },
            }

            obj.stac_extensions.extend(
                [
                    "https://stac-extensions.github.io/storage/v2.0.0/schema.json",
                    "https://stac-extensions.github.io/authentication/v1.1.0/schema.json",
                ]
            )
            obj_dict = obj.to_dict()
            obj_dict["links"] = []

            file_path = obj.get_self_href()
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                json.dump(obj_dict, f, indent=2)

        for obj in krotka[2]:
            obj_dict = obj.to_dict()
            obj_dict["links"] = []

            file_path = obj.get_self_href()
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "w") as f:
                json.dump(obj_dict, f, indent=2)


@dataclass
class DataOfInterest:
    """Class to handle data after input"""

    url: str
    collections: list[str]
    catalogue: Client = field(init=False, repr=False)

    def __post_init__(self):
        self.catalogue = Client.open(self.url)

    def get_items(self, collection: str) -> pystac.item_collection.ItemCollection:
        search = self.catalogue.search(collections=collection)
        all_items = search.item_collection()
        return all_items

    def handle_cols(
        self,
    ) -> list[tuple[pystac.Collection, pystac.item_collection.ItemCollection]]:
        """
        Fetches collection objects and their corresponding items.
        """
        to_be_added = []
        for col_id in self.collections:
            collection_client = self.catalogue.get_collection(col_id)
            static_collection = pystac.Collection.from_dict(collection_client.to_dict())
            some_items = self.get_items(col_id)
            to_be_added.append((static_collection, some_items))

        return to_be_added


@dataclass
class InputData:
    """Class to handle input data"""

    stac_collections: list[DataOfInterest]

    @classmethod
    def from_yaml(cls, path: Path = Path("scripts/input.yaml")) -> list[DataOfInterest]:
        collections_list = []
        with path.open() as f:
            data = yaml.safe_load(f)
        collections_list = []

        for item_data in data.get("stac_collections", []):
            collections_list.append(
                DataOfInterest(item_data["url"], item_data["collections"])
            )

        return cls(stac_collections=collections_list)


@dataclass
class LocalSTACCollections:
    """Class to handle loadinging data to local catalogue"""

    collection: pystac.Collection
    items: pystac.item_collection.ItemCollection

    def add_to_local_catalogue(self) -> None:
        LOCAL_CATALOGUE.add_child(self.collection)
        for item in self.items:
            self.collection.add_item(item)
