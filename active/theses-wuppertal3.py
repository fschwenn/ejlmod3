# -*- coding: utf-8 -*-
#harvest Wuppertal U.
#FS: 2020-02-24
#FS: 2023-04-04

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Wuppertal U.'
hdr = {'User-Agent' : 'Magic Browser'}

docthresh = 1
years = 2
skipalreadyharvested = True

recs = []
prerecs = []
jnlfilename = 'THESES-WUPPERTAL-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:    
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

for (ddc, fc) in [('004', 'c'), ('510', 'm'), ('530', '')]:
    tocurl = 'http://elpub.bib.uni-wuppertal.de/servlets/MCRSearchServlet?mask=browse/ddc.xml&query=(ddc%20=%20%225%22)%20AND%20(status%20=%20%22published%22)&maxResults=0&datecreation.sortField.1=descending'
    tocurl = 'https://elpub.bib.uni-wuppertal.de/servlets/solr/select?q=%2Bcategory.top:%22SDNB:' + ddc + '%22+%2BobjectType:mods+%2Bcategory.top:%22state:published%22%2Bcategory.top:%22collection:Diss%22&mask=content/diss/thesis-by-sdnb.xml&sort=mods.dateIssued+desc'
    ejlmod3.printprogress('=', [[ddc], [tocurl]])
    tocfilname = '/tmp/%s.%s.toc' % (jnlfilename, ddc)
    if not os.path.isfile(tocfilname):
        os.system('wget -T 300 -t 3 -q -O %s "%s"' % (tocfilname, tocurl))
        time.sleep(5)
    inf = open(tocfilname, 'r')
    tocpage = BeautifulSoup(''.join(inf.readlines()), features='lxml')
    inf.close()
    for li in tocpage.find_all('div', attrs = {'class' : 'hit_item_body'}):
            print('li')
            for h3 in li.find_all('h3', attrs = {'class' : 'hit_title'}):
                for a in h3.find_all('a'):
                    rec = {'tc' : 'T', 'jnl' : 'BOOK', 'link' : a['href'], 'note' : []}
                    rec['docnr'] = int(re.sub('\D', '', a['href']))
                    rec['doi'] = '20.2000/Wuppertal/%09i' % (rec['docnr'])
            for div in li.find_all('div', attrs = {'class' : 'hit_type'}):
                rec['MARC'] = [['502', [('c', publisher)]]]
                if div.text.strip() == 'Dissertation':
                    rec['MARC'][0][1].append(('b', 'PhD'))
                elif div.text.strip() == 'Habilitation':
                    rec['MARC'][0][1].append(('b', 'Habilitation'))
            for div in li.find_all('div', attrs = {'class' : 'hit_date'}):
                #this is the year of last update of files (which can not be befor date of thesis)
                year = re.sub('.*([12]\d\d\d).*', r'\1', div.text.strip())            
                if int(year) >= ejlmod3.year() - years:
                    if rec['docnr'] > docthresh:
                     #   if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                            if fc: rec['fc'] = fc
                            prerecs.append(rec)

i = 0
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs), rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
        time.sleep(10-8)
    except:
        try:
            print('retry %s in 180 seconds' % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
        except:
            print('no access to %s' % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.language', 'DC.title',
                                        'DC.identifier', 'citation_pdf_url'])
    #abstract
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.description'}):
        rec['abs'] = re.sub('<p>', '', meta['content'])
    #date
    for div in artpage.body.find_all('div', attrs = {'class' : 'container_12'}):
        datum = False
        for div2 in div.find_all('div'):
            div2t = div2.text.strip()
            if datum:
                if re.search('.*([12]\d\d\d).*', div2t):
                    rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', div2t)
                    rec['MARC'][0][1].append(('d', rec['year']))
                    rec['date'] =  re.sub('(\d\d).(\d\d).(\d\d\d\d)', r'\3-\2-\1', div2t)                    
                datum = False
            if re.search('Datum der Promotion', div2t):
                datum = True
            elif re.search('Datum der Habilitation', div2t):
                datum = True
    if not 'date' in list(rec.keys()):
        for div in artpage.body.find_all('div', attrs = {'class' : 'container_12'}):
            for div2 in div.find_all('div'):
                div2t = div2.text.strip()
                if re.search('20[12]\d', div2t):
                    rec['year'] = re.sub('.*(2\d\d\d).*', r'\1', div2t)
                    rec['MARC'][0][1].append(('d', rec['year']))                    
    #make 502entry by "hand" for habilitations
    rec['autaff'][-1].append(publisher)
    if 'year' in rec and int(rec['year']) < ejlmod3.year(backwards=years):
        print('  skip', rec['year'])
    elif skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        print('  %s already in backup' % (rec['doi']))
    elif skipalreadyharvested and 'urn' in rec and rec['urn'] in alreadyharvested:
        print('  %s already in backup' % (rec['urn']))
    else:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
