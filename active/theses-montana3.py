# -*- coding: utf-8 -*-
#harvest theses from Montana State U.
#FS: 2020-11-27
#FS: 2023-04-17
#FS: 2024-04-02

import sys
import os
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
import re
import ejlmod3
import time

publisher = 'Montana State U.'
jnlfilename = 'THESES-MONTANASTATEU-%s' % (ejlmod3.stampoftoday())

rpp = 100-60
pages = 4+6
skipalreadyharvested = True

hdr = {'User-Agent' : 'Firefox'}

boring = ['American Studies.', 'Chemical+%26+Biological+Engineering.',
          'Chemistry+%26+Biochemistry.', 'Ecology',
          'Doctor+of+Nursing+Practice+%28DNP%29', 'Ecology.', 'EdD',
          'Education.', 'Graduate+Studies', 'Graduate+Studies.',
          'History+%26+Philosophy.', 'Land+Resources+%26+Environmental+Sciences.',
          'Mechanical+%26+Industrial+Engineering.', 'MEd',
          'Microbiology+%26+Cell+Biology.', 'M+Nursing', 'Nursing.',
          'Plant+Sciences+%26+Plant+Pathology.', 'Professional+Paper',
          'Psychology.', 'Animal+%26+Range+Sciences.',
          'Microbiology+%26+Immunology.', 'Civil+Engineering.',
          'Earth+Sciences.', 'Chemical &a; Biological Engineering.',
          'Chemistry &a; Biochemistry.', 'Civil Engineering.',
          'Land Resources &a; Environmental Sciences.',
          'Mechanical &a; Industrial Engineering.', 'Microbiology &a; Cell Biology.', 
          'Plant Sciences &a; Plant Pathology.', 'History &a; Philosophy.',
          'Animal &a; Range Sciences.']
boring += ['MS', 'MFA', 'MA']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

options = uc.ChromeOptions()
#options.binary_location='/usr/bin/chromium'
options.binary_location='/usr/bin/google-chrome'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


baseurl = 'https://scholarworks.montana.edu'
collection = 'eaf2a4ca-5ca2-4c80-ad8d-8cc25c3e6b0b'



recs = []
for page in range(pages):
    tocurl = baseurl + '/collections/' + collection + '?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        time.sleep(10)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        time.sleep(10)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.author',
                                               'dc.date.issued', 'dc.description.abstract', 'dc.subject', 'dc.subject.lcsh',
                                               'dc.title',  'thesis.degree.department', 'thesis.degree.genre', 'thesis.degree.name',
                                               'thesis.format.extentlastpage'],
                            boring=boring, alreadyharvested=alreadyharvested, fakehdl=True):        
        rec['autaff'][-1].append(publisher)
        #bad metadata
        del(rec['supervisor'])
        #print(rec['thesis.metadata.keys'])
        if 'doi' in rec and alreadyharvested and rec['doi'] in alreadyharvested:
            print('  %s already in backup' % (rec['doi']))
        else:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)









