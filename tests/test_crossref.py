from prem.sources import CrossRef

def test_crossref_doi():
    mdata = CrossRef.fetch_by_doi('10.52586/4948')
    assert mdata['title'][0] == 'Smart drugs and neuroenhancement: what do we know?'

def test_fetch_and_parse():
    doi = '10.1103/PhysRevD.13.191'
    mdata = CrossRef.fetch_and_parse(doi)

    assert mdata['dc:title'] == 'Black holes and thermodynamics'
    assert mdata['dc:creator'] == ['S. W. Hawking']
    assert mdata['dc:subject'] == set()
    assert mdata['crossmark:DOI'].lower() == doi.lower()
