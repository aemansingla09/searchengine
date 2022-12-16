from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from w3lib.url import url_query_cleaner
from url_normalize import url_normalize
import json
from requests_html import HTMLSession
import random


class Crawler:
    __STATUS = bool(False) # Whether Crawler Running or Idle
    links_crawled = [] # Crawled Links
    __crawl_links = [] #New Links to be crawled
    unknown_patterns = [] 
    target_links = 0 #How much links to be crawled
    RETRY_COUNT = 5 # If link not responding, retry how many times

    def __init__(self,target_links = 0):
        self.target_links = target_links

        # chrome_options = Options()
        # chrome_options.add_argument("--disable-extensions")
        # chrome_options.add_argument("--headless")
        
        
        # chrome_driver_path= os.path.abspath(glob(os.path.join("userapp","static","crawler","chromedriver",sys.platform  + "*"))[0])
        # os.chmod(chrome_driver_path, 755)
        # self.__driver = webdriver.Chrome(options=chrome_options,executable_path=chrome_driver_path,service_log_path='selenium_logs.txt',)
        # self.__driver.implicitly_wait(5)
        

    
    # def __del__(self):
    #     try:
    #         self.__driver.quit()
    #         self.__driver.close()
    #     except:
    #         pass
        
        

    def get_status(self):
        return self.__STATUS
        
    def is_crawable_tag(self,a_tag)->bool:
        '''
        Not all links are crawlable.
        Check rel attribute of <a> 
        '''
        flag = True

        try:
            if re.search("nofollow|license|noopener",str(a_tag["rel"]))!= None:
                flag=False
        except:
            pass

        return flag

    def clean_url(self,u)->str:
        u = url_normalize(u)
        u = url_query_cleaner(u,parameterlist = ['utm_source','utm_medium','utm_campaign','utm_term','utm_content'],remove=True)

        # if u.startswith("http://"):
        #     u = u[7:]
        # if u.startswith("https://"):
        #     u = u[8:]
        # if u.startswith("www."):
        #     u = u[4:]
        
        if u.endswith("/"):
            u = u[:-1]
        return u
    
    def clean_str(self,text) :
        text = (text.encode('ascii', 'ignore')).decode("utf-8")
        text = re.sub("&.*?;", "", text)
        text = re.sub(">", "", text)    
        text = re.sub("[\]\|\[\@\,\$\%\*\&\\\(\)\":]", "", text)
        text = re.sub("-", " ", text)
        text = re.sub("\.+", "", text)
        text = re.sub("^\s+","" ,text)
        text = text.lower()
        return text
    
    def start_crawl(self,initial_links=[])->None:
        #If cache exists, update __crawl_links
        try: 
            with open('cache.json') as cache:
                self.__crawl_links = set(json.load(cache))
        except:
                pass
        
        self.__driver = HTMLSession()
        self.links_crawled = [] # Crawled Links
        self.__crawl_links = [] #New Links to be crawled
        
        #Check Initial Links,skipping it
        for link in initial_links:
            self.__crawl_links.append(self.clean_url(link))

        # crawl_links shouldn't be empty
        if len(self.__crawl_links) == 0:
            raise Exception("No url is given, provide a new links")

        self.__STATUS = True

        #Start Crawling
        while True:
            if len(self.links_crawled) >= self.target_links or len(self.__crawl_links)==0:
                break
            
            if not self.__STATUS:
                print("Crawler Stopped by Request")
                break
            
            link = self.__crawl_links.pop(random.randrange(len(self.__crawl_links)))
            

            # if link not in Database:
            self.crawl_urls(link)

        self.__driver.close()
        self.__STATUS = False
        
    def force_stop_crawl(self):
        self.__STATUS = False

    def save_crawl_state(self):

        #Dump to database, in future
        with open('data.json','a',encoding='utf-8') as data:
            json.dump(self.links_crawled,data,indent=4)


        with open('cache.json','w',encoding='utf-8') as data:
            json.dump(list(self.__crawl_links),data)
        
        self.links_crawled = []
        self.__crawl_links = []

    def crawl_urls(self,link):

        page_info ={"Title":"",
                "Description":"",
                "Status":"",
                "Link":""}
        
        try:
            response = self.__driver.get(link)
        except Exception as e:
            page_info["Status"] = 500
            print(f"ERROR while fetching {link}. Skipping \nCAUSE of Error : {e}\n")
            return
        
        try:
            response.html.render(timeout = 20)
        except:
            print(f'Skipping rendering for {link}')
            pass
        
        try:
            html_page = BeautifulSoup(response.html.html,'lxml')

            page_info["Title"] = self.clean_str(html_page.title.text)
            page_info["Link"] = self.clean_url( response.url) # Cleaned URL
            page_info["Status"] = response.status_code
        except Exception as e:
            print(f"Error in parsing {link}. Cause:{e}\n")
        
        try:
            page_info["Description"] = self.clean_str(html_page.find('meta',attrs={"name": "description"}).get('content'))
            
            for h_tag in html_page.find_all(['h1','h2','h3']):
                page_info['Description'] += " " + self.clean_str(h_tag.text.strip())
                
        except:
            pass
        
        for a_tag in html_page.find_all('a',href=True):# Only if href present

            if not self.is_crawable_tag(a_tag):
                continue

            url = a_tag['href']
            
            
            if re.search("^mailto:|^javascript:|^#",url):
                continue
            
            elif re.search("^https?://",url) == None: 

                if re.search("^//?|^[a-zA-Z1-9]|^..?/|^\?",url):  # Conversion of Relative path to Absolute Path
                    url = str(urljoin(link,url))
                
                else:
                    self.unknown_patterns.append(url)
                    continue
            url = self.clean_url(url)
            if url not in self.__crawl_links:
                self.__crawl_links.append(url)
        
        print(f"Crawled {link}")
        self.links_crawled.append(json.dumps(page_info,indent=4))
    

# if __name__ == "__main__":
    

#     C = Crawler(target_links = 100)
#     C.start_crawl()
#     C.stop_crawl()




