import requests
from collections import defaultdict
from joblib import Memory
import os
import xml.etree.ElementTree as ET
import re
from prem.utils import string_sanitizer
from prem.logging import defaultLogger

CACHE_DIR = f"{os.environ['HOME']}/.cache/prem"
memory = Memory(location=CACHE_DIR, verbose=0)

arxiv_namespaces = {
        'atom': "http://www.w3.org/2005/Atom"
        }

arxiv_id_regex = r'(?<=arXiv:)\d{4}\.\d{4,5}'
arxiv_id_regex_compiled = re.compile(arxiv_id_regex)

identifier_name = 'arXiv ID'
identifier_regex = arxiv_id_regex
identifier_regex_compiled = arxiv_id_regex_compiled

@memory.cache
def fetch_metadata_arxiv(id:str):
    params = {'search_query': f'id:{id}', 'start': 0, 'max_results': 10}
    response = requests.get('http://export.arxiv.org/api/query', params=params)
    # print(response.content)

    return ET.fromstring(response.content)

def fetch_and_parse(arxiv_id:str, logger=None):
    """
    Fetch metadata from arXiv based on provided id and parse it into a useful dict.
    """
    logger = logger or defaultLogger
    module_name = __name__.split('.')[-1]

    mdata = fetch_metadata_arxiv(arxiv_id)
    if not mdata.find('atom:entry', arxiv_namespaces):
        logger.error(f"Error fetching metadata from {module_name}", indent_level=1)
        return defaultdict(str)
    logger.info(f"Fetched metadata from {module_name} or local cache", indent_level=1)

    return parse(mdata)

def parse(root:ET.Element):
    # Extract the paper titles and authors
    out = defaultdict(str)
    entry = root.find('atom:entry', arxiv_namespaces)

    if entry: 
        title = string_sanitizer(entry.find('atom:title', arxiv_namespaces).text)
        url = entry.find('atom:id', arxiv_namespaces).text
        authors = [author.text for author in entry.findall('atom:author/atom:name', arxiv_namespaces)]
        year = entry.find('atom:published', arxiv_namespaces).text.split('-')[0]
        id = re.sub("https?://arxiv.org/abs/", '', url)

        out['dc:creator'] = authors
        # out['Year'] = year
        # out['URL'] = id

        out['dc:format'] = 'application/pdf'
        out['dc:identifier'] = f"arXiv:{id}"
        out['dc:title'] = title
        # out['dc:subject'] = 
        # out['dc:description'] = f"{mdata['container-title'][0]}, {mdata['volume']} ({mdata['issued']['date-parts'][0][0]}) {mdata['page']}"
        # out['dc:publisher'] = set(mdata['publisher'])

        out['prem:author'] = authors[0].split()[-1]
        out['prem:title'] = title
        out['prem:year'] = year

    return out

def query(string):
    raise NotImplementedError("arXiv.query() is not built yet!")
