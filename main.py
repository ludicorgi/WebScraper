from bs4 import BeautifulSoup
import requests, re, queue, threading, time

URL_main = 'https://www.dlsu.edu.ph/'
q_links = queue.Queue()
timeout = 0

consumer_threads=2

links_visited = []
links_scraped = []

class producer (threading.Thread):
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url=url

    def run(self):
        global q_links
        global timeout

        i = 1
        while True:
            q_links.put(i) 
            i += 1
            time.sleep(0.3)

            if time.time() > timeout:
                break

class consumer (threading.Thread):
    def __init__(self, thread_ID):
        threading.Thread.__init__(self)
        self.list=[]
        self.item=0
        self.ID=thread_ID

    def run(self):
        global q_links
        global timeout

        while True:
            self.item = q_links.get()
            print ("Consumer %i got an item %i \n"%(self.ID ,self.item))
            time.sleep(1)

            if time.time() > timeout:
                break

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

if __name__=="__main__":
    timeout = time.time() + 60*0.5
    c_threads_list=[]

    p = producer("url")

    for n in range(consumer_threads):
        c=consumer(n)
        c_threads_list.append(c)
        c.start()

    p.start()

    p.join()

    for c in c_threads_list:
        c.join()
        
# for x in getEmails('https://www.dlsu.edu.ph/offices/osa/constituent-offices/'):
#     print(x)
# getEmails('https://www.dlsu.edu.ph/offices/osa/constituent-offices/')