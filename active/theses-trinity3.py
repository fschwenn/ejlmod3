# -*- coding: utf-8 -*-
#harvest theses from TCD, Dublin 
#FS: 2020-09-02
#FS: 2023-03-09

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

years = [ejlmod3.year(backwards=1), ejlmod3.year()]
rpp = 50
pages = 20
numberofrecords = rpp*pages
skipalreadyharvested = True

publisher = 'TCD, Dublin'
jnlfilename = 'THESES-TrinityCollegeDublin-%s' % (ejlmod3.stampoftoday())

boringschools = ['Biochemistry & Immunology', 'Business', 'Chemistry',
                 'Creative Arts', 'Dental Sciences', 'Religion',
                 'Ecumenics', 'Education', 'Engineering', 'English',
                 'Histories & Humanities', 'Lang, Lit', 'Law',
                 'Linguistic Speech & Comm Sci', 'Medicine', 'Natural Sciences',
                 'Nursing & Midwifery', 'Pharmacy & Pharma', 'Psychology',
                 'Social Sciences & Philosophy', 'Social Work & Social Policy']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdls = []

prerecs = []
for year in years:
    for section in ['76240', '221', '171']:
        realpages = pages
        for page in range(pages):
            if page*rpp < numberofrecords:
                tocurl = 'http://www.tara.tcd.ie/handle/2262/' + section + '/discover?rpp=' + str(rpp) + '&page=' + str(page+1) + '&group_by=none&etal=0&filtertype_0=dateIssued&filtertype_1=type&filter_0=[' + str(year) + '+TO+' + str(year) + ']&filter_relational_operator_1=equals&filter_1=Thesis&filter_relational_operator_0=equals'
                ejlmod3.printprogress("=", [[year], [section], [page+1, realpages]])
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
                for rec in ejlmod3.getdspacerecs(tocpage, 'http://www.tara.tcd.ie'):
                    if rec['hdl'] in hdls or rec['hdl'] in ['2262/82940']:
                        print('  HDL:%s already from other collection' % (rec['hdl']))
                    elif skipalreadyharvested and rec['hdl'] in alreadyharvested:
                        print('  HDL:%s already in backup' % (rec['hdl']))                        
                    else:
                        prerecs.append(rec)
                        hdls.append(rec['hdl'])
        print('  %4i records so far' % (len(prerecs)))
    
i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[year], [i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['link'] + '?show=full'))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_authors', 'DCTERMS.issued', 'DCTERMS.abstract',
                                        'DC.subject'])
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.publisher'}):
        if re.search('School of', meta['content']):
            rec['school'] = re.sub('.*School of (.*?)\..*', r'\1', meta['content'])
        else:
            rec['note'].append(meta['content'])
    if 'school' in list(rec.keys()):
        if rec['school'] == 'Mathematics':
            rec['autaff'][-1].append('Trinity Coll., Dublin')
            rec['fc'] = 'm'
        elif rec['school'] in boringschools:
            print('   skip School of %s' % (rec['school']))
            keepit = False
        else:
            rec['note'].append(rec['school'])
    if len(rec['autaff'][-1]) == 1:
        rec['autaff'][-1].append(publisher)
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    #fulltext
    for div in artpage.body.find_all('div', attrs = {'class' : 'simple-item-view-download'}):
        for a in div.find_all('a'):
            if 'license' in list(rec.keys()):
                rec['FFT'] = a['href']
            else:
                rec['hidden'] = a['href']
    #supervisor
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'ds-table-row'}):
        tdt = ''
        for td in tr.find_all('td'):
            if td.has_attr('label-cell'):
                tdt = td.text.strip()
            else:
                if tdt == 'dc.contributor.advisor':
                    rec['supervisor'].append(td.text.strip())
                
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
