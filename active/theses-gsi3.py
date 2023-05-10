# -*- coding: utf-8 -*-
#program to harvest theses from GSI
# FS 2020-07-08
# FS 2023-03-26

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time 

publisher = 'Darmstadt, GSI '
jnlfilename = 'THESES-GSI-%s' % (ejlmod3.stampoftoday())

skipalreadyharvested = True
uninteresting = ['Von Materie zu Materialien und Leben', 'Krebsforschung']


if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
    alreadyharvested += ejlmod3.getalreadyharvested('THESES-FRANKFURT') 
    alreadyharvested += ejlmod3.getalreadyharvested('THESES-HEIDELBERG')
    alreadyharvested += ejlmod3.getalreadyharvested('THESES-TUD')

recs = []
dois = []
for year in range(ejlmod3.year()-1, ejlmod3.year()+1):
    tocurl = 'https://repository.gsi.de/search?ln=de&cc=PhDThesis&p=260__c%3A' + str(year) + '&f=&action_search=Suchen&c=PhDThesis&c=&sf=&so=d&rm=&rg=200&sc=1&of=xm'
    time.sleep(2)
    ejlmod3.printprogress("=", [[year], [tocurl]])
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features='lxml')
    for record in tocpage.find_all('record'):
        rec = {'jnl' : 'BOOK', 'tc' : 'T', 'rn' : [], 'date' : str(year), 'year' : str(year),
               'oa' : False, 'note' : []}
        #record id
        for cf in record.find_all('controlfield', attrs = {'tag' : '001'}):
            recordid = cf.text.strip()
            ejlmod3.printprogress("-", [[recordid]])
        #reportnumber
        for df in record.find_all('datafield', attrs = {'tag' : '037'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
                rec['rn'].append(sf.text.strip())
        #language
        for df in record.find_all('datafield', attrs = {'tag' : '041'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
                if not sf.text.strip() in ['eng', 'English']:
                    rec['language'] = sf.text.strip()
        #author
        for df in record.find_all('datafield', attrs = {'tag' : '100'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
                rec['autaff'] = [[ sf.text.strip() ]]
        #affiliation
        for df in record.find_all('datafield', attrs = {'tag' : '502'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'c'}):
                rec['autaff'][0].append(sf.text.strip())
        #DOI
        for df in record.find_all('datafield', attrs = {'tag' : '024'}):
            for sf in df.find_all('subfield', attrs = {'code' : '2'}):                
                doityp = sf.text.strip().lower()
                if doityp == 'datacite_doi': doityp = 'doi'
            for sf in df.find_all('subfield', attrs = {'code' : 'a'}):                
                rec[doityp] = sf.text.strip()
        #title
        for df in record.find_all('datafield', attrs = {'tag' : '245'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
                rec['tit'] = sf.text.strip()
        #pages
        for df in record.find_all('datafield', attrs = {'tag' : '300'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
                if re.search('\d', sf.text):
                    pages = int(re.sub('\D*(\d+).*', r'\1', sf.text))
                    if 0 < pages < 500:
                        rec['pages'] = str(pages)
        #abstract
        for df in record.find_all('datafield', attrs = {'tag' : '520'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
                rec['abs'] = sf.text.strip()
        #open access
        for df in record.find_all('datafield', attrs = {'tag' : '915'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
                sft = sf.text.strip()
                if re.search('Creative Commons.*CC', sft):
                    rec['license'] = {'statement' : re.sub(' ', '-', re.sub('.*(CC.*)', r'\1', sft))}
                    rec['oa'] = True
                elif sft == 'OpenAccess':
                    rec['oa'] = True

        #comment
        for df in record.find_all('datafield', attrs = {'tag' : '500'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
                rec['note'].append(sf.text.strip())
        #fulltext
        for df in record.find_all('datafield', attrs = {'tag' : '856'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'u'}):
                url = sf.text.strip()
                if re.search('\.pdf$', url):
                    if rec['oa']:
                        rec['FFT'] = url
                    else:
                        rec['hidden'] = url
        #experiment
        for df in record.find_all('datafield', attrs = {'tag' : '920'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'l'}):
                exp = sf.text.strip()
                if exp in ['PANDA Detektoren', 'Collaboration FAIR: PANDA']:
                    rec['exp'] = 'GSI-FAIR-PANDA'
                elif exp in ['CBM', 'Collaboration FAIR: CBM']:
                    rec['exp'] = 'GSI-FAIR-CBM'
        #pseudo-DOI
        if not ('doi' in list(rec.keys()) or 'hdl' in list(rec.keys())):
            rec['link'] = 'https://repository.gsi.de/record/' + recordid
            if not 'urn' in list(rec.keys()):
                rec['doi'] = '20.2000/GSI/' + recordid
        #subject
        keepit = True
        for df in record.find_all('datafield', attrs = {'tag' : '913'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'l'}):
                subject = sf.text.strip()
                if subject in uninteresting:
                    print('   skip', subject)
                    keepit = False
                else:
                    rec['note'].append(subject)
        if keepit:
            if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
                pass
            elif skipalreadyharvested and 'urn' in rec and rec['urn'] in alreadyharvested:
                pass
            else:
                if 'doi' in rec and rec['doi'] in dois:
                    print('   already in list')
                else:
                    ejlmod3.printrecsummary(rec)
                    recs.append(rec)
                    if 'doi' in rec:
                        dois.append(rec['doi'])
    
ejlmod3.writenewXML(recs, publisher, jnlfilename)
