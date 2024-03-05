# -*- coding: utf-8 -*-
#program to harvest Iraqi J.Phys.
# FS 2023-08-25

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc

regexpref = re.compile('[\n\r\t]')

publisher = 'Baghdad U.'

issueid = sys.argv[1]
urltrunc = 'https://ijp.uobaghdad.edu.iq/index.php/physics/issue/view/%s' % (issueid)

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

print(urltrunc)
try:
    #tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(urltrunc), features="lxml")
    driver.get(urltrunc)
    tocpage = BeautifulSoup(driver.page_source, features="lxml")
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (urltrunc))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(urltrunc), features="lxml")

#print(tocpage.text)


problematiclinnks = ['https://revistasinvestigacion.unmsm.edu.pe/index.php/fisica/article/view/15167']
recs = []
for div in tocpage.body.find_all('h3', attrs = {'class' : 'media-heading'}):
    for a in div.find_all('a'):
        rec = {'tc' : 'P', 'jnl' : 'Iraqi J.Phys.', 'note' : []}
        rec['artlink'] = a['href']
        if not rec['artlink'] in problematiclinnks:
            recs.append(rec)

i = 0
for rec in recs:
    i += 1
    autaff = False
    time.sleep(3)
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    try:
        #artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(30)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_date', 'citation_title', 'citation_firstpage',
                                        'citation_keywords', 'citation_doi', 'citation_author',
                                        'citation_author_institution', 'citation_issue',
                                        'citation_volume', 'DC.Description', 'citation_pdf_url',
                                        'citation_reference', 'citation_language', 'DC.Rights',
                                        'citation_lastpage'])
    if 'language' in rec and rec['language'] == 'es':
        for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.Title.Alternative'}):
            rec['transtit'] = meta['content']
    #ORCIDs
    rec['autaff'] = []
    for ul in artpage.body.find_all('div', attrs = {'class' : 'authors'}):
        for li in ul.find_all('div', attrs = {'class' : 'author'}):
            for span in li.find_all('strong'):
                rec['autaff'].append([span.text.strip()])
            for a in li.find_all('a'):
                if a.has_attr('href') and re.search('orcid.org', a['href']):
                    rec['autaff'][-1].append(re.sub('.*org\/', 'ORCID:', a.text.strip()))
            for span in li.find_all('div', attrs = {'class' : 'article-author-affilitation'}):    
                rec['autaff'][-1].append(span.text.strip())
                
    ejlmod3.printrecsummary(rec)

jnlfilename = 'iraqijphys%s.%s_%s' % (rec['vol'], rec['issue'], issueid)

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
