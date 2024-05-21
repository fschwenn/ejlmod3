# -*- coding: utf-8 -*-
#harvest theses from Carleton U. (main)
#FS: 2019-12-12
#FS: 2023-04-07
#FS: 2024-03-07

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import undetected_chromedriver as uc
import ejlmod3
import time

rpp = 50 
pages = 15
skipalreadyharvested = True
boring = ['Geography', 'Engineering, Environmental', 'Architecture',
          'Digital Media', 'Applied Linguistics and Discourse Studies', 'Biology',
          'Earth Sciences', 'Engineering, Building', 'Engineering, Civil',
          'Management', 'Political Science', 'Psychology', 'Public Policy',
          'Sociology', 'Anthropology', 'Cognitive Science', 'Economics',
          'English', 'Neuroscience', 'Canadian Studies', 'Chemistry',
          'Communication', 'Cultural Mediations', 'Engineering, Aerospace',
          'Ethics and Public Affairs', 'Health Sciences', 'International Affairs',
          'Legal Studies', 'Social Work', 'DIS:::Engineering, Biomedical',
          'History']
boring += ["Master's"]
baseurl = 'https://repository.library.carleton.ca'
collection = 'm039k491c'
tags = ['dc.contributor.author', 'dc.title']


publisher = 'Carleton U. (main)'
jnlfilename = 'THESES-CARLETON-%s' % (ejlmod3.stampoftoday())
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []



options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
options.binary_location='/usr/bin/google-chrome'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

prerecs = []
for page in range(pages):
    tocurl = baseurl + '/collections/' + collection + '?page=' + str(page+1) + '&per_page=' + str(rpp) + '&sort=system_create_dtsi+desc'
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        time.sleep(5)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    for tr in tocpage.find_all('tr'):
        for p in tr.find_all('p', attrs = {'class' : 'media-heading'}):
            rec = {'jnl' : 'BOOK', 'tc' : 'T', 'note' : [], 'keyw' : []}
            for a in p.find_all('a'):
                rec['artlink'] = baseurl + a['href']
                if ejlmod3.checkinterestingDOI(rec['artlink']):
                    prerecs.append(rec)
                else:
                    print('  ', rec['artlink'], 'is uninteresting')
    print('  %i records so far' % (len(prerecs)))
    time.sleep(20)


recs = []
for (i, rec) in enumerate(prerecs):
    keepit = True
    ejlmod3.printprogress('-', [[i+1, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        driver.get(rec['artlink'])
        time.sleep(5)
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_pdf_url', 'citation_title', 'citation_author',
                                        'citation_publication_date'])
    for dl in artpage.find_all('dl'):
        for child in dl.children:
            try:
                dn = child.name
            except:
                dn = ''
            if dn == 'dt':
                dt = child.text.strip()
            elif dn == 'dd':
                #abstract
                if dt == 'Abstract':
                    rec['abs'] = child.text.strip()
                #subject
                if dt == 'Subject':
                    for a in child.find_all('a'):
                        rec['keyw'].append(a.text.strip())
                #Thesis Degree Level
                if dt == 'Thesis Degree Level':
                    degree = child.text.strip()
                    if degree in boring:
                        print('  skip "%s"' % (degree))
                        keepit = False                        
                    if degree != 'Doctoral':
                        rec['note'].append('DEG:::' + degree)
                #DOI
                if dt == 'Identifier':
                    for a in child.find_all('a'):
                        rec['doi'] = re.sub('.*doi.org\/', '', a['href'])
                #discipline
                if dt == 'Thesis Degree Discipline' and keepit:
                    discipline = child.text.strip()
                    if discipline in boring:
                        print('  skip "%s"' % (discipline))
                        keepit = False
                    elif discipline in ['Pure Mathematics']:
                        rec['fc'] = 'm'
                    elif discipline in ['Computer Science']:
                        rec['fc'] = 'c'
                    elif not discipline in ['Physics']:
                        rec['note'].append('DIS:::' + discipline)
    if keepit:
        if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
            print('  already in backup')
        else:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])
        

    
    
ejlmod3.writenewXML(recs, publisher, jnlfilename)





        
