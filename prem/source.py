import requests
from addict import Dict
from prem.utils import fetch_metadata_crossref

class Source:
    def __init__(self):
        self.BASE_URL = ""


class CrossRef(Source):
    def __init__(self):
        self.BASE_URL = "https://api.crossref.org/works"

    def fetch_by_doi(self, doi:str):
        return fetch_metadata_crossref(doi)

    def query(self, string):
        """ Given a title string, return search results """
        response = requests.get(f"{self.BASE_URL}?query={string}")

        if not response.ok: 
            print(response)
            raise RuntimeError(f"Error querying for string: {string}")

        result = Dict(response.json()["message"])

        return result["items"]

