# -*- coding: utf-8 -*-
#harvest theses from Michigan
#FS: 2019-10-28
#FS: 2023-02-03

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Michigan U.'
numofpages = 10
rpp = 25
skipalreadyharvested = True
boringsubjects = ['Arts', 'Health Sciences', 'Humanities', 'Government Information and Law',
                  'College of Education, Health, & Human Services',
                  'Doctor of Nurse Anesthesia Practice',
                  'Industrial and Systems Engineering',
                  'Engineering', 'Business and Economics', 'Social Sciences', 'Education',
                  'School for Environment and Sustainability', 'Manufacturing Engineering',
                  'Business', 'Government  Politics and Law', 'Physical Therapy']
boringdegrees = ['MSE', 'MS', "Master's Thesis", 'Ed.D.', 'Doctor of Anesthesia Practice (DAP)']

jnlfilename = 'THESES-MICHIGAN-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
                    
hdr = {'User-Agent' : 'Magic Browser'}

allrecs = []
for i in range(numofpages):
    #tocurl = 'https://deepblue.lib.umich.edu/handle/2027.42/39366/recent-submissions?offset=%i' % (20*i)
    tocurl = 'https://deepblue.lib.umich.edu/handle/2027.42/39366/browse?order=DESC&rpp=' + str(rpp) + 'sort_by=3&etal=-1&offset=' + str(i*rpp) + '&type=dateissued'
    ejlmod3.printprogress("=", [[i+1, numofpages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(10)
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://deepblue.lib.umich.edu'):
        if skipalreadyharvested and rec['hdl'] in alreadyharvested:
            pass
        else:
            allrecs.append(rec)
    print('  %4i records so far' % (len(allrecs)))

j = 0
recs = []
for rec in allrecs:
    keepit = True
    restricted = False
    j += 1
    ejlmod3.printprogress("-", [[j, len(allrecs), [rec['link']]], [len(recs)]])
    try:
        req = urllib.request.Request(rec['link']+'?show=full')
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(20)
    except:
        print('wait 10 minutes')
        time.sleep(600)
        try:
            req = urllib.request.Request(rec['link']+'?show=full')
            artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
            time.sleep(30)
        except:
            continue
    tabelle = {}
    subject = ''
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DCTERMS.issued', 'DCTERMS.abstract'
                                        'DC.identifier', 'DC.subject'])
    for meta in artpage.find_all('meta', attrs = {'name' : 'citation_pdf_url'}):
        for dd in artpage.body.find_all('dd', attrs = {'class' : 'word-break'}):
            if re.search('Restricted', dd.text):
                restricted = True
            if not restricted:
                rec['hidden'] = meta['content']
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'ds-table-row'}):
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            label = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : ['data-cell', 'word-break']}):
            if label in list(tabelle.keys()):
                tabelle[label].append(td.text.strip())
            else:
                tabelle[label] = [ td.text.strip() ]
    #Department
    if 'dc.description.thesisdegreediscipline' in list(tabelle.keys()):
        subject = tabelle['dc.description.thesisdegreediscipline'][0]
    if 'dc.subject.hlbtoplevel' in list(tabelle.keys()):
        subject = tabelle['dc.subject.hlbtoplevel'][0]
    if subject:
        if subject in boringsubjects:
            print('   skip "%s"' % (subject))
            keepit = False
        else:
            rec['note'].append('SUBJECT=%s' % (subject))
    #PDF
    if 'dc.description.bitstreamurl' in list(tabelle.keys()):
        for dd in artpage.body.find_all('dd', attrs = {'class' : 'word-break'}):
            if re.search('Restricted', dd.text):
                restricted = True
        if not restricted:
            rec['hidden'] =  tabelle['dc.description.bitstreamurl'][0]
    #ORCID
    if 'dc.identifier.orcid' in list(tabelle.keys()):
        rec['autaff'][-1].append('ORCID:%s' % (re.sub('.*orcid.org.', '', tabelle['dc.identifier.orcid'][0])))
    rec['autaff'][-1].append(publisher)
    #Degree
    if not 'dc.description.thesisdegreename' in list(tabelle.keys()):
        if 'dc.description' in list(tabelle.keys()):
            for dd in  tabelle['dc.description']:
                if re.search('Master', dd):
                    tabelle['dc.description.thesisdegreename'] = [dd]
    if 'dc.description.thesisdegreename' in list(tabelle.keys()):
        if tabelle['dc.description.thesisdegreename'][0] in boringdegrees or re.search('Master', tabelle['dc.description.thesisdegreename'][0]):
            print('   skip "%s"' % (tabelle['dc.description.thesisdegreename'][0]))
            keepit = False
        elif tabelle['dc.description.thesisdegreename'][0] in ['Ph.D.', 'PHD', 'PhD']:
            pass
        else:
            rec['note'].append('DEGREE=%s' % (tabelle['dc.description.thesisdegreename'][0]))
    else:
        rec['note'] = ['NO DEGREE TYPE?!']
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
