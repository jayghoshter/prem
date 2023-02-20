import requests
import os
import re
from joblib import Memory
from pathlib import Path
import subprocess
from collections import defaultdict

doi_regex = r'10.\d{4,9}/[A-Za-z0-9./:;()\-_]+'

CACHE_DIR = f"{os.environ['HOME']}/.cache/prem"
memory = Memory(location=CACHE_DIR, verbose=0)

@memory.cache
def fetch_metadata_crossref(doi:str):
    """
    Fetch metadata for a given DOI from CrossRef
    """
    print(f"Fetching data for {doi} using CrossRef... ", end="")
    response = requests.get(f"https://api.crossref.org/works/{doi}")

    if not response.ok: 
        print(f"Error fetching data for doi: {doi}")
        return None
        # raise RuntimeError(f"Error fetching data for doi: {doi}")

    print("done!")
    return defaultdict(str, response.json()["message"])

@memory.cache
def fetch_bibliography(doi:str):
    """
    Fetch citation as bibtex string from dx.doi.org for given DOI
    """
    header = {'Accept': 'text/bibliography; style=bibtex'}
    response = requests.get(f"https://dx.doi.org/{doi}", headers=header)

    if not response.ok: 
        print(f"Error fetching bibtex for doi: {doi}")
        return None

    return response.text.strip()

def extract_from_crossref_metadata(mdata:dict): 
    """
    Extract metadata from given crossref metadata dictionary.
    """
    # TODO: Fix this and clean it up
    outdict = defaultdict(str)
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

def find_generic_pdf_opener_linux():
    """
    Find the default pdf opener in Linux
        - Use xdg-mime
        - Search XDG directories for .desktop
        - Parse file and find command
    """
    xdg_query = subprocess.run(['xdg-mime', 'query', 'default', 'application/pdf'], capture_output=True)
    default_app_xdg_str = xdg_query.stdout.strip().decode()

    HOME=Path(os.environ['HOME'])
    xdg_user_dir= os.environ.get('XDG_DATA_HOME', None) or str(HOME/'.local/share')
    xdg_system_dirs = os.environ.get('XDG_DATA_DIRS', '') or '/usr/local/share/:/usr/share/'
    search_dirs = xdg_system_dirs.split(':')
    search_dirs.append(xdg_user_dir)
    search_dirs = map(lambda p: Path(p) / 'applications', search_dirs)

    app_name = None

    for dir in search_dirs: 
        if dir.exists():
            files = [ x for x in dir.rglob(default_app_xdg_str) ]
            if files:
                desktop_file = files[0]
                with open(desktop_file, 'r') as fp:
                    lines = fp.read()
                    app_name = re.search(r'^Exec\s*=\s*(\w+).*\n', lines, re.MULTILINE)
                break

    if app_name:
        return app_name.group(1)
    else:
        raise RuntimeError("Could not find default pdf application command!")

def generic_open_linux(fname):
    """
    Open a pdf file using the system default in Linux.
    Return the subprocess object
    """
    app = find_generic_pdf_opener_linux()
    return subprocess.Popen([app, fname])
