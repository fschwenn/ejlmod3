# -*- coding: utf-8 -*-
#harvest theses from Goettingen U.
#FS: 2019-11-13
#FS: 2023-02-10
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import os

rpp = 60
pages = 1
skipalreadyharvested = True

publisher = 'Gottingen U.'
jnlfilename = 'THESES-GOETTINGEN-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
hdr = {'User-Agent' : 'Magic Browser'}
recs = []
hdls = ['11858/00-1735-0000-002E-E4D9-E']
for dep in ['7', '8']:
    for page in range(pages):
        tocurl = 'https://ediss.uni-goettingen.de/handle/11858/' + dep + '/browse?rpp=' + str(rpp) + '&sort_by=2&type=dateissued&offset=' + str(rpp*page) + '&etal=-1&order=DESC'
        ejlmod3.printprogress('=', [[dep], [page+1, pages], [tocurl]])
        tocfilename = '/tmp/%s.%s.%02i.toc'% (jnlfilename, dep, page)
        if not os.path.isfile(tocfilename):
            os.system('wget -q -O %s "%s"' % (tocfilename, tocurl))
            time.sleep(10)
        inf = open(tocfilename, 'r')            
        lines = inf.readlines()
        inf.close()
        tocpage = BeautifulSoup(' '.join(lines), features="lxml")
        for rec in ejlmod3.getdspacerecs(tocpage, 'https://ediss.uni-goettingen.de'):
            if rec['hdl'] in hdls:
                print('   %s already in list' % (rec['hdl']))                
            elif skipalreadyharvested and rec['hdl'] in alreadyharvested:
                print('   %s already in backup' % (rec['hdl']))
            else:
                recs.append(rec)
                hdls.append(rec['hdl'])
        print('  %4i records so far' % (len(recs)))

    
for (i, rec) in enumerate(recs):
    ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['link']]])
    artfilename = '/tmp/goettingen.%s' % (re.sub('\W', '', rec['link']))
    if not os.path.isfile(artfilename):
        os.system('wget -q -O  %s "%s"' % (artfilename, rec['link']))
        time.sleep(3)
    inf = open(artfilename, 'r')
    lines = inf.readlines()
    inf.close()
    artpage = BeautifulSoup(' '.join(lines), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['DC.rights', 'citation_title', 'DCTERMS.issued',
                                        'DC.subject', 'DC.language', 'citation_pdf_url',
                                        'DC.description', 'DC.creator', 'DC.identifier'])
    rec['autaff'][-1].append(publisher)
    #supervisor
    for div in artpage.body.find_all('div', attrs = {'class' : 'simple-item-view-other'}):
        for span in div.find_all('span'):
            if re.search('(Advisor|Betreuer)', span.text):
                divt = re.sub('(Dr|Prof)\.', '', div.text)
                divt = re.sub('PD ', '', divt)
                divt = re.sub('.*: *', '', divt)
                rec['supervisor'].append([divt.strip()])
                             
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)

