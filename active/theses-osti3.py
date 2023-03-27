# -*- coding: utf-8 -*-
#harvest theses from OSTI
#FS: 2020-05-26
#FS: 2023-03-27


import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl



numofpages = 1
skipalreadyharvested = True
publisher = 'OSTI'
startyear = ejlmod3.year(backwards=2)
pages = 20
chunksize = 100

uninteresting = [re.compile('biolog'), re.compile('chemic'), re.compile('medic'),
                 re.compile('waste'), re.compile('wildlife'), re.compile('chemistry')]
jnlfilename = 'THESES-OSTI-%s' % (ejlmod3.stampoftoday())

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}

prerecs = []
for page in range(pages):
    tocurl = 'https://www.osti.gov/search/sort:publication_date%20desc/publish-date-start:01/01/' + str(startyear) + '/publish-date-end:31/12/2050/product-type:Thesis/Dissertation/page:' + str(page+1)
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    try:
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(10)
    except:
        print('    try again in 180s')
        time.sleep(180)
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(10)
    for h2 in tocpage.body.find_all('h2', attrs = {'class' : 'title'}):
        for a in h2.find_all('a'):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : [], 'rn' : [], 'keyw' : []}
            rec['artlink'] = 'https://www.osti.gov' + a['href']
            if ejlmod3.checkinterestingDOI(rec['artlink']):
                prerecs.append(rec)
    print('   ', len(prerecs))

i = 0
recs = []
for rec in prerecs:
    skipit = False
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']))
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    for script in artpage.find_all('script', attrs = {'type' : 'text/javascript'}):
        script.decompose()
    ejlmod3.metatagcheck(rec, artpage, ['citation_date', 'citation_doi', 'citation_pdf_url',
                                        'citation_title', 'citation_keywords'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] in ['citation_authors', 'citation_author']:
                author = meta['content']
                if re.search('ORCID:', author):
                    rec['autaff'] = [[re.sub(' .ORCID.*', '', author)]]
                    orcid = re.sub('.*ORCID:(.*[\dX]).*', r'\1', author)
                    if len(orcid) == 16:
                        rec['autaff'][-1].append('ORCID:%s-%s-%s-%s' % (orcid[0:4], orcid[4:8], orcid[8:12], orcid[12:16]))
                    else:
                        rec['note'].append('ORCID? '+orcid)
                else:
                    rec['autaff'] = [[author]]
            #report number
            elif meta['name'] == 'citation_technical_report_number':
                for rn in re.split('; ', meta['content']):
                    rec['rn'].append(rn)
                    if re.search('FERMILAB', rn):
                        skipit = True
                        print('  skip "%s"' % (rn))
            #not affiliation but Lab
            #elif meta['name'] == 'citation_technical_report_institution':
            #    rec['autaff'][-1].append(meta['content'])
    #affiliation
    for ol in artpage.find_all('ol', attrs = {'class' : 'affiliation_list'}):
        for li in ol.find_all('li'):
            if 'autaff' in list(rec.keys()):
                rec['autaff'][-1].append(li.text.strip())
    for script in artpage.body.find_all('script', attrs = {'type' : 'application/ld+json'}):
        if script.contents:
            scriptt = re.sub('[\n\t]', '', script.contents[0].strip())
            metadata = json.loads(scriptt)
            #abstract
            if 'description' in list(metadata.keys()):
                rec['abs'] = metadata['description']
            if 'datePublished' in list(metadata.keys()):
                rec['date'] = metadata['datePublished']
    #OSTI-number
    for dl in artpage.body.find_all('dl'):
        for dt in dl.find_all('dt'):
            if re.search('OSTI Identifier:', dt.text):
                for dd in dl.find_all('dd'):
                    rec['rn'].append('OSTI-%s' % (dd.text.strip()))
                    #fake doi
                    if not 'doi' in list(rec.keys()):
                        rec['doi'] = '20.2000/OSTI/' + dd.text.strip()
                        rec['link'] = rec['artlink']
    #abstract
    if not 'abs' in list(rec.keys()):
        for p in artpage.body.find_all('p', attrs = {'id' : 'citation-abstract'}):
            rec['abs'] = p.text.strip()
    for keyw in rec['keyw']:
        if not skipit:
            for unin in uninteresting:
                if unin.search(keyw):
                    skipit = True
                    print('  skip "%s"' % (keyw))
                    break
    if skipit:
        ejlmod3.adduninterestingDOI(rec['artlink'])
    else:
        if not skipalreadyharvested or not 'doi' in rec or not rec['doi'] in alreadyharvested:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
