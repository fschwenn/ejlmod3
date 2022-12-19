# -*- coding: utf-8 -*-
#harvest theses from Goettingen U.
#FS: 2019-11-13
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import os

publisher = 'Gottingen U.'
jnlfilename = 'THESES-GOETTINGEN-%s' % (ejlmod3.stampoftoday())

tocurl = 'https://ediss.uni-goettingen.de/handle/11858/8/discover?fq=dateIssued.year=[' + str(ejlmod3.year(backwards=1)) + '+TO+' + str(ejlmod3.year()) + ']&rpp=50'
print(tocurl)

hdr = {'User-Agent' : 'Magic Browser'}

prerecs = {}
if not os.path.isfile('/tmp/%s.toc'% (jnlfilename)):
    os.system('wget -q -O /tmp/%s.toc "%s"' % (jnlfilename, tocurl))
inf = open('/tmp/%s.toc' % (jnlfilename), 'r')
lines = inf.readlines()
inf.close()
tocpage = BeautifulSoup(' '.join(lines), features="lxml")
i = 0
for div in tocpage.body.find_all('div', attrs = {'class' : 'artifact-description'}):
    i += 1
    for a in div.find_all('a'):
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK'}
        rec['artlink'] = 'https://ediss.uni-goettingen.de' + a['href'] + '?show=full'
        rec['hdl'] = re.sub('.*handle\/', '', a['href'])
        if not a['href'] in prerecs:
            prerecs[a['href']] = rec

    
recs = []
i = 0
for rec in list(prerecs.values()):
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']]])
    artfilename = '/tmp/goettingen.%s' % (re.sub('\W', '', rec['artlink']))
    if not os.path.isfile(artfilename):
        time.sleep(3)
        os.system('wget -q -O  %s "%s"' % (artfilename, rec['artlink']))
    inf = open(artfilename, 'r')
    lines = inf.readlines()
    inf.close()
    artpage = BeautifulSoup(' '.join(lines), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['DC.rights', 'citation_title', 'DCTERMS.issued',
                                        'DC.subject', 'DC.language', 'citation_pdf_url',
                                        'DC.description'])
    #author
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.creator'}):
        author = re.sub(' *\[.*', '', meta['content'])
        rec['autaff'] = [[ author ]]
        rec['autaff'][-1].append('Gottingen U.')
    recs.append(rec)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)

