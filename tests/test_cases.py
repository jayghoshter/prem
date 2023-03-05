from prem import PDF
from prem.sources import CrossRef, arXiv
import os
import sys

# FIXME:
sys.path.append(os.path.join(os.path.dirname(__file__), 'helpers'))
from helpers.utils import get_pdf

# WARNING: Cache is not invalidated before these tests. So we get the cached versions of whatever functions are cached.

"""
These cases should test the workflow on specific pdfs.

Workflow:
    1. Look for identifiers in pdf metadata
    2. Look for identifiers in pdf text
    3. Manual search/query
"""

def test_case_01():
    """ Test case for origin_of_gravity 
    - No DOI in either pdf metadata or text
    - crossref query provided, returns multiple matches: one for preprint and one complete publication.
    """
    filename = get_pdf('origin_of_gravity')
    pdf = PDF(filename)

    # No DOIs in pdf metadata
    ids_in_metadata = pdf.find_in_metadata(CrossRef.identifier_regex_compiled)
    assert not ids_in_metadata

    # No arXiv IDs in pdf metadata
    ids_in_metadata = pdf.find_in_metadata(arXiv.identifier_regex_compiled)
    assert not ids_in_metadata

    # No arXiv IDs in pdf text
    ids_in_text = pdf.find_in_text(arXiv.identifier_regex_compiled)
    assert not ids_in_text

    # Finds truncated DOI in text
    ids_in_text = pdf.find_in_text(CrossRef.identifier_regex_compiled)
    assert ids_in_text == ['10.4172/2320-']

    # Unfortunately CrossRef doesn't have this DOI registered
    mdata = CrossRef.fetch_and_parse('10.4172/2320-2459.10.6.004')
    assert not mdata

    # Look manually for papers with this title In this case, we have multiple
    # matches! 
    query_results = CrossRef.query("The Origin of Gravity a second order lorentz transformation for accelerated electromagnetic fields generating a gravitational field and the property of mass")

    # One for the preprint,
    mdata = CrossRef.parse(query_results[0])
    assert "The Origin of Gravity" in mdata['dc:title']
    assert "Wim Vegt" in mdata['dc:creator']
    assert mdata['crossmark:DOI'] == '10.31219/osf.io/qtpv6'

    # One for the published article
    mdata = CrossRef.parse(query_results[2])
    assert "The Origin of Gravity" in mdata['dc:title']
    assert "Wim Vegt" in mdata['dc:creator']
    assert mdata['prism3:publicationName'] == "International Research Journal of Pure and Applied Physics"
    assert mdata['crossmark:DOI'] == '10.37745/irjpap.13/vol9n11252'

def test_case_02():
    """ Test case for neuroscience education paper.
    - Finds DOI in pdf text, not in metadata
    """
    filename = get_pdf('neuroscience_education')
    pdf = PDF(filename)

    # No DOIs in pdf metadata
    ids_in_metadata = pdf.find_in_metadata(CrossRef.identifier_regex_compiled)
    assert not ids_in_metadata

    # No arXiv IDs in pdf metadata
    ids_in_metadata = pdf.find_in_metadata(arXiv.identifier_regex_compiled)
    assert not ids_in_metadata

    # No arXiv IDs in pdf text
    ids_in_text = pdf.find_in_text(arXiv.identifier_regex_compiled)
    assert not ids_in_text

    # Finds DOI in text
    ids_in_text = pdf.find_in_text(CrossRef.identifier_regex_compiled)
    assert ids_in_text == ['10.1038/nrn1907']

    mdata = CrossRef.fetch_and_parse('10.1038/nrn1907')
    assert mdata['dc:title'] == "Neuroscience and education: from research to practice?"
    assert "Usha Goswami" in mdata['dc:creator']

def test_case_03():
    """ Test case for Black holes and thermodynamics, by Hawking
    - finds DOI in pdf metadata
    """

    filename = get_pdf('black_holes')
    pdf = PDF(filename)
    doi = "10.1103/PhysRevD.13.191"

    # DOIs in pdf metadata
    ids_in_metadata = pdf.find_in_metadata(CrossRef.identifier_regex_compiled)
    assert ids_in_metadata
    assert doi in ids_in_metadata

    mdata = CrossRef.fetch_and_parse(doi)
    assert mdata['dc:title'] == "Black holes and thermodynamics"
    assert "S. W. Hawking" in mdata['dc:creator']

def test_case_04():
    """ Test case for smart drugs and neuroenhancement.
    - Finds DOI in text, but dc:creator is missing in CrossRef metadata.
    """
    filename = get_pdf('smart_drugs_and_neuroenhancement')
    pdf = PDF(filename)
    doi = "10.52586/4948"

    # No DOIs in pdf metadata
    ids_in_metadata = pdf.find_in_metadata(CrossRef.identifier_regex_compiled)
    assert not ids_in_metadata

    # No arXiv IDs in pdf metadata
    ids_in_metadata = pdf.find_in_metadata(arXiv.identifier_regex_compiled)
    assert not ids_in_metadata

    # No arXiv IDs in pdf text
    ids_in_text = pdf.find_in_text(arXiv.identifier_regex_compiled)
    assert not ids_in_text

    # Finds DOI in text
    ids_in_text = pdf.find_in_text(CrossRef.identifier_regex_compiled)
    assert ids_in_text
    assert doi in ids_in_text

    mdata = CrossRef.fetch_and_parse(doi)
    assert mdata['dc:title'] == "Smart drugs and neuroenhancement: what do we know?"
    # NOTE: metadata is missing authors
    assert not mdata['dc:creator']
