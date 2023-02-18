# prem

**WORK IN PROGRESS**

Pdf REference Manager: Simple PDF file based CLI reference management. Prem means love in some Indian languages.

Rewritten from a bash script that I had built for my own pdf-file-based reference management system.

# Features

- Simple python CLI application
- No pdf renderer included
- Find article doi (from existing pdf metadata or within pdf text) 
- Fetch article metadata from crossref
- store article metadata in pdf metadata
- rename pdfs based on metadata

This allows us to work with just pdf files, and name and store them in any way we want. No additional metadata files. This also allows us to use tools like `ripgrepa`, `pdfgrep`, and `recoll` with our pdf library without duplication.

Another software to handle keywords is in the works. It might be incorporated into this project.

# Installation

```
pip install git+https://github.com/jayghoshter/prem
```

# Usage

```
prem [-a] [PDF_FILES...]
```

The `-a` or `--auto` flag essentially disables the manual query mode when no DOI is automatically found.

# Notes
- See requirements.compiled for a guaranteed working python dependency chain.
- Developed and tested on Linux with Zathura PDF reader.
- Uses `pikepdf` and `pdfrw` for reading and writing pdfs
- Uses `pdfplumber` for converting pdf to text when necessary
- Uses `click.edit()` for easy text editing
- Uses `pyfzf` for fuzzy selection
