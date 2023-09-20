# -*- coding: utf-8 -*-
#harvest theses from Rio Grande do Norte U.
#FS: 2023-08-15

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

publisher = 'Rio Grande do Norte U.'
skipalreadyharvested = True
rpp = 20
pages = 1
hdr = {'User-Agent' : 'Magic Browser'}
jnlfilename = 'THESES-RioGrandedoNorteU-%s' % (ejlmod3.stampoftoday())

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for (dep, fc) in [('12024', ''), ('12058', 'c')]:
    for page in range(pages):
        tocurl = 'https://repositorio.ufrn.br/handle/123456789/' + dep + '/browse?type=type&sort_by=2&order=DESC&rpp=' + str(rpp) + '&etal=-1&value=doctoralThesis&offset=' + str(rpp*page)
        ejlmod3.printprogress("=", [[dep], [page+1, pages], [tocurl]])
        try:
            req = urllib.request.Request(tocurl, headers=hdr)
            tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        except:
            print("retry in 300 seconds")
            time.sleep(300)
            req = urllib.request.Request(tocurl, headers=hdr)
            tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(3)
        for div in tocpage.body.find_all('td', attrs = {'headers' : 't2'}):
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'note' : [], 'supervisor'  : []}
            for a in div.find_all('a'):
                rec['link'] = 'https://repositorio.ufrn.br' + a['href'] + '?mode=full'
                rec['doi'] = '20.2000/RioGrandedoNorteU/' + re.sub('.*handle\/', '', a['href'])
                if fc: rec['fc'] = fc
                if ejlmod3.checkinterestingDOI(rec['doi']):
                    if skipalreadyharvested and rec['doi'] in alreadyharvested:
                        #print('   already in backup')
                        pass
                    else:
                        prerecs.append(rec)

recs = []
i = 0
for rec in prerecs:
    keepit = True
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
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue      
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.title', 'DCTERMS.issued',
                                        'DC.subject', 'citation_pdf_url',
                                        'DC.language', 'DC.rights',
                                        'DCTERMS.abstract'])
    for tr in artpage.body.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldLabel'}):
            label = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldValue', 'headers' : 's2'}):
            #supervisor
            if label == 'dc.contributor.advisor':
                rec['supervisor'].append([td.text.strip()])
            #ORCID
            elif label == 'dc.contributor.advisorID':
                tdt = td.text.strip()
                if re.search('orcid.org', tdt):
                    rec['supervisor'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', tdt))
            elif label == 'dc.contributor.authorID':
                tdt = td.text.strip()
                if re.search('orcid.org', tdt):
                    rec['autaff'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', tdt))
    rec['autaff'][-1].append(publisher)
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])
        
ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
