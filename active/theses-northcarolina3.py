# -*- coding: utf-8 -*-
#harvest theses from UNC, Chapel Hill
#FS: 2020-07-07
#FS: 2023-03-24

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

irrelevantsubjects = []

publisher = 'UNC, Chapel Hill'
jnlfilename = 'THESES-UNC-%s' % (ejlmod3.stampoftoday())

rpp = 50
skipalreadyharvested = True
startyear = ejlmod3.year(backwards=1)
stopyear = ejlmod3.year() + 1
departments = [('Department+of+Physics+and+Astronomy', 'North Carolina U.', 'PHYSICS', ''),
               ('Department+of+Mathematics', 'North Carolina U., Math. Dept.', 'MATHEMATICS', 'm'),
               ('Department+of+Computer+Science', 'UNC, Chapel Hill', 'COMPUTER', 'c')]
urltrunc = 'https://cdr.lib.unc.edu'
hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

prerecs = []
for (affurl, aff, affname, fc) in departments:
    tocurl = urltrunc + '/catalog?f[affiliation_label_sim][]=' + affurl + '&f[resource_type_sim][]=Dissertation&locale=en&per_page=' + str(rpp) + '&range[date_issued_isim][begin]=' + str(startyear) + '&range[date_issued_isim][end]=' + str(stopyear) + '&search_field=dummy_range&sort=date_issued_sort_dtsi+desc&view=list'
    ejlmod3.printprogress("=", [[affname], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for li in tocpage.body.find_all('li', attrs = {'class' : 'document'}):
        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : [], 'affiliation' : aff}
        for h4 in li.find_all('h3', attrs = {'class' : 'search-result-title'}):
            for a in h4.find_all('a'):
                rec['link'] = urltrunc + a['href']
                rec['tit'] = a.text.strip()
        if fc:
            rec['fc'] = fc
        for dd in li.find_all('dd'):
            ddt = dd.text.strip()
            if re.search('^[12]\d\d\d', ddt):
                rec['date'] = ddt
                rec['year'] = re.sub('.*(\d\d\d\d).*', r'\1', ddt)
        prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(10)

j = 0
recs = []
for rec in prerecs:
    j += 1
    ejlmod3.printprogress("-", [[j, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        req = urllib.request.Request(rec['link'])
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(7)
    except:
        print('wait 10 minutes')
        time.sleep(600)
        req = urllib.request.Request(rec['link'])
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_pdf_url', 'citation_title'])
    rec['autaff'][-1].append(rec['affiliation'])
    for dl in artpage.find_all('dl', attrs = {'class' : 'dissertation'}):
        for child in dl.children:
            try:
                dn = child.name
            except:
                dn = ''
                dt = ''
            if dn == 'dt':
                dt = child.text.strip()
            elif dn == 'dd':
                #abstract
                if dt == 'Abstract':
                    rec['abs'] = child.text.strip()
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
                elif dt == 'Keyword':
                    rec['keyw'] = []
                    for li in child.find_all('li'):
                        rec['keyw'].append(li.text.strip())
                #date
                elif dt == 'Date of publication':
                    rec['date'] = re.sub('.*([12]\d\d\d).*', r'\1', child.text.strip())
                #
                elif dt == '':
                    rec[''] = child.text.strip()

        
    #supervisor
    for dd in artpage.body.find_all('dd', attrs = {'class' : 'custom-dd-contributor'}):
        rec['supervisor'] = []
        for a in dd.find_all('a'):
            at = a.text.strip()
            if re.search('Supervisor', at):
                rec['supervisor'].append([re.sub(' *\(.*', '', at)])
    #abstract
    for dd in artpage.body.find_all('dd', attrs = {'class' : 'custom-dd-abstract'}):
        for div in dd.find_all('div', attrs = {'class' : 'panel'}):
            for h5 in div.find_all('h5'):
                if re.search('English', h5.text):
                    h5.replace_with('')
                    rec['abs'] = div.text.strip()
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        print('   already in backup')
    else:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
        
ejlmod3.writenewXML(recs, publisher, jnlfilename)
