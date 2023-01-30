#!/usr/bin/env python3

import argparse
import click
from pyfzf.pyfzf import FzfPrompt
import plumbum
from pathlib import Path

from rich import print
from ptdpy.utils import fetch_metadata
from ptdpy.utils import get_doi_from_pdf_metadata
from ptdpy.utils import modify_pdf_metadata
from ptdpy.utils import extract_from_crossref_metadata
from ptdpy.utils import extract_n_pdf_pages
from ptdpy.utils import query_title


def driver(fname): 
    """ Given a filename, get DOI (or search crossref), fetch metadata, and rename the file """
    doi = get_doi_from_pdf_metadata(fname)

    fzf = FzfPrompt()
    FZF_FILE_OPTS =  '--cycle --bind="ctrl-x:execute@xdg-open {}@" --bind="ctrl-y:execute@echo {} | xclip -i -selection clipboard@"'

    if doi: 
        mdata = fetch_metadata(doi)
        mdata = extract_from_crossref_metadata(mdata)
        outfname = f"{mdata['Year']} - {mdata['Author']} - {mdata['Title']}"
        modify_pdf_metadata(fname, mdata, outfname, rename=True)
    else: 
        text = extract_n_pdf_pages(fname, n=3)
        querystr = click.edit(text)
        if querystr: 
            print(f"Searching for {querystr}")
            crossref_matches = query_title(querystr)
            crossref_matches_processed = list(map(extract_from_crossref_metadata, crossref_matches))
            crossref_identifiers = list(map(lambda x: f"{x['Year']} - {x['Author']} - {x['Title']}", crossref_matches_processed))
            try: 
                selected = fzf.prompt(crossref_identifiers, FZF_FILE_OPTS)[0]
                selected_index = crossref_identifiers.index(selected)
                mdata = crossref_matches_processed[selected_index]
                modify_pdf_metadata(fname, mdata, selected, rename=True)
            except plumbum.commands.processes.ProcessExecutionError:
                pass

def main():

    ap = argparse.ArgumentParser()

    ap.add_argument("files", nargs = '*', help="PDF files to operate on")

    args = ap.parse_args()

    for current_file in args.files: 
        driver(current_file)

if __name__ == "__main__": 
    main()
