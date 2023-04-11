# -*- coding: utf-8 -*-
#harvest theses from Georgia Tech
#FS: 2022-04-18
#FS: 2023-03-27

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

publisher = 'Georgia Tech'
jnlfilename = 'THESES-GEORGIATECH-%s' % (ejlmod3.stampoftoday())

rpp = 50
pages = 5
skipalreadyharvested = True

boring = ['Electrical and Computer Engineering', 'Civil and Environmental Engineering',
          'Aerospace Engineering', 'Biology', 'Chemical and Biomolecular Engineering',
          'City and Regional Planning', 'Computational Science and Engineering',
          'Industrial and Systems Engineering', 'Interactive Computing', 'Music',
          'Mechanical Engineering', 'Psychology', 'Public Policy', 'Architecture',
          'Biomedical Engineering (Joint GT/Emory Department)', 'Chemistry and Biochemistry',
          'Economics', 'History, Technology and Society', 'International Affairs',
          'Building Construction', 'Business', 'Earth and Atmospheric Sciences',
          'Literature, Media, and Communication', 'Materials Science and Engineering',
          'Applied Physiology', 'Industrial Design', 'Biomedical Engineering',
          'Polymer, Textile and Fiber Engineering', 'Bioengineering',
          'Center for Music Technology', 'Chemical Engineering', 'City Planning',
          'Digital Media', 'Literature, Communication, and Culture', 'Management',
          'Materials Science &amp; Engineering', 'Medical Physics', 'Robotics',
          'Strategic Management']

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

prerecs = []
for page in range(pages):
    tocurl = 'https://smartech.gatech.edu/handle/1853/3739/browse?rpp=' + str(rpp) + '&sort_by=2&type=dateissued&offset=' + str(rpp*(page)) + '&etal=-1&order=DESC'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    prerecs += ejlmod3.getdspacerecs(tocpage, 'https://smartech.gatech.edu', alreadyharvested=alreadyharvested)
    print('  %i records so far' % (len(prerecs)))
    time.sleep(7)

i = 0
recs = []
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        req = urllib.request.Request(rec['link'] + '?show=full', headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue

    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.title','DCTERMS.issued', 'DC.subject',
                                        'DCTERMS.abstract', 'citation_pdf_url'])
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'ds-table-row'}):
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            label = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'word-break'}):
            word = td.text.strip()
        #Department
        if label == 'dc.contributor.department':
            if word in boring:
                keepit = False
            elif word == 'Mathematics':
                rec['fc'] = 'm'
            elif word == 'Computer Science':
                rec['fc'] = 'c'
            elif word != 'Physics':
                rec['note'].append(word)
        #supervisor
        elif label == 'dc.contributor.advisor':
            rec['supervisor'].append([word])

    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
