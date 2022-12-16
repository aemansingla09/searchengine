from django.shortcuts import render,redirect
from django.urls import reverse
from allauth.account.decorators import login_required
from django.contrib import messages
from django.utils.http import urlencode

from userapp.tasks import start_crawl
from .models import *
from .forms import *

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .helpers import clean_url
import requests


def userpage(request):
    '''
    URL: /
    name: user-page
    '''
    
    sites = None
    if not request.user.is_anonymous:
        sites = UserSites.objects.filter(owner = request.user.email)
    
    return render(request,'userapp/mysites.html',{'sites':sites})


@login_required
def addsite(request):
    '''
    url : site/add/
    name : add-site
    '''
    siteform = SiteForm(request.POST or None)
    
    if request.POST :
        print(request.POST)
        if siteform.is_valid():
            data = siteform.cleaned_data
            data['domain'] = clean_url(data['domain'])
            try:
                site = UserSites.objects.create(**data)
                SiteLinks.objects.create(site_id = site,url = data.get('domain'))
                return redirect('start-crawl',site_id = site.site_id)
            except Exception as e: # Same Site is given again
                print(e)
                messages.error(request,'Please enter a unique domain')

    return render(request,'userapp/addsite.html',{'form':siteform})

@login_required
def listurls(request,site_id):
    try:
        query = request.GET.get('q',"")
        
        site = UserSites.objects.get(site_id = site_id)
        links = SiteLinks.objects.filter(site_id = site)
        
        if query:
            links = links.filter(url__contains = query)
    except:
        messages.error(request,'Access to Invalid Page')
        return redirect(reverse('user-page'))
        
    return render(request,'userapp/listurls.html',{'links':links,'q':query})

@login_required
def deleteurl(request,link_id):
    
    try:
        link = SiteLinks.objects.get(link_id = link_id)
        site = link.site_id
        link.delete()
        
        site.links_fetched = site.links_fetched - 1
        site.save()
        
        links = SiteLinks.objects.filter(site_id = site)
    
    except:
        messages.error(request,'Access to Invalid Page')
        return redirect(reverse('user-page'))
    
    return render(request,'userapp/listurls.html',{'links':links})

@login_required
def deletesite(request,site_id):
    
    try:
        site = UserSites.objects.get(site_id = site_id)
        site.delete()
    except:
        messages.error(request,'Invalid Operation')
    
    return redirect(reverse('user-page'))

@login_required
def initiatecrawl(request,site_id):
    '''
    start_crawl automatically updates site properties
    '''
    site = UserSites.objects.get(site_id = site_id)
    
    if not site.crawler_status:
        start_crawl.delay(site_id)
    

    return redirect(reverse('user-page'))

@login_required
def demosearch(request,site_id):
    try:
        query = request.GET.get('q',"")
        
        links = []
        
        #Api url : /api/{site_id}/search
        if query:
            api_url = "https://custom-search-engine.azurewebsites.net" + reverse('search-query',kwargs={'site_id':site_id})
            response = requests.get(api_url,params={'q':query})
            if response.status_code == 200:
                links = response.json().get('data')
            
            
    except Exception as e:
        messages.error(request,'Access to Invalid Page')
        return redirect(reverse('user-page'))
        
    return render(request,'userapp/demosearch.html',{'links':links,'q':query})

class SearchQueryAPI(APIView):
    def get(self,request,site_id):
        
        query = request.query_params.get('q',"")
        
        if not query:
            return Response(data = {'message':"Provide a query",'data':[]},status=status.HTTP_400_BAD_REQUEST)
        q_words = query.strip().split(" ")
        link_scores = {}
        for q in q_words:
            q = q.strip()
            if len(q) == 0:
                continue
            try:
                sites = SiteIndexer.objects.filter(site_id = site_id,word = q)   
                
                for site in sites:
                    if site.link_id in link_scores:
                        link_scores[site.link_id] += site.score
                    else:
                        link_scores[site.link_id] = site.score
            except:
                continue
            
        scores_list = []
        for link,score in link_scores.items():
            scores_list.append([score,link])
        
        results= []
        for score,link_id in sorted(scores_list, key = lambda k: k[0], reverse=True): 
            try:
                site = SiteLinks.objects.get(link_id = link_id,site_id = site_id)
                results.append({'url': site.url,'title':site.title})
            except:
                continue
        
        return Response(data = {'message':"Success",'q':query,'data':results},status=status.HTTP_200_OK)
