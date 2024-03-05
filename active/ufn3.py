# -*- coding: UTF-8 -*-
#program to harvest Physics-Uspekhi
#FS: 2023-08-15

import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import sys
import time

publisher = 'Uspekhi Fizicheskikh Nauk'
year = sys.argv[1]
issue = sys.argv[2]

vol = str(int(year) - 1957)

jnlfilename = 'physusp%s.%s' % (vol, issue)

recs = []
tocurl = 'https://ufn.ru/en/articles/%s/%s/' % (year, issue)
print(tocurl)
hdr = {'User-Agent' : 'Magic Browser'}
req = urllib.request.Request(tocurl, headers=hdr)
tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
rubric = ''
for p in tocpage.body.find_all('p'):
    if p.has_attr('class'):
        if 'rubric' in p['class']:
            rubric = p.text.strip()
            ejlmod3.printprogress('=', [[rubric]])
        elif 'articles' in p['class']:
            for a in p.find_all('a'):
                rec = {'tc' : 'P', 'year' : year, 'issue' : issue, 'vol' : vol, 
                       'jnl' : 'Phys.Usp.', 'note' : ['UspekhiFizicheskikhNauk'], 'pacs' : [],
                       'auts' : [], 'aff' : []}
                if not rubric in ['Personalia', 'Bibliography',
                                  'Conferences and symposia',
                                  'From the ediorial board', 'Announcement',
                                  'Physics news on the internet']:
                    if rubric:
                        rec['note'].append(rubric)
                    if a.has_attr('href') and re.search('articles', a['href']):
                        rec['artlink'] = 'https://ufn.ru' + a['href']
                        ejlmod3.printprogress(' ', [[rec['artlink']]])
                        recs.append(rec)
print('\n')
for (i, rec) in enumerate(recs):
    ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['artlink']]])
    time.sleep(4)
    try:
        req = urllib.request.Request(rec['artlink'] + 'references.html')
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    except:
        time.sleep(4)        
        req = urllib.request.Request(rec['artlink'])
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_firstpage', 'citation_lastpage',
                                        'citation_title', 'keywords', 'citation_author'])
    #fulltext
    for a in artpage.body.find_all('a', attrs = {'class' : 'track-fulltext-download'}):
        rec['hidden'] = 'https://ufn.ru' + a['href']
    #abstract
    for p in artpage.body.find_all('p', attrs = {'itemprop' : 'articleBody'}):
        rec['abs'] = p.text
    #PACS, DOI
    for a in artpage.body.find_all('a'):
        if a.has_attr('href'):
            if re.search('\/pacs\/\d', a['href']):
                if not re.search(',', a['href']):
                    rec['pacs'].append(re.sub('.*\/pacs\/(.*)\/', r'\1', a['href']))
            elif re.search('^10.3367\/UFNe.', a.text):
                rec['doi'] = a.text.strip()
    #references
    for ol in artpage.body.find_all('ol', attrs = {'class' : 'ref'}):
        rec['refs'] = []
        for li in ol.find_all('li'):
            rdoi = False
            for a in li.find_all('a'):
                if a.has_attr('href') and re.search('doi.org\/10', a['href']):
                    rdoi = re.sub('.*org\/', 'doi:', a['href'])
            if rdoi:
                ref = [('a', rdoi), ('x', li.text.strip())]
            else:
                ref = [('x', li.text.strip())]
            rec['refs'].append(ref)
    #2nd pubnote
    for p in artpage.body.find_all('p', attrs = {'class' : 'c'}):
        for a in p.find_all('a'):
            if a.has_attr('href'):
                if re.search('doi.org\/10.*UFNr', a['href']):
                    #might interfer with mathnet.ru-harvesting
                    #rec['alternatedoi'] = re.sub('.*org\/', 'doi:', a['href'])
                    pass
                elif re.search('\/ru\/articles\/', a['href']):
                    rec['transtit'] = a.text.strip()
            rec['alternatejnl'] = 'Usp.Fiz.Nauk'
            rec['alternateissue'] = rec['issue']
            for b in p.find_all('b'):
                rec['alternatevol'] = b.text.strip()
                b.replace_with('ALTERNATEVOL')
            pages = re.sub('.*ALTERNATEVOL *(.*?) *\(.*', r'\1', p.text.strip())
            rec['alternatep1'] = re.sub('\D.*', '', pages)
            rec['alternatep2'] = re.sub('.*\D', '', pages)
    
    #authors (is a mess in HTML)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
