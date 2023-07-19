# -*- coding: utf-8 -*-
#harvest theses from Rio de Janeiro State U.
#FS: 2022-04-18
#FS: 2023-05-19

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

publisher = 'Rio de Janeiro State U.'
jnlfilename = 'THESES-RioDeJaneiroStateU-%s' % (ejlmod3.stampoftoday())

rpp = 20
pages = 1
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for (fc, depno) in [('', '3687'), ('m', '3696'), ('c', '3702'), ('c', '18054')]:
    for page in range(pages):
        tocurl = 'https://www.bdtd.uerj.br:8443/handle/1/' + depno + '/browse?type=dateissued&sort_by=2&order=DESC&rpp=' + str(rpp) + '&etal=-1&null=&offset=' + str(rpp*page) 
        ejlmod3.printprogress("=", [[depno], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        for tr in tocpage.body.find_all('tr'):
            for td in tr.find_all('td', attrs = {'headers' : 't3'}):
                rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'autaff' : [], 'note' : [], 'keyw' : []}
                if fc:
                    rec['fc'] = fc
                for a in td.find_all('a'):
                    rec['link'] = 'https://www.bdtd.uerj.br:8443' + a['href']
                    rec['doi'] = '20.2000/EstadoDeRioDeJaneiro/' + re.sub('.*handle\/', '',  a['href'])
                    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                        prerecs.append(rec)
    print(' %4i records so far' % (len(prerecs)))
    time.sleep(7)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:        
        req = urllib.request.Request(rec['link'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            req = urllib.request.Request(rec['link'], headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")

        except:
            print("no access to %s" % (rec['link']))
            continue

    
    ejlmod3.metatagcheck(rec, artpage, ['DC.language', 'DC.title', 'DCTERMS.issued',
                                        'DCTERMS.abstract', 'citation_pdf_url'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'DC.creator':
                if re.search('\d\d\d\d\-\d\d\d\d',  meta['content']):
                    rec['autaff'][-1].append('ORCID:' + re.sub('.*?(\d)', r'\1', meta['content']))
                elif re.search(' ', meta['content']):
                    author = meta['content']
                    rec['autaff'].append([ author ])
            #keywords
            elif meta['name'] == 'DC.subject':
                if not re.search('::', meta['content']):
                    rec['keyw'].append(meta['content'])
    if len(rec['autaff']) == 1:
        rec['autaff'][-1].append(publisher)
    recs.append(rec)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
