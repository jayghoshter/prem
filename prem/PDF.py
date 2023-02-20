from pdfrw import PdfReader, PdfWriter, IndirectPdfDict, PdfDict
import pdfplumber
import os
from pikepdf import Pdf, Name

class PDF:
    metadata: dict

    def __init__(self, filename=None, engine='pikepdf'):
        self.filename = filename
        self.metadata = {}
        self.pages = None
        self.engine = engine

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
            pdf.save(filename)

    def rename(self, newname):
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
