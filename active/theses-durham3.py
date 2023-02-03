# -*- coding: utf-8 -*-
#harvest theses from University of Durham
#FS: 2019-09-26
#FS: 2023-02-01

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

publisher = 'Durham U.'
jnlfilename = 'THESES-DURHAM-%s' % (ejlmod3.stampoftoday())
pages = 3
rpp = 20
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
hdr = {'User-Agent' : 'Magic Browser'}
recs = []
for i in range(pages):
    tocurl = 'http://etheses.dur.ac.uk/cgi/search/advanced?screen=Public%3A%3AEPrintSearch&_action_search=Search&_fulltext__merge=ALL&_fulltext_=&title_merge=ALL&title=&creators_name_merge=ALL&creators_name=&supervisors_name_merge=ALL&supervisors_name=&abstract_merge=ALL&abstract=&date=&keywords_merge=ALL&keywords=&thesis_qualification_name=PhD&department_merge=ALL&department=&department_dur=DDD21&department_dur=DDD25&department_dur=DDD4&department_dur_merge=ANY&satisfyall=ALL&order=-date%2Fcreators_name%2Ftitle&search_offset=' + str(rpp*i)
    ejlmod3.printprogress('=', [[i+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for tr in tocpage.body.find_all('tr', attrs = {'class' : 'ep_search_result'}):
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK'}
        for td in tr.find_all('td'):
            for span in td.find_all('span'):
                for a in td.find_all('a'):
                    rec['link'] = a['href']
                    rec['doi'] = '20.2000/' + re.sub('\W', '', a['href'])
                    if skipalreadyharvested and rec['doi'] in alreadyharvested:
                        pass                    
                    else:
                        recs.append(rec)
    print('  %4i records so far' % (len(recs)))

                
for (i, rec) in enumerate(recs):
    ejlmod3.printprogress("-", [[i+1, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['eprints.title', 'eprints.date', 'DC.subject', 'eprints.abstract',
                                        'eprints.document_url'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'eprints.creators_name':
                author = meta['content']
                author = re.sub(',', ';', author, count=1)
                author = re.sub(' *, *', ' ', author)
                author = re.sub(';', ',', author)
                rec['autaff'] = [[ author ]]
            #email
            elif meta['name'] == 'eprints.creators_id':
                rec['autaff'][-1].append('EMAIL:' + meta['content'])
    rec['autaff'][-1].append(publisher)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
