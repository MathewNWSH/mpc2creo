import json
import os


def remove_tilejson_asset(root_dir):
    """
    Iteruje po plikach JSON w podanym katalogu i jego podkatalogach,
    wyszukując i usuwając asset o nazwie 'tilejson'.

    Args:
        root_dir (str): Ścieżka do katalogu głównego do przeszukania.
    """
    if not os.path.isdir(root_dir):
        print(f"Błąd: Podany katalog '{root_dir}' nie istnieje.")
        return

    # Użyj os.walk do rekurencyjnego przejścia przez katalogi
    for subdir, _, files in os.walk(root_dir):
        for filename in files:
            # Sprawdź, czy plik ma rozszerzenie .json
            if filename.endswith(".json"):
                file_path = os.path.join(subdir, filename)
                print(f"Przetwarzanie pliku: {file_path}")

                try:
                    with open(file_path, "r+", encoding="utf-8") as f:
                        data = json.load(f)
                        modified = False

                        # Sprawdź, czy klucz 'assets' istnieje i jest słownikiem
                        if "assets" in data and isinstance(data["assets"], dict):
                            # Sprawdź, czy asset 'tilejson' istnieje do usunięcia
                            if "tilejson" in data["assets"]:
                                print("  - Znaleziono i usunięto asset 'tilejson'.")
                                del data["assets"]["tilejson"]
                                modified = True
                            else:
                                print("  - Pomijanie: brak assetu 'tilejson'.")
                        else:
                            print(
                                "  - Pomijanie: brak klucza 'assets' lub nie jest on słownikiem."
                            )

                        # Jeśli wprowadzono zmiany, zapisz plik z powrotem
                        if modified:
                            f.seek(0)  # Wróć na początek pliku
                            json.dump(data, f, indent=2)  # Zapisz zmodyfikowane dane
                            f.truncate()  # Usuń resztę starej zawartości, jeśli nowa jest krótsza
                            print(f"  > Zapisano zmiany w {file_path}")

                except json.JSONDecodeError:
                    print(f"  - Błąd: Nie można zdekodować JSONa w pliku {file_path}.")
                except Exception as e:
                    print(
                        f"  - Wystąpił nieoczekiwany błąd podczas przetwarzania pliku {file_path}: {e}"
                    )


# --- UŻYCIE ---
# 1. Zmień wartość zmiennej 'target_directory' na ścieżkę do folderu,
#    który chcesz przeszukać.
#
# Przykłady ścieżek:
#   - Windows: 'C:\\Users\\TwojaNazwa\\Desktop\\dane'
#   - Linux/macOS: '/home/uzytkownik/dane'
#   - Bieżący katalog: '.'

target_directory = "/home/mniemyjski/mpc2creo/results"  # <-- ZMIEŃ TĘ ŚCIEŻKĘ

# Wywołanie funkcji
remove_tilejson_asset(target_directory)

print("\nZakończono przetwarzanie.")
