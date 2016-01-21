"""
from bibtexparser.compare_names import *

file = 'bibtexparser/tests/data/random.bib'

cleaner = AuthorOrganizer(file)

cleaner.clean_authors()
"""

import requests
import feedparser

"""
r = requests.get('http://api.crossref.org/works/works/10.1103/PhysRevA.62.052316')

info = r.json()

if 'message' in info:
    if 'URL' in info['message']:
        print(info['message']['URL'])

#print(info)


import urllib
url = 'http://export.arxiv.org/api/query?search_query=all:Methodology&for&quantum&logic&gate&construction&start=0&max_results=1'
data = urllib.request.urlopen(url).read()
#print(data)




content = requests.get('http://export.arxiv.org/api/query?search_query='
                       'all:+AND+yao+AND+andrew+AND+computations+AND+secure+AND+protocols+for&start=0&max_results=1')
info = str(content.text)
print(info)
"""
import xml.etree.ElementTree as ET

result = requests.get('http://export.arxiv.org/api/query?search_query='
                      'all:quantum+AND+copy+AND+protection+AND+quantum+AND+money'
                      '+AND+Scott+AND+Aaronson&start=0&max_results=1')

result = result.text
result = str(result)
print(result)


feed = feedparser.parse(result)

for entry in feed.entries:
    title = entry.title
print(title)



"""



###############
# CODE SKETCH #
###############

parse entry: title, if necessary authors

    insert this into arxiv api

get link to pdf

add link to full pdf to entry


#########

(for springer editions)

parse entry: doi, or else other information for arxiv

    insert this into arxiv/crossref api

get editors

add editors to (new) editor field in entry
"""