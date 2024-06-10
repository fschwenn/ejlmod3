# -*- coding: utf-8 -*-
#harvest theses from Imperial Coll., London
#FS: 2019-09-26
#FS: 2023-02-13

import getopt
import sys
import os
#import urllib.request, urllib.error, urllib.parse
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

startyear = str(ejlmod3.year(backwards=1+1))
pages = 1
rpp = 20+40
skipalreadyharvested = True

publisher = 'Imperial Coll., London'
jnlfilename = 'THESES-IMPERIAL-%s' % (ejlmod3.stampoftoday())
hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename, years=5)

options = uc.ChromeOptions()
#options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
#options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


driver.get('https://spiral.imperial.ac.uk')
time.sleep(30)
recs = []
deps = [('1240', ''), ('1241', 'm'), ('6103', 'm'), ('1232', 'c')]
i = 0
hdls = []
for (dep, fc) in deps:
    for page in range(pages):
        i += 1
        tocurl = 'https://spiral.imperial.ac.uk/handle/10044/1/' + dep + '/simple-search?location=10044%2F1%2F' + dep +'&query=&filter_field_1=dateIssued&filter_type_1=equals&filter_value_1=%5B' + startyear + '+TO+2040%5D&rpp=' + str(rpp) + '&sort_by=dc.date.issued_dt&order=DESC&etal=5&submit_search=Update&start=' + str(rpp*page)
        ejlmod3.printprogress("=", [[i, len(deps)*pages], [dep], [page+1, pages], [tocurl]])
        #req = urllib.request.Request(tocurl, headers=hdr)
        #tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        for tr in tocpage.body.find_all('tr'):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'supervisor' : []}
            for a in tr.find_all('a'):
                rec['artlink'] = 'https://spiral.imperial.ac.uk' + a['href'] #+ '?show=full'
                rec['hdl'] = re.sub('.*handle\/', '', a['href'])
                if skipalreadyharvested and rec['hdl'] in alreadyharvested:
                    print('   %s already in backup' % (rec['hdl']))
                elif not rec['hdl'] in hdls:
                    if fc:
                        rec['fc'] = fc
                    recs.append(rec)
                    hdls.append(rec['hdl'])
        print('  %4i records so far' % (len(recs)))
        time.sleep(5)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    try:
        #artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            #artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
            driver.get(rec['artlink'])
            artpage = BeautifulSoup(driver.page_source, features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.title', 'DC.identifier',  'DCTERMS.issued',
                                        'DC.subject', 'DCTERMS.abstract', 'citation_pdf_url'])
    ejlmod3.globallicensesearch(rec, artpage)
    #supervisor
    for tr in artpage.body.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldLabel'}):
            if re.search('Supervisor:', td.text):
                for br in tr.find_all('br'):
                    br.replace_with('BRBRBR')
                for td2 in tr.find_all('td', attrs = {'class' : 'metadataFieldValue'}):
                    for supervisor in re.split(' *BRBRBR *', td2.text.strip()):
                        rec['supervisor'].append([ supervisor,  'Imperial Coll., London'])
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
