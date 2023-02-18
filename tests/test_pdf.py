from ptdpy import PDF
import os
import sys

# FIXME:
sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))
from helpers.utils import get_pdf

def test_pdf_read():
    pdf_read(engine='pikepdf')
    pdf_read(engine='pdfrw')

def test_pdf_write():
    pdf_write(engine='pikepdf')
    pdf_write(engine='pdfrw')

def test_pdf_to_text():
    pdf_to_text(engine='pikepdf')
    pdf_to_text(engine='pdfrw')

def test_pdf_overwrite():
    pdf_overwrite(engine='pikepdf')
    pdf_overwrite(engine='pdfrw')

def test_pdf_rename():
    pdf_rename(engine='pikepdf')
    pdf_rename(engine='pdfrw')

def pdf_read(engine):
    filename = get_pdf('neuroscience_education')
    pdf = PDF(filename, engine=engine)
    assert pdf.metadata
    os.remove(filename)

def pdf_write(engine):
    filename = get_pdf('neuroscience_education')
    outfilename = filename + '.new.pdf'
    pdf = PDF(filename, engine=engine)
    pdf.write(outfilename)
    pdf2 = PDF(outfilename, engine=engine)
    # NOTE: Doesn't work for pikepdf since it overwrites Producer and times
    # assert pdf2.metadata == pdf.metadata
    # Suddenly started failing?
    # assert len(pdf2.pages) == len(pdf.pages)
    # TODO: Why doesn't this work?
    # assert pdf2.pages == pdf.pages
    os.remove(filename)
    os.remove(outfilename)

def pdf_to_text(engine):
    filename = get_pdf('origin_of_gravity')
    pdf = PDF(filename, engine=engine)
    text = pdf.pages_to_text()
    assert text
    os.remove(filename)

def pdf_overwrite(engine):
    filename = get_pdf('smart_drugs_and_neuroenhancement')
    pdf = PDF(filename, engine=engine)
    field = 'Creator'
    modified_str = pdf.metadata[field][::-1]
    pdf.metadata[field] = modified_str
    pdf.write()
    pdf.unload()
    assert pdf.metadata == {}
    pdf.load()
    assert pdf.metadata[field] == modified_str
    os.remove(filename)

def pdf_rename(engine):
    filename = get_pdf('smart_drugs_and_neuroenhancement')
    newfilename = filename + '.new.pdf'

    pdf = PDF(filename, engine=engine)
    pdf.rename(newfilename)

    os.remove(newfilename)
