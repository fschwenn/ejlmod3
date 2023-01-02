# -*- coding: utf-8 -*-
#harvest theses from Siegen U.
#FS: 2020-02-14
#FS: 2022-12-21

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Siegen U.'
jnlfilename = 'THESES-SIEGEN-%s' % (ejlmod3.stampoftoday())

rpp = 50
pages = 1

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for i in range(pages):
    tocurl = 'https://dspace.ub.uni-siegen.de/handle/ubsi/8/browse?type=type&sort_by=2&order=DESC&rpp=' + str(rpp) + '&etal=-1&value=Doctoral+Thesis&offset=' + str(i*rpp)
    ejlmod3.printprogress('=', [[i+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for tr in tocpage.body.find_all('tr'):
        for td in tr.find_all('td', attrs = {'headers' : 't2'}):
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : [], 'keyw_de' : []}
            for a in td.find_all('a'):
                rec['link'] = 'https://dspace.ub.uni-siegen.de' + a['href'] #+ '?show=full'
                if ejlmod3.ckeckinterestingDOI(rec['link']):
                    prerecs.append(rec)
    time.sleep(15)

i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_title', 'DCTERMS.issued',
                                        'DC.identifier', 'DCTERMS.abstract', 'citation_pdf_url',
                                        'DC.rights'])
    rec['autaff'][-1].append(publisher)
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #thesis type
            if meta['name'] == 'DC.type':
                rec['note'].append(meta['content'])
            #keywords
            elif meta['name'] == 'DC.subject':
                if meta.has_attr('scheme') and meta['scheme'] == 'DCTERMS.DDC':
                    rec['ddc'] = re.sub('^.*?(\d\d\d).*', r'\1', meta['content'])
                else:
                    if meta.has_attr('xml:lang'):
                        if meta['xml:lang'] == 'de':
                            rec['keyw_de'].append(meta['content'])
                        else:
                            rec['keyw'].append(meta['content'])
    #german abstract?
    if not 'keyw' in list(rec.keys()) and 'keyw_de' in list(rec.keys()):
        rec['keyw'] = rec['keyw_de']
    #german kywords?
    if not 'abs' in list(rec.keys()) and 'abs_de' in list(rec.keys()):
        rec['abs'] = rec['abs_de']
    #pseudo DOI?
    if not 'urn' in list(rec.keys()):
        rec['doi'] = '20.2000/' + re.sub('\W', '', rec['link'])
    if 'ddc' in list(rec.keys()):
        if rec['ddc'][0] not in  ['5', '0']:
            print('  skip ddc=%s' % (rec['ddc']))
            keepit = False
        elif rec['ddc'] == '004':
            rec['fc'] = 'c'
        elif rec['ddc'] == '510':
            rec['fc'] = 'm'
        elif rec['ddc'] == '520':
            rec['fc'] = 'a'
        elif rec['ddc'] in ['540', '550', '560', '570', '580', '590', '020']:
            print('  skip ddc=%s' % (rec['ddc']))
            keepit = False
        elif rec['ddc'] != '530':
            rec['note'].append('DDC=%s' % (rec['ddc']))
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
