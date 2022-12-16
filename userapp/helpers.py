from w3lib.url import url_query_cleaner
from url_normalize import url_normalize
import re

def clean_url(u)->str:
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
    
def clean_str(text) :
    text = (text.encode('ascii', 'ignore')).decode("utf-8")
    text = re.sub("&.*?;", "", text)
    text = re.sub(">", "", text)    
    text = re.sub("[\]\|\[\@\,\$\%\*\&\\\(\)\":]", "", text)
    text = re.sub("-", " ", text)
    text = re.sub("\.+", "", text)
    text = re.sub("^\s+","" ,text)
    text = text.lower()
    return text