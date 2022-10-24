# -*- coding: utf-8 -*-
#harvest theses from Cracow, INP 
#FS: 2022-09-30

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

publisher = 'Cracow, INP'
jnlfilename = 'THESES-CracowINP-%s' % (ejlmod3.stampoftoday())

rpp = 10
pages = 1

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}
for (dep, degree) in [('3', 'phd'), ('6', 'habilitation')]:
    prerecs = []
    recs = []
    for page in range(pages):
        tocurl = 'https://rifj.ifj.edu.pl/handle/item/' + dep + '/browse?order=DESC&rpp=' + str(rpp) + '&sort_by=3&etal=-1&offset=' + str(page*rpp) + '&type=dateissued'
        ejlmod3.printprogress('=', [[degree], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        prerecs += ejlmod3.getdspacerecs(tocpage, 'https://rifj.ifj.edu.pl', fakehdl=True)
        print('  %4i records do far' % (len(prerecs)))
        time.sleep(10)

    for (i, rec) in enumerate(prerecs):
        if not ejlmod3.ckeckinterestingDOI(rec['link']):
            continue
        ejlmod3.printprogress('-', [[i+1, len(prerecs)], [rec['link']], [len(recs)]])
        try:
            req = urllib.request.Request(rec['link']+'?show=full', headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
            time.sleep(3)
        except:
            try:
                print("   retry %s in 15 seconds" % (rec['link']))
                time.sleep(15)
                req = urllib.request.Request(rec['link']+'?show=full', headers=hdr)
                artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
            except:
                print("   no access to %s" % (rec['link']))
                continue
        #fulltext
        for a in artpage.body.find_all('a', attrs = {'class' : 'image-link'}):
            if a.has_attr('href') and re.search('\.pdf', a['href']):
                rec['pdf_url'] = 'https://rifj.ifj.edu.pl' + a['href']
        ejlmod3.metatagcheck(rec, artpage, ['citation_language', 'citation_author', #'citation_pdf_url',
                                            'citation_date', 'citation_isbn', 'DCTERMS.abstract',
                                            'citation_title', 'DC.rights'])
        rec['MARC'] = [('502', [('b', degree), ('c', publisher), ('d', rec['date'])])]
        rec['autaff'][-1].append(publisher)
        for tr in artpage.body.find_all('tr'):
            for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
                tdt = td.text.strip()
                td.decompose()
            for td in tr.find_all('td'):
                if td.text.strip() == 'pl_PL.UTF-8':
                    continue
                #supervisor
                if tdt in ['dc.contributor.supervisor', 'dc.contributor.advisor']:
                    sv = td.text.strip()
                    if sv:
                        rec['supervisor'].append( [sv] )
                #pages
                elif tdt == 'dc.description.physical':
                    if re.search('\d\d', td.text):
                        rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', td.text.strip())                        
        if len(rec['autaff']) == 1:
            if degree == 'habilitation':
                rec['note'].append('ONLY MAY BE A HABILITATION')
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
        else:
            ejlmod3.adduninterestingDOI(rec['link'])
        
    ejlmod3.writenewXML(recs, publisher, jnlfilename+degree)
