# -*- coding: utf-8 -*-
#harvest Stanford U.
#FS: 2020-02-20


import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Stanford U.'
hdr = {'User-Agent' : 'Magic Browser'}

pages = 1
recordsperpage = 50

recs = []
jnlfilename = 'THESES-STANFORD-%s' % (ejlmod3.stampoftoday())
for page in range(pages):
    tocurl = 'https://searchworks.stanford.edu/?f[genre_ssim][]=Thesis%2FDissertation&f[stanford_dept_sim][]=Department+of+Physics&page=' + str(page) + '&per_page=' + str(recordsperpage)
    print(tocurl)
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(2)
    for div in tocpage.find_all('div', attrs = {'class' : 'document'}):
        for h3 in div.find_all('h3'):
            for a in h3.find_all('a'):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'artlink' : 'https://searchworks.stanford.edu' + a['href'], 'note' : []}
                rec['tit'] = re.sub(' \[electronic resource\]', '', a.text.strip()                )
                rec['doi'] = '20.2000/Stanford/' + re.sub('\D', '', a['href'])
            for span in h3.find_all('span', attrs = {'class' : 'main-title-date'}):
                rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', span.text.strip())
                rec['date'] = rec['year']
            for a in div.find_all('a'):
                if a.has_attr('href') and re.search('purl.stanford', a['href']):
                    rec['link'] = a['href']
            recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['artlink']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(5)
    except:
        try:
            print('retry %s in 180 seconds' % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print('no access to %s' % (rec['artlink']))
            continue
    #author and supervisor
    for div in artpage.body.find_all('div', attrs = {'id' : 'contributors'}):
        for dd in div.find_all('dd'):
            for a in dd.find_all('a'):
                person = re.sub(' *,$', '', a.text.strip())
                person = re.sub(', [12]\d.*', '', person) 
                person = re.sub(' \(.*', '', person) 
                #a.replace_with('')
            if re.search('author', dd.text):
                rec['autaff'] = [[ person ]]
            elif re.search('upervisor', dd.text):
                rec['supervisor'] = [[ person ]]
    #author2
    if not 'autaff' in list(rec.keys()):
        for div in artpage.body.find_all('div', attrs = {'id' : 'contributors'}):
            for dl in div.find_all('dl'):
                for child in dl.children:
                    try:
                        child.name
                    except:
                        continue
                    if child.name == 'dt':
                        dtt = child.text
                    elif child.name == 'dd':
                        ddt = re.sub('([a-z][a-z])\.', r'\1', child.text.strip())
                        ddt = re.sub('[\n\t\r]', '', ddt)
                        if ddt:
                            if re.search('[aA]uthor', dtt):
                                rec['autaff'] = [[ ddt ]]
                            elif re.search('[sS]upervisor', dtt) or re.search('rimary [Aa]dvisor', dtt):
                                rec['supervisor'] = [[ ddt ]]
    #print(rec['autaff'])
    #abstract
    for div in artpage.body.find_all('div', attrs = {'id' : 'contents-summary'}):
        for dd in div.find_all('dd'):
            rec['abs'] = dd.text.strip()
    #purl
    if 'link' in rec:
        print('     check license on %s' % (rec['link']))
        try:
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
            #license
            for div in artpage.body.find_all('div', attrs = {'id' : 'access-conditions'}):
                for a in div.find_all('a'):
                    if a.has_attr('href') and re.search('creativecommons.org', a['href']):
                        rec['license'] = {'url' : a['href']}
        except:
            print('     not found')
    else:
        rec['link'] = rec['artlink']
    
    rec['autaff'][-1].append(publisher)
    ejlmod3.printrecsummary(rec)
                
ejlmod3.writenewXML(recs, publisher, jnlfilename)

