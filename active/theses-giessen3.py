# -*- coding: utf-8 -*-
#harvest theses from Giessen
#FS: 2021-02-09
#FS: 2023-04-24
#FS: 2024-05-11


import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

publisher = 'U. Giessen (main)'
jnlfilename = 'THESES-GIESSEN-%s' % (ejlmod3.stampoftoday())

rpp = 60
skipalreadyharvested = True
pages = 7
boring = ['FB 08 - Biologie und Chemie', 'FB 03 - Sozial- und Kulturwissenschaften',
          'FB 09 - Agrarwissenschaften, Ökotrophologie und Umweltmanagement',
          'FB 10 - Veterinärmedizin', 'FB 11 - Medizin', 'FB 02 - Wirtschaftswissenschaften',
          'FB 01 - Rechtswissenschaft', 'FB 04 - Geschichts- und Kulturwissenschaften'
          'FB 06 - Psychologie und Sportwissenschaft']

hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

host = os.uname()[1]
if host == 'l00schwenn':
    options = uc.ChromeOptions()
    options.binary_location='/usr/bin/chromium'
    chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    driver = uc.Chrome(version_main=chromeversion, options=options)
else:
    options = uc.ChromeOptions()
    options.binary_location='/usr/bin/google-chrome'
    options.add_argument('--headless')
    chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    driver = uc.Chrome(version_main=chromeversion, options=options)



baseurl = 'https://jlupub.ub.uni-giessen.de'
collection = '57d6734c-6672-4d24-838e-550310ea2b94'






recs = []
for page in range(pages):
    tocurl = baseurl + '/collections/' + collection + '?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
    tocurl = baseurl + '/search?query=&spc.page=' + str(page+1) + '&spc.sf=dc.date.issued&spc.sd=DESC&spc.rpp=' + str(rpp)
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
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.author', 'local.affiliation',
                                               'dc.date.issued', 'dc.description.abstract',
                                               'dc.language.iso', 'dc.rights',
                                               'dc.rights.uri', 'dc.subject.ddc',
                                               'dc.contributor.advisor', 'dc.title'],
                            boring=boring, alreadyharvested=alreadyharvested, fakehdl=True):
        if 'autaff' in rec and rec['autaff']:
            rec['autaff'][-1].append(publisher)
        else:
            rec['autaff'] = [[ 'Dee, John' ]] 
        ejlmod3.printrecsummary(rec)
        #print(rec['thesis.metadata.keys'])
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)





