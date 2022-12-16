from django import forms
from .models import *

class SiteForm(forms.ModelForm):
    class Meta:
        model = UserSites
        fields = ['domain','links_limit','alias','contact','owner']
        widgets = {
            'links_limit': forms.NumberInput(attrs={'type':'range','max':1000,'min':0,'step':10,'id':'myRange'}),
        }