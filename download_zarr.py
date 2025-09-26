import os
import requests
from urllib.parse import urljoin
from pathlib import Path
import logging
from tqdm import tqdm
from pystac_client import Client

# ===========================
# KONFIGURACJA
# ===========================
STAC_API_URL = "https://stac.core.eopf.eodc.eu/"  # Twój katalog STAC
OUTPUT_DIR = "results"
TIMEOUT = 30
MAX_ITEMS = 50  # np. 1000 żeby ograniczyć ilość danych (None = wszystkie)

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stac_downloader")

# ===========================
# FUNKCJE POMOCNICZE
# ===========================
def safe_download(href: str, dest_path: Path) -> bool:
    """Ściąga plik z href, zwraca True jeśli sukces."""
    try:
        head = requests.head(href, timeout=TIMEOUT)
        if head.status_code != 200:
            logger.warning(f"Asset niedostępny (HEAD {head.status_code}): {href}")
            return False

        resp = requests.get(href, stream=True, timeout=TIMEOUT)
        if resp.status_code == 200:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                for chunk in resp.iter_content(8192):
                    if chunk:
                        f.write(chunk)
            return True
        else:
            logger.warning(f"Nie udało się pobrać: {href} ({resp.status_code})")
            return False
    except Exception as e:
        logger.error(f"Błąd przy pobieraniu {href}: {e}")
        return False

# ===========================
# GŁÓWNA LOGIKA
# ===========================
def main():
    client = Client.open(STAC_API_URL)

    collections = client.get_collections()
    #logger.info(f"Znaleziono {len(collections)} kolekcji.")

    for coll in collections:
        coll_id = coll.id
        logger.info(f"Przetwarzam kolekcję: {coll_id}")

        items = client.search(collections=[coll_id])
        count = 0
        for item in tqdm(items.items(), desc=f"Kolekcja {coll_id}"):
            count += 1
            if MAX_ITEMS and count > MAX_ITEMS:
                break

            for asset_key, asset in item.assets.items():
                href = asset.href
                filename = os.path.basename(href.split("?")[0]) or asset_key
                local_path = Path(OUTPUT_DIR) / coll_id / item.id / asset_key / filename

                if local_path.exists():
                    continue

                success = safe_download(href, local_path)
                if not success:
                    logger.warning(f"Pominięto asset {asset_key} w item {item.id}")

if __name__ == "__main__":
    main()