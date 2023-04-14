# -*- coding: utf-8 -*-
#harvest theses from U. Wurzburg (main) 
#FS: 2019-11-06
#FS: 2023-04-14

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

skipalreadyharvested = True

publisher = 'U. Wurzburg (main)'
jnlfilename = 'THESES-WURZBURG-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}
repacs = re.compile('.*(\d\d\.\d\d\...).*')
prerecs = []
for (inst, fc) in [('Physikalisches+Institut', ''),
                   ('Institut+f%C3%BCr+Theoretische+Physik+und+Astrophysik', ''),
                   ('Institut+f%C3%BCr+Mathematik', 'm'),
                   ('Institut+f%C3%BCr+Informatik', 'c')]:
    for year in [ejlmod3.year(), ejlmod3.year(backwards=1), ejlmod3.year(backwards=2)]:
        tocurl = 'https://opus.bibliothek.uni-wuerzburg.de/solrsearch/index/search/searchtype/simple/query/%2A%3A%2A/browsing/true/doctypefq/doctoralthesis/start/0/rows/100/institutefq/' + inst + '/yearfq/' + str(year)
        ejlmod3.printprogress("=", [[inst], [year], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(5)
        for div in tocpage.body.find_all('div', attrs = {'class' : 'result_box'}):
            for div2 in div.find_all('div', attrs = {'class' : 'results_title'}):
                for a in div2.find_all('a'):
                    rec = {'tc' : 'T', 'jnl' : 'BOOK', 'keyw' : [], 'pacs' : []}
                    rec['link'] = 'https://opus.bibliothek.uni-wuerzburg.de' + a['href']
                    rec['tit'] = a.text.strip()
                    rec['year'] = str(year)
                    if fc:
                        rec['fc'] = fc
                    prerecs.append(rec)
        print('  %4i records so far' % (len(prerecs)))
            
i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(10)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'description', 'DC.subject',
                                        'citation_doi', 'DC.identifier', 'DC.rights',
                                        'citation_pdf_url'])
    rec['autaff'][-1].append(publisher)   
    for tr in artpage.body.find_all('tr'):
        for th in tr.find_all('th'):
            #PACS
            if re.search('PACS..lassification', th.text.strip()):
                for td in tr.find_all('td'):
                    for pacspart in re.split('\/' ,td.text.strip()):
                        if repacs.search(pacspart):
                            pacs = repacs.sub(r'\1', pacspart)
                            if not re.search('00', pacs):
                                rec['pacs'].append(pacs)
            #Language
            if re.search('Language', th.text.strip()):
                for td in tr.find_all('td'):
                    if re.search('erman', td.text.strip()):
                        rec['language'] = 'german'
                        #translated title
                        for h3 in artpage.body.find_all('h3', attrs = {'class' : 'titlemain', 'lang' : 'en'}):
                            rec['transtit'] = h3.text.strip()
    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
        
ejlmod3.writenewXML(recs, publisher, jnlfilename)
