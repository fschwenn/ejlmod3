# -*- coding: utf-8 -*-
#harvest theses from Mississippi U.
#FS: 2020-05-26
#FS: 2023-04-05

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

numofpages = 3
skipalreadyharvested = True


publisher = 'Mississippi U.'
jnlfilename = 'THESES-MISSISSIPPI-%s' % (ejlmod3.stampoftoday())

uninteresting = [re.compile('M\.A\.'), re.compile('M\.S\.'), re.compile('Ed\.D\.'),
                 re.compile('Ed\.S\.'), re.compile('M\.C\.J\.'), re.compile('M\.F\.A\.'),
                 re.compile('M\.M\.'), re.compile('Accountancy'), re.compile('Art'),
                 re.compile('Biological Science'), re.compile('Business Administration'),
                 re.compile('Chemistry'), re.compile('Counselor Education'),
                 re.compile('Creative Writing'), re.compile('Criminal Justice'),
                 re.compile('Curriculum and Instruction'), re.compile('Documentary Expression'),
                 re.compile('Economics'), re.compile('Education'), re.compile('English'),
                 re.compile('Health and Kinesiology'), re.compile('Higher Education'),
                 re.compile('History'), re.compile('Music'),
                 re.compile('Nutrition and Hospitality Management'),
                 re.compile('Pharmaceutical Sciences'), re.compile('Political Science'),
                 re.compile('Psychology')]

if skipalreadyharvested:    
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
                 
hdr = {'User-Agent' : 'Magic Browser'}

prerecs = []
for i in range(numofpages):
    if i == 0:
        tocurl = 'https://egrove.olemiss.edu/etd/index.html'
    else:
        tocurl = 'https://egrove.olemiss.edu/etd/index.%i.html' % (i+1)
    ejlmod3.printprogress("=", [[i+1, numofpages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(3)
    for p in tocpage.body.find_all('p', attrs = {'class' : 'article-listing'}):
        for a in p.find_all('a'):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : []}
            rec['artlink'] = a['href']
            if ejlmod3.checkinterestingDOI(rec['artlink']):
                if not skipalreadyharvested or not '20.2000/Mississippi/' + re.sub('\D', '', rec['artlink']) in alreadyharvested:
                    prerecs.append(rec)
    print('  %4i records so far ' % (len(prerecs)))
            
i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    #license
    for link in artpage.head.find_all('link', attrs = {'rel' : 'license'}):
        rec['license'] = {'url' : link['href']}
    ejlmod3.metatagcheck(rec, artpage, ['bepress_citation_title', 'bepress_citation_date',
                                        'description', 'bepress_citation_pdf_url',
                                        'bepress_citation_doi'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'bepress_citation_author':
                author = re.sub(' *\[.*', '', meta['content'])
                rec['autaff'] = [[ author ]]
                for div in artpage.body.find_all('div', attrs = {'id' : 'orcid'}):
                    for p in div.find_all('p'):
                        rec['autaff'][-1].append('ORCID:%s' % (p.text.strip()))
                for meta2 in artpage.head.find_all('meta', attrs = {'name' : 'bepress_citation_author_institution'}):
                    rec['autaff'][-1].append(meta2['content']+', USA')
            #typ of dissertation
            elif meta['name'] == 'bepress_citation_dissertation_name':
                disstyp = meta['content'].strip()
    if not 'doi' in list(rec.keys()):
        rec['doi'] = '20.2000/Mississippi/' + re.sub('\D', '', rec['artlink'])
        rec['link'] = rec['artlink']
    skipit = False
    for regexpr in uninteresting:
        if regexpr.search(disstyp):
            skipit = True
            break
    if skipit:
        ejlmod3.adduninterestingDOI(rec['artlink'])
        print('     skip %s' % (disstyp))
    else:
        if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
            rec['note'].append(disstyp)
            recs.append(rec)
            ejlmod3.printrecsummary(rec)

line = jnlfilename+'.xml'+ "\n"




ejlmod3.writenewXML(recs, publisher, jnlfilename)
