# -*- coding: utf-8 -*-
#program to harvest journals from DergiPark
# FS 2022-07-12
import re
import os
import sys
from bs4 import BeautifulSoup
from time import sleep
import urllib.request, urllib.error, urllib.parse
import urllib.parse
import ejlmod3
import undetected_chromedriver as uc

publisher = 'DergiPark'

jnl = sys.argv[1]
jnlfilename = 'dergipark_%s_%s.' % (jnl, ejlmod3.stampoftoday())


#check issues already harvested
ejlpath = '/afs/desy.de/user/l/library/dok/ejl/backup'
reiss = re.compile('.*dergipark_%s_.*?\.(\d+)\..*' % (jnl))
highestissunumber = 0
for path in [ejlpath, os.path.join(ejlpath, str(ejlmod3.year(backwards=1)))]:
    for datei in os.listdir(path):
        if reiss.search(datei):
            issuenumber = int(reiss.sub(r'\1', datei))
            if issuenumber > highestissunumber:
                highestissunumber = issuenumber
print('highest issuenumber so far: %i' % (highestissunumber))

hdr = {'User-Agent' : 'Magic Browser'}
reiss = re.compile('.*issue\/(\d+)$')
todo = []
if jnl == 'jum':
    jnlname = 'J.Universal Math.'
    tocurl = 'https://dergipark.org.tr/en/pub/jum/archive'

print(tocurl)
req = urllib.request.Request(tocurl, headers=hdr)
tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
for a in tocpage.find_all('a'):
    if a.has_attr('href') and reiss.search(a['href']):
        issuenumber = int(reiss.sub(r'\1', a['href']))
        print('    %2i'  % (issuenumber))
        if issuenumber > highestissunumber:
            if not (issuenumber, 'https:' + a['href']) in todo:
                todo.append((issuenumber, 'https:' + a['href']))

todo.sort()
                
i = 0
for (issuenumber, issuelink) in todo:
    recs = []
    i += 1
    ejlmod3.printprogress('=', [[i, len(todo)], [issuelink]])
    sleep(3)
    req = urllib.request.Request(issuelink, headers=hdr)
    issuepage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for a in issuepage.find_all('a', attrs = {'class' : 'article-title'}):
        rec = {'tc' : 'P', 'jnl' : jnlname}
        rec['artlink'] = a['href']
        recs.append(rec)
    j = 0
    for rec in recs:
        j += 1
        ejlmod3.printprogress('-', [[i, len(todo)], [j, len(recs)], [rec['artlink']]])
        sleep(6)
        req = urllib.request.Request(rec['artlink'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_publication_date', 'citation_volume',
                                            'citation_issue', 'citation_firstpage', 'citation_lastpage',
                                            'citation_abstract', 'citation_keywords',
                                            'DC.Creator.PersonalName', 'citation_doi'])
        #PDF
        for meta in artpage.find_all('meta', attrs = {'name' : 'citation_pdf_url'}):
            rec['FFT'] = meta['content']
        #authors
        for tr in artpage.find_all('tr'):
            for th in tr.find_all('th'):
                autaff = []
                if re.search('Authors', th.text):
                    for p in tr.find_all('p'):
                        for a in p.find_all('a'):
                            if a.has_attr('href'):
                                if re.search('\/pub', a['href']):
                                    autaff.append([a.text.strip()])
                                elif re.search('orcid', a['href']) and autaff:
                                    autaff[-1].append('ORCID:' + a.text.strip())
                if autaff:
                    rec['autaff'] = autaff
        #references
        for div in artpage.find_all('div', attrs = {'class' : 'article-citations'}):
            rec['refs'] = []
            for li in div.find_all('li'):
                lit = li.text.strip()
                for ref in re.split('\[\d+\]', lit):
                    rec['refs'].append([('x', ref)])
        ejlmod3.printrecsummary(rec)
                        
            
    ejlmod3.writenewXML(recs, publisher, jnlfilename+str(issuenumber))
