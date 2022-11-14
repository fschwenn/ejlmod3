# -*- coding: utf-8 -*-
#harvest theses from Stellenbosch U.
#FS: 2022-11-08

import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

jnlfilename = 'THESES-STELLENBOSCH-%s' % (ejlmod3.stampoftoday())

publisher = 'U. Stellenbosch'

hdr = {'User-Agent' : 'Magic Browser'}

rpp = 10
pages = 1
years = 2

recs = []
for (fc, dep) in [('c', '96338'), ('m', '852'), ('', '3640'), ('c', '96343')]:
    for page in range(pages):
        tocurl = 'https://scholar.sun.ac.za/handle/10019.1/' + dep + '/browse?rpp=' + str(rpp) + '&offset=' + str(rpp*page) + '&etal=-1&sort_by=2&order=DESC'
        ejlmod3.printprogress('=', [[dep], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        prerecs = ejlmod3.getdspacerecs(tocpage, 'https://scholar.sun.ac.za', fakehdl=True)
        for rec in prerecs:
            keepit = True
            #check year
            if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
                keepit = False
            if keepit:
                if fc: rec['fc'] = fc
                recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(3)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+'?show=full'), features="lxml")
        time.sleep(4)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+'?show=full'), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_date', 'DCTERMS.abstract', 'citation_pdf_url',
                                        'citation_language', 'citation_author', 'DC.rights', 'DC.subject', 'DCTERMS.extent'])
    if 'abs' in rec:
        rec['abs'] = re.sub('^ENGLISH[ A-Z]+:  *', '', rec['abs'])
    for tr in artpage.body.find_all('tr'):
        tdt = ''
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            tdt = td.text.strip()
            td.decompose()
        for td in tr.find_all('td'):
            if td.text.strip() in ['en_ZA', 'af_ZA', '']:
                continue
            #supervisor
            if tdt in ['dc.contributor.supervisor', 'dc.contributor.advisor']:
                if td.text.strip():
                    rec['supervisor'].append([ re.sub(' \(.*', '', td.text.strip()) ])
    rec['autaff'][-1].append(publisher)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)

