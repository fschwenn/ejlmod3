# -*- coding: utf-8 -*-
#harvest theses from Giessen
#FS: 2021-02-09
#FS: 2023-04-24


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

rpp = 100
skipalreadyharvested = True
pages = 5
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

prerecs = []
for page in range(pages):
    tocurl = 'https://jlupub.ub.uni-giessen.de/browse?rpp=' + str(rpp) + '&offset=' + str(rpp*page) + '&etal=-1&sort_by=2&type=type&value=doctoralThesis&order=DESC'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    skip = False
    try:
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    except:
        try:
            time.sleep(1)
            driver.get(tocurl)
            tocpage = BeautifulSoup(driver.page_source, features="lxml")
        except:
            try:
                time.sleep(100)
                driver.get(tocurl)
                tocpage = BeautifulSoup(driver.page_source, features="lxml")
            except:
                skip = True
    if not skip:
        for rec in ejlmod3.getdspacerecs(tocpage, 'https://jlupub.ub.uni-giessen.de', fakehdl=True):
            doi = re.sub('.*pub\/', '10.22029/jlupub-', rec['link'])
            if skipalreadyharvested and doi in alreadyharvested:
                print('  %s already in backup' % (doi))
            elif ejlmod3.checkinterestingDOI(doi):
                prerecs.append(rec)
            else:
                print('  %s uninteresting' % (doi))            
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(20)

i = 0
recs = []
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        time.sleep(10)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(1.80)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'))
        except:
            print("no access to %s" % (rec['link']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.language', 'DC.rights', 
                                        'DC.identifier', 'DCTERMS.abstract', 
                                        'DC.title', 'citation_pdf_url'
                                        'citation_date'])
    rec['autaff'][-1].append(publisher)
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.subject'}):
        if meta.has_attr('scheme') and meta['scheme'] == "DCTERMS.DDC":
            rec['ddc'] = meta['content']
            if rec['ddc'] == 'ddc:510':
                rec['fc'] = 'm'
            elif rec['ddc'] == 'ddc:520':
                rec['fc'] = 'a'
            elif len(rec['ddc']) >= 7 and rec['ddc'][4] in ['1', '2', '3', '4', '6', '7', '8', '9']:
                keepit = False
            elif len(rec['ddc']) >= 7 and rec['ddc'][4:5] in ['55', '54', '56', '57', '58', '59', '09']:
                keepit = False
            else:
                rec['note'].append(meta['content'])
        else:
            rec['keyw'].append(meta['content'])
    for tr in artpage.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            tht = td.text.strip()
            for td2 in tr.find_all('td', attrs = {'class' : 'word-break'}):
                if tht == 'local.affiliation':
                    inst = td2.text.strip()
                    if inst in boring:
                        keepit = False
                    elif not inst in ['FB 07 - Mathematik und Informatik, Physik, Geographie']:
                        rec['note'].append(inst)
    if skipalreadyharvested and 'urn' in rec and rec['urn'] in alreadyharvested:
        print('  %s already in backup' % (rec['urn']))
    elif skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        print('  %s already in backup' % (rec['doi']))
    elif keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])


ejlmod3.writenewXML(recs, publisher, jnlfilename)
