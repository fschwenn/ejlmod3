# -*- coding: utf-8 -*-
#harvest theses from Calgary
#FS: 2020-11-21

import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Calgary U.'
rpp = 50
numofpages = 1
jnlfilename = 'THESES-CALGARY-%s' % (ejlmod3.stampoftoday())

boring = ['Biological Sciences', 'Chemistry', 'Geoscience', 'Psychology – Clinical', 'Economics', 'Medicine – Neuroscience']
boring += ['Biological+Sciences', 'Chemistry', 'Geoscience', 'Psychology+%E2%80%93+Clinical', 'Medicine+%E2%80%93+Neuroscience']

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for i in range(numofpages):
    tocurl = 'https://prism.ucalgary.ca/handle/1880/100031/discover?rpp=' + str(rpp) + '&etal=0&scope=&group_by=none&page=' + str(i+1) + '&sort_by=dc.date.issued_dt&order=desc&filtertype_0=pubFaculty&filtertype_1=degree&filter_relational_operator_1=equals&filter_relational_operator_0=equals&filter_1=Doctor+of+Philosophy+%28PhD%29&filter_0=Science'
    ejlmod3.printprogress('=', [[i+1, numofpages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://prism.ucalgary.ca'):
        if ejlmod3.checkinterestingDOI(rec['hdl']):
            keepit = True            
            if 'degrees' in rec:
                for deg in rec['degrees']:
                    if deg in boring:
                        keepit = False
            if keepit: 
                prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(3)
            
j = 0
recs = []
for rec in prerecs:
    keepit = True
    j += 1
    ejlmod3.printprogress('-', [[j, len(prerecs)], [rec['link']], [len(recs)]])
    req = urllib.request.Request(rec['link']+'?show=full')
    artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(5)
    ejlmod3.metatagcheck(rec, artpage, ['citation_date', 'DC.creator', 'DC.subject',
                                        'DC.rights', 'citation_pdf_url', 'DC.identifier',
                                        'DCTERMS.abstract'])
    rec['autaff'][-1].append(publisher)                        
    #supervisor
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'ds-table-row'}):
        (label, word) = ('', '')
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            label = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'word-break'}):
            word = td.text.strip()
        #department
        if re.search('thesis.degree.discipline', label):
            if word in boring:
                keepit = False
            elif word == 'Mathematics & Statistics':
                rec['fc'] = 'm'
            elif word == 'Computer Science':
                rec['fc'] = 'c'
            elif word != 'Physics & Astronomy':
                rec['note'].append(word)
        #supervisor
        elif re.search('dc.contributor.advisor', label):
            rec['supervisor'].append(word)
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])
        

ejlmod3.writenewXML(recs, publisher, jnlfilename)

