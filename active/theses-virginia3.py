# -*- coding: utf-8 -*-
#harvest theses from Virginia U.
#FS: 2021-11-15
#FS: 2023-04-28

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc
from selenium.webdriver.remote.webdriver import By
from selenium.webdriver.support.ui import WebDriverWait
#import requests


publisher = 'Virginia U.'
jnlfilename = 'THESES-VIRGINIA-%s' % (ejlmod3.stampoftoday())

deps = [('Physics+-+Graduate+School+of+Arts+and+Sciences', ''),
        ('Department+of+Physics', ''),
        ('Mathematics+-+Graduate+School+of+Arts+and+Sciences', 'm'),
        ('Computer+Science+-+School+of+Engineering+and+Applied+Science', 'c'),
        ('Computer+Engineering+-+School+of+Engineering+and+Applied+Science', 'c'),
        ('Astronomy', 'a'),
        ('Department+of+Astronomy', '')]
startday = '%4d-01-01' % (ejlmod3.year()-2)
endday = '%4d-12-31' % (ejlmod3.year())
rpp = 20
skipalreadyharvested = True
boringdegrees = ['BA (Bachelor of Arts)', 'MA (Master of Arts)',
                 'MS (Master of Science)', 'BS (Bachelor of Science)']

#driver
# Initilize Webdriver
options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
#options.binary_location='/opt/google/chrome/google-chrome'

options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
driver.implicitly_wait(30)
#driver.set_window_position(0, 0)
#driver.set_window_size(1920, 10800)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for (dep, fc) in deps:
    numofreloads = 0
    tocurl = 'https://search.lib.virginia.edu/?mode=advanced&q=date:+{' + startday + '+TO+' + endday + '}&pool=uva_library&sort=SortDatePublished_desc&filter={%22FilterResourceType%22:[%22Theses%22],%22FilterCollection%22:[%22Libra+Repository%22],%22FilterDepartment%22:[%22' + dep + '%22]}'
    ejlmod3.printprogress("=", [[dep], [tocurl]])
    try:
        driver.get(tocurl)
        time.sleep(10)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(180)
        driver.get(tocurl)
        time.sleep(10)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    for span in tocpage.find_all('span', attrs = {'class' : 'total'}):
        numoftheses = int(re.sub('\D', '', span.text.strip()))
        numofreloads = (numoftheses-1) // rpp
        print('   %i theses waiting' % (numoftheses))
    for i in range(numofreloads):
        time.sleep(6)
        print('       click for more result %i/%i' % (i+1, numofreloads))
        if len(driver.find_elements(By.CLASS_NAME, 'primary-button')) == 4:
            print('         click!')
            driver.find_elements(By.CLASS_NAME, 'primary-button')[-1].click()
    tocpage = BeautifulSoup(driver.page_source, features="lxml")
    time.sleep(6)
    for div in tocpage.find_all('div', attrs = {'class' : 'access-urls'}):
        for a in div.find_all('a'):
            rec = {'jnl' : 'BOOK', 'tc' : 'T', 'note' : []}
            if fc:
                rec['fc'] = fc
            rec['artlink'] = a['href']
            rec['doi'] = re.sub('.*org\/', '', a['href'])
            if ejlmod3.checkinterestingDOI(rec['doi']):
                if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                    prerecs.append(rec)
    print('  -{ %4i theses so far }-' % (len(prerecs)))
    time.sleep(10)

i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        print('   wait 5 minutes')
        time.sleep(300)
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    time.sleep(10)
    for div in artpage.find_all('div', attrs = {'id' : 'document'}):
        #title
        for h1 in div.find_all('h1'):
            rec['tit'] = h1.text.strip()
            h1.decompose()
        for d2 in div.find_all('div', attrs = {'class' : 'document-row'}):
            orcid = False
            for a in d2.find_all('a'):
                if a.has_attr('href') and re.search('orcid.org', a['href']):
                    orcid = re.sub('.*org\/', 'ORCID:', a['href'])
                a.decompose()
            for span in d2.find_all('span', attrs = {'class' : 'document-label'}):
                label = span.text.strip()
            for span in d2.find_all('span', attrs = {'class' : 'document-value'}):
                #author and affiliation
                if label == 'Author:':
                    parts = re.split(', ', span.text.strip())
                    if orcid:
                        rec['autaff'] = [[ '%s, %s' % (parts[0], parts[1]), orcid, ', '.join(parts[2:]) ]]
                    else:
                        rec['autaff'] = [[ '%s, %s' % (parts[0], parts[1]), ', '.join(parts[2:]) ]]
                #Supervisor
                elif label == 'Advisor:':
                    parts = re.split(', ', span.text.strip())
                    if len(parts) > 2:
                        rec['supervisor'] = [[ '%s, %s' % (parts[0], parts[1]), ', '.join(parts[2:]) ]]
                    else:
                        rec['supervisor'] = [[ span.text.strip() ]]
                elif label == 'Advisors:':
                    rec['supervisor'] = []
                    for br in span.find_all('br'):
                        br.replace_with('XXX')
                    for sv in re.split('XXX', span.text.strip()):
                        if sv:
                            parts = re.split(', ', sv.strip())
                            if len(parts) > 2:
                                rec['supervisor'].append([ '%s, %s' % (parts[0], parts[1]), ', '.join(parts[2:]) ])
                            else:
                                rec['supervisor'].append([ sv ])
                #abstract
                elif label == 'Abstract:':
                    rec['abs'] = span.text.strip()
                #degree
                elif label == 'Degree:':
                    degree = span.text.strip()
                    if not degree  == 'PHD (Doctor of Philosophy)':
                        if degree in boringdegrees:
                            print('   skip %s' % (degree))
                            keepit = False
                        else:
                            rec['note'].append(degree)
                #keywords
                elif label == 'Keywords:':
                    rec['keyw'] = re.split(', ', span.text.strip())
                #rights
                elif label == 'Rights:':
                    for a in span.find_all('a'):
                        if a.has_attr('href') and re.search('creativecommons', a['href']):
                            rec['license'] = {'url' : a['href']}
                    rec['note'].append(span.text.strip())
                #date
                elif label == 'Issued Date:':
                    rec['date'] = span.text.strip()
    #fulltext
    for div in artpage.find_all('div', attrs = {'id' : 'uploads'}):
        for a in div.find_all('a'):
            if a.has_attr('href') and re.search('pdf$', a['href']):
                if 'license' in list(rec.keys()):
                    rec['FFT'] = 'https://libraetd.lib.virginia.edu' + a['href']
                else:
                    rec['hidden'] = 'https://libraetd.lib.virginia.edu' + a['href']
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['doi'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
