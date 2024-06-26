# -*- coding: utf-8 -*-
#harvest theses from Louvain 
#FS: 2020-08-26
#FS: 2023-03-26

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl


skipalreadyharvested = True

publisher = 'Louvain U.'
jnlfilename = 'THESES-LOUVAIN-%s' % (ejlmod3.stampoftoday())
                                                        
boringdeps = ['SSH/IACS', 'SSH/ILC', 'SSH/ILC/PCOM', 'SSH/ILC/PLIN', 'SSH/INCA',
              'SSH/IPSY', 'SSH/JURI', 'SSH/JURI/PJPR', 'SSH/JURI/PJPU',
              'SSH/LIDAM/CORE', 'SSH/LIDAM/IRES', 'SSH/LouRIM', 'SSH/RSCS',
              'SSH/SPLE', 'SSS/DDUV/CELL', 'SSS/DDUV', 'SSS/DDUV/LPAD',
              'SSS/DDUV/SIGN', 'SSS/IONS/CEMO', 'SSS/IONS/COSY', 'SSS/IONS',
              'SSS/IREC/EPID', 'SSS/IREC/FATH', 'SSS/IREC/GAEN', 'SSS/IREC/GYNE',
              'SSS/IREC/IMAG', 'SSS/IREC', 'SSS/IREC/LTAP', 'SSS/IREC/MIRO',
              'SSS/IRSS', 'SSS/LDRI', 'SST/ELI', 'SST/ELI/ELIA', 'SST/ELI/ELIB',
              'SST/ELI/ELIC', 'SST/ELI/ELIE', 'SST/IMCN/MODL', 'SST/IMMC/IMAP',
              'SST/LIBST']
boringdeps += ["SSH/IRIS-L/CERE", "SSH/IRIS-L/CRSP", "SSH/IRIS-L/IEE",
               "SSH/IRIS-L/SIEJ", "SSH/ISP", "SSH/JURI/PJIE", "SSH/JURI/PJPC",
               "SSH/LIDAM/ISBA", "SSH/LIDAM/LFIN", "SSH/LIDAM", "SSS/DDUV/BCHM",
               "SSS/DDUV/CBIO", "SSS/DDUV/GECE", "SSS/DDUV/GEHU", "SSS/DDUV/MEXP",
               "SSS/DDUV/PHOS", "SSS/IONS/NEUR", "SSS/IREC/CARD", "SSS/IREC/EDIN",
               "SSS/IREC/LUNS", "SSS/IREC/MEDA", "SSS/IREC/MORF", "SSS/IREC/NMSK",
               "SSS/IREC/PEDI", "SSS/IREC/REPR", "SST/ELI/ELIM", "SST/IMCN/BSMA",
               "SST/IMCN/MOST", "SST/IMMC/GCE", "SST/IMMC", "SST/LAB"]

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)


#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for year in [ejlmod3.year(), ejlmod3.year(backwards=1)]:
    tocurl = 'https://dial.uclouvain.be/pr/boreal/en/search/site/%2A%3A%2A?page=1&f%5B0%5D=sm_type%3ATh%C3%A8se%20%28Dissertation%29&f%5B1%5D=sm_date%3A' + str(year) + '&solrsort=ss_date%20desc'
    ejlmod3.printprogress("=", [[year], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpages = [BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")]
    numofpages = 0
    for div in tocpages[0].body.find_all('div', attrs = {'class' : 'result-label'}):
        numofrecs = int(re.sub('.*of *(\d+).*', r'\1', div.text.strip()))
        numofpages = (numofrecs-1) // 25 + 1
    for page in range(numofpages-1):
        tocurl = 'https://dial.uclouvain.be/pr/boreal/en/search/site/%2A%3A%2A?page=' + str(page+2) + '&f%5B0%5D=sm_type%3ATh%C3%A8se%20%28Dissertation%29&f%5B1%5D=sm_date%3A' + str(year) + '&solrsort=ss_date%20desc'
        ejlmod3.printprogress("=", [[year], [page+2, numofpages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpages.append(BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml"))
        time.sleep(5)
    for tocpage in tocpages:
        for div in tocpage.body.find_all('div', attrs = {'class' : 'publication'}):
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'year' : str(year), 'date' : str(year), 'note' : [],
                   'oa' : False, 'ftispdf' : False, 'supervisor' : [], 'keyw' : []}
            for a in div.find_all('a', attrs = {'class' : 'cart_update'}):
                rec['link'] = re.sub('.*A', 'https://dial.uclouvain.be/pr/boreal/object/boreal:', a['href'])
            for span in div.find_all('span', attrs = {'class' : 'title'}):
                for a in span.find_all('a'):
                    rec['hdl'] = re.sub('.*net\/', '', a['href'])
                    rec['tit'] = a.text.strip()
                    if ejlmod3.checkinterestingDOI(rec['hdl']):
                        if not skipalreadyharvested or not rec['hdl'] in alreadyharvested:
                            prerecs.append(rec)
        print('  %4i records so far' % (len(prerecs)))

    i = 0
    recs = []
    for rec in prerecs:
        keepit = True
        i += 1
        ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
        try:
            req = urllib.request.Request(rec['link'], headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
            time.sleep(4)
        except:
            try:
                print("retry %s in 180 seconds" % (rec['link']))
                time.sleep(180)
                artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
            except:
                print("no access to %s" % (rec['link']))
                continue    
        #author
        for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_author'}):
            rec['autaff'] = [[ meta['content'], publisher ]]
        #fulltext
        for div in artpage.body.find_all('div', attrs = {'class' : 'datastream-small'}):
            for li in div.find_all('li'):
                if re.search('Open access', li.text):
                    rec['oa'] = True
                elif re.search('PDF', li.text):
                    rec['ftispdf'] = True
            if rec['oa'] and rec['ftispdf']:
                for a in div.find_all('a'):
                    rec['FFT'] = a['href']
        #abstract
        for p in artpage.body.find_all('p', attrs = {'class' : 'publication-metadata'}):
            rec['abs'] = p.text.strip()
        for table in artpage.body.find_all('table', attrs = {'class' : 'publication-metadata'}):
            for tr in table.find_all('tr'):
                for th in tr.find_all('th'):
                    tht = th.text.strip()
                for td in tr.find_all('td'):
                    #language
                    if tht == 'Language':
                        if td.text.strip()[:3] == 'Fra':
                            rec['language'] = 'French'
                    #supervisor
                    elif tht == 'Promotors':
                        for sv in re.split(' *\| *', td.text.strip()):
                            rec['supervisor'].append([sv])
                    #keywords
                    elif tht == 'Keywords':
                        for a in td.find_all('a'):
                            rec['keyw'].append(a.text.strip())
                    #Department
                    elif tht == 'Affiliations':
                        for a in td.find_all('a'):
                            if re.search('^[A-Z][A-Z]', a.text):
                                dep = re.sub(' .*', '', a.text.strip())
                                if dep in ['SST/IMCN']:
                                    rec['fc'] = 'f'
                                elif dep in boringdeps:
                                    try:
                                        print('  skip "%s"' % (a.text.strip()))
                                    except:
                                        print('  skip "%s"' % (dep))
                                    keepit = False
                                else:
                                    rec['note'].append(a.text.strip())
        if keepit:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
        else:
            ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
