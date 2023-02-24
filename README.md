# prem

**WORK IN PROGRESS**: This is alpha code. Please backup your data before using this on your pdfs.

Pdf REference Manager: Simple PDF file based CLI reference management. Prem means love in some Indian languages.

Rewritten from a bash script that I had built for my own pdf-file-based reference management system.

# Features

- Simple python CLI application
- No pdf renderer included
- Find article doi (or any supported identifier) from existing pdf metadata or within pdf text
- Fetch article metadata from crossref (or any other supported source)
- store article metadata in pdf metadata
- rename pdfs based on metadata
- Source/identifier combos supported:
    - CrossRef/DOI
    - arXiv/arXivID

This allows us to work with just pdf files, and name and store them in any way we want. No additional metadata files. This also allows us to use tools like `ripgrepa`, `pdfgrep`, and `recoll` with our pdf library without duplication.

Another software to handle keywords is in the works. It might be incorporated into this project.

# Installation

```
pip install git+https://github.com/jayghoshter/prem
```

## Dependencies

- See requirements.compiled for a guaranteed working python dependency chain.
- Developed and tested on Linux with Zathura PDF reader.
- Uses `pikepdf` for reading and writing pdfs
- Uses `pdfplumber` for converting pdf to text when necessary
- Uses `click.edit()` for easy text editing
- Uses `pyfzf` for fuzzy selection

# Usage

```
prem [ARGS | FLAGS] [PDF_FILES...]
```

- The `-a` or `--auto` flag essentially disables the manual query mode when no identifier is automatically found.
- The `-s` or `--sources` argument expects a list of sources. Choices are any of `['crossref', 'arxiv']`
- The `-b` or `--bib` argument fetches bibliography info from `doi.org` and dumps it into the provided argument (or `ref.bib` by default)
- The `-nt` or `--name-template` argument takes a string templated with curly braces to generate pdf names:
    - e.g., `"{year} - {author} - {title}"` will result in the pdf being renamed in that manner. 
    - Only the above tags are currently supported, 
    - `{author}` resolves to the last name of the first author when known.
- The `-d` or `--doi` argument takes a known DOI and fetches info an renames a given pdf.
- The `-m` or `--mode` argument allows switching between the new default `complete` and `classic` modes. 
    - `complete` mode: search pdf metadata and text together for identifiers (DOI/arXivID)
    - `classic` mode: search pdf metadata -> search pdf text
    - Complete mode doesn't ignore secondary sources if only one is found in the metadata.
    - Classic mode will be faster for newer pdfs with identifiers existing within the metadata

# Notes
- Running the script in `--auto` mode might result in a wrong doi and bad metadata due to incorrect parsing of pdf text. Typically this would result in an invalid DOI, but a valid DOI for another journal article is not impossible.
- Built with pdfs of journal articles in mind. Currently not considering books and other volumes.
- Sometimes CrossRef and doi.org have bad/unsanitized titles: 
    - http://dx.doi.org/10.1002/btpr.3065
    - https://dx.doi.org/10.1117/12.363723
    - They are sanitized by prem, but in case some patterns are buggy or incorrect, please report them.
    - only titles are sanitized currently
- DOIs and identifiers in general evolve and have evolved over time. This means that the current regex might not work well for really old pdfs with different schemes. I will eventually fix this.

# Reporting issues and bugs
If you encountered a bug or would like to report odd behavior, please open an issue on the GitHub page with a detailed description. You are also welcome to submit a PR.
