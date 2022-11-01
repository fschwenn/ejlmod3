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

boring = ['Theses - Chemistry', 'Department of Chemistry']

tocurls = []
tocurls.append('https://www.repository.cam.ac.uk/handle/1810/256064/discover?rpp=100&etal=0&scope=&group_by=none&page=1&sort_by=dc.date.issued_dt&order=desc&filtertype_0=type&filter_relational_operator_0=equals&filter_0=Thesis')
tocurls.append('https://www.repository.cam.ac.uk/handle/1810/256064/discover?rpp=100&etal=0&scope=&group_by=none&page=2&sort_by=dc.date.issued_dt&order=desc&filtertype_0=type&filter_relational_operator_0=equals&filter_0=Thesis')
tocurls.append('https://www.repository.cam.ac.uk/handle/1810/256064/discover?rpp=100&etal=0&scope=&group_by=none&page=1&sort_by=dc.date.issued_dt&order=asc&filtertype_0=type&filter_relational_operator_0=equals&filter_0=Thesis')
tocurls.append('https://www.repository.cam.ac.uk/handle/1810/256064/discover?rpp=100&etal=0&scope=&group_by=none&page=2&sort_by=dc.date.issued_dt&order=asc&filtertype_0=type&filter_relational_operator_0=equals&filter_0=Thesis')
tocurls.append('https://www.repository.cam.ac.uk/handle/1810/256064/discover?rpp=100&etal=0&scope=&group_by=none&page=3&sort_by=dc.date.issued_dt&order=asc&filtertype_0=type&filter_relational_operator_0=equals&filter_0=Thesis')

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
    for div in tocpage.body.find_all('div', attrs = {'class' : 'artifact-description'}):
        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'supervisor' : [], 'note' : []}
        for h4 in div.find_all('h4'):
            for a in h4.find_all('a'):
                rec['tit'] = a.text.strip()
                rec['artlink'] = 'https://www.repository.cam.ac.uk' + a['href']
                if ejlmod3.ckeckinterestingDOI(rec['artlink']) and not rec['artlink'] in artlinks:
                    prerecs.append(rec)
                    artlinks.append(rec['artlink'])

recs = []
for (i, rec) in enumerate(prerecs):
    keepit = True
    aff = []
    ejlmod3.printprogress('-', [[i+1, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['artlink']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    for a in artpage.body.find_all('a'):
        #check department
        if a.has_attr('role') and a['role'] == 'menuitem':
            at = a.text.strip()
            if at in boring:
                keepit = False
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
        if int(re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])) < ejlmod3.year(backwards=years*10):
            ejlmod3.adduninterestingDOI(rec['artlink'])            
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
                    ejlmod3.adduninterestingDOI(rec['artlink'])
                else:
                    rec['note'] = [ dt ]
    if aff:
        rec['autaff'][-1].append(', '.join(aff))
    else:
        rec['autaff'][-1].append(publisher)
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
