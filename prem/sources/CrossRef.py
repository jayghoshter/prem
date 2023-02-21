import requests
from collections import defaultdict
from joblib import Memory
import os

CACHE_DIR = f"{os.environ['HOME']}/.cache/prem"
memory = Memory(location=CACHE_DIR, verbose=0)

@memory.cache
def fetch_metadata_crossref(doi:str):
    """
    Fetch metadata for a given DOI from CrossRef
    """
    response = requests.get(f"https://api.crossref.org/works/{doi}")

    if not response.ok: 
        print(f"Error fetching data for doi: {doi}")
        return {}
        # raise RuntimeError(f"Error fetching data for doi: {doi}")

    return response.json()["message"]

def fetch_by_doi(doi:str):
    return fetch_metadata_crossref(doi)

def query(string):
    """ Given a title string, return search results """
    response = requests.get(f"https://api.crossref.org/works?query={string}")

    if not response.ok: 
        print(response)
        raise RuntimeError(f"Error querying for string: {string}")

    result = defaultdict(str, response.json()["message"])

    return result["items"]

def extract(mdata:dict): 
    """
    Extract metadata from given crossref metadata dictionary.
    """
    out = defaultdict(str)
    mdata = defaultdict(str, mdata)

    try: 
        out['dc:format'] = 'application/pdf'
        out['dc:identifier'] = f"doi:{mdata['DOI']}"
        out['dc:title'] = mdata['title'][0].replace('/', ' ')
        out['dc:creator'] = list(map(lambda a: f"{a.get('given')} {a.get('family')}" , mdata['author']))
        out['dc:subject'] = set(mdata['subject'])
        out['dc:description'] = f"{mdata['container-title'][0]}, {mdata['volume']} ({mdata['issued']['date-parts'][0][0]}) {mdata['page']}"
        out['dc:publisher'] = set(mdata['publisher'])

        out['prism3:publicationName'] = mdata['container-title'][0]
        out['prism3:aggregationType'] = mdata['type']
        # out['prism3:copyright'] = mdata['assertion']...
        out['prism3:issn'] = mdata['ISSN'][0] if mdata['ISSN'] else ''
        out['prism3:volume'] = mdata['volume']
        out['prism3:pageRange'] = mdata['page']
        out['prism3:startingPage'] = mdata['page']
        out['prism3:doi'] = mdata['DOI']
        out['prism3:url'] = mdata['URL']
        out['prism3:coverDisplayDate'] = "-".join(str(mdata['issued']['date-parts'][0]))

        out['crossmark:DOI'] = mdata['DOI']
        out['pdfx:doi'] = mdata['DOI']
        out['pdfx:CrossMarkDomains'] = mdata['content-domain']['domain']

        out['prem:author'] = next(filter(lambda x: x['sequence'] == 'first', mdata['author']))['family']
        out['prem:title'] = mdata['title'][0].replace('/', ' ')
        out['prem:year'] = str(mdata['issued']['date-parts'][0][0])
    except:
        with open('prem.dump', 'w') as dumpfile:
            import json
            json.dump(mdata, dumpfile, indent=2)
        raise RuntimeError("Error with accessing some tags in crossref metadata")

    return out
