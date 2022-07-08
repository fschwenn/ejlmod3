# -*- coding: utf-8 -*-
#harvest theses from Bergen U.
#FS: 2022-07-05

import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

jnlfilename = 'THESES-BERGEN-%s' % (ejlmod3.stampoftoday())

publisher = 'U. Bergen (main)'

hdr = {'User-Agent' : 'Magic Browser'}

rpp = 10
pages = 1
years = 2

recs = []
for (fc, dep, aff) in [('c', '918', 'U. Bergen (main)'), ('m', '920', 'U. Bergen (main)'), ('', '914', ' Bergen U.')]:
    for page in range(pages):
        tocurl = 'https://bora.uib.no/bora-xmlui/handle/1956/' + dep + '/browse?rpp=' + str(rpp) + '&offset=' + str(rpp*page) + '&etal=-1&sort_by=2&type=type&value=Doctoral+thesis&order=DESC'
        ejlmod3.printprogress('=', [[dep], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        prerecs = ejlmod3.getdspacerecs(tocpage, 'https://bora.uib.no')
        for rec in prerecs:
            keepit = True
            #check year
            if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
                keepit = False
            if keepit:
                if fc: rec['fc'] = fc
                rec['affiliation'] = aff
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
                                        'citation_language', 'citation_author', 'DC.rights', 'DC.identifier'])
    for tr in artpage.body.find_all('tr'):
        tdt = ''
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            tdt = td.text.strip()
            td.decompose()
        for td in tr.find_all('td'):
            if td.text.strip() in ['en_US', '']:
                continue
            #supervisor
            if tdt in ['dc.contributor.supervisor', 'dc.contributor.advisor']:
                if td.text.strip():
                    rec['supervisor'].append([ re.sub(' \(.*', '', td.text.strip()) ])
            #ORCID
            elif tdt == 'dc.contributor.orcid':
                rec['autaff'][-1].append('ORCID:' + re.sub('.*org\/', '', td.text.strip()))
    rec['autaff'][-1].append(rec['affiliation'])
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)

