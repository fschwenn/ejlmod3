# -*- coding: utf-8 -*-
#harvest theses from Cambridge Univeristy
#FS: 2018-02-02
#FS: 2022-10-30

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

publisher = 'Cambridge U.'
jnlfilename = 'THESES-CAMBRIDGE-%s' % (ejlmod3.stampoftoday())
years = 2
skipalreadyharvested = True
skiptooold = True
dokidir = '/afs/desy.de/user/l/library/dok/ejl/backup'


boring = ['Theses - Chemistry', 'Department of Chemistry']

tocurls = []
tocurls.append('https://www.repository.cam.ac.uk/handle/1810/256064/discover?rpp=100&etal=0&scope=&group_by=none&page=1&sort_by=dc.date.issued_dt&order=desc&filtertype_0=type&filter_relational_operator_0=equals&filter_0=Thesis')
tocurls.append('https://www.repository.cam.ac.uk/handle/1810/256064/discover?rpp=100&etal=0&scope=&group_by=none&page=2&sort_by=dc.date.issued_dt&order=desc&filtertype_0=type&filter_relational_operator_0=equals&filter_0=Thesis')
tocurls.append('https://www.repository.cam.ac.uk/handle/1810/256064/discover?rpp=100&etal=0&scope=&group_by=none&page=1&sort_by=dc.date.issued_dt&order=asc&filtertype_0=type&filter_relational_operator_0=equals&filter_0=Thesis')
tocurls.append('https://www.repository.cam.ac.uk/handle/1810/256064/discover?rpp=100&etal=0&scope=&group_by=none&page=2&sort_by=dc.date.issued_dt&order=asc&filtertype_0=type&filter_relational_operator_0=equals&filter_0=Thesis')
tocurls.append('https://www.repository.cam.ac.uk/handle/1810/256064/discover?rpp=100&etal=0&scope=&group_by=none&page=3&sort_by=dc.date.issued_dt&order=asc&filtertype_0=type&filter_relational_operator_0=equals&filter_0=Thesis')

alreadyharvested = []
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
artlinks = []
for tocurl in tocurls:
    try:
        print(tocurl)
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (tocurl))
        time.sleep(180)
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://www.repository.cam.ac.uk', fakehdl=True):
        if ejlmod3.checkinterestingDOI(rec['link']):
            if not rec['link'] in artlinks:
                if skiptooold:
                    if ejlmod3.checknewenoughDOI(rec['link']):
                        prerecs.append(rec)
                    else:
                        print('    %s too old' % (rec['link']))
                else:
                    prerecs.append(rec)
        else:
            print('    %s uninteresting' % (rec['link']))



recs = []
for (i, rec) in enumerate(prerecs):
    keepit = True
    aff = []
    ejlmod3.printprogress('-', [[i+1, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['link']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
    for a in artpage.body.find_all('a'):
        #check department
        if a.has_attr('role') and a['role'] == 'menuitem':
            at = a.text.strip()
            if at in boring:
                keepit = False
                ejlmod3.adduninterestingDOI(rec['link'])
            elif at in ['Department of Pure Mathematics and Mathematical Statistics (DPMMS)',
                        'Theses - Pure Mathematics and Mathematical Statistics']:
                rec['fc'] = 'm'
            elif not a.text.strip() in ['Apollo Home', 'School of the Physical Sciences',
                                        'Department of Physics - The Cavendish Laboratory',
                                        'Theses - Physics']:
                rec['note'].append(a.text.strip())
        #PDF link often not in meta tags
        elif a.has_attr('href') and re.search('bitstream.*\.pdf', a['href']):
            rec['pdf_url'] = 'https://www.repository.cam.ac.uk' + a['href']
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DCTERMS.issued', 'DCTERMS.abstract', 'DC.rights',
                                        'citation_pdf_url', 'DC.identifier', 'citation_date'])
    if int(re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])) < ejlmod3.year(backwards=years):
        keepit = False
        print('   skip', rec['date'])
        ejlmod3.addtoooldDOI(rec['link'])            
    for div in artpage.body.find_all('div', attrs = 'item-page-field-wrapper'):
        for h5 in div.find_all('h5'):
            h5text = h5.text.strip()
        if h5text == 'Authors':
            for div2 in div.find_all('div'):
                rec['autaff'] = [[ div2.text.strip() ]]
                for a in div2.find_all('a', attrs = {'title' : 'ORCID iD'}):
                    rec['autaff'][-1].append(re.sub('.*\/(.*)', r'ORCID:\1', a['href']))
        elif h5text == 'Advisors':
            for div2 in div.find_all('div'):
                sv = [ div2.text.strip() ]
                for a in div2.find_all('a', attrs = {'title' : 'ORCID iD'}):
                    sv.append(re.sub('.*\/(.*)', r'ORCID:\1', a['href']))
                rec['supervisor'].append(sv)
        elif h5text == 'Author Affiliation':
            aff += [div2.text.strip() for div2 in div.find_all('div')]
        elif h5text == 'Awarding Institution':
            aff += [div2.text.strip() for div2 in div.find_all('div')]
        elif h5text == 'Qualification':
            for div2 in div.find_all('div'):
                dt = div2.text.strip()
                if dt in ['MPhil']:
                    print('  skip "%s"' % (dt))
                    keepit = False
                    ejlmod3.adduninterestingDOI(rec['link'])
                else:
                    rec['note'] = [ dt ]
    if aff:
        rec['autaff'][-1].append(', '.join(aff))
    else:
        rec['autaff'][-1].append(publisher)
    if keepit:
        if 'doi' in rec and rec['doi'] in alreadyharvested:
            print('  already in backup')
        else:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
