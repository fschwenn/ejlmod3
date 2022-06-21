# -*- coding: utf-8 -*-
#harvest theses from SISSA
#FS: 2018-01-30

import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'UNESP'
jnlfilename = 'THESES-UNESP-%s' % (ejlmod3.stampoftoday())

tocurl = 'https://repositorio.unesp.br/handle/11449/77166/discover?filtertype=dateIssued&filter_relational_operator=equals&filter=[' + str(ejlmod3.year(backwards=1)) + '+TO+' + str(ejlmod3.year()) + ']&rpp=100'
print(tocurl)

hdr = {'User-Agent' : 'Magic Browser'}

prerecs = []
for offset in [0]:
    try:
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req))
        time.sleep(3)
    except:
        print("retry in 180 seconds")
        time.sleep(180)
        tocpage = BeautifulSoup(urllib2.build_opener(urllib2.HTTPCookieProcessor).open('%s%i' % (tocurl, offset)))
    for div in tocpage.body.find_all('div', attrs = {'class' : 'artifact-description'}):
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK'}
        for a in div.find_all('a'):
            rec['artlink'] = 'https://repositorio.unesp.br' + a['href'] + '?show=full'
            rec['hdl'] = re.sub('.*handle\/', '', a['href'])
            prerecs.append(rec)


recs = []
i = 0
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']))
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']))
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'DC.subject', 'DC.language', 'citation_pdf_url'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'DC.creator':
                author = re.sub(' *\[.*', '', meta['content'])
                rec['autaff'] = [[ author ]]
                if re.search('\[UNESP\]', meta['content']):
                    rec['autaff'][-1].append('Universidade Estadual Paulista (UNESP), Instituto de Fisica Teorica (IFT), 01140-070, Sao Paulo, Brazil')
            #abstract
            elif meta['name'] == 'DCTERMS.abstract':
                if meta['xml:lang'] == 'en':
                    rec['abs'] = meta['content']
    recs.append(rec)    
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)

