import requests
from collections import defaultdict
from joblib import Memory
import os
from prem.utils import string_sanitizer
from prem.logging import defaultLogger
import re

CACHE_DIR = f"{os.environ['HOME']}/.cache/prem"
memory = Memory(location=CACHE_DIR, verbose=0)

doi_regex = r'10\.\d{4,9}/[A-Za-z0-9./:;()\-_]+'
doi_regex_compiled = re.compile(doi_regex)

# Regex to avoid DOIs pertaining to volumes
doi_journal_regex = r'10\.\d{4,9}/(?!\(ISSN\))[A-Za-z0-9./:;()\-_]+'
doi_journal_regex_compiled = re.compile(doi_journal_regex)

identifier_name = 'DOI'
identifier_regex = doi_journal_regex
identifier_regex_compiled = doi_journal_regex_compiled

@memory.cache
def fetch_metadata_crossref(doi:str):
    """
    Fetch metadata for a given DOI from CrossRef
    """
    response = requests.get(f"https://api.crossref.org/works/{doi}")

    if not response.ok: 
        return {}

    return response.json()["message"]

def fetch_by_doi(doi:str):
    return fetch_metadata_crossref(doi)

def fetch_and_parse(doi:str, logger=None):
    """
    Fetch metadata from CrossRef based on provided id and parse it into a useful dict.
    """
    logger = logger or defaultLogger
    module_name = __name__.split('.')[-1]

    mdata = fetch_by_doi(doi)
    if not mdata:
        logger.error(f"Error fetching metadata from {module_name}", indent_level=1)
        return defaultdict(str)
    logger.info(f"Fetched metadata from {module_name} or local cache", indent_level=1)

    return parse(mdata, logger)

def query(string):
    """ Given a title string, return search results """
    response = requests.get(f"https://api.crossref.org/works?query={string}")

    if not response.ok: 
        print(response)
        raise RuntimeError(f"Error querying for string: {string}")

    result = defaultdict(str, response.json()["message"])

    return result["items"]

def parse(mdata:dict, logger=None): 
    """
    Extract metadata from given crossref metadata dictionary.
    """
    out = defaultdict(str)
    mdata = defaultdict(str, mdata)
    logger = logger or defaultLogger

    if mdata['type'] == 'journal-issue':
        logger.error("DOI corresponds to a journal issue, not an article!", indent_level=1)
        return out

    try: 
        title = string_sanitizer(mdata['title'][0])
        container_title = mdata['container-title'][0] if mdata['container-title'] else ''

        if mdata['author']:
            try: 
                author = next(filter(lambda x: x['sequence'] == 'first', mdata['author'])).get ('family', '') 
            except StopIteration: 
                author = mdata['author'][0].get('family', '')
        else:
            author = ''

        out['dc:format'] = 'application/pdf'
        out['dc:identifier'] = f"doi:{mdata['DOI']}"
        out['dc:title'] = title
        out['dc:creator'] = list(map(lambda a: f"{a.get('given')} {a.get('family')}" , mdata['author']))
        out['dc:subject'] = set(mdata['subject'])
        out['dc:description'] = f"{container_title}, {mdata['volume']} ({mdata['issued']['date-parts'][0][0]}) {mdata['page']}"
        out['dc:publisher'] = mdata['publisher']

        out['prism3:publicationName'] = container_title
        out['prism3:aggregationType'] = mdata['type']
        # out['prism3:copyright'] = mdata['assertion']...
        out['prism3:issn'] = mdata['ISSN'][0] if mdata['ISSN'] else ''
        out['prism3:volume'] = mdata['volume']
        out['prism3:pageRange'] = mdata['page']
        out['prism3:startingPage'] = mdata['page']
        out['prism3:doi'] = mdata['DOI']
        out['prism3:url'] = mdata['URL']
        out['prism3:coverDisplayDate'] = "-".join(map(str, mdata['issued']['date-parts'][0]))

        out['crossmark:DOI'] = mdata['DOI']
        out['pdfx:doi'] = mdata['DOI']
        out['pdfx:CrossMarkDomains'] = mdata['content-domain']['domain']

        out['prem:author'] = author
        out['prem:title'] = title
        out['prem:year'] = str(mdata['issued']['date-parts'][0][0])
    except Exception as e:
        with open('prem.dump', 'w') as dumpfile:
            import json
            json.dump(mdata, dumpfile, indent=2)
        raise RuntimeError(f"{e}: Error with accessing some tags in crossref metadata")
        # print(f"Error with accessing some tags in crossref metadata, {e}")
        # return defaultdict(str)

    return out

