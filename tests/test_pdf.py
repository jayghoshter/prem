from prem import PDF
from prem.sources import CrossRef
import os
import sys

# FIXME:
sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))
from helpers.utils import get_pdf

def test_pdf_read():
    filename = get_pdf('neuroscience_education')
    pdf = PDF(filename)
    assert pdf.metadata
    os.remove(filename)

def test_pdf_write():
    filename = get_pdf('neuroscience_education')
    outfilename = filename + '.new.pdf'
    pdf = PDF(filename)
    pdf.write(outfilename)
    pdf2 = PDF(outfilename)
    # NOTE: Doesn't work for pikepdf since it overwrites Producer and times
    # assert pdf2.metadata == pdf.metadata
    assert len(pdf2.pages) == len(pdf.pages)
    # TODO: Why doesn't this work?
    # assert pdf2.pages == pdf.pages
    os.remove(filename)
    os.remove(outfilename)

def test_pdf_to_text():
    filename = get_pdf('origin_of_gravity')
    pdf = PDF(filename)
    text = pdf.pages_to_text()
    assert text
    os.remove(filename)


def test_pdf_overwrite():
    filename = get_pdf('black_holes')
    doi = '10.1103/PhysRevD.13.191'
    pdf = PDF(filename)
    mdata = CrossRef.fetch_and_parse(doi)
    pdf.update_metadata(mdata)
    field = 'dc:title'
    modified_str = pdf.metadata[field][::-1]
    pdf.update_metadata({field: modified_str})
    pdf.write()
    pdf.unload()
    assert pdf.metadata == {}
    pdf.load()
    assert pdf.metadata[field] == modified_str
    os.remove(filename)

def test_pdf_rename():
    filename = get_pdf('smart_drugs_and_neuroenhancement')
    newfilename = filename + '.new.pdf'

    pdf = PDF(filename)
    pdf.rename(newfilename)

    os.remove(newfilename)

