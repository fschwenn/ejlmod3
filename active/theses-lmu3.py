# -*- coding: utf-8 -*-
#harvest theses from LMU Munich
#FS: 2019-10-23
#FS: 2023-02-03

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Munich U.'
skipalreadyharvested = True

prerecs = {}
reyear = re.compile('.*\(([12]\d\d\d)\):.*')
for fac in ['16', '17']:
    tocurl = 'https://edoc.ub.uni-muenchen.de/view/subjects/fak%s.html' % (fac)
    ejlmod3.printprogress('+', [[tocurl]])
    hdr = {'User-Agent' : 'Magic Browser'}
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")

    #get all links 
    for p in tocpage.body.find_all('p'):
        for a in p.find_all('a'):
            rec = {'tc' : 'T',  'jnl' : 'BOOK', 'note' : []}
            rec['artlink'] = a['href']
            pt = re.sub('[\n\t\r]', '', p.text.strip())
            if reyear.search(pt):
                rec['year'] = reyear.sub(r'\1', pt)
                if int(rec['year']) in list(prerecs.keys()):
                    prerecs[int(rec['year'])].append(rec)
                else:
                    prerecs[int(rec['year'])] = [rec]

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested('THESES-LMU')
                    
for year in [ ejlmod3.year(backwards=1), ejlmod3.year()]:
    jnlfilename = 'THESES-LMU-%s-%i' % (ejlmod3.stampoftoday(), year)
    if year in list(prerecs.keys()):
        ejlmod3.printprogress('=', [[year], [len(prerecs[year])]])
        recs = []
        i = 0
        for rec in prerecs[year]:
            keepit = True
            i += 1
            ejlmod3.printprogress("-", [[year], [i, len(prerecs[year])], [rec['artlink']], [len(recs)]])
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
            ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'eprints.title_name', 'eprints.date',
                                                'eprints.keywords', 'eprints.abstract_name',
                                                'eprints.document_url', 'eprints.urn', 'eprints.language'])
            rec['autaff'][-1].append(publisher)
            #DDC
            for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.subject'}):
                if meta['content'][:3] == 'ddc':
                    if meta['content'] == 'ddc:510':
                        rec['fc'] = 'm'
                    elif meta['content'] == 'ddc:004':
                        rec['fc'] = 'c'
                    elif meta['content'] == 'ddc:310':
                        rec['fc'] = 's'
                    elif not meta['content'] in ['ddc:500', 'ddc:530', 'ddc:000', 'ddc:300']:
                        rec['note'].append(meta['content'])
            #DOI
            for div in artpage.body.find_all('div', attrs = {'class' : 'ep_block_doi'}):
                for a in div.find_all('a'):
                    if a.has_attr('href') and re.search('doi.org', a['href']):
                        rec['doi'] = re.sub('.*doi.org\/', '', a['href'])
            if not 'doi' in list(rec.keys()):
                rec['link'] = rec['artlink']
            #license
            ejlmod3.globallicensesearch(rec, artpage)
            if skipalreadyharvested:
                if 'urn' in rec and rec['urn'] in alreadyharvested:
                    keepit = False
                elif 'doi' in rec and rec['doi'] in alreadyharvested:
                    keepit = False
            if keepit:
                ejlmod3.printrecsummary(rec)
                recs.append(rec)
        ejlmod3.writenewXML(recs, publisher, jnlfilename)
    else:
        print(year, 0)


