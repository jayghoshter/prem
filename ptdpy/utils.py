import requests
from addict import Dict
from pdfrw import PdfReader, PdfWriter, PdfReader, PdfDict, PdfName, IndirectPdfDict, PdfString
import unicodedata
import pdfplumber
import os
import re

doi_regex = r'10.\d{4,9}/[A-Za-z0-9./:;()-_]+'

def fetch_metadata(doi:str, base_url:str ="https://api.crossref.org/works/") -> Dict: 
    """ Fetch metadata for a given DOI """
    response = requests.get(base_url + doi)

    if not response.ok: 
        raise RuntimeError(f"Error fetching data for doi: {doi}")

    return Dict(response.json()["message"])

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

def extract_from_crossref_metadata(mdata:dict): 
    return {
        'Title' : mdata["title"][0].replace('/', '-') if "title" in mdata.keys() else '',
        'Author': mdata["author"][0]["family"] if "author" in mdata.keys() else '',
        'Producer': f'{mdata["publisher"]} - {mdata["container-title"][0]}' if "publisher" in mdata.keys() and "container-title" in mdata.keys() else '',
        'DOI': mdata["DOI"] if "DOI" in mdata.keys() else '',
        'URL': f'https://doi.org/{mdata["DOI"]}' if "DOI" in mdata.keys() else '',
        'Year': mdata["issued"]["date-parts"][0][0] if "issued" in mdata.keys() else '',
    }

def extract_n_pdf_pages(fname, n=1):
    pdf = pdfplumber.open(fname)
    pages = pdf.pages[:n]
    text = ''
    for page in pages:
        text = text + page.extract_text()
    pdf.close()
    return text
