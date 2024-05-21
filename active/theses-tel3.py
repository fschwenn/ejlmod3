# -*- coding: utf-8 -*-
#harvest theses from TEL
#FS: 2019-11-11
#FS: 2023-01-30

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

ejldir = '/afs/desy.de/user/l/library/dok/ejl'

rpp = 100
skipalreadyharvested = True

years = [ejlmod3.year(backwards=1), ejlmod3.year()]

#which domains (topics) should be checked
subdomains = [("phys.hexp", "e"), ("phys.nucl", "n"), ("phys.mphy", "m"), ("phys.nexp", "x"), ("phys.qphy", "k"),
              ("phys.hthe", "t"), ("phys.hphe", "p"), ("phys.grqc", "g"), ("phys.hlat", "l"),
              ("phys.phys.phys-ins-det", "i"), ("phys.phys.phys-comp-ph", "c"), ("phys.phys.phys-acc-ph", "b"),
              ("phys.cond.cm-sm", "f"), ("phys.cond.cm-msqhe", "f"), ("phys.cond.cm-sce", "f"),
              ("phys.astr.co", "a"), ("phys.astr.im", "ai"), ("phys.astr.he", "a"), ("phys.astr.ga", "a"),
              ("phys.phys.phys-atom-ph", "q"), ("phys.phys.phys-data-an", ""), ("phys.phys.phys-plasm-ph", ""),
              ("phys.phys", ""),
              ("math.math-ap", "m"), ("math.math-pr", "m"), ("math.math-ag", "m"), ("math.math-co", "m"),
              ("math.math-dg", "m"), ("math.math-nt", "m"), ("math.math-at", "m"), ("math.math-rt", "m"),
              ("math.math-ca", "m"), ("math.math-gt", "m"), ("math.math-oa", "m"), ("math.math-sg", "m"),
              ("math.math-qa", "m"), ("math.math-ra", "m"), ("math.math-ph", "m"),
              ("info.info-ni", "c"), ("info.info-se", "c"), ("info.info-dc", "c"), ("info.info-cv", "c"),
              ("info.info-lg", "c"), ("info.info-it", "c"), ("info.info-sc", "c"), ("info.info-ms", "c"),
              ("info.info-dl", "c"),
              ("stat.ml", "s"), ("stat.ap", "s"), ("stat.co", "s")]

domains = {}
for (subdom, fc) in subdomains:
    dom = re.sub('\..*', '', subdom)
    if dom in list(domains.keys()):
        domains[dom].append((subdom, fc))
    else:
        domains[dom] = [(subdom, fc)]

#avoid duplicates as some theses are in more than one domain
doiliste = {}

#check theses already done before
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested('THESES-TEL')

publisher = 'TEL'
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
for year in years:
    for dom in list(domains.keys()):
        ejlmod3.printprogress("=", [[year], [dom]])
        recs = []
        for (subdom, fc) in domains[dom]:
            tocurl = 'https://tel.archives-ouvertes.fr/search/index/?q=%2A&domain_t=' + subdom + '&producedDateY_i=' + str(year) + '&rows=' + str(rpp)
            ejlmod3.printprogress("=", [[year], [subdom], [tocurl]])
            try:
                req = urllib.request.Request(tocurl, headers=hdr)
                tocpages = [BeautifulSoup(urllib.request.urlopen(req), features="lxml")]
            except:
                print('  try again')
                time.sleep(30)
                req = urllib.request.Request(tocurl, headers=hdr)
                tocpages = [BeautifulSoup(urllib.request.urlopen(req), features="lxml")]
            time.sleep(5)
            for div in tocpages[0].body.find_all('div', attrs = {'class' : 'results-header'}):
                divt = re.sub('[\n\t\r]', '', div.text.strip())
                try:
                    results = int(re.sub('.*?(\d+)..?[rR]esult.*', r'\1', divt))
                    print('        expecting %i results' % (results))
                    for j in range((results-1) // rpp):
                        ptocurl = tocurl + '&page=' + str(j+2)
                        print('           ---{ %s : %s }---' % (subdom, ptocurl))
                        req = urllib.request.Request(ptocurl, headers=hdr)
                        tocpages.append(BeautifulSoup(urllib.request.urlopen(req), features="lxml"))
                        time.sleep(5)
                except:
                    print('        could not extract expected number of results')
            for tocpage in tocpages:
                divs = tocpage.body.find_all('td', attrs = {'class' : 'pl-4'})
                for div in divs:
                    for a in div.find_all('a'):
                        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'year' : str(year), 'keyw' : [],
                               'note' : [ subdom ], 'rn' : [], 'refs' : [], 'supervisor' : []}
                        rec['link'] = 'https://tel.archives-ouvertes.fr' + a['href']
                        if fc:
                            rec['fc'] = fc
                        rec['doi'] = re.sub('v\d+$', '', '20.2000/TEL' + a['href'])
                    if skipalreadyharvested and rec['doi'] in alreadyharvested:
                        print('           %s already in backup' % (rec['doi']))
                        pass
                    elif rec['doi'] in doiliste:
                        print('           %s already in list via %s' % (rec['doi'], doiliste[rec['doi']]))
                    else:
                        recs.append(rec)
                        doiliste[rec['doi']] = subdom
                print('      %3i theses in %s (%i in %s)' % (len(divs), subdom, len(recs), dom))
        j = 0
        for rec in recs:
            j += 1
            ejlmod3.printprogress("-", [[year], [dom], [j, len(recs)], [rec['link']]])
            try:
                req = urllib.request.Request(rec['link'])
                artpage = BeautifulSoup(urllib.request.urlopen(req),features="lxml" )
                time.sleep(5)
            except:
                print('wait 5 minutes')
                time.sleep(300)
                req = urllib.request.Request(rec['link'])
                artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
                time.sleep(10)
            ejlmod3.metatagcheck(rec, artpage, ['citation_language', 'citation_author', 'DC.issued',
                                                'citation_pdf_url', "citation_abstract",
                                                 "citation_title"])
            for meta in artpage.find_all('meta'):
                if meta.has_attr('name'):
                    #report number
                    if meta['name'] == 'DC.identifier':
                        if re.search('^tel', meta['content']):
                            rec['rn'].append(meta['content'])
                            rec['doi'] = '20.2000/TEL/' + meta['content']

                    #affiliation
                    elif meta['name'] == 'citation_author_institution':
                        rec['autaff'][-1].append(meta['content'] + ', France')
                    #keywords
                    elif meta['name'] == 'keywords':
                        rec['keyw'] += re.split(';', meta['content'])
            #French National Number (NNT) ?
            for div in artpage.body.find_all('div', attrs = {'id' : 'citation'}):
                for a in div.find_all('a'):
                    if a.has_attr('href'):
                        if re.search('www.theses.fr', a['href']):
                            rec['rn'].append(re.sub('.*\/', '', a['href']))
            ejlmod3.printrecsummary(rec)
        jnlfilename = 'THESES-TEL-%s_%s_%i' % (ejlmod3.stampoftoday(), dom, year)
        #closing of files and printing
        ejlmod3.writenewXML(recs, publisher, jnlfilename)
