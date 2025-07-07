from scripts.config import (
    InputData,
    LocalSTACCollections,
    save_with_empty_links,
)


def main():
    other_stacs = InputData.from_yaml()

    for cat in other_stacs.stac_collections:
        list_of_packages = cat.handle_cols()
        for package in list_of_packages:
            local_stac_instance = LocalSTACCollections(*package)
            local_stac_instance.add_to_local_catalogue()

    # modify_asset_hrefs()
    # LOCAL_CATALOGUE.normalize_hrefs(root_href="s3://eodata/auxdata/")

    save_with_empty_links()


if __name__ == "__main__":
    main()
