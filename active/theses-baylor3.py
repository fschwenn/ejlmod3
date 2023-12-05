# -*- coding: utf-8 -*-
#harvest theses from Baylor U.
#FS: 2019-09-25
#FS: 2023-01-09
#FS: 2023-11-28

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

publisher = 'Baylor U.'

rpp = 60
pages = 3
skipalreadyharvested = True

jnlfilename = 'THESES-BAYLOR-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []


boring = ['Baylor University. Dept. of Biology.', 'Baylor University. Dept. of Chemistry &a; Biochemistry.',
          'Baylor University. Dept. of Curriculum &a; Instruction.', 'Baylor University. Dept. of Educational Leadership.',
          'Baylor University. Dept. of Educational Psychology.', 'Baylor University. Dept. of Electrical &a; Computer Engineering.',
          'Baylor University. Dept. of English.', 'Baylor University. Dept. of Environmental Science.',
          'Baylor University. Dept. of Geosciences.', 'Baylor University. Dept. of Health, Human Performance &a; Recreation.',
          'Baylor University. Dept. of History.', 'Baylor University. Dept. of Mechanical Engineering.',
          'Baylor University. Dept. of Philosophy.', 'Baylor University. Dept. of Political Science.',
          'Baylor University. Dept. of Psychology &a; Neuroscience.', 'Baylor University. Dept. of Religion.',
          'Baylor University. Dept. of Sociology.', 'Baylor University. Institute for Ecological, Earth &a; Environmental Sciences.',
          'Baylor University. Institute of Biomedical Studies.', 'Baylor University. School of Business.',
          'Baylor University. School of Music.', 'Baylor University. School of Social Work.',
          'Baylor University. Dept. of Information Systems.']


options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


recs = []
for page in range(pages):
    tocurl = 'https://baylor-ir.tdl.org/collections/06d889b5-9220-4479-a150-c2ab24cd63b3?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)

    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    
    try:
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    baseurl = 'https://baylor-ir.tdl.org'
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.creator', 'dc.date.issued', 'thesis.degree.department', 'dc.rights.accessrights'], boring=boring, alreadyharvested=alreadyharvested):
        rec['autaff'][-1].append(publisher)
        for note in rec['note']:
            if note in ['THESIS.DEGREE.DEPARTMENT=Baylor University. Dept. of Mathematics.']:
                rec['fc'] = 'm'
            elif note in ['Baylor University. Dept. of Statistical Science.']:
                rec['fc'] = 's'
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
