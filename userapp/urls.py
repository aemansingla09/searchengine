from django.urls import path
from .views import *

urlpatterns = [
    path('',userpage,name='user-page'),
    path('site/add/',addsite,name='add-site'),
    path('site/urls/<uuid:site_id>',listurls,name='list-urls'),
    path('site/demo/<uuid:site_id>',demosearch,name='demo-search'),
    path('site//urls/delete/<uuid:link_id>',deleteurl,name='delete-url'),
    path('site/delete/<uuid:site_id>',deletesite,name='delete-site'),
    
    path('site/crawl/init/<uuid:site_id>',initiatecrawl,name='start-crawl'),
    
    path('api/<uuid:site_id>/search',SearchQueryAPI.as_view(),name='search-query'),
]