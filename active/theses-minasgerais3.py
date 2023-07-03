# -*- coding: utf-8 -*-
#harvest theses from Minas Gerais U.
#FS: 2023-07-01

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Minas Gerais U.'
jnlfilename = 'THESES-MINASGERAIS-%s' % (ejlmod3.stampoftoday())

rpp = 20
pages = 1
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}
recs = []
for (dep, fc) in [('443', ''), ('570', 'm'), ('645', 'c')]:
    for j in range(pages):
        tocurl = 'https://repositorio.ufmg.br/handle/1843/' + dep +'/browse?offset=' + str(j*rpp) + '&rpp=' + str(rpp) + '&sort_by=2&type=dateissued&etal=-1&order=DESC'
        ejlmod3.printprogress("=", [[dep, fc], [j+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
        for tr in tocpage.body.find_all('tr'):
            for td in tr.find_all('td', attrs = {'headers' : 't2'}):
                rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'autaff' : [], 'note' : [],
                       'supervisor' : []}
                if fc: rec['fc'] = fc
                for a in td.find_all('a'):
                    rec['link'] = 'https://repositorio.ufmg.br' + a['href'] + '?mode=full'
                    rec['hdl'] = re.sub('.*handle\/', '', a['href'])
                    if not skipalreadyharvested or not rec['hdl'] in alreadyharvested:
                        if ejlmod3.checkinterestingDOI(rec['hdl']):
                            recs.append(rec)
        print('  %4i records so far' % (len(recs)))
    time.sleep(10)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
        except:
            print("no access to %s" % (rec['link']))
            continue
    #check whether really thesis

    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'DC.title', 'DCTERMS.issued',
                                        'DC.subject', 'DC.rights', 'citation_pdf_url',
                                        'DC.language'])
    for tr in artpage.body.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldLabel'}):
            label = td.text.strip()
        for td in tr.find_all('td', attrs = {'headers' : 's2'}):
            #supervisor
            if label in ['dc.contributor.advisor1', 'dc.contributor.advisor2']:
                rec['supervisor'].append([td.text.strip()])
            #abstract
            elif label == 'dc.description.abstract':
                rec['abs'] = td.text.strip()
            #alternative title
            elif label == 'dc.title.alternative':
                rec['transtit'] = td.text.strip()

    rec['autaff'][-1].append(publisher)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
