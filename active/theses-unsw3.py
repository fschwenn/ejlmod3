# -*- coding: utf-8 -*-
#harvest theses from UNSW
#FS: 2023-12-20

import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

jnlfilename = 'THESES-UNSW-%s' % (ejlmod3.stampoftoday())

publisher = 'New South Wales U.'

rpp = 60
pages = 1000
skipalreadyharvested = True
years = 2

boring = ['School of Biological, Earth &a; Environmental Sciences',
          'Medicine &a; Health',
          'Centre for Ecosystem Science or Climate Change Research Centre',
          'Centre for Marine Science and Innovation',
          'School of Biological, Earth &a; Environmental Sciences',
          'School of Biotechnology &a; Biomolecular Sciences',
          'School of Civil and Environmental Engineering',
          'School of Clinical Medicine', 'School of Medical Sciences',
          'School of Psychology', 'Business', 'School of Aviation',
          'School of Banking &a; Finance', 'School of Chemical Engineering',
          'School of Chemistry', 'School of Risk &a; Safety Science',
          'Arts Design &a; Architecture', 'ARC Centre of Excellence for Climate Extremes',
          'Climate Change Research Centre', 'School of Biomedical Engineering',
          'School of Built Environment', 'School of Humanities &a; Languages']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


recs = []
baseurl = 'https://unsworks.unsw.edu.au'
for page in range(pages):
    #date sorting does not work
    #tocurl = 'https://unsworks.unsw.edu.au/search?spc.page=' + str(page+1) + '&spc.sf=dc.date.accessioned&spc.sd=DESC&spc.rpp=' +str(rpp) + '&f.resourceType=PhD%20Doctorate,equals&f.faculty=Science,equals'
    tocurl = 'https://unsworks.unsw.edu.au/search?spc.page=' + str(page+1) + '&spc.sf=score&spc.sd=DESC&spc.rpp=' +str(rpp) + '&f.resourceType=PhD%20Doctorate,equals&f.faculty=Science,equals&f.publicationYear.min=' + str(ejlmod3.year(backwards=years-1)) + '&f.publicationYear.max=' + str(ejlmod3.year())
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        time.sleep(5)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        time.sleep(5)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    for small in tocpage.find_all('small', attrs = {'class' : 'results'}):
        if re.search('^\d+ results', small.text):
            numofrecs = int(re.sub('\D', '', small.text.strip()))
    pages = numofrecs // rpp
    
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.author', 'dc.contributor.advisor', 'dc.date.issued',
                                               'dc.description.abstract', 'dc.identifier.uri', 'dc.rights',
                                               'dc.rights.uri', 'dc.subject.other', 'dc.title', 'unsw.identifier.doi',
                                               'unsw.relation.faculty', 'unsw.relation.school', 'unsw.thesis.degreetype'],
                            boring=boring, alreadyharvested=alreadyharvested):
        rec['autaff'] = [[ rec['autaff'][0][0], publisher ]]
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
        #print(rec['doi'], rec['thesis.metadata.keys'])
    print('  %i records so far' % (len(recs)))
    if page+1 >= pages:
        break
    time.sleep(20)



#2nd run to get ORCIDs
for (i, rec) in enumerate(recs):
    arturl = '%s/entities/publication/%s' % (baseurl, rec['uuid'])
    ejlmod3.printprogress('-', [[i+1, len(recs)], [arturl]])
    try:
        driver.get(arturl)
        time.sleep(5)
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(arturl)
        time.sleep(5)
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    for ds in artpage.find_all('ds-metadata-representation-list'):
        for h5 in ds.find_all('h5'):
            h5t = h5.text.strip()
            for (reckey, meta) in [('autaff', 'Author(s)'), ('supervisor', 'Supervisor(s)')]:
                if h5t == meta:
                    #print(reckey)
                    rec[reckey] = []
                    for div in ds.find_all('div', attrs = {'class' : 'simple-view-element-body'}):
                        for a in div.find_all('a'):
                            if a.has_attr('href'):
                                if re.search('\/browse\/author.value', a['href']):
                                    rec[reckey].append([a.text.strip()])
                                elif re.search('orcid.org', a['href']):
                                    rec[reckey][-1].append(re.sub('.*orcid.org\/', 'ORCID:', a['href']))
                                    #print('        ', rec[reckey][-1])
                    if reckey == 'autaff':
                        rec[reckey][-1].append(publisher)
    ejlmod3.printrecsummary(rec)
    time.sleep(10)

    
ejlmod3.writenewXML(recs, publisher, jnlfilename)
