from bs4 import BeautifulSoup
import requests

URL_main = 'https://www.dlsu.edu.ph/'

def getLinks(url):
    # Fetch all the HTML source from the url
    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.select('a')
    links_text = []

    for link in links:
        if link.get('href') != None:
            if 'https://' in link.get('href'):
                if link.get('href') not in links_text:
                    links_text.append(link.get('href'))
            else:
                if link.get('href') not in links_text:
                    links_text.append(URL_main + link.get('href'))

    return links_text

for x in getLinks('https://www.dlsu.edu.ph/'):
    print(x)