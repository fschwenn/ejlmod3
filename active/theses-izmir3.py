# -*- coding: utf-8 -*-
#harvest theses from Izmir Inst. Tech.
#FS: 2020-12-24
#FS: 2023-02-01

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

publisher = 'Izmir Inst. Tech.'
skipalreadyharvested = True
rpp = 50
pages = 1
boringfacs = ['Architecture', 'Chemistry', 'Architectural Restoration',
              'Biotechnology and Bioengineering', 'Civil Engineering', 
              'Food Engineering', 'Materials Science and Engineering',
              'Chemical Engineering', 'City and Regional Planning',
              'Molecular Biology and Genetics',
              'Conservation and Restoration of Cultural Heritage']
hdr = {'User-Agent' : 'Magic Browser'}
jnlfilename = 'THESES-IZMIR-%s' % (ejlmod3.stampoftoday())

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for page in range(pages):
    tocurl = 'https://openaccess.iyte.edu.tr/xmlui/handle/11147/60/discover?filtertype=type&filter_relational_operator=equals&filter=doctoralThesis&sort_by=dc.date.issued_dt&order=desc&rpp=' + str(rpp) + '&page=' + str(page+1)
    tocurl = 'https://openaccess.iyte.edu.tr/browse?type=type&sort_by=2&order=DESC&rpp=' + str(rpp) + '&etal=-1&value=doctoralThesis&offset=' + str(rpp*page)
    tocurl = 'https://openaccess.iyte.edu.tr/simple-search?query=&location=publications&filter_field_1=itemtype&filter_type_1=equals&filter_value_1=Doctoral+Thesis&filter_field_2=dateIssued&filter_type_2=equals&filter_value_2=%5B2021+TO+2040%5D&crisID=&relationName=&sort_by=score&order=desc&rpp=' + str(rpp) + '&etal=0&start=' + str(rpp*page)
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
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
            rec['link'] = 'https://openaccess.iyte.edu.tr' + a['href'] + '?mode=full'
            rec['hdl'] = re.sub('.*handle\/', '', a['href'])
            if ejlmod3.checkinterestingDOI(rec['hdl']):
                if skipalreadyharvested and rec['hdl'] in alreadyharvested:
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
                                        'citation_language', 'DCTERMS.extent'])
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DCTERMS.abstract'}):
        if re.search(' the ', meta['content']):
            rec['abs'] = meta['content']
    for tr in artpage.body.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldLabel'}):
            label = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldValue'}):
            #department
            if label in ['dc.contributor.department', 'dc.department']:
                fac = re.sub('.zmir Institute of Technology. ', '', td.text.strip())
                if fac in boringfacs:
                    keepit = False
                elif fac in ['Mathematics']:
                    rec['fc'] = 'm'
                elif fac in ['Computer Engineering']:
                    rec['fc'] = 'c'
                else:
                    rec['note'].append(fac)
            #supervisor
            elif label == 'dc.contributor.advisor':
                rec['supervisor'].append([td.text.strip()])
            #ORCID
            elif label == 'dc.authorid':
                rec['autaff'][-1].append('ORCID:'+td.text.strip())
    rec['autaff'][-1].append(publisher)
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

        
ejlmod3.writenewXML(recs, publisher, jnlfilename)
