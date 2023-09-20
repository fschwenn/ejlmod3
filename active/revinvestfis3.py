# -*- coding: utf-8 -*-
#program to harvest Rev.Invest.Fis.
# FS 2023-08-25

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time

regexpref = re.compile('[\n\r\t]')

publisher = 'San Marcos Natl. U.'

issueid = sys.argv[1]
urltrunc = 'https://revistasinvestigacion.unmsm.edu.pe/index.php/fisica/issue/view/%s' % (issueid)
    
print(urltrunc)
try:
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(urltrunc), features="lxml")
    time.sleep(13)
except:
    print("retry %s in 180 seconds" % (urltrunc))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(urltrunc), features="lxml")

#print(tocpage.text)


problematiclinks = ['https://revistasinvestigacion.unmsm.edu.pe/index.php/fisica/article/view/15167',
                    'https://revistasinvestigacion.unmsm.edu.pe/index.php/fisica/article/view/11574',
                    'https://revistasinvestigacion.unmsm.edu.pe/index.php/fisica/article/view/8695',
                    'https://revistasinvestigacion.unmsm.edu.pe/index.php/fisica/article/view/8541',
                    'https://revistasinvestigacion.unmsm.edu.pe/index.php/fisica/article/view/8928',
                    'https://revistasinvestigacion.unmsm.edu.pe/index.php/fisica/article/view/8856',
                    'https://revistasinvestigacion.unmsm.edu.pe/index.php/fisica/article/view/8721',
                    'https://revistasinvestigacion.unmsm.edu.pe/index.php/fisica/article/view/8722',
                    'https://revistasinvestigacion.unmsm.edu.pe/index.php/fisica/article/view/8679']
recs = []
for div in tocpage.body.find_all('h3', attrs = {'class' : 'title'}):
    for a in div.find_all('a'):
        rec = {'tc' : 'P', 'jnl' : 'Rev.Invest.Fis.', 'note' : []}
        rec['artlink'] = a['href']
        if not rec['artlink'] in problematiclinks:
            recs.append(rec)

i = 0
for rec in recs:
    i += 1
    autaff = False
    time.sleep(10)
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    except:
        print('wait 180s')
        time.sleep(180)
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
    for ul in artpage.body.find_all('ul', attrs = {'class' : 'authors'}):
        for li in ul.find_all('li'):
            for span in li.find_all('span', attrs = {'class' : 'name'}):
                rec['autaff'].append([span.text.strip()])
            for span in li.find_all('span', attrs = {'class' : 'orcid'}):    
                rec['autaff'][-1].append(re.sub('.*org\/', 'ORCID:', span.text.strip()))
            for span in li.find_all('span', attrs = {'class' : 'affiliation'}):    
                rec['autaff'][-1].append(span.text.strip())
                
    ejlmod3.printrecsummary(rec)

jnlfilename = 'revinvestfis%s.%s_%s' % (rec['vol'], rec['issue'], issueid)

ejlmod3.writenewXML(recs, publisher, jnlfilename, retfilename='retfiles_special')
