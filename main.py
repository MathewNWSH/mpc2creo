from scripts.config import (
    LOCAL_CATALOGUE,
    InputData,
    LocalSTACCollections,
    modify_asset_hrefs,
    save_with_empty_links,
)

from scripts.asset_downloader import create_hrefs, download_single_item
import os

def main():
    other_stacs = InputData.from_yaml()

    for cat in other_stacs.stac_collections:
        list_of_packages = cat.handle_cols()
        for package in list_of_packages:
            local_stac_instance = LocalSTACCollections(*package)
            local_stac_instance.add_to_local_catalogue()

    modify_asset_hrefs()
    LOCAL_CATALOGUE.normalize_hrefs(root_href="s3://eodata/auxdata/")
    
    ids = save_with_empty_links()
    hrefs = create_hrefs(other_stacs.stac_collections[0].url, ids)

    for item in hrefs:
        item_splitted = item.split('/')
        download_single_item(item, os.path.join('./results/', item_splitted[-3], item_splitted[-1], '.'))

if __name__ == "__main__":
    main()
