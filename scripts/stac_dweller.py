import os

import pystac
from config import (
    modify_asset_hrefs,
    save_with_empty_links,
)

root_url = "https://s3.eu-central-1.wasabisys.com/stac/openlandmap/catalog.json"
pystac.stac_io.RetryStacIO()
cat = pystac.read_file(root_url)
copied_cat = cat.get_all_collections()
for collection in copied_cat:
    if collection.id not in [
        "dtm.bareearth_ensemble",
        "pop.count_ghs.jrc",
        "nightlights.average_viirs.v21",
        "forest.cover_esacci.ifl",
    ]:
        cat.remove_child(collection.id)

copied_cat = cat.full_copy()

output_dir = "static_results"
os.makedirs(output_dir, exist_ok=True)
modify_asset_hrefs(catalog=copied_cat, new_base_s3_path="s3://eodata/auxdata/IPCEI")
save_with_empty_links(catalog=copied_cat, dest_dir=output_dir)
