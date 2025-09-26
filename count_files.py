import os

FOLDER = 'results'

subfolders = os.listdir(FOLDER)
zarr = []
for sub in subfolders:
    collections = os.listdir(os.path.join(FOLDER, sub))
    for i in collections:
        files = os.listdir(os.path.join(FOLDER, sub, i))
        if len(files) > 1:
            zarr.append(files)

