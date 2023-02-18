import shutil
import tempfile
import requests
import os
from fake_useragent import UserAgent


PDF_LINKS = {
        'origin_of_gravity': 'https://www.rroij.com/open-access/the-origin-of-gravity.pdf',
        'smart_drugs_and_neuroenhancement': 'https://www.imrpress.com/journal/FBL/26/8/10.52586/4948/pdf',
        'neuroscience_education': 'https://cursos.aiu.edu/Avances%20de%20las%20neurociencias%20aplicadas%20a%20la%20Educaci%C3%B3n/PDF/Tema%202.pdf',
        'black_holes': 'https://www.relativitycalculator.com/X-Cart/files/attachments/432/Hawking_black_holes_thermodynamics.pdf'
        }

def get_pdf(key, filename=None, headers=None):
    cachefile = f'{os.environ["HOME"]}/.cache/prem/{key}.pdf'
    filename = filename if filename else f"/tmp/prem/{next(tempfile._get_candidate_names())}.pdf"

    ua = UserAgent()

    if not headers:
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36'}

    if not os.path.isfile(cachefile):
        r = requests.get(PDF_LINKS[key], stream=True, headers=headers)
        if r.status_code == 200:
            with open(cachefile, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        else:
            print(r.content)
            raise RuntimeError(r)
    
    shutil.copy(cachefile, filename)

    return filename
