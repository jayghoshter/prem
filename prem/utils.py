import requests
import os
import re
from joblib import Memory
from pathlib import Path
import subprocess
import readline
from prem import logger

CACHE_DIR = f"{os.environ['HOME']}/.cache/prem"
memory = Memory(location=CACHE_DIR, verbose=0)

@memory.cache
def fetch_bibliography(doi:str):
    """
    Fetch citation as bibtex string from dx.doi.org for given DOI
    """
    header = {'Accept': 'text/bibliography; style=bibtex'}
    response = requests.get(f"https://dx.doi.org/{doi}", headers=header)

    if not response.ok: 
        logger.err(f"Error fetching bibtex for doi: {doi}", indent_level=1)
        return ''

    return response.text.lstrip()


def find_generic_pdf_opener_linux():
    """
    Find the default pdf opener in Linux
        - Use xdg-mime
        - Search XDG directories for .desktop
        - Parse file and find command
    """
    xdg_query = subprocess.run(['xdg-mime', 'query', 'default', 'application/pdf'], capture_output=True)
    default_app_xdg_str = xdg_query.stdout.strip().decode()

    HOME=Path(os.environ['HOME'])
    xdg_user_dir= os.environ.get('XDG_DATA_HOME', None) or str(HOME/'.local/share')
    xdg_system_dirs = os.environ.get('XDG_DATA_DIRS', '') or '/usr/local/share/:/usr/share/'
    search_dirs = xdg_system_dirs.split(':')
    search_dirs.append(xdg_user_dir)
    search_dirs = map(lambda p: Path(p) / 'applications', search_dirs)

    app_name = None

    for dir in search_dirs: 
        if dir.exists():
            files = [ x for x in dir.rglob(default_app_xdg_str) ]
            if files:
                desktop_file = files[0]
                with open(desktop_file, 'r') as fp:
                    lines = fp.read()
                    app_name = re.search(r'^Exec\s*=\s*(\w+).*\n', lines, re.MULTILINE)
                break

    if app_name:
        return app_name.group(1)
    else:
        raise RuntimeError("Could not find default pdf application command!")

def generic_open_linux(fname):
    """
    Open a pdf file using the system default in Linux.
    Return the subprocess object
    """
    app = find_generic_pdf_opener_linux()
    return subprocess.Popen([app, fname])

def string_sanitizer(string):
    sanity_dict = {
            r'\n': ' ',
            r'/' : ' ',
            r'\s+': ' ',
            r'<[^>]*>(.*)<[^>]*>': r'\1',
            }

    for k,v in sanity_dict.items():
        string = re.sub(k, v, str(string))

    return string

def input_with_prefill(prompt, text):
    def hook():
        readline.insert_text(text)
        readline.redisplay()
    readline.set_pre_input_hook(hook)
    result = input(prompt)
    readline.set_pre_input_hook()
    return result
