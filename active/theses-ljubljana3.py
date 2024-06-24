# -*- coding: utf-8 -*-
#harvest theses from Ljubljana U.
#FS: 2022-02-09
#FS: 2023-01-06


import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time


publisher = 'Ljubljana U.'
jnlfilename = 'THESES-LJUBLJANA-%s' % (ejlmod3.stampoftoday())
rpp = 10

years = [ejlmod3.year(), ejlmod3.year(backwards=1)]

hdr = {'User-Agent' : 'Magic Browser'}
recs = []
for year in years:
    numberoftheses = 0
    tocurl = 'https://repozitorij.uni-lj.si/Iskanje.php?type=napredno&lang=eng&niz0=&stl0=Naslov&op1=AND&niz1=&stl1=Avtor&op2=AND&niz2=&stl2=Opis&op3=AND&niz3=' + str(year) + '&stl3=LetoIzida&vrsta=dok&jezik=0&vir=11'
    ejlmod3.printprogress("=", [[year], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpages = [BeautifulSoup(urllib.request.urlopen(req), features="lxml")]
    for div in tocpages[0].body.find_all('div', attrs = {'class' : 'Stat'}):
        numberoftheses = int(re.sub('\D', '', re.sub('.*\/', '', div.text.strip())))
        print('  %i theses expected' % (numberoftheses))
    for page in range((numberoftheses-1) // rpp):
        tocurlp = tocurl+'&page=' + str(page+2)
        print(tocurlp)
        req = urllib.request.Request(tocurlp, headers=hdr)
        tocpages.append(BeautifulSoup(urllib.request.urlopen(req), features="lxml"))
        time.sleep(3)
    for tocpage in tocpages:
        for table in tocpage.body.find_all('table', attrs = {'class' : 'ZadetkiIskanja'}):
            for a in table.find_all('a'):
                if a.has_attr('href') and re.search('IzpisGradiva.*id=\d', a['href']):
                    rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'autaff' : [], 'note' : [],
                           'year' : str(year), 'supervisor' : []}
                    rec['link'] = 'https://repozitorij.uni-lj.si/' + a['href']
                    rec['doi'] = '30.3000/Ljubljana/' + re.sub('\W', '', a['href'])
                    recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.contributor', 'DC.description',
                                        'DCTERMS.issued', 'citation_pdf_url', 'DC.language'])
    rec['autaff'][-1].append(publisher)
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #title
            if meta['name'] == 'DC.title':
                rec['tit'] = re.sub(': (doctoral thesis|doktorska disertacija|PhD thesis)$', '', meta['content'])
            #keywords
            elif meta['name'] == 'DC.subject':
                for keyw in re.split(', ', meta['content']):
                    rec['keyw'].append(keyw)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
