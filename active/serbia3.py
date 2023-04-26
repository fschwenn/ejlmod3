# -*- coding: utf-8 -*-
#program to harvest from doiSerbia
# FS 2019-10-25
# FS 2023-04-25

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time
import ssl

tmpdir = '/tmp'

jnl = sys.argv[1]
issueid = sys.argv[2]

if jnl == 'facta':
    jnlname = 'Facta Univ.Ser.Phys.Chem.Tech.'
    typecode = 'P'
    issn = '0354-4656'
    publisher = 'Nis U.'
else:
    print('journal unknown')
    sys.exit(0)

    
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

toclink = 'http://www.doiserbia.nb.rs/issue.aspx?issueid=%s' % (issueid)
tocfile = '/tmp/%s%s' % (jnl, issueid)

print(toclink)
if not os.path.isfile(tocfile):
    os.system('lynx -source "%s" > %s' % (toclink, tocfile))

inf = open(tocfile, 'r')
tocpage = BeautifulSoup(''.join(inf.readlines()), features="lxml")
inf.close()
              
recs = []
#for div in tocpage.body.find_all('div', attrs = {'id' : 'ContentRight'}):
#    for a in div.find_all('a'):
for a in tocpage.body.find_all('a'):
        if re.search('Details', a.text.strip()):
            rec = {'jnl' : jnlname, 'tc' : typecode, 'auts' : []}
            #rec['artlink'] = 'http://www.doiserbia.nb.rs/' + a['href']
            rec['artlink'] =  a['href']
            recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    req = urllib.request.Request(rec['artlink'], headers=hdr)
    artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    time.sleep(4)
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_author', 'citation_keywords',
                                        'citation_year', 'citation_volume', 'citation_issue',
                                        'citation_firstpage',  'citation_lastpage',
                                        'citation_abstract', 'citation_pdf_url'])
    for a in artpage.find_all('a'):
        if a.has_attr('href') and re.search('doi.org.10', a['href']):
            rec['doi'] = re.sub('.*doi.org.(10\..*)', r'\1', a['href'])
    ejlmod3.printrecsummary(rec)
    
jnlfilename = '%s%s.%s' % (jnl, rec['vol'], rec['issue'])
ejlmod3.writenewXML(recs, publisher, jnlfilename)
