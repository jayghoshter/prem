from pdfrw import PdfReader, PdfWriter, IndirectPdfDict, PdfDict
import pdfplumber
import os

class PDF:
    metadata: dict

    def __init__(self, filename=None):
        self.filename = filename
        self.metadata = {}
        self.pages = None

        self.load()

    def load(self, filename=None):
        filename = filename if filename else self.filename

        if not filename:
            return

        reader = PdfReader(filename)
        self.metadata = self._pdfdict_to_dict(reader.Info)
        self.pages = reader.pages

    def write(self, filename=None):
        filename = filename if filename else self.filename

        writer = PdfWriter()
        writer.addpages(self.pages)
        writer.trailer.Info = IndirectPdfDict(**self.metadata)
        writer.write(filename)

    def rename(self, newname):
        self.write(newname)
        os.remove(self.filename)
        self.filename = newname

    def _pdfdict_to_dict(self, data:PdfDict):
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
