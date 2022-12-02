from bs4 import BeautifulSoup
import requests, re
import time

URL_main = 'https://www.dlsu.edu.ph/'
links_visited = []
links_scraped = []

def getLinks(url):
    response = requests.get(url)
    bs = BeautifulSoup(response.text, 'html.parser')
    links = bs.select('a')
    links_text = []

    for link in links:
        if link.get('href') != None:
            if 'https://' in link.get('href') or 'http://' in link.get('href'):
                newlink = link.get('href')
            elif link.get('href').startswith('www'):
                newlink = 'https://' + link.get('href')
            else:
                newlink = URL_main + link.get('href')
            
            newlink = re.sub(r'(?<=\w)(\/\/\/|\/\/)(?=\w)', "/", newlink) #remove extra slashes

            if newlink not in links_text and newlink.startswith('https://www.dlsu.edu.ph'):
                links_text.append(newlink)

    return links_text

def getEmails(url):
    re_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    response = requests.get(url)
    bs = BeautifulSoup(response.text, 'html.parser')

    emails = bs.select('span.__cf_email__')
    emails_text = []

    for email in emails:
        if(re.search(re_email, cfDecodeEmail(email.get('data-cfemail')))):
            emails_text.append(cfDecodeEmail(email.get('data-cfemail')))
    
    return emails_text

def cfDecodeEmail(encodedString):
    r = int(encodedString[:2],16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email

# for x in getEmails('https://www.dlsu.edu.ph/offices/osa/constituent-offices/'):
#     print(x)
# getEmails('https://www.dlsu.edu.ph/offices/osa/constituent-offices/')