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
    outdict = defaultdict(str)
    mdata = defaultdict(str, mdata)

    outdict['Title'] = mdata.get('title', ['NoTitle'])[0].replace('/', '-') if mdata['title'] else 'NoTitle'
    outdict['Author'] = mdata['author'][0].get('family', ['NoAuthor']) if mdata['author'] else 'NoAuthor'

    # TODO: 
    if mdata['publisher'] and mdata['container-title']:
        outdict['Producer'] = f"{mdata.get('publisher', 'NoPublisher')} - {mdata.get('container-title',['NoJournal'])[0]}"

    outdict['DOI'] = mdata['DOI'] if mdata['DOI'] else 'NoDOI'
    outdict['URL'] = f"https://doi.org/{mdata['DOI']}" if mdata['DOI'] else 'NoURL'

    # TODO: published-online? published-print? issued?
    outdict['Year'] = mdata['issued'].get('date-parts', [['NoDate']])[0][0] if mdata['issued']['date-parts'] else 'NoDate'

    return outdict
