# -*- coding: utf-8 -*-
#harvest theses from Stellenbosch U.
#FS: 2022-11-08
#FS: 2023-12-02

from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc
import os

jnlfilename = 'THESES-STELLENBOSCH-%s' % (ejlmod3.stampoftoday())

publisher = 'U. Stellenbosch'

skipalreadyharvested = True
rpp = 10
pages = 1
boring = []


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

recs = []
for (fc, dep) in [('m', '6fa3027a-cbc2-420a-89b2-d14704b58f0e'),
                  ('m', 'a0564044-0e05-451d-94ed-5fc5fd3160f4'),
                  ('c', '6162c8d4-f5ce-45f1-ba42-225b8d7f9fb4'),
                  ('', '628e526d-ce10-4841-a09b-48b265bd6412')]:
    for page in range(pages):
        tocurl = 'https://scholar.sun.ac.za/collections/' + dep + '?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
        ejlmod3.printprogress('=', [[fc,dep], [page+1, pages], [tocurl]])
        try:
            driver.get(tocurl)
            time.sleep(5)
            tocpage = BeautifulSoup(driver.page_source, features="lxml")
        except:
            time.sleep(60)
            driver.get(tocurl)
            time.sleep(5)
            tocpage = BeautifulSoup(driver.page_source, features="lxml")
        baseurl = 'https://scholar.sun.ac.za/'
        
        for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.contributor.author', 'dc.date.issued', 'dc.description.abstract', 'dc.format.extent', 'dc.identifier.uri', 'dc.language.iso', 'dc.rights', 'dc.subject', 'dc.title'], boring=boring, alreadyharvested=alreadyharvested):
            rec['autaff'][-1].append(publisher)
            if fc:
                rec['fc'] = fc
            ejlmod3.printrecsummary(rec)
            #print(rec['thesis.metadata.keys'])
            recs.append(rec)
        print('  %i records so far' % (len(recs)))
        time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
