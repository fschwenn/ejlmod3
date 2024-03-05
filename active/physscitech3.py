# -*- coding: utf-8 -*-
#program to harvest Phys.Sci.Tech.
# FS 2023-08-25

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time

regexpref = re.compile('[\n\r\t]')

publisher = 'Al Farabi Kazakh Natl. U.'

issueid = sys.argv[1]
urltrunc = 'https://phst.kaznu.kz/index.php/journal/issue/view/%s' % (issueid)
    
print(urltrunc)
try:
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(urltrunc), features="lxml")
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (urltrunc))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(urltrunc), features="lxml")

#print(tocpage.text)


problematiclinks = []
recs = []
links = []
for div in tocpage.body.find_all('div', attrs = {'class' : 'section'}):
    for h2 in div.find_all('h2'):
        section = h2.text.strip()
#        for div2 in div.find_all('div', attrs = {'class' : 'title'}):
        for div2 in div.find_all('h3', attrs = {'class' : 'title'}):
            for a in div2.find_all('a'):
                rec = {'tc' : 'P', 'jnl' : 'Phys.Sci.Tech..', 'note' : []}
                rec['artlink'] = a['href']
                if section == 'Condensed Matter Physics and Related Techology':
                    rec['fc'] = 'f'
                else:
                    rec['note'] = [section]
                if not rec['artlink'] in problematiclinks:
                    recs.append(rec)
                    links.append(rec['artlink'])
    div.decompose()

for div in tocpage.body.find_all('div', attrs = {'class' : 'title'}):
    for a in div.find_all('a'):
        rec = {'tc' : 'P', 'jnl' : 'Phys.Sci.Tech.', 'note' : []}
        rec['artlink'] = a['href']
        if not rec['artlink'] in problematiclinks:
            recs.append(rec)

i = 0
for rec in recs:
    i += 1
    autaff = False
    time.sleep(3)
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    except:
        time.sleep(30)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_date', 'citation_title', 'citation_firstpage',
                                        'citation_keywords', 'citation_doi', 'citation_author',
                                        'citation_author_institution', 'citation_issue',
                                        'citation_volume', 'DC.Description', 'citation_pdf_url',
                                        'citation_reference', 'citation_language', 'DC.Rights',
                                        'citation_lastpage'])
    ejlmod3.globallicensesearch(rec, artpage)
    #ORCIDs
    rec['autaff'] = []
    for ul in artpage.body.find_all('ul', attrs = {'class' : 'authors'}):
        for li in ul.find_all('li'):
            for span in li.find_all('span', attrs = {'class' : 'name'}):
                rec['autaff'].append([span.text.strip()])
            for span in li.find_all('span', attrs = {'class' : 'orcid'}):    
                rec['autaff'][-1].append(re.sub('.*org\/', 'ORCID:', span.text.strip()))
            for span in li.find_all('span', attrs = {'class' : 'affiliation'}):    
                rec['autaff'][-1].append(span.text.strip())
                
    ejlmod3.printrecsummary(rec)

jnlfilename = 'physscitech%s.%s_%s' % (rec['vol'], rec['issue'], issueid)

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
