# -*- coding: utf-8 -*-
#harvest theses from Buenos Aires, CONICET
#FS: 2022-02-14
#FS: 2023-04-11

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

rpp = 50
skipalreadyharvested = True
startyear = ejlmod3.year(backwards=2)
stopyear = ejlmod3.year()


publisher = 'Buenos Aires, CONICET'
jnlfilename = 'THESES-BuenosAiresCONICET-%s' % (ejlmod3.stampoftoday())

hdr = {'User-Agent' : 'Magic Browser'}
#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

recs = []
artlinks = []
for (dep, fc) in [('16', 'a'), ('2', 'm'), ('1', ''), ('9', '')]:
    urltrunc = 'https://ri.conicet.gov.ar/discover?filtertype_0=type&filtertype_1=dateIssued&filter_relational_operator_1=equals&filter_relational_operator_0=contains&filter_1=%5B' + str(startyear) + '+TO+' + str(stopyear) + '%5D&filter_0=thesis&filtertype=subjectClassification&filter_relational_operator=authority&filter=' + dep + '&rpp=' + str(rpp) + '&page='
    tocurl = urltrunc + '1'
    ejlmod3.printprogress("=", [[dep], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpages = [ BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml") ]
    for h2 in tocpages[0].find_all('h2', attrs = {'class' : 'ds-div-head'}):
        for span in h2.find_all('span'):
            span.decompose()
        try:
            numoftheses = int(re.sub('.*\D(\d+).*', r'\1', h2.text.strip()))
        except:
            numoftheses = 0
        if numoftheses > 0:
            print('   %4i theses to harvest' % (numoftheses))
    for page in range((numoftheses-1) // rpp):
        time.sleep(3)
        tocurl = urltrunc + str(page+2)
        ejlmod3.printprogress("=", [[dep], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpages.append(BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml"))
    for tocpage in tocpages:
        for div in tocpage.body.find_all('div', attrs = {'class' : 'artifact-title'}):
            for a in div.find_all('a'):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'keyw' : [], 'note' : [], 'supervisor' : []}
                rec['artlink'] = 'https://ri.conicet.gov.ar' + a['href'] + '?show=full'
                rec['hdl'] = re.sub('.*handle\/', '', a['href'])
                if fc:
                    rec['fc'] = fc
                if not rec['artlink'] in artlinks:
                    if not skipalreadyharvested or not rec['hdl'] in alreadyharvested:
                        recs.append(rec)
                        artlinks.append(rec['artlink'])
        print('   %4i' %  (len(recs)))

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    try:
        req = urllib.request.Request(rec['artlink'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(4)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.contributor', 'DC.title',
                                        'DC.subject', 'DCTERMS.abstract', 'citation_date',
                                        'citation_doi', 'citation_pdf_url', 'DC.language',
                                        'DC.rights'])
    rec['autaff'][-1].append(publisher)
    ejlmod3.printrecsummary(rec)
    print('   ', list(rec.keys()))

ejlmod3.writenewXML(recs, publisher, jnlfilename)
