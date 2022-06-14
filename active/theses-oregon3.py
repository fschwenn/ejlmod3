# -*- coding: utf-8 -*-
#harvest theses from Oregon U.
#FS: 2021-01-27

import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

jnlfilename = 'THESES-OREGON-%s' % (ejlmod3.stampoftoday())

publisher = 'Oregon U.'

hdr = {'User-Agent' : 'Magic Browser'}

rpp = 50
pages = 4
years = 2
boringdisciplines = ['Department+of+Geography', 'Department+of+Educational+Methodology%2C+Policy%2C+and+Leadership',
                     'Department+of+Psychology', 'School+of+Music+and+Dance', 'Department+of+Geological+Sciences',
                     'Department+of+Biology', 'Department+of+Linguistics', 'Department+of+Anthropology',
                     'Department+of+Architecture', 'Department+of+Comparative+Literature',
                     'Department+of+Economics', 'Department+of+English', 'Department+of+Finance',
                     'Department+of+History', 'Department+of+Marketing', 'Department+of+Political+Science',
                     'Department+of+Sociology', 'Department+of+Special+Education+and+Clinical+Sciences',
                     'Environmental+Studies+Program', 'School+of+Journalism+and+Communication',
                     'Department+of+Chemistry+and+Biochemistry', 'Department+of+Counseling+Psychology+and+Human+Services',
                     'Department+of+Human+Physiology', 'Conflict+and+Dispute+Resolution+Program',
                     'Department+of+Accounting', 'Department+of+Chemistry', 'Department+of+Decision+Sciences',
                     'Department+of+East+Asian+Languages+and+Literatures', 'Department+of+Education+Studies',
                     'Department+of+German+and+Scandinavian', 'Department+of+Landscape+Architecture',
                     'Department+of+Management', 'Department+of+Philosophy',
                     'Department+of+Romance+Languages', 'Department+of+Theater+Arts']
boringdegrees = ['M.A.', 'M.S.', 'masters', 'D.Ed.']

recs = []
for page in range(pages):
    tocurl = 'https://scholarsbank.uoregon.edu/xmlui/handle/1794/13076/discover?rpp='+str(rpp)+'&etal=0&group_by=none&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc'
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    prerecs = ejlmod3.getdspacerecs(tocpage, 'https://scholarsbank.uoregon.edu')
    for rec in prerecs:
        keepit = True
        #check year
        if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
            keepit = False
        #check degree
        for degree in rec['degree']:
            if degree in boringdisciplines or degree in boringdegrees:
                keepit = False
            elif not degree in ['Ph.D.', 'doctoral']:
                rec['note'].append(degree)
        if keepit:
            recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(2)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+'?show=full'), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+'?show=full'), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_date', 'DCTERMS.abstract', 'citation_pdf_url', 'citation_keywords'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'DC.creator':
                author = re.sub(' *\[.*', '', meta['content'])
                rec['autaff'] = [[ author ]]
                rec['autaff'][-1].append(publisher)
    for tr in artpage.body.find_all('tr'):
        for td in tr.find_all('th', attrs = {'class' : 'label-cell'}):
            tdt = td.text.strip()
            td.decompose()
        for td in tr.find_all('td'):
            if td.text.strip() == 'en_US':
                continue
            #supervisor
            if tdt in ['dc.contributor.supervisor', 'dc.contributor.advisor']:
                if td.text.strip():
                    rec['supervisor'].append([ re.sub(' \(.*', '', td.text.strip()) ])
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
ejlmod3.writeretrival(jnlfilename)
