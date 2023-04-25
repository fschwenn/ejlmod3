#!/usr/bin/python
#program to harvest Ukrainian Journal of Physics
# FS 2019-01-22

import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time

publisher = 'National Academy of Sciences of Ukraine'
tc = 'P'
jnl = 'ujp'
jnlname = 'Ukr.J.Phys.'

tocurl = 'https://ujp.bitp.kiev.ua/index.php/ujp/issue/view/%s' % (sys.argv[1])
try:
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (tocurl))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")

recs = []
#for div in tocpage.body.find_all('div', attrs = {'class' : 'title'}):
for div in tocpage.body.find_all('h3', attrs = {'class' : 'title'}):
    rec = {'jnl' : jnlname, 'tc' : tc, 'autaff' : [], 'keyw' : []}
    for a in div.find_all('a'):
        rec['artlink'] = a['href']
        rec['tit'] = a.text.strip()                    
    recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['artlink']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_author_institution', 'citation_date',
                                        'citation_volume', 'citation_issue', 'citation_firstpage',
                                        'citation_lastpage', 'citation_doi', 'citation_keywords',
                                        'DC.Description'])
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.Type.articleType'}):
        rec['note'] = [meta['content']]                
    if 'Reviews' in rec['note']:
        rec['tc'] = 'R'
    for a in artpage.body.find_all('a', attrs = {'class' : 'obj_galley_link pdf'}):
        if a.text.strip() == 'PDF':
            rec['FFT'] = a['href']
    for div in artpage.body.find_all('div', attrs = {'class' : 'item references'}):
        rec['refs'] = []
        for p in div.find_all('p'):
            for a in p.find_all('a'):
                atext = a.text.strip()
                if re.search('doi.org', atext):
                    a.replace_with(re.sub('.*doi.org\/', ', DOI: ', atext))
            rec['refs'].append([('x', p.text.strip())])
    ejlmod3.printrecsummary(rec)
    
jnlfilename = '%s%s.%s' % (jnl, rec['vol'], rec['issue'])
ejlmod3.writenewXML(recs, publisher, jnlfilename)
