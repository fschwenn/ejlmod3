# -*- coding: utf-8 -*-
#harvest theses from Hamburg
#FS: 2020-01-27
#FS: 2023-03-19

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'U. Hamburg (main)'
jnlfilename = 'THESES-HAMBURG-%s' % (ejlmod3.stampoftoday())

pages = 2
pagesmultiplier = 10
skipalreadyharvested = True
rpp = 50 
years = 2

hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
recs = []
artlinks = []
#for fac in ['510+Mathematik', '530+Physik', '004+Informatik']:
for (fac, fc) in [('510%3A+Mathematik', 'm'),
                  ('CMS-Detektor', 'e'), ('ATLAS', 'e'), ('LHC', 'e'),
                  ('39.22%3A+Astrophysik', 'a'),
                  ('33.24%3A+Quantenfeldtheorie', 't'),
                  ('33.23%3A+Quantenphysik', 'k'),
                  ('33.61%3A+Festk%C4%B6rperphysik', 'f'),
                  ('530%3A+Physik', ''),
                  ('004%3A+Informatik', 'c')]:
    #ejlmod3.printprogress("=", [[fac]])
    for page in range(pages):
        tocurl = 'https://ediss.sub.uni-hamburg.de/simple-search?query=&location=&filter_field_1=dateIssued&filter_type_1=equals&filter_value_1=%5B' + str(ejlmod3.year(backwards=years)+1) + '+TO+' + str(ejlmod3.year()) + '%5D&filter_field_2=subject&filter_type_2=equals&filter_value_2=' + fac + '&relationName=&sort_by=dc.date.issued_dt&order=desc&rpp=' + str(rpp) + '&etal=0&start=' + str(page*rpp)
        
        ejlmod3.printprogress("=", [[fac], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
        for tr in tocpage.body.find_all('tr'):
            for td in tr.find_all('td', attrs = {'headers' : 't1'}):
                rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : []}
                if fc:
                    rec['fc'] = fc
                for a in td.find_all('a'):
                    rec['artlink'] = 'https://ediss.sub.uni-hamburg.de' + a['href']
                    if ejlmod3.checknewenoughDOI(rec['artlink']) and not rec['artlink'] in artlinks:
                        prerecs.append(rec)
                        artlinks.append(rec['artlink'])
        print('  %4i records so far' % (len(prerecs)))
        time.sleep(1)
    time.sleep(5)



#stopped DDC :-(
#for page in range(pages*pagesmultiplier):
#    time.sleep(3)
#    tocurl = 'https://ediss.sub.uni-hamburg.de/handle/ediss/2?sort_by=2&order=DESC&rpp=' + str(rpp) + '&offset=' + str(page*rpp)
#    ejlmod3.printprogress("=", [['all'], [page+1, pages*pagesmultiplier], [tocurl]])
#    req = urllib.request.Request(tocurl, headers=hdr)
#    tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
#    for tr in tocpage.body.find_all('tr'):
#        for td in tr.find_all('td', attrs = {'headers' : 't1'}):
#            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : []}
#            for a in td.find_all('a'):
#                rec['artlink'] = 'https://ediss.sub.uni-hamburg.de' + a['href']
#                if ejlmod3.checknewenoughDOI(rec['artlink']) and not rec['artlink'] in artlinks:
#                    if ejlmod3.checkinterestingDOI(rec['artlink']):
#                        prerecs.append(rec)
#                        artlinks.append(rec['artlink'])
#    print('  %4i records so far' % (len(prerecs)))
    
    

for (i, rec) in enumerate(prerecs):
    keepit = True
    ejlmod3.printprogress("-", [[i+1, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features='lxml')
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features='lxml')
        except:
            print("no access to %s" % (rec['artlink']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'DCTERMS.abstract', 'citation_title',
                                        'DCTERMS.issued', 'DC.subject', 'language',
                                        'DC.Identifier', 'DC.identifier', 'citation_pdf_url',
                                        'DC.contributor'])
    #DDC
    for meta in artpage.find_all('meta', attrs = {'scheme' : 'DCTERMS.DDC'}):
        if meta.has_attr('content'):
            #print(meta['content'], meta['content'][:3], meta['content'][0])
            if meta['content'][:3] == '004':
                rec['fc'] = 'c'
            elif meta['content'][:3] == '510':
                rec['fc'] = 'm'
            elif meta['content'][0] in ['1', '2', '3', '4', '6', '7', '8', '9']:
                keepit = False
                print('   skip "%s"' % (meta['content']))
            elif meta['content'][1] in ['5', '6', '7', '8', '9'] or meta['content'][:3] == '020':
                keepit = False
                print('   skip "%s"' % (meta['content']))
            else:
                rec['note'].append('DDC:::' + meta['content'])
    ejlmod3.globallicensesearch(rec, artpage)
    rec['autaff'][-1].append(publisher)

# invalid HTML: <td class="metadataFieldLabel">Betreuer*in:&nbsp;</td><td class="metadataFieldValue">Parak,&#x20;Wolfgang<br />Torres,&#x20;Neus</td></tr>
    
 #        for meta in artpage.head.find_all('meta'):
#            if meta.has_attr('name'):#
                #supervisor
#                elif meta['name'] == 'DC.contributor':
#                    rec['supervisor'].append([re.sub(' *\(.*', '', meta['content'])])
    if keepit:
        if skipalreadyharvested and 'urn' in rec and rec['urn'] in alreadyharvested:
            print('    already in backup')
        elif 'date' in rec and int(re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])) <= ejlmod3.year(backwards=years):
            print('    too old')
            ejlmod3.addtoooldDOI(rec['artlink'])
        else:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
