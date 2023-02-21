import pdfplumber
import os
from pikepdf import Pdf, Name
import re
from pathlib import Path

class PDF:
    doi_regex = r'10\.\d{4,9}/[A-Za-z0-9./:;()\-_]+'
    doi_regex_compiled = re.compile(doi_regex)

    filename: str
    name_template:str


    def __init__(self, filename=None, name_template="{year} - {author} - {title}.pdf"):
        self.filename = filename
        self.metadata = {}
        self.pages = None
        self.name_template = name_template
        self.pdf = None

        self.load()

    def __del__(self):
        self.unload()

    def load(self, filename=None):
        filename = filename if filename else self.filename

        if not filename:
            return

        self.pdf = Pdf.open(filename, allow_overwriting_input=True)
        self.metadata = self.pdf.open_metadata()
        self.metadata._updating = True
        self.metadata.register_xml_namespace('https://github.com/jayghoshter/prem', 'prem')
        self.pages = self.pdf.pages

        # Fix for malformed XML metadata
        try: 
            for k,v in self.metadata.items():
                pass
        except KeyError as e: 
            from lxml import etree as ET
            root = ET.fromstring(str(self.metadata))
            out = root.find(f'.//{e.args[0]}')
            outp = out.getparent()
            outp.remove(out)
            self.metadata._load_from(bytes(ET.tostring(root)))

    def update_metadata(self, indict):
        self.metadata.update(indict)
        self.metadata._apply_changes()

    def write(self, filename=None):
        if filename: 
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
        self.pdf.save(filename)

    def rename(self, newname=None, name_template=None):
        if not newname:
            newname = self.strtemplate_to_str(name_template)
        self.write(newname)
        if str(self.filename) != str(newname): 
            print(f"Renaming {self.filename} -> {newname}")
            os.remove(self.filename)
        self.filename = newname

    def find_in_metadata(self, pattern, flags=0):
        compiled_pattern = re.compile(pattern, flags)
        matches = []
        for k,v in self.metadata.items():
            if isinstance(v, str):
                res = compiled_pattern.findall(v)
            elif isinstance(v, list) or isinstance(v, set):
                res = compiled_pattern.findall(" ".join(str(v)))
            elif v is None:
                pass
            else:
                raise RuntimeError(f"Unknown metadata value type!\n{k}: {v} => {type(v)}")
            matches.extend(res)
        return matches

    def unload(self):
        self.metadata = {}
        self.pages = None
        if self.pdf:
            self.pdf.close()

    def pages_to_text(self, n=None):
        pdf = pdfplumber.open(self.filename)
        pages = pdf.pages[:n]
        text = ''
        for page in pages:
            text = text + '\n' +  page.extract_text()
        pdf.close()
        return text

    def strtemplate_to_str(self, strtemplate = None, mdata = None):
        """
        Given string template like strtemplate = "{year} - {author} - {title}", 
        find the corresponding keys and values in metadata dictionary and build a corresponding string.
        """
        if strtemplate is None:
            strtemplate = self.name_template
        if mdata is None:
            mdata = self.metadata

        strtemplate = strtemplate.lower()
        tags =  re.findall(r'{\w+}', strtemplate)
        values = list(map(lambda x: mdata['prem:' + x[1:-1]], tags))
        final_string = strtemplate
        for t,v in zip(tags, values):
            final_string = final_string.replace(t, str(v))

        if Path(final_string).suffix.lower() != '.pdf':
            final_string = final_string + '.pdf'

        return final_string
