# -*- coding: utf-8 -*-
#harvest theses from Melbourne U.
#JH: 2022-05-08
#FS: 2023-03-26

import getopt
import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
from time import sleep
from urllib.request import urlopen
from json import loads

pages = 3
skipalreadyharvested = True

jnlfilename = 'THESES-MELBOURNE-%s' % (ejlmod3.stampoftoday())
publisher = 'U. Melbourne (main)'

recs = []
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

def get_sub_site(url):
    print("[%s] --> Harversting Data" % url)
    sleep(5)

    rec = {'tc': 'T', 'jnl': 'BOOK', 'artlink': url}
    data = loads(urlopen(url).read())
    rec_data = data.get('metadata')

    # Get the author
    rec['autaff'] = []
    raw_author_section = rec_data.get('dc.contributor.author')
    for i in raw_author_section:
        rec['autaff'].append([i.get('value'), publisher])

    # Get the Date
    rec['date'] = rec_data.get('dc.date.issued')[0].get('value')

    # Get the abstract
    try:
        rec['abs'] = rec_data.get('dc.description.abstract')[0].get('value')
    except:
        pass

    # Get the handle
    rec['hdl'] = re.sub('.*handle.net\/', '', rec_data.get('dc.identifier.uri')[0].get('value'))
    rec['link'] = 'http://hdl.handle.net/' + rec['hdl']

    # Get keywords
    rec['keyw'] = []
    if rec_data.get('dc.subject') is not None:
        for keyword in rec_data.get('dc.subject'):
            rec['keyw'].append(keyword.get('value'))

    # Get title
    rec['tit'] = rec_data.get('dc.title')[0].get('value')

    # Get the supervisor
    rec['supervisor'] = []
    if rec_data.get('melbourne.thesis.supervisorothername') is not None:
        for supervisor in rec_data.get('melbourne.thesis.supervisorname') + rec_data.get('melbourne.thesis.supervisorothername'):
            rec['supervisor'].append([supervisor.get('value')])
    elif rec_data.get('melbourne.thesis.supervisorname') is not None:
        for supervisor in rec_data.get('melbourne.thesis.supervisorname'):
            rec['supervisor'].append([supervisor.get('value')])

    # Get pdf link
    doc_id = data.get('id')
    rec['hidden'] = 'https://rest.neptune-prod.its.unimelb.edu.au/server/api/core/bitstreams/%s/content' % doc_id
    rec['hidden'] = 'https://minerva-access.unimelb.edu.au/bitstreams/%s/download' % doc_id
    if not skipalreadyharvested or not rec['hdl'] in alreadyharvested:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)

schools = ['https://rest.neptune-prod.its.unimelb.edu.au/server/api/discover/search/objects?savedList=list_d76f1a6b'
           '-c97b-4b12-9b0c-a6f25e58d073&projection=SavedItemLists&sort=dc.date.available,'
           'DESC&page=0&size=10&scope=3f5551c5-a54a-5156-9e70-b35365953f96&embed=thumbnail']

link = 'https://rest.neptune-prod.its.unimelb.edu.au/server/api/discover/search/objects?savedList=list_d76f1a6b-c97b' \
       '-4b12-9b0c-a6f25e58d073&projection=SavedItemLists&sort=dc.date.available,' \
       'DESC&page=0&size=10&scope=3f5551c5-a54a-5156-9e70-b35365953f96&f.itemtype=PhD%20thesis,equals&embed=thumbnail '

print(link)

url_response = loads(urlopen(link).read())
maxpages = url_response.get('_embedded').get('searchResult').get('page').get('totalPages')


for page in range(min(pages, maxpages)):
    link = 'https://rest.neptune-prod.its.unimelb.edu.au/server/api/discover/search/objects?savedList=list_d76f1a6b-c97b' \
           '-4b12-9b0c-a6f25e58d073&projection=SavedItemLists&sort=dc.date.available,' \
           'DESC&page=' \
           + str(
        page) + '&size=10&scope=3f5551c5-a54a-5156-9e70-b35365953f96&f.itemtype=PhD%20thesis,equals&embed=thumbnail '
    ejlmod3.printprogress("=", [[page+1, min(pages, maxpages)]])
    url_response = loads(urlopen(link).read())
    for article in url_response.get('_embedded').get('searchResult').get('_embedded').get('objects'):
        get_sub_site(article.get('_links').get('indexableObject').get('href'))
    sleep(5)



    
ejlmod3.writenewXML(recs, publisher, jnlfilename)
