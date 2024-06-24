# -*- coding: utf-8 -*-
#harvest theses from Barcelona U.
#FS: 2020-11-19
#FS: 2023-03-27

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

publisher = 'U. Barcelona (main)'
jnlfilename = 'THESES-BARCELONA-%s' % (ejlmod3.stampoftoday())

rpp = 20
startyear = ejlmod3.year(backwards=1)
skipalreadyharvested = True
departments = [('PHYS', 'Barcelona U.', ['35246', '41813', '103124', '106688', '41840', '41381']),
	       ('MATH', 'U. Barcelona (main)', ['42083', '43181', '35131', '182780']),
               ('COMP', 'U. Barcelona (main)', ['99760'])]
hdr = {'User-Agent' : 'Magic Browser'}
#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdls = []
recs = []
for (subj, aff, deps) in departments:
    for dep in deps:
        tocurl = 'https://diposit.ub.edu/dspace/handle/2445/' + dep + '/browse?type=title&sort_by=2&order=DESC&rpp=' + str(rpp) + '&etal=0&submit_browse=Update'
        ejlmod3.printprogress("=", [[subj], [dep], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(3)
        for tr in tocpage.body.find_all('tr'):
            keepit = True
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'affiliation' : aff,
                   'supervisor' : []}
            for td in tr.find_all('td', attrs = {'headers' : 't1'}):
                if re.search('\d\d\d\d$', td.text):
                    rec['date'] = re.sub('.*(\d\d\d\d)$', r'\1', td.text.strip())
                    if int(rec['date']) < startyear:
                        keepit = False
            if dep in ['35246', '41840']:
                rec['fc'] = 'a'
            elif subj == 'MATH':
                rec['fc'] = 'm'
            elif subj == 'COMP':
                rec['fc'] = 'c'
            for td in tr.find_all('td', attrs = {'headers' : 't2'}):
                for a in td.find_all('a'):                
                    rec['artlink'] = 'https://diposit.ub.edu' + a['href'] 
                    rec['hdl'] = re.sub('.*handle\/', '', a['href'])
                    if keepit:
                        if not rec['hdl'] in hdls:
                            if not skipalreadyharvested or not rec['hdl'] in alreadyharvested:
                                recs.append(rec)
                                hdls.append(rec['hdl'])
        print('   %i records so far' % (len(recs)))

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue      
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.contributor', 'DC.title',
                                        'DCTERMS.issued', 'DC.subject', 'citation_pdf_url',
                                        'DCTERMS.extent'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):

            #abstract
            if meta['name'] == 'DCTERMS.abstract':
                if re.search('\[eng\]', meta['content']):
                    rec['abs'] = re.sub('\[eng\] *', '', meta['content'])
                else:
                    rec['absspa'] = re.sub('^\[.*\] ', '', meta['content'])
            if not 'abs' in list(rec.keys()) and 'absspa' in list(rec.keys()):
                rec['abs'] = rec['absspa']
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
