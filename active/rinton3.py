# -*- coding: UTF-8 -*-
#program to harvest Quantum Information and Computation
# FS 2023-09-12

import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time

publisher = 'Rinton Press'
years = 1+4+2+4
skipalreadyharvested = True

jnl = sys.argv[1]

if jnl == 'qic':
    jnlname = 'Quant.Inf.Comput.'

jnlfilename = 'rinton%s-%s' % (jnl, ejlmod3.stampoftoday())

tocurl = 'https://www.rintonpress.com/journals/%sonline.html' % (jnl)

hdr = {'User-Agent' : 'Magic Browser'}
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
    alreadyharvested.append('10.26421/QIC16.13-14-4')
    
print(tocurl)
req = urllib.request.Request(tocurl, headers=hdr)
tocpage = BeautifulSoup(urllib.request.urlopen(req),features="lxml" )
for table in tocpage.find_all('table', attrs = {'border' : '1'}):
    table.decompose()
recs = []
for tr in tocpage.find_all('tr'):
    subtrs = tr.find_all('tr')
    if subtrs: continue
    trt = re.sub('[\n\t\r]', '', tr.text)
    if re.search('2[01]\d\d', trt):
        year = re.sub('.*?(2[01]\d\d)\D.*', r'\1', trt)
        vol = re.sub('.*?Vol\. *(\d+).*', r'\1', trt)
        if re.search('.*?Vol\. *\d.*?No. *\d', trt):
            iss = re.sub('.*?Vol\. *\d.*?No. *(\d.*?) .*', r'\1', trt)
            iss = re.sub('\D+', '-', iss)
        else:
            iss = False
        if int(year) > ejlmod3.year(backwards=years):
            print(year, vol, iss)
            for a in tr.find_all('a'):
                if a.has_attr('href') and re.search('doi.org', a['href']):
                    rec = {'tc' : 'P', 'jnl' : jnlname, 'vol' : vol, 'year' : year}
                    if iss:
                        rec['issue'] = iss
                        rec['artlink'] = a['href']
                        rec['doi'] = re.sub('.*org\/', '', a['href'])
                        if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                            recs.append(rec)
                            alreadyharvested.append(rec['doi'])

for (i, rec) in enumerate(recs):
    ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['artlink']]])
    time.sleep(3)
    req = urllib.request.Request(rec['artlink'], headers=hdr)
    artpage = BeautifulSoup(urllib.request.urlopen(req),features="lxml")
    #tile and PDF
    for a in artpage.find_all('a'):
        if a.has_attr('href') and len(a.text.strip()) > 5:
            if re.search('pdf$', a['href']):
                rec['hidden'] = a['href']
                rec['tit'] = re.sub('[\n\t\r\xa0]', ' ', a.text.strip())
                a.replace_with('TIT_TIT')
            elif re.search('doi.org', a['href']):
                a.replace_with('DOI_DOI')
    #structuring text
    for font in artpage.find_all('font'):
        fts = font.text.strip() 
        if re.search('^Abstracts?:$', fts):
            font.replace_with('ABS_ABS')
        elif re.search('^Key ?[wW]ords?:', fts):
            font.replace_with('KEY_KEY')
             
    for table in artpage.find_all('table'):        
        tts = table.text.strip()
        if re.search('TIT_TIT', tts) and not 'auts' in rec:
            print(len(tts))
            tts = re.sub('[\n\t\r\xa0]', ' ', tts)
            tts = re.sub('.nbsp;', ' ', tts)
            tts = re.sub('  +', ' ', tts)
            tts = re.sub('.*TIT_TIT *', '', tts)
            tts = re.sub('\`{c}', 'ć', tts)
            #keywords
            keywords = re.sub('.*KEY_KEY *', '', re.sub(' ˇˇ', '', tts))
            rec['keyw'] = re.split(', ', keywords)
            tts = re.sub(' *KEY_KEY.*', '', tts)
            #abstract
            rec['abs'] = re.sub('.*ABS_ABS *', '', tts)
            tts =  re.sub(' *ABS_ABS.*', '', tts)
            #pages
            if re.search('^\(pp\d+\-\d+\)', tts):
                rec['p1'] = re.sub('^.pp(\d+).*', r'\1', tts)
                rec['p2'] = re.sub('^.pp\d+\-(\d+).*', r'\1', tts)
                tts = re.sub('^\(pp\d+\-\d+\) *', '', tts)
            tts = re.sub(',? and ', ', ', tts)
            tts = re.sub(' *doi.* *DOI_DOI.*', '', tts).strip()
            #authors
            rec['auts'] = re.split(', ', tts)
#    ejlmod3.printrec(rec)
    ejlmod3.printrecsummary(rec)
    
ejlmod3.writenewXML(recs, publisher, jnlfilename)

