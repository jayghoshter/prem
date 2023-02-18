from rich import print
import re
from pdfrw import IndirectPdfDict
import sys
import os

from prem.utils import fetch_metadata
from prem.utils import query_title
from prem.utils import get_pdf_metadata
from prem.utils import modify_pdf_metadata
from prem.utils import get_doi_from_pdf_metadata
from prem.utils import delete_metadata_key
from prem.utils import extract_n_pdf_pages

# FIXME:
sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))
from helpers.utils import get_pdf

doi_regex = r'10.\d{4,9}/[A-Za-z0-9./:;()\-_]+'

def test_modify_metadata(): 
    infname = get_pdf('origin_of_gravity')
    outfname = "/tmp/test_mod.pdf"

    metadata={
        'Author': "New Author",
        'Title': "New Title",
        'Subject': "New Subject"
    }

    modify_pdf_metadata(infname, metadata=metadata, outfname=outfname)

    out_metadata = get_pdf_metadata(outfname)
    in_metadata = IndirectPdfDict(**metadata)

    os.remove(infname)
    os.remove(outfname)

    for k,v in in_metadata.items():
        assert out_metadata[k].decode() == v

def test_get_doi_from_pdf_metadata_success():
    fname = get_pdf('black_holes')
    out = get_doi_from_pdf_metadata(fname)
    os.remove(fname)
    assert out
    assert re.fullmatch(doi_regex, out)

def test_get_doi_from_pdf_metadata_fail():
    fname = get_pdf('neuroscience_education')
    out = get_doi_from_pdf_metadata(fname)
    os.remove(fname)
    assert not out
