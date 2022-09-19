# -*- coding: utf-8 -*-
#harvest theses Jyvaskyla U
#FS: 2022-09-06

import sys
import os
import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

rpp = 60
pages = 1

publisher = 'Jyvaskyla U'

jnlfilename = 'THESES-JYVASKYLA-%s' % (ejlmod3.stampoftoday())
boring = [u'Akvaattiset tieteet', u'Ekologia ja evoluutiobiologia', u'Englannin kieli',
          u'Erityispedagogiikka', u'Filosofia', u'Fysioterapia', u'Gerontologia ja kansanterveys',
          u'Journalistiikka', u'Kasvatustiede', u'Liikunnan yhteiskuntatieteet',
          u'Liikuntapedagogiikka', u'Likes; Liikunnan ja kansanterveyden julkaisuja',
          u'Markkinointi', u'Musiikkiterapia', u'Musiikkitiede',
          u'Nykykulttuurin tutkimuskeskuksen julkaisuja', u'Psykologia', u'Sosiologia',
          u'Soveltava kielitiede', u'Terveyskasvatus', u'Valtio-oppi', u'Varhaiskasvatustiede',
          u'Viestintä', u'Yrittäjyys', u'Yritysten ympäristöjohtaminen']

recs = []
prerecs = []
for section in ['56881', '56880', '56990']:
    for page in range(pages):        
        tocurl = 'https://jyx.jyu.fi/handle/123456789/' + section + '/discover?rpp=' + str(rpp) + '&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc'
        ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
        try:
            tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
            time.sleep(4)
        except:
            print("retry %s in 180 seconds" % (tocurl))
            time.sleep(180)
            tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
        prerecs += ejlmod3.getdspacerecs(tocpage, 'https://jyx.jyu.fi', fakehdl=True)

i = 0
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+'?show=full'), features="lxml")
        time.sleep(4)
    except:
        print("retry %s in 180 seconds" % (rec['link']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+'?show=full'), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ["citation_author", "citation_date", "citation_language", "citation_pdf_url", "DCTERMS.extent", "DC.subject", "DC.identifier", "DC.rights", "DCTERMS.abstract"])
    if not 'autaff' in rec or not rec['autaff']:
        for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.creator'}):
            rec['autaff'] = [[ meta['content'] ]]
    rec['autaff'][-1].append(publisher)

    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.type'}):
        if meta['content'] in ["Master’s thesis"]:
            keepit = False
        elif not meta['content'] in ['Diss.']:
            rec['note'].append('DEGREE='+meta['content'])
    
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'ds-table-row'}):
        tdt = ''
        for td in tr.find_all('td'):
            if td.has_attr('class') and 'label-cell' in td['class']:
                tdt = td.text.strip()
            else:
                if tdt == 'dc.contributor.advisor':
                    sv = td.text.strip()
                    if sv != 'en':
                        rec['supervisor'].append([sv])
                elif tdt == 'dc.identifier.isbn':
                    rec['isbn'] = td.text.strip()
                elif tdt in ['thesis.degree.discipline', 'dc.relation.ispartofseries',
                             'dc.contributor.oppiaine', 'dc.contributor.tiedekunta',
                             'dc.contributor.laitos']:
                    disc = td.text.strip()
                    if disc in boring:
                        keepit = False
                    else:
                        rec['note'].append(disc)
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
