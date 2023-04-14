# -*- coding: utf-8 -*-
#harvest theses from greek national archive of PhD theses
#FS: 2021-02-08
#FS: 2023-04-13

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json
import ssl

publisher = 'didaktorika.gr'
jnlfilename = 'THESES-DIDAKTORIKA-%s' % (ejlmod3.stampoftoday())

rpp = 50
pages = 2
skipalreadyharvested = True

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

for page in range(pages):
    tocurl = 'https://www.didaktorika.gr/eadd/browse?type=subject&value=Physical+Sciences&sort_by=2&order=DESC&rpp=' + str(rpp) + '&submit_browse=Update&locale=en&offset=' + str(page*rpp)
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    for tr in tocpage.body.find_all('tr'):
        if tr.find_all('th'):
            continue
        for td in tr.find_all('td', attrs = {'headers' : 't1'}):
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'note' : [], 'auts' : []}
            rec['year'] = td.text.strip()
            rec['date'] = td.text.strip()
            if int(rec['date']) > ejlmod3.year() - 2:
                for td2 in tr.find_all('td', attrs = {'headers' : 't2'}):
                    for a in td2.find_all('a'):
                        rec['artlink'] = 'https://www.didaktorika.gr' + a['href']
                    prerecs.append(rec)
    print('  %i records do far' % (len(prerecs)))
    time.sleep(10)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        req = urllib.request.Request(rec['artlink'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(3)
    except:
        try:
            print("   retry %s in 15 seconds" % (rec['artlink']))
            time.sleep(15)
            req = urllib.request.Request(rec['artlink'], headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        except:
            print("   no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DCTERMS.extent', 'DCTERMS.issued', 'DC.language',
                                        'citation_pdf_url', 'DC.identifier'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'DC.creator':
                if meta.has_attr('xml:lang'):
                    if meta['xml:lang'] in ['EN', 'en']:
                        rec['auten'] = meta['content']
                    elif meta['xml:lang'] in ['EL', 'el']:
                        rec['autel'] = meta['content']
                else:
                    rec['auts'] = [ meta['content'] ]
            #title
            elif meta['name'] == 'DC.title':
                rec['tit'] = meta['content']
                if meta.has_attr('xml:lang') and meta['xml:lang'] in ['EL', 'el']:
                    for meta2 in artpage.head.find_all('meta', attrs = {'name' : 'DCTERMS.alternative'}):
                        rec['transtit'] = meta2['content']
            #keywords
            elif meta['name'] == 'DC.subject':
                if meta.has_attr('xml:lang') and meta['xml:lang'] in ['EN', 'en']:
                    for keyw in re.split(' *; *', meta['content']):
                        rec['keyw'].append(keyw)
            #license
            elif meta['name'] == 'DC.relation':
                if re.search('^BY', meta['content']):
                    rec['license'] = {'statement' : 'CC-' + re.sub('_', '-', meta['content'])}
            #abstract
            elif meta['name'] == 'DCTERMS.abstract':
                if meta.has_attr('xml:lang'):
                    if meta['xml:lang'] in ['EN', 'en']:
                        rec['abs'] = meta['content']
                    elif meta['xml:lang'] in ['EL', 'el']:
                        rec['absel'] = meta['content']
            #handle
            elif meta['name'] == 'citation_abstract_html_url':
                if re.search('handle.net\/\d', meta['content']):
                    rec['hdl'] = re.sub('.*handle.net\/', '', meta['content'])
    #authors
    if 'auten' in list(rec.keys()):
        if 'autel' in list(rec.keys()):
            rec['auts'] = [ '%s, CHINESENAME: %s' %  (rec['auten'], rec['autel']) ]
        else:
            rec['auts'] = [ rec['auten'] ]
    elif 'autel' in list(rec.keys()):
        rec['auts'] = [ rec['autel'] ]
    #abstract
    if not 'abs' in list(rec.keys()) and 'absel' in list(rec.keys()):
        rec['abs'] = rec['absel']
    #pseudodoi
    if not 'hdl' in list(rec.keys()) and not 'doi' in list(rec.keys()):
        rec['doi'] = '20.2000/Didktorika/' + re.sub('\D', '', rec['artlink'])
        rec['link'] = rec['artlink']
    if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        print('  %s already in backup' % (rec['doi']))
    elif skipalreadyharvested and 'hdl' in rec and rec['hdl'] in alreadyharvested:
        print('  %s already in backup' % (rec['hdl']))
    else:        
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
