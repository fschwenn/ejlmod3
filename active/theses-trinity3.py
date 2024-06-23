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

rpp = 20 # fix
pages = 5
skipalreadyharvested = True
years = 2

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
for section in ['76240', '221', '171']:
    for page in range(pages):
        #tocurl = 'http://www.tara.tcd.ie/handle/2262/' + section + '/discover?rpp=' + str(rpp) + '&page=' + str(page+1) + '&group_by=none&etal=0&filtertype_0=dateIssued&filtertype_1=type&filter_0=[' + str(year) + '+TO+' + str(year) + ']&filter_relational_operator_1=equals&filter_1=Thesis&filter_relational_operator_0=equals'
        tocurl = 'https://www.tara.tcd.ie/handle/2262/' + section + '/recent-submissions?offset=' + str(rpp*page)
        ejlmod3.printprogress("=", [[section], [page+1, pages], [tocurl]])
        try:
            tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
            time.sleep(3)
        except:
            print("retry %s in 180 seconds" % (tocurl))
            time.sleep(180)
            tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
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
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['link'] + '?show=full'))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['link'] + '?show=full'))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'DCTERMS.issued', 'DCTERMS.abstract',
                                        'DC.subject', 'citation_pdf_url'])
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.publisher'}):
        if re.search('(Department|School) of', meta['content']):
            rec['school'] = re.sub('.*(Department|School) of (.*?)\..*', r'\2', meta['content'])
            rec['school'] = re.sub('.*(Department|School) of (.*)', r'\2', rec['school'])
        else:
            rec['note'].append(meta['content'])
    if 'school' in list(rec.keys()):
        if rec['school'] == 'Mathematics':
            rec['autaff'][-1].append('Trinity Coll., Dublin')
            rec['fc'] = 'm'
        elif rec['school'] in boringschools:
            print('   skip School of %s' % (rec['school']))
            keepit = False
        elif not rec['school'] in ['Physics', 'Computer Science & Statistics']:
            rec['note'].append(rec['school'])
    if len(rec['autaff'][-1]) == 1:
        rec['autaff'][-1].append(publisher)
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
        #print('\ntr: ', tr.text.strip())
        for td in tr.find_all('td'):
            #print('td: ', td.text.strip())
            if td.has_attr('class') and 'label-cell' in td['class']:
                tdt = td.text.strip()
                #print('tdt:', tdt)
            else:
                if tdt == 'dc.contributor.advisor':
                    tdtt = td.text.strip()
                    if len(tdtt) > 3:
                        rec['supervisor'].append([td.text.strip()])
                        #print('\033[93msv: ', td.text.strip(), '\033[0m')
    #degree level
                elif tdt == 'dc.type.qualificationlevel':
                    degreelevel = td.text.strip()
                    if degreelevel in ['Masters']:
                        keepit = False
                        print('  skip', degreelevel)
                    elif not degreelevel in ['Doctoral', 'en']:
                        rec['note'].append('DEG:::' + degreelevel)    
    
    if keepit:
        if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
            print('   %s too old' % (rec['year']))
        else:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
