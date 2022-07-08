# -*- coding: utf-8 -*-
#harvest theses from Andes U., Bogota
#FS: 2020-08-28

import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Andes U., Bogota'
jnlfilename = 'THESES-BOGOTA-%s' % (ejlmod3.stampoftoday())
years = 3

hdr = {'User-Agent' : 'Magic Browser'}
recs = []
for (fc, dep) in [('', '52401'), ('m', '52426')]:
    tocurl = 'https://repositorio.uniandes.edu.co/handle/1992/' + dep
    ejlmod3.printprogress('=', [[dep], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for div in tocpage.body.find_all('div', attrs = {'class' : 'artifact-description'}):
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'autaff' : []}
        if fc: rec['fc'] = fc
        for h4 in div.find_all('h4'):
            for a in h4.find_all('a'):
                rec['link'] = 'https://repositorio.uniandes.edu.co' + a['href'] #+ '?show=full'
                rec['hdl'] = re.sub('.*handle\/', '', a['href'])
        for span in div.find_all('span', attrs = {'class' : 'date'}):
            rec['year'] = re.sub('.*?([12]\d\d\d).*', r'\1', span.text.strip())
            if int(rec['year']) > ejlmod3.year(backwards=years):
                recs.append(rec)
            else:
                print('  skip', rec['year'])

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['link']]])
    try:
        req = urllib.request.Request(rec['link'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            req = urllib.request.Request(rec['link'], headers=hdr)
            artpage = BeautifulSoup(urllib .request.urlopen(req), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'DC.title', 'citation_language',
                                        'DCTERMS.issued', 'DC.subject', 'DCTERMS.abstract',
                                        'citation_pdf_url'])
    rec['autaff'][-1].append(publisher)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)

