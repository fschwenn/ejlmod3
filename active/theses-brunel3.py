# -*- coding: utf-8 -*-
#harvest theses from Brunel U.
#FS: 2021-01-27
#FS: 2023-03-26

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Brunel U.'
jnlfilename = 'THESES-BRUNEL-%s' % (ejlmod3.stampoftoday())

rpp = 50
pages = 1
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
#for dep in ['8623', '8629']:
for dep in ['8623', '8638', '8629']:
    for j in range(pages):
        tocurl = 'https://bura.brunel.ac.uk/handle/2438/' + dep +'/browse?rpp=' + str(rpp) + '&sort_by=2&type=dateissued&offset=' + str(j*rpp) + '&etal=-1&order=DESC'
        ejlmod3.printprogress("=", [[dep], [j+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
        for tr in tocpage.body.find_all('tr'):
            for td in tr.find_all('td', attrs = {'headers' : 't2'}):
                rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'autaff' : [], 'note' : []}
                for a in td.find_all('a'):
                    rec['link'] = 'https://bura.brunel.ac.uk' + a['href'] #+ '?show=full'
                    rec['doi'] = '20.2000/BRUNEL' + a['href']
                    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                        if ejlmod3.checkinterestingDOI(rec['link']):
                            if dep == '8638':
                                rec['fc'] = 'c'
                            elif dep == '8629':
                                rec['fc'] = 'm'
                            prerecs.append(rec)
        print('  %4i records so far' % (len(prerecs)))
    time.sleep(10)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
        except:
            print("no access to %s" % (rec['link']))
            continue
    #check whether really thesis
    
    ejlmod3.metatagcheck(rec, artpage, ['DC.description', 'DC.title', 'DCTERMS.issued',
                                        'DC.subject', 'DCTERMS.abstract', 'citation_pdf_url'])
    for meta in artpage.head.find_all('meta', attrs = {'name' :  'DC.creator'}):
                if re.search('\d\d\d\d\-\d\d\d\d',  meta['content']):
                    rec['autaff'][-1].append('ORCID:' + meta['content'])
                else:
                    author = re.sub(' *\[.*', '', meta['content'])
                    rec['autaff'].append([ author ])
    if len(rec['autaff']) == 1:
        rec['autaff'][-1].append(publisher)
        #license
        for a in artpage.find_all('a'):
            if a.has_attr('href') and re.search('creativecommons.org', a['href']):
                rec['license'] = {'url' : a['href']}
                if 'pdf_url' in list(rec.keys()):
                    rec['FFT'] = rec['pdf_url']
                else:
                    for div in artpage.find_all('div'):
                        for a2 in div.find_all('a'):
                            if a2.has_attr('href') and re.search('bistream.*\.pdf', a['href']):
                                divt = div.text.strip()
                                if re.search('Restricted', divt):
                                    print(divt)
                                else:
                                    rec['FFT'] = 'https://bura.brunel.ac.uk' + re.sub('\?.*', '', a['href'])

        if 'note' in rec.keys() and rec['note'] and not re.search('[th]hesis', rec['note'][0]):
            print(' skip "%a"' % (rec['note'][0]))
            ejlmod3.adduninterestingDOI(rec['link'])
        else:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
