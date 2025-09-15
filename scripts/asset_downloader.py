import pystac
import stac_asset
import asyncio
import os
import stac_asset.blocking
import requests

def download_single_item(href: str, dir_path: str):
    #print(get_assets_href(href))
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

def get_assets_href(item_href: str) -> list[str]:
    r = requests.get(item_href)
    assets = r.json()['assets']
    assets_hrefs = [assets[x]['href'] for x in assets.keys()]
    return assets_hrefs

#asyncio.run(download_single_item())