# -*- coding: UTF-8 -*-
#program to harvest scielo.org.mx
# FS 2017-03-27
# FS 2023-05-30

import os
import ejlmod3
import re
import sys
#import unicodedata
#import string
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup
import ssl

tmpdir = '/tmp'

jnl = sys.argv[1]
year = sys.argv[2]
issue = sys.argv[3]

jnlfilename = jnl+year+'.'+issue
typecode = 'P'

#if   (jnl == 'rbef'):
#    trunc = 'http://www.scielo.br'
#    issn = '1806-1117'
#    jnlname = 'Rev.Bras.Ens.Fis.'
#    publisher = 'Sociedade Brasileira de Fisica'
#    #despite its name it does not contain reviews
#    #typecode = 'R'
if (jnl == 'rmaa'):
    trunc = 'http://www.scielo.org.mx'
    issn = '0185-1101'
    jnlname = 'Rev.Mex.Astron.Astrofis.'
    publisher = 'National Autonomous University of Mexico'
else:
    print('Dont know journal %s!' % (jnl))
    sys.exit(0)

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}

tocurl = '%s/scielo.php?script=sci_issuetoc&pid=%s%s%04i&lng=en&nrm=iso' % (trunc, issn, year, int(issue))
print("get table of content of %s%s.%s via %s ..." %(jnlname, year, issue, tocurl))
req = urllib.request.Request(tocurl, headers=hdr)
tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")

recs = []
for tr in tocpage.body.find_all('tr'):
    rec = {'jnl' : jnlname, 'year' : year, 'issue' : issue, 'tc' : typecode,
           'autaff' : [], 'refs' : []}
    for a in tr.find_all('a'):
        if a.has_attr('href') and re.search('text.*ngl', a.text):
                rec['artlink'] = a['href']
    if 'artlink' in list(rec.keys()):
        time.sleep(5)
        print(rec['artlink'])
        req = urllib.request.Request(rec['artlink'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_author','citation_author_institution',
                                            'citation_firstpage', 'citation_lastpage', 'citation_volume',
                                            'citation_issue', 'citation_doi', 'citation_pdf_url'])
        #abstract
        for div in artpage.find_all('div', attrs = {'class' : 'trans-abstract'}):
            englabs = False
            for p in div.find_all('p'):
                if p.text.strip() == 'ABSTRACT':
                    p.decompose()
                    englabs = True
            if englabs:
                for p in div.find_all('p'):
                    for b in p.find_all('b'):
                        if re.search('Key Word', b.text):
                            b.decompose()
                            rec['keyw'] = re.split('; ', p.text.strip())
                rec['abs'] = div.text.strip()
        #references
        for p in artpage.find_all('p', attrs = {'class' : 'ref'}):
            rec['refs'].append([('x', re.sub('\[ *Links *\]', '', p.text.strip()))])
        #license
        for a in artpage.body.find_all('a', attrs = {'rel' : 'license'}):
            rec['licence'] = {'url' : a['href']}
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
