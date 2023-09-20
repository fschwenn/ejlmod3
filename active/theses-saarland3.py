# -*- coding: utf-8 -*-
#harvest theses from Saarland U.
#FS: 2023-07-24

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Saarland U.'
jnlfilename = 'THESES-SAARLAND-%s' % (ejlmod3.stampoftoday())

rpp = 10
pages = 1
skipalreadyharvested = True
departments = [('NT+-+Physik', ''), ('MI+-+Mathematik', 'm'), ('MI+-+Informatik', 'c'), ('SE+-+Max-Planck-Institut+f%C3%BCr+Informatik', 'c')]
hdr = {'User-Agent' : 'Magic Browser'}
timespan = 2*100

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

j = 0
prerecs = []
recs = []
for (dep, fc) in departments:
    j += 1
    for page in range(pages):
        tocurl = 'https://publikationen.sulb.uni-saarland.de/handle/20.500.11880/3/simple-search?query=&filter_field_1=UBSTyp&filter_type_1=equals&filter_value_1=doctoralThesis&filter_field_2=Institut&filter_type_2=equals&filter_value_2=' + dep + '&sort_by=dc.date.issued_dt&order=desc&rpp=' + str(rpp) + '&etal=0&start=' + str(rpp*page)
        ejlmod3.printprogress("=", [[dep], [page+1 + (j-1)*pages, pages*len(departments)], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(6)
        for tr in tocpage.find_all('tr'):
            year = 9999
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : []}
            for td in tr.find_all('td', attrs = {'headers' : 't1'}):
                year = int(td.text.strip())
            if year >= ejlmod3.year(backwards=timespan):
                if fc:
                    rec['fc'] = fc
                for td in tr.find_all('td', attrs = {'headers' : 't2'}):
                    for a in td.find_all('a'):
                        if a.has_attr('href') and re.search('handle\/', a['href']):
                            rec['artlink'] = 'https://publikationen.sulb.uni-saarland.de' + a['href']  + '?mode=full&locale=en'
                            rec['hdl'] = re.sub('.*handle\/', '', a['href'])
                            prerecs.append(rec)
            else:
                print('   %i too old' % (year))
        print('\n  %4i records so far\n' % (len(prerecs)))

i = 0
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']))
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_languag', 
                                        'citation_date', 'citation_author',
                                        'DCTERMS.abstract', 'DC.identifier'])
    rec['autaff'][-1].append(publisher)
    #more metadata
    for table in artpage.body.find_all('table', attrs = {'class' : 'panel-body'}):
        for tr in table.find_all('tr'):
            for td in tr.find_all('td', attrs = {'class' : 'metadataFieldLabel'}):
                label = td.text.strip()
            for td in tr.find_all('td', attrs = {'class' : 'metadataFieldValue', 'headers' : 's2'}):
                #supervisor
                if label == 'dc.contributor.advisor':
                    if td.text.strip():
                        rec['supervisor'].append([re.sub('.*\((.*)\)', r'\1', td.text.strip())])
                #open access
                elif label == 'sulb.rights.access':
                    if td.text.strip() == 'openAccess':
                        ejlmod3.metatagcheck(rec, artpage, ['citation_pdf_url'])
    if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        print('   %s already in backup' % (rec['doi']))
    elif skipalreadyharvested and 'urn' in rec and rec['urn'] in alreadyharvested:
        print('   %s already in backup' % (rec['urn']))
    else:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
