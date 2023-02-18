from ptdpy import CrossRef

def test_crossref_doi():
    cr = CrossRef()
    mdata = cr.fetch_by_doi('10.52586/4948')
    assert mdata['title'][0] == 'Smart drugs and neuroenhancement: what do we know?'
