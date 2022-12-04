from bs4 import BeautifulSoup
import requests, re, queue, threading, time

shared_resource_lock=threading.Lock()
terminated = False
links_scraped = []
emails_scraped = []

URL_main = 'https://www.dlsu.edu.ph/'
q_links = queue.Queue()
q_links_copy = queue.Queue()

links_visited = []


program_timeout = 0
consumer_threads = 1

class producer (threading.Thread):
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.url=url

    def run(self):
        global q_links
        global program_timeout
        temp_links = []
        while True:
            if time.time() > program_timeout:
                output_stats(self.url)
                break

            if(self.url not in links_visited):
                print("accessing " + self.url)
                response = requests.get(self.url)

                bs = BeautifulSoup(response.text, 'html.parser')
                links = bs.select('a')
                links_text = []

                for link in links:
                    if time.time() > program_timeout:
                        output_stats(self.url)
                        break

                    if link.get('href') != None:
                        if 'https://' in link.get('href') or 'http://' in link.get('href'):
                            newlink = link.get('href')
                        elif link.get('href').startswith('www'):
                            newlink = 'https://' + link.get('href')
                        else:
                            newlink = URL_main + link.get('href')
                        
                        newlink = re.sub(r'(?<=\w)(\/\/\/|\/\/)(?=\w)', "/", newlink) #remove extra slashes

                        temp_links.append(newlink)

                        if temp_links.count(newlink) < 2 and newlink.startswith('https://www.dlsu.edu.ph'):
                            links_text.append(newlink)
                            # this file is just for testing, will remove this
                            # with open("links_list.txt", "a") as f:
                            #     f.write(newlink + '\n')
                            q_links.put(newlink)
                            q_links_copy.put(newlink)
                
                links_visited.append(self.url)
                print("link done " + self.url + " " + str(len(links_text)) + " links added" )
                
            self.url = q_links_copy.get(timeout=5)
            #print(q_links.qsize())

class consumer (threading.Thread):
    def __init__(self, thread_ID, url):
        threading.Thread.__init__(self)
        self.list=[]
        self.item=0
        self.ID=thread_ID
        self.url=url

    def run(self):
        global q_links
        global program_timeout
        global emails_scraped

        re_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        while True:
            if time.time() > program_timeout:
                output_stats(self.url)
                break

            self.item = q_links.get()
            # print ("Consumer %i got an item %i \n"%(self.ID ,self.item))
            # time.sleep(1)

            response = requests.get(q_links.get())
            bs = BeautifulSoup(response.text, 'html.parser')

            emails = bs.select('span.__cf_email__')

            for email in emails:
                if time.time() > program_timeout:
                    output_stats(self.url)
                    break

                if(re.search(re_email, cfDecodeEmail(email.get('data-cfemail')))):
                    with shared_resource_lock:
                        if(cfDecodeEmail(email.get('data-cfemail')) not in emails_scraped):
                            decoded_email = cfDecodeEmail(email.get('data-cfemail'))
                            emails_scraped.append(decoded_email)
                            with open("emails_list.csv", "a") as f:
                                f.write(decoded_email + '\n')
                            print("email added " + cfDecodeEmail(email.get('data-cfemail')))

            with shared_resource_lock:
                links_scraped.append(self.item)
                print('consumed ' + self.item)
                
def cfDecodeEmail(encodedString):
    r = int(encodedString[:2],16)
    email = ''.join([chr(int(encodedString[i:i+2], 16) ^ r) for i in range(2, len(encodedString), 2)])
    return email

def output_stats(url):
    global shared_resource_lock
    global terminated
    global links_scraped
    global emails_scraped
    
    with shared_resource_lock:
        if (not terminated):
            with open("website_stats.txt", "w") as f:
                f.write(url + ', ' + str(len(links_scraped)) + 'pages scraped, ' + str(len(emails_scraped)) + ' email addresses found')
            
            print("Time's up!")
            terminated = True



if __name__=="__main__":

    open("emails_list.csv", 'w').close()

    url = input('Enter URL: ') #'https://www.dlsu.edu.ph/offices/osa/constituent-offices/'
    in_time = float(input('Enter time (in minutes): '))
    program_timeout = time.time() + 60 * in_time
    consumer_threads = int(input('Enter number of consumer threads: '))
    c_threads_list=[]

    p = producer(url)

    for n in range(consumer_threads):
        c=consumer(n, url)
        c_threads_list.append(c)
        c.start()

    p.start()

    p.join()

    for c in c_threads_list:
        c.join()