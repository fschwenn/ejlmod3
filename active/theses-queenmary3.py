# -*- coding: utf-8 -*-
#harvest theses from Queen Mary, U. of London (main)
#FS: 2020-09-02
#FS: 2023-02-17

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

startyear = ejlmod3.year(backwards=1)
stopyear = ejlmod3.year(backwards=-1)
rpp = 50
pages = 4
skipalreadyharvested = True

publisher = 'Queen Mary, U. of London (main)'

jnlfilename = 'THESES-QUEEN_MARY-%s' % (ejlmod3.stampoftoday())
boring = ['Engineering and Materials Science', 
          'Biological and Chemical Sciences', 'Law', 'Medicine', 'Electronic Engineering',
          'Medicine and Dentistry', 'Engineering and Material Science',
          'School of Medicine and Dentistry', 'School of Law',
          'School of Biological and Chemical Sciences',
          'Cancer', #'Computer Science',
          'Electronic engineering and computer science',
          'Dentistry',
          'Barts and the London School of Medicine and Dentistry',
          'Geography', 'History', 'C4DM', 'Business and Management']
prerecs = []

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

numberofrecords = rpp*pages
realpages = pages
for page in range(pages):
    if len(prerecs) < numberofrecords and page < realpages:
        tocurl = 'https://qmro.qmul.ac.uk/xmlui/handle/123456789/56376/discover?rpp=' + str(rpp) + '&etal=0&group_by=none&page=' + str(page+1) + '&filtertype_0=dateIssued&filtertype_1=type&filter_relational_operator_1=equals&filter_relational_operator_0=equals&filter_1=Thesis&filter_0=%5B' + str(startyear) + '+TO+' + str(stopyear) + '%5D'
        tocurl = 'https://qmro.qmul.ac.uk/xmlui/handle/123456789/56376/browse?rpp=' + str(rpp) + '&sort_by=3&type=dateissued&offset=' + str(rpp*page) + '&etal=-1&order=DESC'
        ejlmod3.printprogress("=", [[page+1, realpages], [tocurl]])
        try:
            tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
            time.sleep(3)
        except:
            print("retry %s in 180 seconds" % (tocurl))
            time.sleep(180)
            tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
        if page == 0:
            for p in tocpage.body.find_all('p', attrs = {'class' : 'pagination-info'}):
                if re.search('\d of \d+', p.text):
                    numberofrecords = int(re.sub('.*of (\d+).*', r'\1', p.text.strip()))
                    print('  %i theses in query' % (numberofrecords))
                    realpages = (numberofrecords-1) // rpp + 1
        for rec in ejlmod3.getdspacerecs(tocpage, 'https://qmro.qmul.ac.uk', fakehdl=True):
            rec['doi'] = '20.2000/QueenMary/' + re.sub('\W', '', rec['link'][24:])
            if ejlmod3.checkinterestingDOI(rec['doi']):
                if skipalreadyharvested and rec['doi'] in alreadyharvested:
                    pass
                else:
                    prerecs.append(rec)
        print('  %4i records so far' % (len(prerecs)))

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['link']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['DCTERMS.issued', 'DCTERMS.abstract', 'DC.subject',
                                        'DC.contributor', 'citation_pdf_url', 'DC.identifier',
                                        'citation_date'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            if meta['name'] in ['citation_author', 'DC.creator']:
                if not re.search('Queen Mary', meta['content']):
                    rec['autaff'] = [[ meta['content'], publisher ]]
    keepit = True
    for kw in rec['keyw']:
        if kw in boring:
            print('  skip', kw)
            keepit = False
    if keepit:
        if skipalreadyharvested and rec['doi'] in alreadyharvested:
            pass
        else:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['doi'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
