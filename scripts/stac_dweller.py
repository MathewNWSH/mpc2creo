import os

import pystac
from config import modify_asset_hrefs, save_with_empty_links

roots = [
    "https://capella-open-data.s3.us-west-2.amazonaws.com/stac/capella-open-data-by-product-type/catalog.json",
    "https://s3.eu-central-1.wasabisys.com/stac/openlandmap/catalog.json",
    "https://coclico.blob.core.windows.net/stac/v1/catalog.json",
    "https://esa.pages.eox.at/cubes-and-clouds-catalog/MOOC_Cubes_and_clouds/catalog.json",
    "https://s3.eu-central-1.wasabisys.com/stac/odse/catalog.json",
]

for root_url in roots:
    pystac.stac_io.RetryStacIO()
    cat = pystac.read_file(root_url)
    # cat.links = []
    # cat.add_child(
    #     pystac.read_file(
    #         "https://pgc-opendata-dems.s3.us-west-2.amazonaws.com/arcticdem/mosaics/v3.0/2m.json"
    #     )
    # )
    # cat.add_child(
    #     pystac.read_file(
    #         "https://pgc-opendata-dems.s3.us-west-2.amazonaws.com/arcticdem/mosaics/v4.1/2m.json"
    #     )
    # )
    cat.links = [
        link for link in cat.links if link.rel != "root" or link.rel != "parent"
    ]
    copied_cat = cat.get_all_collections()

    # zamiast katalogu dodawać kolekcje i wczytywać je jako readfile
    for collection in copied_cat:
        if collection.id not in [
            "capella-open-data-cphd",
            "capella-open-data-csi",
            "capella-open-data-gec",
            "capella-open-data-geo",
            "capella-open-data-sicd",
            "capella-open-data-slc",
            "dtm.bareearth_ensemble",
            "forest.cover_esacci.ifl",
            "nightlights.average_viirs.v21",
            "pop.count_ghs.jrc",
            "slp",
            "snow_map",
            "veg_abies.alba_anv.eml",
        ]:
            cat.remove_child(collection.id)
        else:
            collection.links = [
                link
                for link in collection.links
                if link.rel != "root" or link.rel != "parent"
            ]
            print(len(collection.links))
            items_to_process = list(collection.get_items())
            for i, item in enumerate(items_to_process):
                item.links = []

    # zamiast tego semafor tak jak jest w eometadatatoolu

    copied_cat = cat.full_copy()

    output_dir = "static_results"
    os.makedirs(output_dir, exist_ok=True)
    modify_asset_hrefs(catalog=copied_cat, new_base_s3_path="s3://eodata/auxdata/IPCEI")
    save_with_empty_links(catalog=copied_cat, dest_dir=output_dir)
