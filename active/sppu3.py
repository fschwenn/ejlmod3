# -*- coding: utf-8 -*-
#program to harvest journals from St.Petersburg Polytech.Univ.
# FS 2022-07-11
import re
import os
import sys
from bs4 import BeautifulSoup
from time import sleep
import urllib.request, urllib.error, urllib.parse
import urllib.parse
import ejlmod3

publisher = 'St. Petersburg State Polytechnical University'

jnl = sys.argv[1]
jnlfilename = 'sppu_%s_%s.' % (jnl, ejlmod3.stampoftoday())

#check issues already harvested
ejlpath = '/afs/desy.de/user/l/library/dok/ejl/backup'
reiss = re.compile('.*sppu_%s_.*?\.(\d+)\..*' % (jnl))
highestissunumber = 0
for path in [ejlpath, os.path.join(ejlpath, str(ejlmod3.year(backwards=1)))]:
    for datei in os.listdir(path):
        if reiss.search(datei):
            issuenumber = int(reiss.sub(r'\1', datei))
            if issuenumber > highestissunumber:
                highestissunumber = issuenumber
print('highest issuenumber so far: %i' % (highestissunumber))
highestissunumber = 65
hdr = {'User-Agent' : 'Magic Browser'}
reiss = re.compile('.*issue\/(\d+)\/$')
todo = []
if jnl == 'jpm':
    jnlname = 'St.Petersburg Polytech.Univ.J.Phys.Math.'
    tocurl = 'https://physmath.spbstu.ru/en/archive/'

print(tocurl)
req = urllib.request.Request(tocurl, headers=hdr)
tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
for a in tocpage.find_all('a'):
    if a.has_attr('href') and reiss.search(a['href']):
        issuenumber = int(reiss.sub(r'\1', a['href']))
        print('    %2i'  % (issuenumber))
        if issuenumber > highestissunumber:
            if not (issuenumber, a['href']) in todo:
                todo.append((issuenumber, a['href']))

todo.sort()
                
i = 0
for (issuenumber, issuelink) in todo:
    recs = []
    i += 1
    ejlmod3.printprogress('=', [[i, len(todo)], [issuelink]])
    sleep(3)
    req = urllib.request.Request(issuelink, headers=hdr)
    issuepage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for h2 in issuepage.find_all('h2', attrs = {'class' : 'article-item-heading'}):
        for a in h2.find_all('a'):
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
        ejlmod3.metatagcheck(rec, artpage, ["keywords", "citation_doi", "citation_date",
                                            "citation_title", "citation_issue",
                                            "citation_abstract_content", "citation_firstpage",
                                            "citation_lastpage"])
        #"citation_volume" in fact is issuenumber not real volume!
        for div in artpage.find_all('div', attrs = {'class' : 'j-info'}):
            for span in div.find_all('span'):
                print(span)
                spant = span.text.strip()
                if re.search('Volume', spant):
                    rec['vol'] = re.sub('Volume:? *', '', spant)
        if 'doi' in rec:
            rec['doi'] = re.sub(' ', '', rec['doi'])
        #authors
        for meta in artpage.find_all('meta', attrs = {'name' : 'citation_authors'}):            
            rec['auts'] = []
            for author in re.split(';', meta['content']):
                rec['auts'].append(re.sub('(.*?) (.*)', r'\1, \2', author))
        #pdf
        for a in artpage.find_all('a', attrs = {'class' : 'download'}):
            rec['pdf_url'] = a['href']        
        #license
        ejlmod3.globallicensesearch(rec, artpage)
        ejlmod3.printrecsummary(rec)
        
    ejlmod3.writenewXML(recs, publisher, jnlfilename+str(issuenumber))
