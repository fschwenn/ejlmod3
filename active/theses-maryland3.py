# -*- coding: utf-8 -*-
#harvest Maryland University theses
#FS: 2018-01-31
#FS: 2022-11-18

import getopt
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Maryland U., College Park'

jnlfilename = 'THESES-MARYLAND-%s' % (ejlmod3.stampoftoday())

rpp = 40
pages = 1
years = 2 
skipalreadyharvested = True


if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
recs = []
for  (fc, dep, aff) in [('m', '2793', 'Maryland U., College Park'), ('c', '2756', 'Maryland U., College Park'),
                        ('a', '2746', 'Maryland U., College Park'), ('', '2800', 'Maryland U.')]:
    for page in range(pages):
        tocurl = 'https://drum.lib.umd.edu/handle/1903/' + dep + '/browse?rpp=' + str(rpp) + '&sort_by=2&type=dateissued&offset=' + str(page*rpp) + '&etal=-1&order=DESC'
        ejlmod3.printprogress('=', [[dep, page+1, pages], [tocurl]])
        try:
            tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
            time.sleep(4)
        except:
            print("retry %s in 180 seconds" % (tocurl))
            time.sleep(180)
            tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
        for rec in ejlmod3.getdspacerecs(tocpage, 'https://drum.lib.umd.edu'):
            if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
                print('     %s too old' % (rec['hdl']))
            elif skipalreadyharvested and rec['hdl'] in alreadyharvested:
                print('     %s already in backup' % (rec['hdl']))
            else:
                if fc: rec['fc'] = fc
                rec['affiliation'] = aff
                recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(4)
    except:
        print("retry %s in 180 seconds" % (rec['link']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['DCTERMS.abstract', 'DC.subject', 'DC.creator', 'bepress_citation_pdf_url',
                                        'DC.identifier', 'citation_pdf_url'])
    rec['autaff'][-1].append(rec['affiliation'])
    for div in artpage.body.find_all('div', attrs = {'class' : 'simple-item-view-advisor'}):
        for p in div.find_all('div'):
            rec['supervisor'].append([ re.sub('^Dr. ', '', p.text.strip()) ])
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
