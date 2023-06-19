# -*- coding: utf-8 -*-
#program to harvest Bulgarian Academy of Science
# FS 2022-04-14
# FS 2023-04-14

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time

jnls = {'cr' : 'Compt.Rend.Acad.Bulg.Sci.',
        'aj' : 'Bulg.Astron.J.'}

regexpref = re.compile('[\n\r\t]')

jnl = sys.argv[1]

publisher = 'Bulgarian Academy of Sciences'


if jnl == 'cr':
    issueid = sys.argv[2]
    urltrunc = 'http://www.proceedings.bas.bg/index.php/cr/issue/view/%s' % (issueid)
elif jnl == 'aj':
    volume = sys.argv[2]
    urltrunc = 'https://astro.bas.bg/AIJ/issues/n' + volume
    
print(urltrunc)
try:
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(urltrunc), features="lxml")
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (urltrunc))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(urltrunc), features="lxml")

recs = []
for div in tocpage.body.find_all('div', attrs = {'class' : 'section'}):
    for h2 in div.find_all('h2'):
        note = regexpref.sub('', h2.text).strip()
        print(' - %s - ' % (note))
    for h3 in div.find_all('h3'):
        rec = {'jnl' : jnls[jnl], 'tc' : 'P', 'note' : [note], 'keyw' : [], 'autaff' : []}
        if note in ['Mathematics']:
            rec['fc'] = 'm'
        elif note in ['Chemistry', 'Biology', 'Medicine', 'Geophysics', 'Agricultural Sciences'
                      'Engineering Sciences', 'Geology']:
            rec['fc'] = 'o'
        elif note in ['Space Sciences']:
            rec['fc'] = 'a'
        for a in h3.find_all('a'):
            rec['artlink'] = a['href']
            recs.append(rec)

i = 0
for rec in recs:
    i += 1
    autaff = False
    time.sleep(3)
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']))
    ejlmod3.metatagcheck(rec, artpage, ['citation_date', 'citation_title', 'citation_firstpage',
                                        'citation_keywords', 'citation_doi', 'citation_author',
                                        'citation_author_institution', 'citation_issue',
                                        'citation_volume', 'DC.Description', 'citation_pdf_url',
                                        'citation_reference'])
    ejlmod3.printrecsummary(rec)

if not recs:
    for h1 in tocpage.body.find_all('h1'):
        if re.search('\([12]\d\d\d\)', h1.text):
            year = re.sub('.*\(([12]\d\d\d)\).*', r'\1', h1.text.strip())
    for div in tocpage.body.find_all('div', attrs = {'class' : 'media'}):
        rec = {'jnl' : jnls[jnl], 'tc' : 'P', 'vol' : volume, 'year' : year}
        for a in div.find_all('a'):
            rec['FFT'] = '%s/%s' % (urltrunc, a['href'])
            at = a.text.strip()
            if at:
                rec['tit'] = at
            a.decompose()
        rec['auts'] = re.split(' *, *', re.sub(' and ', ', ', regexpref.sub('', div.text.strip())))
        rec['doi'] = '30.3000/bas.bg/%s/%s/%s' % (jnl, volume, re.sub('\W', '', rec['tit']))
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    
if jnl == 'cr':
    jnlfilename = 'crabs%s.%s_%s' % (rec['vol'], rec['issue'], issueid)
elif jnl == 'aj':
    jnlfilename = 'bulgaj%s_%s' % (volume, ejlmod3.stampoftoday())
ejlmod3.writenewXML(recs, publisher, jnlfilename)
