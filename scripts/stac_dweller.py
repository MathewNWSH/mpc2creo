import os

import pystac
from config import (
    modify_asset_hrefs,
    save_with_empty_links,
)

root_url = "https://coclico.blob.core.windows.net/stac/v1/catalog.json"
pystac.stac_io.RetryStacIO()
cat = pystac.read_file(root_url)
copied_cat = cat.get_all_collections()
for collection in copied_cat:
    if collection.id not in [
        "slp",
    ]:
        cat.remove_child(collection.id)

copied_cat = cat.full_copy()

output_dir = "static_results"
os.makedirs(output_dir, exist_ok=True)
modify_asset_hrefs(catalog=copied_cat, new_base_s3_path="s3://eodata/auxdata/IPCEI")
save_with_empty_links(catalog=copied_cat, dest_dir=output_dir)

# copied_cat.normalize_hrefs(output_dir)

# copied_cat.save(catalog_type=pystac.CatalogType.ABSOLUTE_PUBLISHED)
