# -*- coding: utf-8 -*-
#program to harvest theses from Karlsruhe Insitute of Technolgy ETP
# FS 2020-01-13
# FS 2023-04-28

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time 
import ssl

publisher = 'KIT'
jnlfilename = 'THESES-KIT_ETP-%s' % (ejlmod3.stampoftoday())

pages = 18
years = 2
skipalreadyharvested = True
#tocurl = 'https://publish.etp.kit.edu/search?page=1&size=20&q=resource_type.type:%20thesis&sort=-publication_date&subtype=phd-thesis'
tocurl = 'https://publish.etp.kit.edu/oai2d?verb=ListRecords&metadataPrefix=marcxml&from=%4d-01-01' % (ejlmod3.year(backwards=years))

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

records = []
cls = 999
for i in range(pages):
    if 100*i <= cls:
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        for record in tocpage.find_all('record'):
            for df in record.find_all('datafield', attrs = {'tag' : '980'}):
                for sf in df.find_all('subfield', attrs = {'code' : 'b'}):
                    if sf.text.strip() == 'phd-thesis':
                        records.append(record)
        ejlmod3.printprogress("=", [[i+1, pages], [tocurl], [len(records), cls]])
        cls = 1
        for rt in tocpage.find_all('resumptiontoken'):
            tocurl = 'https://publish.etp.kit.edu/oai2d?verb=ListRecords&resumptionToken=' + rt.text.strip()
            cls = int(rt['completelistsize'])
        time.sleep(1)

i = 0
recs = []
for record in records:
    i += 1 
    ejlmod3.printprogress("-", [[i, len(records)], [len(recs)]])
    rec = {'jnl' : 'BOOK', 'tc' : 'T', 'keyw' : []}
    isnew = False
    for cf in record.find_all('controlfield', attrs = {'tag' : '001'}):
        recordid = cf.text.strip()
        rec['link'] = 'https://publish.etp.kit.edu/record/' + recordid
        rec['doi'] = '20.2000/KIT_ETP/' + recordid
    #DOI
    for df in record.find_all('datafield', attrs = {'tag' : '024'}):
        for sf in df.find_all('subfield', attrs = {'code' : '2'}):
            doityp = sf.text.strip()
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            rec[doityp] = sf.text.strip()
    #pages
    for df in record.find_all('datafield', attrs = {'tag' : '773'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'g'}):
            if re.search('\d', sf.text):
                pages = int(re.sub('\D*(\d+).*', r'\1', sf.text))
                if 0 < pages < 500:
                    rec['pages'] = str(pages)
    #title
    for df in record.find_all('datafield', attrs = {'tag' : '245'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            rec['tit'] = sf.text.strip()
    #author
    for datafield in record.find_all('datafield', attrs = {'tag' : '100'}):
        for subfield in datafield.find_all('subfield', attrs = {'code' : 'a'}):
            rec['autaff'] = [[ subfield.text.strip() ]]
        for subfield in datafield.find_all('subfield', attrs = {'code' : 'u'}):
            rec['autaff'][0].append( subfield.text.strip() )
    #title
    for datafield in record.find_all('datafield', attrs = {'tag' : '245'}):
        for subfield in datafield.find_all('subfield', attrs = {'code' : 'a'}):
            rec['tit'] =  subfield.text.strip()  
    #reportnumber
    for datafield in record.find_all('datafield', attrs = {'tag' : '909'}):
        for subfield in datafield.find_all('subfield', attrs = {'code' : 'v'}):
            if 'rn' in rec:
                rec['rn'].append(re.sub(' ', '-', subfield.text.strip()))
            else:
                rec['rn'] = [ re.sub(' ', '-', subfield.text.strip()) ]
    #language
    for datafield in record.find_all('datafield', attrs = {'tag' : '041'}):
        for subfield in datafield.find_all('subfield', attrs = {'code' : 'a'}):
            if not subfield.text.strip() in ['eng', 'English']:
                rec['language'] = subfield.text.strip()
    #date
    for datafield in record.find_all('datafield', attrs = {'tag' : '260'}):
        for subfield in datafield.find_all('subfield', attrs = {'code' : 'c'}):
            rec['date'] = subfield.text.strip()
            year = int(re.sub('.*([12]\d\d\d).*', r'\1', rec['date']))
            if year > ejlmod3.year(backwards=years):
                isnew = True
    #abstract
    for datafield in record.find_all('datafield', attrs = {'tag' : '520'}):
        for subfield in datafield.find_all('subfield', attrs = {'code' : 'a'}):
            rec['abs'] = subfield.text.strip()
    #FFT
    for datafield in record.find_all('datafield', attrs = {'tag' : '542'}):
        for subfield in datafield.find_all('subfield', attrs = {'code' : 'l'}):
            if subfield.text.strip() == 'open':
                for df in record.find_all('datafield', attrs = {'tag' : '856'}):
                    for sf in df.find_all('subfield', attrs = {'code' : 'u'}):
                        url = subfield.text.strip()
                        if re.search('\.pdf$', url):
                            rec['FFT'] = url
    #hidden PDF
    if not 'FFT' in list(rec.keys()):
        for df in record.find_all('datafield', attrs = {'tag' : '856'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'u'}):
                url = subfield.text.strip()
                if re.search('\.pdf$', url):
                    rec['hidden'] = url
    #experiment
    for datafield in record.find_all('datafield', attrs = {'tag' : '980'}):
        for subfield in datafield.find_all('subfield', attrs = {'code' : 'a'}):
            exp = subfield.text.strip()
            if exp == 'user-cms':
                rec['exp'] = 'CERN-LHC-CMS'
            elif exp == 'user-belle':
                rec['exp'] = 'KEK-BF-BELLE-II'
            elif exp == 'user-katrin':
                rec['exp'] = 'KATRIN'
            elif exp == 'user-cdf':
                rec['exp'] = 'FNAL-E-0830'
            elif exp == 'user-delphi':
                rec['exp'] = 'CERN-LEP-DELPHI'    
    #check record page for more information
    if isnew:
        if not skipalreadyharvested or not 'doi' in rec or not rec['doi'] in alreadyharvested:
            print('  ->', rec['link'])
            req = urllib.request.Request(rec['link'], headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
            #keywords        
            for a in artpage.find_all('a', attrs = {'class' : 'label-link'}):
                for span in a.find_all('span'):
                    rec['keyw'].append(span.text.strip())
            #report number
#            for div in artpage.find_all('div', attrs = {'class' : 'metadata'}):
#                for dl in div.find_all('dl'):
            for dl in artpage.find_all('div', attrs = {'class' : 'metadata'}):
                    rncoming = False
                    for child in dl.children:
                        try:
                            child.text
                        except:
                            continue
                        if rncoming:
                            if 'rn' in rec:
                                rec['rn'].append(re.sub('[ \/]', '-', child.text.strip()))
                            else:
                                rec['rn'] = [re.sub('[ \/]', '-', child.text.strip())]
                            rncoming = False
                        if re.search('Report Number', child.text):
                            rncoming = True
            if not 'FFT' in rec and not 'hidden' in rec:
                for link in artpage.find_all('link', attrs = {'type' : 'application/pdf'}):
                    rec['hidden'] = link['href']
            time.sleep(10)        
    if isnew:
        if not rec in recs:
            if not skipalreadyharvested or not 'doi' in rec or not rec['doi'] in alreadyharvested:
                recs.append(rec)
                ejlmod3.printrecsummary(rec)
    else:
        print('     old thesis')
    
ejlmod3.writenewXML(recs, publisher, jnlfilename)
