# -*- coding: utf-8 -*-
#harvest theses from Zagreb U.
#FS: 2020-12-01
#FS: 2023-04-17

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'U. Zagreb (main)'
jnlfilename = 'THESES-ZAGREB-%s' % (ejlmod3.stampoftoday())

pages = 1
skipalreadyharvested = True

hdr = {'User-Agent' : 'Magic Browser'}
recs = []
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

for (subject, aff, fc) in [('Fizika', 'Zagreb U., Phys. Dept.', ''), ('Matematika',  'U. Zagreb (main)', 'm')]:
    for page in range(pages):
        tocurl = 'https://repozitorij.pmf.unizg.hr/en/islandora/search?page=' + str(page) + '&display=default&f%5B0%5D=RELS_EXT_hasModel_uri_s%3A%22info%3Afedora/ir%3AdisertationCModel%22&f%5B1%5D=facet_field_pth%3APRIRODNE%5C%20ZNANOSTI%23' + subject + '%2A&islandora_solr_search_navigation=0&sort=dabar_sort_date_s%20desc'
        ejlmod3.printprogress("=", [[subject], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(5)
        for div in tocpage.body.find_all('div', attrs = {'class' : 'islandora-solr-search-result-inner'}):
            for dd in div.find_all('dd', attrs = {'class' : 'bibl_metadata'}):
                rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'affiliation' : aff,
                       'supervisor' : [], 'note' : [subject]}
                for a in dd.find_all('a'):
                    rec['link'] = a['href']
                    rec['urn'] = a.text.strip()
                    if fc:
                        rec['fc'] = fc
                    if not skipalreadyharvested or not rec['urn'] in alreadyharvested:
                        recs.append(rec)
                    else:
                        print('  ', rec['urn'], 'already in backup')
        print('  %4i records so far' % (len(recs)))

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(10)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_title', 'DC.rights',
                                        'citation_publication_date', 'citation_keywords',
                                        'citation_language', 'citation_pdf_url'])
    rec['autaff'][-1].append(rec['affiliation'])
    if 'keyw' in rec and len(rec['keyw']) == 1:
        rec['keyw'] = re.split(';', rec['keyw'][0])
    for tr in artpage.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) == 2:
            tdt = tds[0].text.strip()
            #supervisor
            if tdt == 'Mentor':
                for a in tds[1].find_all('a'):
                    rec['supervisor'].append([a.text.strip()])
            #Abstract
            elif tdt == 'Abstract (english)' or re.search('Sa.*etak .engleski.', tdt):
                rec['abs'] = tds[1].text.strip()
            elif tdt == 'Abstract'  or re.search('Sa.*etak', tdt):
                if re.search(' the ', tds[1].text):
                    rec['abs'] = tds[1].text.strip()
                else:
                    rec['abshr'] = tds[1].text.strip()
            #coration abstract
            elif tdt == 'Abstract (croatian)':
                rec['abshr'] = tds[1].text.strip()
            #pages
            elif tdt in ['Extent', 'Opseg']:
                if re.search('\d\d', tds[1].text):
                    rec['pages'] = re.sub('\D*(\d\d+).*', r'\1', tds[1].text.strip())
            #english title
            elif tdt in ['Title (english)', 'Naslov (engleski)']:
                if 'language' in list(rec.keys()):
                    rec['transtit'] = tds[1].text.strip()
    if not 'abs' in list(rec.keys()) and 'abshr' in list(rec.keys()):
        rec['abs'] = rec['abshr']
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
