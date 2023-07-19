# -*- coding: utf-8 -*-
#harvest theses from TU Dortmund
#FS: 2019-09-13
#FS: 2023-03-21

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Tech. U., Dortmund (main)'
jnlfilename = 'THESES-TUD-%s' % (ejlmod3.stampoftoday())
skipalreadyharvested = True
years = 2

recs = []
hdr = {'User-Agent' : 'Magic Browser'}

prerecs = []

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
### TUPrints ###

#for (ddc, fc) in [('530', ''), ('510', 'm'), ('520', 'a'), ('004', 'c')]:
for (ddc, fc) in [('510', 'm'), ('520', 'a'), ('004', 'c')]:
    tocurl = 'https://tuprints.ulb.tu-darmstadt.de/view/subjects/ddc=5Fdnb=5F' + ddc + '.html'
    ejlmod3.printprogress('=', [[ddc], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
    time.sleep(3)

    for p in tocpage.body.find_all('p'):
        pt = re.sub('[\n\t\r]', ' ', p.text.strip())
        doctype = re.sub('.*\[(.*)\].*', r'\1', pt)
        if re.search('Ph.*hesis', doctype) or re.search('abilitation', doctype):
            doi = False
            for a in p.find_all('a'):
                if a.has_attr('href') and re.search('doi.org', a['href']):
                    doi = re.sub('.*org\/', '', a['href']).strip()
            for a in p.find_all('a'):
                for em in a.find_all('em'):
                    takeit = True
                    rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK'}
                    rec['artlink'] = a['href']
                    if fc:
                        rec['fc'] = fc
                    if re.search('\([12]\d\d\d\)', p.text):
                        rec['year'] = re.sub('.*\(([12]\d\d\d)\).*', r'\1', pt)
                        if int(rec['year']) <= ejlmod3.year(backwards=years):
                            #print '  skip %s' % (rec['year'])
                            takeit = False
                    if takeit:
                        if doi and skipalreadyharvested and doi in alreadyharvested:
                            #print('    %s already in backup' % (doi))
                            pass
                        else:
                            prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))

i = 0
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features='lxml')
        time.sleep(4)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features='lxml')
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    #author
    ejlmod3.metatagcheck(rec, artpage, ['eprints.creators_name', 'eprints.language', 'eprints.title', 'eprints.keywords',
                                        'eprints.date', 'eprints.doi', 'eprints.urn', 'eprints.document_url',
                                        'DC.rights'])
    ejlmod3.metatagcheck(rec, artpage, ['eprints.contact_email'])
    if 'language' in rec and rec['language'] != 'en':
        for meta in artpage.head.find_all('meta', attrs = {'name' : 'eprints.titlealternative_name'}):
            rec['transtit'] = meta['content']
        for meta in artpage.head.find_all('meta', attrs = {'name' : 'eprints.abstractalternative_name'}):
            rec['abs'] = meta['content']
    else:
        ejlmod3.metatagcheck(rec, artpage, ['eprints.abstract'])
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    rec['autaff'][0].append(publisher)
    if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        pass
    elif skipalreadyharvested and 'urn' in rec and rec['urn'] in alreadyharvested:
        pass
    else:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)

### ELDORDO ###
tocurl = 'https://eldorado.tu-dortmund.de/handle/2003/35/browse?type=dateissued&sort_by=2&order=DESC&rpp=50&etal=0&submit_browse=Update'
print(tocurl)

prerecs = []
for offset in [0]:
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
    time.sleep(3)
    for td in tocpage.body.find_all('td', attrs = {'headers' : 't2'}):
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK'}
        for a in td.find_all('a'):
            rec['artlink'] = 'https://eldorado.tu-dortmund.de' + a['href']
            rec['hdl'] = re.sub('.*handle\/', '', a['href'])
            if ejlmod3.checkinterestingDOI(rec['artlink']):
                prerecs.append(rec)

i = 0
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features='lxml')
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features='lxml')
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.title', 'DCTERMS.issued', 'DC.subject',
                                        'DC.identifier', 'DC.language', 'DCTERMS.extent',
                                        'citation_pdf_url', 'DCTERMS.abstract', 'DC.rights'])
    rec['autaff'][-1].append(publisher)
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.type'}):
        if meta['content'] != "doctoralThesis":
            keepit = False
    if keepit:
        if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
