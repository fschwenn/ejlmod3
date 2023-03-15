# -*- coding: utf-8 -*-
#harvest theses from IMSc, Chennai
#FS: 2020-04-03
#FS: 2023-03-15

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time


publisher = 'IMSc, Chennai'
rpp = 100
skipalreadyharvested = True


hdr = {'User-Agent' : 'Magic Browser'}
recs = []
jnlfilename = 'THESES-CHENNAI-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

years = [ejlmod3.year(), ejlmod3.year(backwards=1)]
for year in years:
    tocurl = 'https://www.imsc.res.in/xmlui/browse?type=datesubmitted&value=%i&rpp=%i' % (year, rpp)
    print(year, tocurl)
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
    time.sleep(2)
    for div in tocpage.body.find_all('div', attrs = {'class' : 'artifact-title'}):
        for a in div.find_all('a'):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : [], 'keyw' : []}
            rec['link'] = 'https://www.imsc.res.in' + a['href']
            rec['doi'] = '20.2000/IMScChennai/' + re.sub('.*\/', '', a['href'])
            if re.search('MSc', a.text):
                print('   skip Master', a.text.strip())
            elif not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                recs.append(rec)

j = 0
for rec in recs:
    j += 1
    ejlmod3.printprogress("-", [[j, len(recs)], [rec['link']]])
    req = urllib.request.Request(rec['link'])
    artpage = BeautifulSoup(urllib.request.urlopen(req))
    time.sleep(5)
    #author
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DCTERMS.issued', 'citation_pdf_url'])
    rec['autaff'][-1].append(publisher)
    for meta in artpage.find_all('meta'):
        if meta.has_attr('name'):
            #title
            if meta['name'] == 'DC.title':
                rec['tit'] = re.sub('\[HBNI.*', '', meta['content'])
            #keywords
            elif meta['name'] == 'DC.subject':
                if not re.search('^HBNI', meta['content']):
                    rec['keyw'].append( meta['content'] )
            #pages
            elif meta['name'] == 'DC.description':
                if re.search('^\d+p\.',  meta['content']):
                    rec['pages'] = re.sub('\D.*', '', meta['content'])
    for div  in artpage.body.find_all('div', attrs = {'class' : 'simple-item-view-other'}):
        spans = div.find_all('span')
        if len(spans) == 2:
            if spans[0].text.strip() == 'Advisor:':
                rec['supervisor'] = [[ spans[1].text.strip() ]]
            elif spans[0].text.strip() == 'Degree:':
                degree = spans[1].text.strip()
                rec['note'].append(degree)                
            elif spans[0].text.strip() == 'Institution:':
                inst = spans[1].text.strip()
                if inst == 'HBNI': inst = 'HBNI, Mumbai'
            elif spans[0].text.strip() == 'Year:':
                rec['year'] = spans[1].text.strip()        
    if degree == 'Ph.D':
        rec['MARC'] = [ ('502', [('b', 'PhD'), ('c', inst), ('d', rec['year'])]) ]
    elif  degree == 'M.Sc':
        rec['MARC'] = [ ('502', [('b', 'Master'), ('c', inst), ('d', rec['year'])]) ]
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
