# -*- coding: utf-8 -*-
#harvest theses from Buenos Aires
#FS: 2022-05-16
#FS: 2023-04-29

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'U. Buenos Aires'
jnlfilename = 'THESES-BuenosAiresU-%s' % (ejlmod3.stampoftoday())

years = 2
skipalreadyharvested = True

hdr = {'User-Agent' : 'Magic Browser'}
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
artlinks = []
for (fc, dep, aff) in [('c', '5', 'U. Buenos Aires'), ('m', '11', 'U. Buenos Aires'), ('', '8', 'Buenos Aires U.')]:
    starturl = 'https://bibliotecadigital.exactas.uba.ar/collection/tesis/browse/CL5/' + dep
    ejlmod3.printprogress("=", [[starturl]])
    req = urllib.request.Request(starturl, headers=hdr)
    startpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for div in startpage.body.find_all('div', attrs = {'class' : 'flex-row'}):
        for span in div.find_all('span'):
            spant = span.text.strip()
            if re.search('^\d+$', spant):
                if int(spant) > ejlmod3.year() - years:
                    for a in div.find_all('a'):
                        tocurl = 'https://bibliotecadigital.exactas.uba.ar' + a['href']
                        print(' =={ %s }==={ %s }===' % (spant, tocurl))
                        req = urllib.request.Request(tocurl, headers=hdr)
                        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
                        for div2 in tocpage.body.find_all('div', attrs = {'class' : 'childrenlist'}):
                            for a2 in div2.find_all('a')[1:]:
                                rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'note' : [], 'supervisor' : []}
                                rec['link'] = 'https://bibliotecadigital.exactas.uba.ar' + a2['href']
                                rec['affiliation'] = aff
                                rec['date'] = spant
                                if fc: rec['fc'] = fc
                                if not rec['link'] in artlinks:
                                    prerecs.append(rec)
                                    artlinks.append(rec['link'])
                        time.sleep(10)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']))
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_language',
                                        'citation_keywords', 'citation_pdf_url',
                                        'DC.rights'])
    rec['autaff'][-1].append(rec['affiliation'])
    for meta in artpage.head.find_all('meta'):
            if meta.has_attr('name'):
                #title
                if meta['name'] == 'citation_title':
                    if meta.has_attr('lang'):
                        if meta['lang'] == 'en':
                            rec['titen'] = meta['content']
                        elif meta['lang'] == 'es':
                            rec['tites'] = meta['content']
                        else:
                            rec['tit'] = meta['content']
                #abstract
                elif meta['name'] == 'citation_abstract':
                    if meta.has_attr('lang' ):
                        if meta['lang'] == 'es':
                            rec['abses'] = meta['content']
                        else:
                            rec['abs'] = meta['content']
                    else:
                        if re.search(' the ', meta['content']):
                            rec['abs'] = meta['content']
                        else:
                            rec['abses'] = meta['content']
    for table in artpage.find_all('table'):
        profdict = {}
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) == 2:
                tht = tds[0].text.strip()
                #supervisor
                if tht in ['Director:']:
                    rec['supervisor'].append([tds[1].text.strip()])
                #handle
                elif tht == 'Handle:':
                    rec['hdl'] = re.sub('.*ndle.net\/', '', tds[1].text.strip())
    #title
    if 'language' in list(rec.keys()):
        if 'tites' in list(rec.keys()):
            rec['tit'] = rec['tites']
            if 'titen' in list(rec.keys()):
                rec['transtit'] = rec['titen']
        elif 'titen' in list(rec.keys()):
            rec['tit'] = rec['titen']
    else:
        if 'titen' in list(rec.keys()):
            rec['tit'] = rec['titen']
            if 'tites' in list(rec.keys()):
                rec['transtit'] = rec['tites']            
    #abstract
    if not 'abs' in list(rec.keys()) and 'abses' in list(rec.keys()):
        rec['abs'] = rec['abses']
    if not 'hdl' in list(rec.keys()):
        rec['doi'] = '20.2000/BuenosAires/' + re.sub('.*\/', '', rec['link'])
    if skipalreadyharvested and 'hdl' in rec and rec['hdl'] in alreadyharvested:
        print('  %s already in backup' % (rec['hdl']))
    elif skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        print('  %s already in backup' % (rec['doi']))
    else:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
