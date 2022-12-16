from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
import uuid
    
class UserSites(models.Model):
    site_id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    owner = models.EmailField(help_text = "Managed by user")
    domain = models.URLField(help_text = "Site URl where to index")
    alias = models.CharField(max_length = 1000,help_text = "Alias for your site url. Max 1000 chars allowed")
    contact = models.EmailField(help_text="For Contact Purposes. Enter a valid email")
    
    links_limit = models.IntegerField(default = 1,validators=[MaxValueValidator(1000), MinValueValidator(1)],help_text = "Max number of links to index. MAX 1000 allowed.")
    links_fetched = models.IntegerField(default = 1)
    last_crawled = models.DateTimeField(auto_now_add = True)
    crawler_status = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('owner', 'domain')
    
class SiteLinks(models.Model):
    link_id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    site_id = models.ForeignKey(UserSites,on_delete = models.CASCADE)
    url = models.URLField()
    title = models.TextField(blank = True)
    response_code = models.CharField(default = 'NA',max_length  = 10)
    class Meta:
        unique_together = ('url','site_id')

class SiteIndexer(models.Model):
    word = models.CharField(max_length = 200)
    site_id = models.UUIDField(blank = False)
    link_id = models.UUIDField(blank = False)
    score = models.FloatField(blank = False)
    
    class Meta:
        unique_together = ('site_id','word','link_id')
    