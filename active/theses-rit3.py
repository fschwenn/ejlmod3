# -*- coding: utf-8 -*-
#harvest theses from Rochester Inst. Tech.
#FS: 2022-07-22

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

numofpages = 5

publisher = 'Rochester Inst. Tech.'
boring = ["Master's Project"]
boring += ['Chester F. Carlson Center for Imaging Science (COS)', 'School of Design (CAD)',
           'Architecture (GIS)', 'Civil Engineering Technology Environmental Management and Safety (CET)',
           'Department of Criminal Justice (CLA)', 'Medical Illustration (CHST)',
           'Department of Electrical and Microelectronic Engineering (KGCOE)',
           'Psychology (CLA)', 'Public Policy (CLA)', 'School for American Crafts (CAD)',
           'School of Art (CAD)', 'School of Chemistry and Materials Science (COS)',
           'School of Communication (CLA)', 'School of Film and Animation (CAD)',
           'School of Photographic Arts and Sciences (CAD)', 'Sustainability (GIS)',
           'Thomas H. Gosnell School of Life Sciences (COS)', 'Wegmans School of Health and Nutrition (CHST)',
           'School for American Crafts (CIAS)', 'School of Art (CIAS)',
           'School of Design (CIAS)', 'School of Film and Animation (CIAS)',
           'School of Media Sciences (CIAS)', 'School of Photographic Arts and Sciences (CIAS)',
           'School of Print Media (CIAS)', 'Biomedical Sciences (CHST)',
           'Center for Materials Science and Engineering',
           'Civil Engineering Technology Environmental Management and Safety (CAST)',
           'School of Media Sciences (CET)']
reboring = re.compile('\((BS|M.Arch.|MFA|MS)\)')

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
jnlfilename = 'THESES-RochesterInstTech-%s' % (ejlmod3.stampoftoday())
for i in range(numofpages):
    if i == 0:
        tocurl = 'https://scholarworks.rit.edu/theses/index.html'
    else:
        tocurl = 'https://scholarworks.rit.edu/theses/index.%i.html' % (i+1)
    ejlmod3.printprogress('=', [[i+1, numofpages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(3)
    for p in tocpage.body.find_all('p', attrs = {'class' : 'article-listing'}):
        for a in p.find_all('a'):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : [], 'supervisor' : []}
            rec['link'] = a['href']
            if ejlmod3.checkinterestingDOI(rec['link']):
                prerecs.append(rec)

i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(10-3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    #license
    ejlmod3.metatagcheck(rec, artpage, ['bepress_citation_title', 'bepress_citation_date', 'description', 'bepress_citation_pdf_url'])
    for link in artpage.head.find_all('link', attrs = {'rel' : 'license'}):
        rec['license'] = {'url' : link['href']}
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'bepress_citation_author':
                author = re.sub(' *\[.*', '', meta['content'])
                rec['autaff'] = [[ author ]]
                for div in artpage.body.find_all('div', attrs = {'id' : 'orcid'}):
                    for p in div.find_all('p'):
                        rec['autaff'][-1].append('ORCID:%s' % (re.sub('.*orcid.org\/', '', p.text.strip())))
            #DOI
            elif meta['name'] == 'bepress_citation_doi':
                rec['doi'] = re.sub('.*org\/(10.*)', r'\1', meta['content'])
                rec['doi'] = re.sub('.*org\/doi:(10.*)', r'\1', rec['doi'])
            #typ of dissertation
            elif meta['name'] == 'bepress_citation_dissertation_name':
                disstyp = meta['content']
                if reboring.search(disstyp):
                    keepit = False
                elif not re.search('Ph.D.', disstyp):
                    rec['note'].append(disstyp)
    rec['autaff'][-1].append(publisher)
    #department
    for div in artpage.body.find_all('div', attrs = {'id' : 'department'}):
        for p in div.find_all('p'):
            department = p.text
            if department in boring:
                keepit = False
            else:
                rec['note'].append(department)
    #type
    for div in artpage.body.find_all('div', attrs = {'id' : 'document_type'}):
        for p in div.find_all('p'):
            doctype = p.text
            if doctype in boring:
                keepit = False
            elif doctype != 'Dissertation':
                rec['note'].append(doctype)
    #supervisor
    for j in range(6):
        for div in artpage.body.find_all('div', attrs = {'id' : 'advisor%i' % (j+1)}):
            for h4 in div.find_all('h4'):
                if h4.text == 'Advisor':
                    for p in div.find_all('p'):
                        rec['supervisor'].append([p.text])
                elif h4.text != 'Committee Member':
                    print(h4.text)
    if keepit:
        if not 'doi' in recs:
            rec['doi'] = '20.2000/RochesterInstTech/%s' % (re.sub('\D', '', rec['link']))
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
