# -*- coding: utf-8 -*-
#program to harvest journals from Global Science Press
# FS 2015-02-11
# FS 2023-02-28

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time

publisher = 'Global Science Press'

jnl = sys.argv[1]
vol = sys.argv[2]
iss = sys.argv[3]
jnlfilename = '%s%s.%s' % (jnl, vol, iss)

if jnl == 'cicp':
    jnlname = 'Commun.Comput.Phys.'
elif (jnl == 'jpde'):
    jnlname = 'J.Part.Diff.Eq.'
else:
    print(' does not know journal "%s"' % (jnl))


#get issue-page
tocurl = False
listurl = 'http://www.global-sci.com/%s/periodical_list.html' % (jnl)
print('get list of issues via "%s"' % (listurl))
listpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(listurl), features='lxml')
for div in listpage.find_all('div', attrs = {'class' : 'periodical-catalog'}):
    for div2 in div.find_all('div'):
        div2t = div2.text.strip()
        if re.search('Vol[a-z]*\.? %s, Iss[a-z]*\.? %s ' % (vol, iss), div2t):
            for a in div2.find_all('a'):
                tocurl = 'http://www.global-sci.com' + a['href']

#get TOC page
print('get table of contents via "%s"' % (tocurl))
if not tocurl:
    print(' could not find TOC for %s' % (jnlfilename))
    sys.exit(0)
else:
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features='lxml')

recs = []
for div in tocpage.body.find_all('div', attrs = {'class' : 'article-list-info'}):
    rec = {'jnl' : jnlname, 'vol' : vol, 'issue' : iss, 'tc' : 'P', 'pacs' : [], 'auts' : [], 'keyw' : []}
    #DOI
    for a in div.find_all('a', attrs = {'class' : 'doi'}):
        rec['doi'] = a.text.strip()
    #title
    for a in div.find_all('a', attrs = {'class' : 'article-list-title'}):
        rec['tit'] = a.text.strip()
        rec['artlink'] = 'http://www.global-sci.com' + a['href']
        recs.append(rec)

#get indiviual article pages
i = 0
repacs = re.compile('.*(\d\d\.\d\d\.[A-Za-z].).*')
regcr = re.compile('[\n\r\t]')
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['doi']], [rec['artlink']]])
    time.sleep(3)
    artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features='lxml')
#ejlmod3.metatagcheck(rec, artpage, [])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #keywords
            if meta['name'] == 'keywords':
                for keyw in re.split(' *, *', meta['content'].strip()):
                    if not keyw in ['Global Science Press', 'JPDE', 'CICP',
                                    'Communications in Computational Physics'
                                    'Journal of Partial Differential Equations']:
                        rec['keyw'].append(keyw)
    for div in artpage.body.find_all('div', attrs = {'class' : 'article-list-info'}):
        #authors and pages
        for div2 in div.find_all('div', attrs = {'class' : 'article-list-content'}):
            ps = div2.find_all('p')
            authors = regcr.sub(' ', ps[0].text.strip())
            pages = ps[1].text.strip()
            for aut in re.split(' *, *', re.sub(' and ', ', ', authors)):
                rec['auts'].append(aut.strip())
            rec['year'] = re.sub('.*\((\d+)\).*', r'\1', pages)
            rec['p1'] = re.sub('.*\).*?(\d+).*', r'\1', pages)
            if re.search('\).*\-', pages):
                rec['p2'] = re.sub('.*\-(\d+).*', r'\1', pages)
        for div2 in div.find_all('div', attrs = {'class' : 'authorization-title'}):
            #date
            for p in div2.find_all('p'):
                pt = regcr.sub(' ', p.text.strip())
                if re.search('Published online:', pt):
                    rec['date'] = re.sub('^\D*', '', pt)
            #PACS (there are some PACS 'hidden' in the AMS classification
            for a in div2.find_all('a'):
                if a.has_attr('href') and re.search('type=ams', a['href']):
                    at = regcr.sub(' ', a.text.strip())
                    if repacs.search(at):
                        rec['pacs'].append(repacs.sub(r'\1', at))
            #abstract
            for ul in div2.find_all('ul', attrs = {'class' : 'authorization-title-nav'}):
                if re.search('Abstract', ul.text):
                    for p in div2.find_all('p', attrs = {'class' : 'authorization-content'}):
                        rec['abs'] = p.text.strip()
                        if not rec['abs']:
                            rec['abs'] = re.sub('^ *Abstract', '', div2.text.strip())
                        rec['abs'] = re.sub('[\n\t\r]+', ' ', rec['abs'])
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
