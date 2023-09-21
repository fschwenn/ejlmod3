# -*- coding: utf-8 -*-
#harvest Kentucky University theses
#FS: 2018-01-30


import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Kentucky University'
jnlfilename = 'THESES-KENTUCKY-%s' % (ejlmod3.stampoftoday())
years = 2
boring = ['Master of Science (MS)', 'Bachelor of Science (BS)']
skipalreadyharvested = True

tocurl = 'https://uknowledge.uky.edu/physastron_etds/'

try:
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (tocurl))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
date = False
for div in tocpage.body.find_all('div', attrs = {'id' : 'series-home'}):
    for child in div.children:
        try:
            name = child.name
        except:
            continue
        if name == 'h4':
            for span in child.find_all('span'):
                date = span.text.strip()
        elif name == 'p':
            #year = int(re.sub('.*(20\d\d).*', r'\1', rec['date']))
            if int(date) >= ejlmod3.year(backwards=years):
                if child.has_attr('class') and 'article-listing' in child['class']:
                    rec = {'jnl' : 'BOOK', 'tc' : 'T', 'date' : date}
                    for a in child.find_all('a'):                    
                        rec['tit'] = a.text.strip()
                        rec['artlink'] = a['href']
                        a.replace_with('')
                    if ejlmod3.checkinterestingDOI(rec['artlink']):
                        prerecs.append(rec)

i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [len(recs)], [rec['artlink']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['artlink']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['description', 'keywords', 'bepress_citation_author',
                                        'bepress_citation_pdf_url',
                                        'bepress_citation_doi', 'bepress_citation_online_date'])
    #thesis type
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'bepress_citation_dissertation_name'}):
        thesistype = meta['content']
        if thesistype in boring:
            keepit = False
        else:
            rec['note'] = [ meta['content'] ]
    #supervisor
    for div in artpage.body.find_all('div', attrs = {'id' : 'advisor1'}):
        for p in div.find_all('p'):
            rec['supervisor'] = [[ re.sub('^Dr. ', '', p.text.strip()) ]]
    for div in artpage.body.find_all('div', attrs = {'id' : 'advisor2'}):
        for p in div.find_all('p'):
            rec['supervisor'].append( [re.sub('^Dr. ', '', p.text.strip())] )
    #ORCID
    for div in artpage.body.find_all('div', attrs = {'id' : 'orcid'}):
        for h4 in div.find_all('h4'):
            if re.search('Author ORCID', h4.text):
                for a in div.find_all('a'):
                    rec['autaff'][-1].append(re.sub('.*\/', 'ORCID:', a.text.strip()))
    if 'doi' not in rec:
        rec['doi'] = '20.2000/KENTUCKY/' + re.sub('\W', '', re.sub('.*edu', '', rec['artlink']))
        rec['link'] = rec['artlink']
    if keepit:
        if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
            rec['autaff'][-1].append(publisher)
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])


ejlmod3.writenewXML(recs, publisher, jnlfilename)
