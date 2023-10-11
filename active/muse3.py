# -*- coding: UTF-8 -*-
#program to harvest journals from MUSE
# FS 2023-09-26

import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup

publisher = 'Johns Hopkins University Press'

jnr = sys.argv[1]
years = 2

#harvest an issue
def harvestissue(inr):
    tocurl = 'https://muse.jhu.edu/issue/' + inr
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    recs = []
    for div in tocpage.find_all('div', attrs = {'class' : 'card'}):
        
        for li in div.find_all('li', attrs = {'class' : 'title'}):
            if re.search('Index to [vV]olume', li.text.strip()):
                print('skip "%s"' % (li.text.strip()))
            else:
                for a in div.find_all('a'):
                    if a.has_attr('href') and re.search('View Summary', a.text):
                        rec = {'tc' : 'P', 'artlink' : 'https://muse.jhu.edu' + a['href']}
                        recs.append(rec)
    for (i, rec) in enumerate(recs):
        time.sleep(2)
        ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['artlink']]])
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_author', 'citation_volume',
                                            'citation_issue', 'citation_firstpage', 'citation_lastpage',
                                            'citation_online_date', 'citation_year', 'citation_doi',
                                            'citation_reference'])
        #abstract
        for div in artpage.find_all('div', attrs = {'class' : 'abstract'}):
            for span in div.find_all('span', attrs = {'class' : 'abstractheader'}):
                span.decompose()
            rec['abs'] = div.text.strip()
        #journalname
        for meta in artpage.find_all('meta', attrs = {'name' : 'citation_journal_abbrev'}):
            cja = meta['content']
            if cja == 'ajm':
                rec['jnl'] = 'Am.J.Math.'
            else:
                print('unknown journal "%s"' % (cja))
                sys.exit(0)
        #fulltext
        for img in artpage.find_all('img', attrs = {'class' : 'left_access'}):
            if img.has_attr('alt') and img['alt'] != 'restricted access':
                ejlmod3.metatagcheck(rec, artpage, ['citation_pdf_url'])
    if 'issue' in rec:
        jnlfilename = 'muse%s%s.%s_inr%s' % (cja, rec['vol'], rec['issue'], inr)
    else:
        jnlfilename = 'muse%s%s_inr%s' % (cja, rec['vol'], inr)
    ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
    return

def getissuenumbers(jnl):    
    issues = []
    tocurl = 'https://muse.jhu.edu/journal/' + jnl
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    for li in tocpage.find_all('li', attrs = {'class' : 'volume'}):
        year = 9999
        if re.search('[12]\d\d\d', li.text):
            year = int(re.sub('.*([12]\d\d\d).*', r'\1', li.text.strip()))
        if year > ejlmod3.year(backwards=years):
            for a in li.find_all('a'):
                issues.append(re.sub('\D', '', a['href']))
    issues.sort()
    print('available', issues)
    return issues

def getdone():
    reg = re.compile('.*mus.*_inr(\d+).*doki')    
    ejldir = '/afs/desy.de/user/l/library/dok/ejl'
    issues = []
    for directory in [ejldir+'/backup', ejldir+'/backup/' + str(ejlmod3.year(backwards=1))]:
        for datei in os.listdir(directory):
            if reg.search(datei):
                issues.append(reg.sub(r'\1', datei))
    issues.sort()
    print('done', issues)
    return issues
            
available = getissuenumbers(jnr)
done = getdone()
todo = []
for inr in available:
    if not inr in done:
        todo.append(inr)

for (i, inr) in enumerate(todo):
    ejlmod3.printprogress('==', [[i+1, len(todo)], [inr]])
    harvestissue(inr)
