import requests
from addict import Dict
from pdfrw import PdfReader, PdfWriter, PdfReader, PdfDict, PdfName, IndirectPdfDict, PdfString
import unicodedata
import pdfplumber
import os
import re
from joblib import Memory
from pathlib import Path
import subprocess

doi_regex = r'10.\d{4,9}/[A-Za-z0-9./:;()\-_]+'

CACHE_DIR = f"{os.environ['HOME']}/.cache/prem"
memory = Memory(location=CACHE_DIR, verbose=0)

def fetch_metadata(doi:str, base_url:str ="https://api.crossref.org/works/") -> Dict: 
    """ Fetch metadata for a given DOI """
    response = requests.get(base_url + doi)

    if not response.ok: 
        raise RuntimeError(f"Error fetching data for doi: {doi}")

    return Dict(response.json()["message"])

@memory.cache
def fetch_metadata_crossref(doi:str):
        print(f"Fetching data for {doi} using CrossRef... ", end="")
        response = requests.get(f"https://api.crossref.org/works/{doi}")

        if not response.ok: 
            print(f"Error fetching data for doi: {doi}")
            return None
            # raise RuntimeError(f"Error fetching data for doi: {doi}")

        print("done!")
        return Dict(response.json()["message"])

@memory.cache
def fetch_bibliography(doi:str):
    header = {'Accept': 'text/bibliography; style=bibtex'}
    response = requests.get(f"https://dx.doi.org/{doi}", headers=header)

    if not response.ok: 
        print(f"Error fetching bibtex for doi: {doi}")
        return None

    return response.text.strip()

def query_title(string:str, base_url="https://api.crossref.org/works?query=") :
    """ Given a title string, return search results """
    response = requests.get(base_url + string)
    
    if not response.ok: 
        raise RuntimeError(f"Error querying for string: {string}")

    result = Dict(response.json()["message"])

    return result["items"]

def get_pdf_metadata(fname): 
    """ Return pdf metadata as PdfDict """
    trailer = PdfReader(fname)
    return trailer.Info

def modify_pdf_metadata(fname, metadata:dict, outfname=None, rename=False): 
    """ Update pdf metadata in-place using given dict. If outfname is given, write out to that file instead """
    reader = PdfReader(fname)
    writer = PdfWriter()

    # writer.trailer = reader
    writer.addpages(reader.pages)
    writer.trailer.Info = reader.Info
    writer.trailer.Info.update(IndirectPdfDict(**metadata))

    if outfname: 
        writer.write(outfname)
        if rename:
            os.remove(fname)
    else: 
        writer.write(fname)

def delete_metadata_key(fname, key:str, outfname=None):
    """ Delete a metadata key from a given pdf """

    reader = PdfReader(fname)
    writer = PdfWriter()

    writer.addpages(reader.pages)
    writer.trailer.Info = reader.Info

    if writer.trailer.Info[PdfName(key)]: 
        del writer.trailer.Info[PdfName(key)]

    if outfname: 
        writer.write(outfname)
    else: 
        writer.write(fname)

def get_doi_from_pdf_metadata(fname):
    mdata = get_pdf_metadata(fname)

    str_values = [ x.decode() for x in mdata.values() if isinstance(x, PdfString) ]
    pattern = re.compile(doi_regex)
    out = pattern.findall(" ".join(str_values))

    if out:
        return out[0]
    else: 
        return None
            
def unicode_normalize(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')

def extract_from_crossref_metadata(mdata:Dict): 
    # TODO: Fix this and clean it up
    outdict = Dict()
    outdict.Title = mdata.get('title', ['NoTitle'])[0].replace('/', '-') if mdata.title else 'NoTitle'
    outdict.Author = mdata.author[0].get('family', ['NoAuthor']) if mdata.author else 'NoAuthor'

    # TODO: 
    if mdata.publisher and mdata['container-title']:
        outdict.Producer = f"{mdata.get('publisher', 'NoPublisher')} - {mdata.get('container-title',['NoJournal'])[0]}"

    outdict.DOI = mdata.DOI if mdata.DOI else None
    outdict.URL = f'https://doi.org/{mdata.DOI}' if mdata.DOI else None

    # TODO: published-online? published-print? issued?
    outdict.Year = mdata.issued.get('date-parts', [['NoDate']])[0][0] if mdata.issued['date-parts'] else 'NoDate'

    return outdict.to_dict()

def extract_n_pdf_pages(fname, n=1):
    pdf = pdfplumber.open(fname)
    pages = pdf.pages[:n]
    text = ''
    for page in pages:
        text = text + page.extract_text()
    pdf.close()
    return text

def find_generic_pdf_opener_linux():
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
    app = find_generic_pdf_opener_linux()
    return subprocess.Popen([app, fname])
