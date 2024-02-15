# -*- coding: utf-8 -*-
#harvest theses from Colorado U.
#FS: 2021-04-16
#FS: 2023-04-24

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'U. Colorado, Boulder'
jnlfilename = 'THESES-COLORADO-%sB' % (ejlmod3.stampoftoday())

rpp = 10
skipalreadyharvested = True
departments = [('Physics', 'Colorado U.', 'PHYSICS', 3),
               ('Computer+Science', 'U. Colorado, Boulder', 'INFORMATICS', 2),
               ('Mathematics', 'U. Colorado, Boulder', 'MATHEMATICS', 2)]
urltrunc = 'https://scholar.colorado.edu'
hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

recs = []
for (affurl, affname, pages) in departments:    
    for page in range(pages):
        tocurl = urltrunc + '/catalog?f%5Bacademic_affiliation_sim%5D%5B%5D=' + affurl + '&f%5Bresource_type_sim%5D%5B%5D=Dissertation&locale=en&per_page=' + str(rpp) + '&sort=system_create_dtsi+desc&page=' + str(page+1)
        ejlmod3.printprogress("-", [[affname], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        for li in tocpage.body.find_all('li', attrs = {'class' : 'document'}):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : [affname]}
            for h4 in li.find_all('h4', attrs = {'class' : 'search-result-title'}):
                for a in h4.find_all('a'):
                    rec['link'] = urltrunc + a['href']
                    rec['doi'] = '20.2000/ColoradoU/' + re.sub('.*\/', '', a['href'])
                    rec['tit'] = a.text.strip()
                    rec['affiliation'] = affname
            if affurl == 'Mathematics':
                rec['fc'] = 'm'
            elif affurl == 'Computer+Science':
                rec['fc'] = 'c'
            if not rec['doi'] in ['20.2000/ColoradoU/6m311p316', '20.2000/ColoradoU/5138jd902']:
                if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                    recs.append(rec)
        print('  %4i records so far' % (len(recs)))
        time.sleep(10)


j = 0
for rec in recs:
    j += 1
    ejlmod3.printprogress("-", [[j, len(recs)], [rec['link']]])
    try:
        req = urllib.request.Request(rec['link'])
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(7)
    except:
        print('wait 10 minutes')
        time.sleep(600)
        req = urllib.request.Request(rec['link'])
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_pdf_url',
                                        'citation_title'])
    rec['autaff'][-1].append(rec['affiliation'])
    for dl in artpage.find_all('dl'):
        for child in dl.children:
            try:
                dn = child.name
            except:
                dn = ''
            if dn == 'dt':
                dt = child.text.strip()
            elif dn == 'dd':
                #abstract
                if dt == 'Abstract':
                    rec['abs'] = child.text.strip()
                #date
                elif dt == 'Date Issued':
                    rec['date'] = child.text.strip()
                #DOI
                elif dt == 'DOI':
                    rec['doi'] = re.sub('.*?(10.176.*)', r'\1', child.text.strip())
                #Rights statement
                elif dt == 'Rights statement':
                    rec['note'].append(child.text.strip())
                #supervisor
                elif dt == 'Advisor':
                    rec['supervisor'] = []
                    for li in child.find_all('li'):
                        rec['supervisor'].append([li.text.strip()])
                    if not rec['supervisor']:
                        rec['supervisor'].append([child.text.strip()])
                #keywords
                elif dt in ['Keyword', 'Subject']:
                    rec['keyw'] = []
                    for li in child.find_all('li'):
                        rec['keyw'].append(li.text.strip())
                #date
                elif dt == 'Date of publication':
                    rec['date'] = re.sub('.*([12]\d\d\d).*', r'\1', child.text.strip())
                dt = ''
    #FFT
    if not 'pdf_url' in list(rec.keys()):
        for a in artpage.find_all('a', attrs = {'title' : 'Download'}):
            rec['pdf_url'] = a['href']
    for a in artpage.find_all('a'):
        if a.has_attr('href') and re.search('creativecommons', a['href']):
            rec['license'] = {'url' : urltrunc + a['href']}
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
