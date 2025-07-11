import pystac
import stac_asset
import asyncio
import os
import stac_asset.blocking

def download_single_item(href: str, dir_path: str):
    item = pystac.read_file(href)
    item = stac_asset.blocking.download_item(item, dir_path)

def create_hrefs(catalog_href, item_ids) -> list[str]:
    hrefs = []
    for collection in item_ids:
        for item in item_ids[collection]:
            hrefs.append(os.path.join(catalog_href, 'collections', collection, 'items', item))
    return hrefs

def download_items(ndjson: list):
    for item in ndjson:
        item_href = item['asset']
    return

#asyncio.run(download_single_item())