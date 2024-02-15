# -*- coding: utf-8 -*-
#harvest theses from UNAM, Mexico
#FS: 2024-02-07

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

startyear = str(ejlmod3.year(backwards=1+1))
pages = 2
rpp = 40
skipalreadyharvested = True

boring = ['Doctorado en Ciencias del Mar y Limnología',
          'Doctorado en Ciencias Biológicas',
          'Doctorado en Ciencias (Biología Marina)',
          'Doctorado en Ciencias Químicas',
          'Doctorado en Ciencias (Biología)']

publisher = 'UNAM, Mexico'
jnlfilename = 'THESES-UNAM-%s' % (ejlmod3.stampoftoday())
hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename, years=5)


prerecs = []
for page in range(pages):
    tocurl = 'https://ru.dgb.unam.mx/simple-search?query=&filter_field_1=department&filter_type_1=equals&filter_value_1=Facultad+de+Ciencias&filter_field_2=level&filter_type_2=equals&filter_value_2=Doctorado&sort_by=dc.date.issued_dt&order=desc&rpp=' + str(rpp) + '&etal=0&start=' + str(rpp*page)
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")

    for td in tocpage.body.find_all('td', attrs = {'headers' : 't2'}):
        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'supervisor' : [], 'note' : []}
        for a in td.find_all('a'):
            rec['link'] = 'https://ru.dgb.unam.mx' + a['href']
            rec['artlink'] = 'https://ru.dgb.unam.mx' + a['href'] + '?mode=full'
            rec['hdl'] = re.sub('.*handle\/', '', a['href'])
            if skipalreadyharvested and rec['hdl'] in alreadyharvested:
                print('   %s already in backup' % (rec['hdl']))
            elif ejlmod3.checkinterestingDOI(rec['hdl']):
                prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(5)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    keepit = True
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
    for tr in artpage.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldLabel'}):
            tdt = td.text.strip()
#        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldValue'}):
        for td in tr.find_all('td', attrs = {'headers' : 's2'}):
            #supervisor
            if tdt == 'dc.contributor.advisor':
                rec['supervisor'].append([td.text.strip()])
            #author
            elif tdt == 'dc.creator':
                rec['autaff'] = [[ td.text.strip() ]]
            #date
            elif tdt == 'dc.date.issued':
                rec['date'] = td.text.strip()
            #pages
            elif tdt == 'dc.format.extent':
                tdt = td.text.strip()
                if re.search('\d\d+ p.gin', tdt):
                    rec['pages'] = re.sub('.*?(\d\d+) p.*', r'\1', tdt)
            #language
            elif tdt == 'dc.language.iso':
                rec['language'] = td.text.strip()
            #license
            elif tdt == 'dc.rights.uri':
                tdt = td.text.strip()
                if re.search('creativecommons.org', tdt):
                    rec['license'] = {'url' : td.text.strip()}
            #title
            elif tdt == 'dc.title':
                rec['tit'] = td.text.strip()
            #abstract
            elif tdt == 'dc.abstract':
                rec['abs'] = td.text.strip()
            #degree
            elif tdt == 'dc.degree.name':
                tdt = td.text.strip()
                if tdt in ['Doctorado en Ciencias Matemáticas']:
                    rec['fc'] = 'm'
                elif tdt in ['Doctorado en Ciencias (Física)']:
                    rec['autaff'][-1].append('Mexico U.')
                elif tdt in ['Doctorado en Ciencias (Astronomía)']:
                    rec['fc'] = 'a'
                    rec['autaff'][-1].append('UNAM, Inst. Astron.')
                elif tdt in ['Doctorado en Ciencia e Ingeniería de la Computación']:
                    rec['fc'] = 'c'
                elif tdt in boring:
                    keepit = False
                else:
                    rec['note'].append('DEG:::' + tdt)
    if keepit:
        if len(rec['autaff'][0]) == 1:
            rec['autaff'][0].append(publisher)
        #fulltext
        for a in artpage.find_all('a'):
            if a.has_attr('href') and re.search('\.pdf$', a['href']):
                rec['pdf_url'] = 'https://ru.dgb.unam.mx' + a['href']
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
