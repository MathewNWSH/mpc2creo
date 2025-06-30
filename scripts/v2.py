from typing import Any

import pystac

@dataclass
class APIData:
    url: str
    collections: list[str]
    catalogue: Client = Client.open(url)

    def get_items(self, collection: str, type: ) -> pystac.item_collection.ItemCollection:
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
class StaticData:
    url: str
    collections: list[str]
    catalogue: pystac.STACObject = pystac.read_file(url)

    def __post_init__(self):
        self.catalogue = Client.open(self.url)

    def get_items(self, collection: str, type: ) -> pystac.item_collection.ItemCollection:
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


    async def handle_static_data(self) -> dict[str, Any]:
        copied_cat = self.catalogue.get_all_collections()
        for collection in copied_cat:
            if collection.id not in self.collections:
                copied_cat.remove_child(collection.id)

        copied_cat = copied_cat.full_copy()
        copied_cat.normalize_hrefs("s3://eodata/auxdata")
        copied_cat.save(catalog_type=pystac.CatalogType.ABSOLUTE_PUBLISHED)
        dict_cat = copied_cat.to_dict(include_self_link=False, transform_hrefs = True)
        return dict_cat


def handle_static_data(catalogue, collections) -> dict[str, Any]:
    item_col = []
    col_col = []
    copied_cat = catalogue.get_all_collections()
    for collection in copied_cat:
        if collection.id in collections:
            for item in collection.get_items(recursive=True):


    copied_cat = catalogue.full_copy()
    copied_cat.normalize_hrefs("static_results")
    copied_cat.save(catalog_type=pystac.CatalogType.ABSOLUTE_PUBLISHED)
    dict_cat = copied_cat.to_dict(include_self_link=False, transform_hrefs=True)
    return dict_cat


handle_static_data(
    pystac.read_file(
        "https://s3.eu-central-1.wasabisys.com/stac/openlandmap/catalog.json"
    ),
    [
        "dtm.bareearth_ensemble",
        "pop.count_ghs.jrc",
        "nightlights.average_viirs.v21",
        "forest.cover_esacci.ifl",
    ],
)
