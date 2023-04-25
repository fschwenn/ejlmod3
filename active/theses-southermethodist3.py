# -*- coding: utf-8 -*-
#harvest theses from Southern Methodist U.
#FS: 2020-04-28
#FS: 2023-04-23

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

#pagestocheck = 2
skipalreadyharvested = True
years = 2

publisher = 'Southern Methodist U. (main)'
jnlfilename = 'THESES-SOUTHERNMETHODIST-%s' % (ejlmod3.stampoftoday())

hdr = {'User-Agent' : 'Magic Browser'}
recs = []

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

for (dep, fc) in [('hum_sci_mathematics', 'm'), ('hum_sci_physics', '')]:
    tocurl = 'https://scholar.smu.edu/%s_etds/' % (dep)
    ejlmod3.printprogress("=", [[tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for div in tocpage.body.find_all('div', attrs = {'id' : 'series-home'}):
        for child in div.children:
            try:
                child.name
            except:
                continue
            if child.name == 'h4':
                for span in child.find_all('span'):
                    year = re.sub('.*(20\d\d).*', r'\1', span.text.strip())
                    print(year)
            elif child.name == 'p' and child.has_attr('class') and 'article-listing' in child['class']:
                if int(year) > ejlmod3.year(backwards=years):
                    rec = {'tc' : 'T', 'jnl' : 'BOOK', 'year' : year}
                    for a in child.find_all('a'):
                        rec['link'] = a['href']
                        rec['doi'] = '20.2000/SoutherMethodist/' + re.sub('\W', '', a['href'][23:])
                        if fc:
                            rec['fc'] = fc
                        if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                            recs.append(rec)
    print('  %4i records so far' % (len(recs)))

#check individual thesis pages
i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
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
    ejlmod3.metatagcheck(rec, artpage, ['bepress_citation_author', 'description',
                                        'twitter:title', 'bepress_citation_pdf_url'])
    rec['autaff'][-1].append(publisher)
    for div in artpage.body.find_all('div', attrs = {'class' : 'element'}):
        if div.has_attr('id'):
            #date
            if div['id'] == 'publication_date':
                for p in div.find_all('p'):
                    if re.search('\d+\-\d+\-\d+', p.text):
                        rec['date'] = re.sub('.*?(\d+)\-(\d+)\-(\d+).*', r'\3-\2-\1', p.text.strip())
            #supervisor
            elif div['id'] == 'advisor1':
                for p in div.find_all('p'):
                    rec['supervisor'] = [[ p.text.strip() ]]
            #pages
            elif div['id'] == 'number_of_pages':
                for p in div.find_all('p'):
                    rec['pages'] = p.text.strip()
    #license
    for link in artpage.find_all('link', attrs = {'rel' : 'license'}):
        rec['license'] = {'url' : link['href']}
    #FFT
    if 'fulltext' in list(rec.keys()):
        if 'license' in list(rec.keys()):
            rec['FFT'] = rec['fulltext']
        else:
            rec['hidden'] = rec['fulltext']                
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
