# -*- coding: utf-8 -*-
#harvest theses from Oslo
#FS: 2020-08-21

import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Oslo U.'
rpp = 20
numofpages = 1
jnlfilename = 'THESES-OSLO-%s' % (ejlmod3.stampoftoday())


hdr = {'User-Agent' : 'Magic Browser'}
recs = []
for (depnr, dep) in [(14, 'Phys'), (11, 'Astro'), (6, 'Math')]:
    for i in range(numofpages):
        tocurl = 'https://www.duo.uio.no/handle/10852/' + str(depnr) + '/discover?order=DESC&rpp=' + str(rpp) + '&sort_by=dc.date.issued_dt&page=' + str(i+1) + '&group_by=none&etal=0&filtertype_0=type&filter_0=Doktoravhandling&filter_relational_operator_0=equals'
        ejlmod3.printprogress('=', [[depnr, dep], [i+1, numofpages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(2)
        for div in tocpage.body.find_all('div', attrs = {'class' : 'artifact-title'}):
            for a in div.find_all('a'):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : [], 'autaff' : []}
                rec['link'] = 'https://www.duo.uio.no' + a['href']
                rec['hdl'] = re.sub('\/handle\/', '', a['href'])
                rec['tit'] = a.text.strip()
                if dep == 'Astro':
                    rec['fc'] = 'a'
                elif dep == 'Math':
                    rec['fc'] = 'm'
                recs.append(rec)
            
j = 0
for rec in recs:
    j += 1
    ejlmod3.printprogress('-', [[j, len(recs)], [rec['link']]])
    req = urllib.request.Request(rec['link'])
    artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(5)
    ejlmod3.metatagcheck(rec, artpage, ['citation_date', 'DC.creator', 'citation_language',
                                        'DC.rights', 'citation_pdf_url', 'DC.identifier'])
    rec['autaff'][-1].append(publisher)                        
    #abstract
    for meta in artpage.find_all('meta', attrs = {'name' : 'DCTERMS.abstract'}):
        if meta.has_attr('xml:lang') and meta['xml:lang'] in ['eng', 'en_US']:
            rec['abs'] = meta['content']
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)

