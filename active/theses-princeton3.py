# -*- coding: utf-8 -*-
#harvest theses from University of Princeton
#FS: 2019-09-25
#FS: 2022-12-20

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Princeton U.'
pages = 1

sections = [('dsp01t722h882n', 'Physics'),
            ('dsp015m60qr913', 'Astrophysics'),
            ('dsp01pg15bd903', 'Plasma'),
            ('dsp018c97kq43p', 'ComputerScience'),
            ('dsp01v692t6222', 'Mathematics')]
sections = [('dsp018c97kq43p', 'ComputerScience')]
hdr = {'User-Agent' : 'Magic Browser'}
for section in sections:
    jnlfilename = 'THESES-PRINCETON-%s-%s' % (ejlmod3.stampoftoday(), section[1])    
    recs = []
    for page in range(pages):
        tocurl = 'https://dataspace.princeton.edu/jspui/handle/88435/' + section[0] + '?offset=' + str(20*page)
        ejlmod3.printprogress('=', [[section[1]], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(3)
        for tr in tocpage.body.find_all('tr'):
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : []}
            for a in tr.find_all('a'):
                if re.search('handle\/88435', a['href']):
                    rec['artlink'] = 'https://dataspace.princeton.edu' + a['href'] #+ '?show=full'
                    #it's not a registered handle
                    #rec['hdl'] = re.sub('.*handle\/', '', a['href'])
                    rec['doi'] = '20.2000/PRINCETON/' + re.sub('.*handle\/', '', a['href'])
                    if section == 'Astrophysics':
                        rec['fc'] = 'a'
                    elif section == 'Mathematics':
                        rec['fc'] = 'm'
                    elif section == 'Computer Science':
                        rec['fc'] = 'c'
                    recs.append(rec)
    i = 0
    for rec in recs:
        rec['link'] = rec['artlink']
        i += 1
        ejlmod3.printprogress('-', [[section[1]], [i, len(recs)], [rec['artlink']]])
        try:
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
            time.sleep(3)
        except:
            try:
                print("retry %s in 180 seconds" % (rec['artlink']))
                time.sleep(180)
                artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
            except:
                print("no access to %s" % (rec['artlink']))
                continue    
        ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'DC.subject',
                                            'DCTERMS.abstract', 'citation_pdf_url'])
        for meta in artpage.head.find_all('meta'):
            if meta.has_attr('name'):
                #author
                if meta['name'] == 'DC.contributor.author':
                    author = re.sub(' *\[.*', '', meta['content'])
                    rec['autaff'] = [[ author ]]
                    rec['autaff'][-1].append(publisher)
        #supervisor
        for tr in artpage.body.find_all('tr', attrs = {'class' : 'dc-contributor-advisor'}):
            for td in tr.find_all('td',  attrs = {'class' : 'metadataFieldValue'}):
                for a in td.find_all('a'):
                    rec['supervisor'].append([a.text.strip()])
        ejlmod3.printrecsummary(rec)
    
    ejlmod3.writenewXML(recs, publisher, jnlfilename)
