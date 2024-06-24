# -*- coding: utf-8 -*-
#harvest theses from Cambridge Univeristy
#FS: 2018-02-02
#FS: 2022-10-30

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

publisher = 'Cambridge U.'
jnlfilename = 'THESES-CAMBRIDGE-%s' % (ejlmod3.stampoftoday())
years = 2
pages = 100
rpp = 50 
skipalreadyharvested = True
skiptooold = True


boring = ['Theses - Chemistry', 'Department of Chemistry', 'Theses - Earth Sciences', 'Theses - Geography',
          'Theses - Materials Science and Metallurgy', 'Department of Materials Science and Metallurgy']
boring += ['MPhil', 'Masters']

alreadyharvested = []
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
artlinks = []
for page in range(pages):
    tocurl = 'https://www.repository.cam.ac.uk/handle/1810/256064' + '/browse/type?value=Thesis&bbm.page=' + str(page+1) + '&bbm.rpp=' + str(rpp) + '&bbm.sd=DESC'
    tocurl = 'https://www.repository.cam.ac.uk/browse/type?scope=3edc4aff-b9e2-4cff-9418-895417421fd8' + '&value=Thesis&bbm.page=' + str(page+1) + '&bbm.rpp=' + str(rpp) + '&bbm.sd=DESC'    
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])    
    try:
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
        time.sleep(6)
    except:
        try:
            print("retry %s in 180 seconds" % (tocurl))
            time.sleep(180)
            tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
        except:
            print("retry %s in 180 seconds" % (tocurl))
            time.sleep(180)
            tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    for div in tocpage.find_all('div', attrs = {'class' : 'pagination-info'}):
        for span in div.find_all('span'):
            if re.search('\d of \d\d', span.text):
                total = int(re.sub('.*of (\d+).*', r'\1', span.text.strip()))
                pages = (total - 1) // rpp + 1
    for ds in tocpage.find_all('ds-item-list-element'):
        for a in ds.find_all('a', attrs = {'class' : 'item-list-title'}):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'tit' : a.text.strip(), 'supervisor' : [],
                   'artlink' : 'https://www.repository.cam.ac.uk' + a['href'], 'note' : [] }
            if ejlmod3.checkinterestingDOI(rec['artlink']):
                if not skiptooold or ejlmod3.checknewenoughDOI(rec['artlink']):
                    prerecs.append(rec)
#            else:
#                print('    %s uninteresting' % (rec['artlink']))
    print('    %4i recors so far' % (len(prerecs)))
    if page > pages:
        break


recs = []
reorcid = re.compile('.*?(\d\d\d\d\-\d\d\d\d\-\d\d\d\d\-\d\d\d.).*')
for (i, rec) in enumerate(prerecs):
    keepit = True
    aff = []
    ejlmod3.printprogress('-', [[i+1, len(prerecs)], [rec['artlink']+'/full'], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']+'/full'), features="lxml")
        time.sleep(4)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']+'/full'), features="lxml")
        except:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']+'/full'), features="lxml")

    ejlmod3.metatagcheck(rec, artpage, ['citation_publication_date', 'citation_publication_date',
                                        'citation_keywords', 'citation_pdf_url',
                                        'citation_author', 'description'])
    for div in artpage.body.find_all('div', attrs = {'class' : 'collections'}):
        coll = div.text.strip()
        if coll in boring:
            keepit = False
            print('     skip', coll)
            ejlmod3.adduninterestingDOI(rec['artlink'])
        elif coll in ['Theses - Institute of Astronomy']:
            rec['fc'] = 'a'
        elif coll in ['Theses - Department of Pure Mathematics and Mathematical Statistics (DPMMS)']:
            rec['fc'] = 'm'
        else:
            rec['note'].append('COL:::' + coll)
    for tr in artpage.body.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) >= 2:
            tdh = tds[0].text.strip()
            #print(' . ', tdh)
            tdd = tds[1].text.strip()
        #ORCID
        if tdh == 'dc.contributor.orcid':
            if reorcid.search(tdd):
                rec['autaff'][-1].append(reorcid.sub(r'ORCID:\1', tdd))
        #DOI
        elif tdh == 'dc.identifier.doi':
            rec['doi'] = re.sub('.*doi\/', '', tdd)
        #supervisor
        elif tdh == 'cam.supervisor':
            rec['supervisor'].append([tdd])
        #department
        elif tdh == 'dc.publisher.department':
            rec['department'] = tdd
            if tdd in boring:
                keepit = False
                print('     skip', tdd)
                ejlmod3.adduninterestingDOI(rec['artlink'])
            else:
                rec['note'].append('DEP:::' + tdd)
        #license
        elif tdh in ['dc.rights.uri', 'rioxxterms.licenseref.uri']:
            if re.search('creativecomm', tdd):
                rec['license'] = {'url' : tdd}
        #date
        elif tdh == 'dc.date.issued':
            rec['date'] = tdd
        #level
        elif tdh == 'dc.type.qualificationlevel':
            if tdd in boring:
                keepit = False
                print('     skip', tdd)
                ejlmod3.adduninterestingDOI(rec['artlink'])
            elif tdd != 'Doctoral':
                rec['note'].append('DEG:::' + tdd)

    if 'date' in rec:
        if int(re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])) < ejlmod3.year(backwards=years):
            keepit = False
            print('     skip', rec['date'])
            ejlmod3.addtoooldDOI(rec['artlink'])
    if 'department' in rec:
        rec['autaff'][-1].append(rec['department'] + ', ' +publisher)
    else:
        rec['autaff'][-1].append(publisher)
    if keepit:
        if 'doi' in rec and rec['doi'] in alreadyharvested:
            print('  already in backup')
        else:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
