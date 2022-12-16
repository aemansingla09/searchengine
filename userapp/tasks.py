import json
from celery import shared_task
from django.utils.timezone import now
from .models import *
from .static.crawler.crawler import Crawler
import math,os


def index_content(content,site_id):
    '''
    TF-IDF based
    
    Index pages, update already exisiting indexes , store in memory first then store to db
    '''
    with open(os.path.join(os.getcwd(),"userapp/static/crawler/stopwords.txt")) as file:
        sw = file.read().split("\n")
        
    df_data={}
    tf_data={}
    idf_data={}
    
    for page in content:
        tf = {}
        title = page['Title'] 
        description = page['Description']
        link = page['Link']
        list_word = (title + " " + description).split(" ")
        
        for word in list_word :
            word = word.strip()
            
            if len(word) == 0:
                continue
            
            if word in sw:
                continue
            
            
            
            #tf term frequency
            if word in tf :
                tf[word] += 1
            else :
                tf[word] = 1

                #df document frequency
                if word in df_data :
                    df_data[word] += 1
                else :
                    df_data[word] = 1

        tf_data[link] = tf
        
    # Calculate Idf
    for x in df_data :
        idf_data[x] = 1 + math.log10(len(tf_data)/df_data[x])

    for word in df_data:
        for page in content:
            tf_value = 0

            if word in tf_data[page['Link']] :
                tf_value = tf_data[page['Link']][word]

            weight = tf_value * idf_data[word]

            

            if weight != 0 :
                # for word -> link_id,score
                siteindex,is_created = SiteIndexer.objects.update_or_create(site_id = site_id,link_id = page['Link'],word = word,defaults={'score':weight})

        

@shared_task
def start_crawl(site_id):
    '''
    Recieves a site with crawl_status active
    It crawls a site and updates site properites
    '''
    
    site = UserSites.objects.get(site_id = site_id)
    site.crawler_status = True
    site.save()
    
    root_url = site.domain

    print(f"BEGIN Crawling for {root_url} by {site.owner}")
    
    crawlprocess = Crawler(10) # Crawler(site.links_limit)
    crawlprocess.start_crawl(initial_links = [root_url,])
    
    content = []
    for link_info in crawlprocess.links_crawled:
        try:
            content.append(json.loads(link_info))
        except:
            continue
    
    print(f"DONE Crawling for {root_url} by {site.owner}. BEGIN INDEXING")
    
    # Updating Site Links
    for link_info in content:
        link = link_info['Link']
        status = str(link_info['Status'])
        
        sitelink,is_created = SiteLinks.objects.update_or_create(site_id = site,url = link,defaults={'response_code':status,'title':link_info.get('Title',"")})
        
        link_info['Link'] = sitelink.link_id
    
    index_content(content,site_id)
        
    print(f"DONE Indexing for {root_url} by {site.owner}")
    
    
    site.links_fetched = SiteLinks.objects.filter(site_id=site).count()
    site.crawler_status = False
    site.last_crawled = now()
    site.save()
    
    
    
