import os

import pystac

root_url = "https://pgc-opendata-dems.s3.us-west-2.amazonaws.com/arcticdem.json"
pystac.stac_io.RetryStacIO()
cat = pystac.read_file(root_url)

copied_cat = cat.full_copy()

output_dir = "static_results"
os.makedirs(output_dir, exist_ok=True)

copied_cat.normalize_hrefs(output_dir)

copied_cat.save(catalog_type=pystac.CatalogType.ABSOLUTE_PUBLISHED)
