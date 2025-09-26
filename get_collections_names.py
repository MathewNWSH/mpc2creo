import requests

catalog_href = 'https://stac.core.eopf.eodc.eu/'
r = requests.get(catalog_href)
answer = r.json()
links = answer['links']
collections = []
for x in links:
    if x['rel'] == 'child':
        collections.append(x['href'].split('/')[-1])
print(collections)