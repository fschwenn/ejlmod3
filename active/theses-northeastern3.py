# -*- coding: utf-8 -*-
#harvest theses from Northeastern U.
#FS: 2020-11-04
#FS: 2023-02-03

import sys
import os
import requests
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

publisher = 'Northeastern U. (main)'
rpp = 20
skipalreadyharvested = True
years = 3

departments = [('Northeastern U.', '228'), ('Northeastern U., Math. Dept.', '200')]
jnlfilename = 'THESES-NEU-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
               
#hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for (aff, depid) in departments:
    tocurl = 'https://repository.library.northeastern.edu/collections/neu:'+depid+'?utf8=%E2%9C%93&sort=date_ssi+desc&per_page=' + str(rpp) + '&utf8=%E2%9C%93&id=neu%3A' + depid + '&rows=' + str(rpp)
    ejlmod3.printprogress("=", [[tocurl]])    
#    req = urllib.request.Request(tocurl, headers=hdr)
    #req = requests.get(tocurl, verify=False)
    driver.get(tocurl)
    tocpage = BeautifulSoup(driver.page_source, features="lxml")
    time.sleep(5)
    for h4 in tocpage.find_all('h4', attrs = {'class' : 'drs-item-title'}):
        for a in h4.find_all('a'):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'depaff' : aff, 'supervisor' : [], 'note' : []}
            rec['artlink'] = 'https://repository.library.northeastern.edu' + a['href']
            rec['tit'] = a.text.strip()
            if depid == '200':
                rec['fc'] = 'm'
            prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))

j = 0
recs = []
for rec in prerecs:
    j += 1
    keepit = True
    ejlmod3.printprogress("-", [[j, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(5)
    except:
        print('wait 10 minutes')
        time.sleep(600)
        try:
            req = urllib.request.Request(rec['artlink'], headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
            time.sleep(30)
        except:
            continue
    for div in artpage.find_all('div', attrs = {'class' : 'drs-item-add-details'}):
        for child in div.children:
            try:
                name = child.name
            except:
                continue
            if name == 'dt':
                dtt = child.text.strip()
            elif name == 'dd':
                #title
                if dtt == 'Title:':
                    rec['tit'] = child.text.strip()
                #author
                elif dtt == 'Creator:':
                    rec['autaff'] = [[ re.sub(' *\(.*', '', child.text.strip()), rec['depaff'] ]]
                #supervisor
                elif dtt == 'Contributor:':
                    for br in child.find_all('br'):
                        br.replace_with('XXX')
                    for contributor in re.split(' *XXX *', child.text.strip()):
                        if re.search('\((Thesis advisor|Advisor)', contributor):
                            rec['supervisor'].append([re.sub(', \d.*', '', re.sub(' *\(.*', '', contributor))])
                #date
                elif dtt == 'Date Awarded:':
                    rec['date'] = re.sub('.*?([12]\d\d\d).*', r'\1', child.text.strip())
                    if int(rec['date']) <= ejlmod3.year(backwards=years):
                        keepit = False
                        print('    to old:', rec['date'])
                #abstract
                elif dtt == 'Abstract/Description:':
                    rec['abs'] = child.text.strip()
                #keywords
                elif dtt == 'Subjects and keywords:':
                    for br in child.find_all('br'):
                        br.replace_with('XXX')
                    rec['keyw'] = re.split(' *XXX *', child.text.strip())
                #HDL
                elif dtt in ['Permanent Link:', 'Permanent URL:']:
                    if re.search('handle.net\/', child.text):
                        rec['hdl'] = re.sub('.*handle.net\/', '', child.text.strip())
                #DOI
                elif dtt == 'DOI:':
                    rec['doi'] = re.sub('.*doi.org\/', '', child.text.strip())
                #rights
                #elif dtt == 'Use and reproduction:':
                #    rec['note'].append(child.text.strip())
    #fulltext
    for section in artpage.body.find_all('section', attrs = {'class' : 'drs-item-derivatives'}):
        for a in section.find_all('a', attrs = {'title' : 'PDF'}):
            rec['hidden'] = 'https://repository.library.northeastern.edu' + a['href']
    if skipalreadyharvested:
        if 'hdl' in rec and rec['hdl'] in alreadyharvested:
            keepit = False
        elif 'doi' in rec and rec['doi'] in alreadyharvested:            
            keepit = False
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
