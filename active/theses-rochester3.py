# -*- coding: utf-8 -*-
#harvest theses from Rochester U.
#FS: 2021-04-15
#FS: 2023-01-17

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'U. Rochester'

startyear = ejlmod3.year(backwards=1)
skipalreadyharvested = True
departments = [('PHYS', 'Rochester U.', '59', ''),
	       ('MATH', 'U. Rochester', '74', 'm'),
	       ('COMP', 'U. Rochester', '135', 'c')]
hdr = {'User-Agent' : 'Magic Browser'}
jnlfilename = 'THESES-ROCHESTER-%s' % (ejlmod3.stampoftoday())

def tfstrip(x): return x.strip()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []


recs = []
prerecs = []
for (subj, aff, dep, fc) in departments:
    starturl = 'https://urresearch.rochester.edu/browseCollectionItems.action?collectionId=' + dep
    ejlmod3.printprogress("=", [[subj], [dep], [starturl]])
    req = urllib.request.Request(starturl)
    startpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for h3 in startpage.find_all('h3'):
        if re.search('Viewing.*of', h3.text):
            rpp = int(re.sub('.* (\d+) of.*', r'\1', h3.text.strip()))
            total = int(re.sub('.*of (\d+).*', r'\1', h3.text.strip()))
            pages = (total-1)//rpp + 1
    tocpages = [startpage]
    for i in range(pages-1):
        time.sleep(5)
        tocurl = 'https://urresearch.rochester.edu/browseCollectionItems.action?rowStart=' + str((i+1)*rpp) + '&startPageNumber=1&currentPageNumber=2&sortElement=name&sortType=asc&collectionId=' + dep + '&selectedAlpha=All&contentTypeId=-1'
        ejlmod3.printprogress("=", [[subj], [dep], [i+2, pages], [(i+2)*rpp, total], [tocurl]])
        req = urllib.request.Request(tocurl)
        tocpages.append(BeautifulSoup(urllib.request.urlopen(req), features="lxml"))
    for tocpage in tocpages:
        for tbody in tocpage.find_all('tbody'):
            for tr in tbody.find_all('tr'):
                keepit = True
                rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'affiliation' : aff,
                       'supervisor' : [], 'note' : [subj]}
                for a in tr.find_all('a'):
                    if a.has_attr('href') and re.search('institutionalItemId', a['href']):
                        rec['link'] = 'https://urresearch.rochester.edu' + re.sub(';jsessionid=.*\?', '?', a['href'])
                        rec['tit'] = a.text.strip()
                        rec['doi'] = '20.2000/Rochester/' + re.sub('\D', '', rec['link'])
                if fc:
                    rec['fc'] = fc
                for td in tr.find_all('td'):
                    if re.search('^\d\d\d\d$', td.text):
                        rec['year'] = td.text.strip()
                        if int(rec['year']) < startyear:
                            keepit = False
                            #print('    %s too old (%s)' % (rec['link'], rec['year']))
                if keepit:
                    if rec['doi'] in alreadyharvested:
                        print('    %s in backup' % (rec['link']))
                    else:
                        prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))

i = 0
keepit = True
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        req = urllib.request.Request(rec['link'])
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
            time.sleep(5)
        except:
            print("no access to %s" % (rec['link']))
            continue      
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_publication_date'])
    if 'autaff' in rec:
        rec['autaff'][-1].append(rec['affiliation'])
    #FFT
    for table in artpage.body.find_all('table', attrs = {'class' : 'greyBorderTable'}):
        for a in table.find_all('a'):
            if a.has_attr('href') and re.search('fileDownloadForInstit', a['href']):
                if re.search('\.pdf', a.text):
                    rec['hidden'] = 'https://urresearch.rochester.edu/' + re.sub(';jsessionid=.*\?', '?', a['href'][1:])
    #abstract
    for table in artpage.body.find_all('table', attrs = {'class' : 'noPaddingTable'}):
        lt = ''
        for tr in table.find_all('tr'):
            if lt == 'Abstract' and not 'abs' in list(rec.keys()):
                rec['abs'] = tr.text.strip()
            for label in tr.find_all('label'):
                lt = label.text.strip()
    #remaining metadata
    for table in artpage.body.find_all('table', attrs = {'width' : '100%'}):
        lt = ''
        for tr in table.find_all('tr'):            
            #supervisor
            if lt == 'Contributor(s):':
                if re.search('Thesis Advisor', tr.text):
                    for a in tr.find_all('a'):
                        if a.has_attr('href') and re.search('orcid.org\/', a['href']):
                            rec['supervisor'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', a['href']))
                        else:
                            rec['supervisor'].append([re.sub(' \(.*', '', a.text.strip())])
            #keywords
            if lt == 'Subject Keywords:':
                rec['keyw'] = re.split('; ', tr.text.strip())
                lt = ''
            #pages
            if lt == 'Extents:':
                if re.search('pages.*\d\d', tr.text):
                    rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', tr.text.strip())
                    lt = ''
            #label
            for label in tr.find_all('td', attrs = {'class' : 'previewLabel'}):
                lt = label.text.strip()
    #handle
    for h3 in artpage.body.find_all('h3'):
        for a in h3.find_all('a'):
            if a.has_attr('href') and re.search('handle.net\/1802', a['href']):
                rec['hdl'] = re.sub('.*handle\/', '', a['href'])
    #embargo
    for div in artpage.body.find_all('div', attrs = {'class' : 'errorMessage'}):
        if re.search('ill be available to view starting', div.text):
            print('embargo')
            keepit = False
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
        
ejlmod3.writenewXML(recs, publisher, jnlfilename)
