from bs4 import BeautifulSoup
import requests

URL = "https://requests.readthedocs.io/en/latest/"

response = requests.get(URL)
soup = BeautifulSoup(response.content, "html.parser")
for header in soup.find_all("h2"):
    print(header.content)
