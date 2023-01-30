import requests
from addict import Dict

class Source:
    def __init__(self):
        self.BASE_URL = ""


class CrossRef(Source):
    def __init__(self):
        self.BASE_URL = "https://api.crossref.org/works"

    def fetch_by_doi(self, doi:str):
        response = requests.get(f"{self.BASE_URL}/{doi}")

        if not response.ok: 
            raise RuntimeError(f"Error fetching data for doi: {doi}")

        return Dict(response.json()["message"])

    def query(self, string):
        """ Given a title string, return search results """
        response = requests.get(f"{self.BASE_URL}?query={string}")
        
        if not response.ok: 
            print(response)
            raise RuntimeError(f"Error querying for string: {string}")

        result = Dict(response.json()["message"])

        return result["items"]

