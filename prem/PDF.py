from pdfrw import PdfReader, PdfWriter, IndirectPdfDict, PdfDict
import pdfplumber
import os
from pikepdf import Pdf, Name
import re
from pathlib import Path

class PDF:
    metadata: dict

    def __init__(self, filename=None, engine='pikepdf', name_template="{year} - {author} - {title}.pdf"):
        self.filename = filename
        self.metadata = {}
        self.pages = None
        self.engine = engine
        self.name_template = name_template

        if self.engine == 'pikepdf':
          self.load = self._load_pikepdf
          self.write = self._write_pikepdf
        elif self.engine == 'pdfrw':
          self.load = self._load_pdfrw
          self.write = self._write_pdfrw
        else:
          raise ValueError(self.engine)


        self.load()

    def _load_pdfrw(self, filename=None):
        filename = filename if filename else self.filename

        if not filename:
            return

        reader = PdfReader(filename)
        self.metadata = self._pdfrwdict_to_dict(reader.Info)
        self.pages = reader.pages

    def _load_pikepdf(self, filename=None):
        filename = filename if filename else self.filename

        if not filename:
            return

        with Pdf.open(filename) as pdf:
            try:
                self.metadata = {f"{str(k)[1:]}": str(v) for k,v in pdf.docinfo.items()}
            except Exception as e:
                print(f"ERROR: Unknown error reading pdf metadata (docinfo) for file {filename}.")
                print(f"{e.__class__.__name__}: {e}")
            self.pages = pdf.pages

    def _write_pdfrw(self, filename=None):
        filename = filename if filename else self.filename

        writer = PdfWriter()
        writer.addpages(self.pages)
        writer.trailer.Info = IndirectPdfDict(**self.metadata)
        writer.write(filename)

    def _write_pikepdf(self, filename=None):
        with Pdf.open(self.filename, allow_overwriting_input=True) as pdf:
            for k,v in self.metadata.items(): 
                key = f"/{k}"
                pdf.docinfo[key] = v
            with pdf.open_metadata() as meta:
                meta.load_from_docinfo(pdf.docinfo)
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            pdf.save(filename)

    def rename(self, newname=None, name_template=None):
        if not newname:
            newname = self.strtemplate_to_str(name_template)
        self.write(newname)
        if str(self.filename) != str(newname): 
            print(f"Renaming {self.filename} -> {newname}")
            os.remove(self.filename)
        self.filename = newname

    def _pdfrwdict_to_dict(self, data:PdfDict):
        return { k[1:] : str(v)[1:-1].replace('\\', '') for k,v in data.items() }

    def unload(self):
        self.metadata = {}
        self.pages = None

    def pages_to_text(self, n=None):
        pdf = pdfplumber.open(self.filename)
        pages = pdf.pages[:n]
        text = ''
        for page in pages:
            text = text + page.extract_text()
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
        values = list(map(lambda x: mdata[x[1:-1].capitalize()], tags))
        final_string = strtemplate
        for t,v in zip(tags, values):
            final_string = final_string.replace(t, str(v))
        return final_string
