# -*- coding: utf-8 -*-
#harvest theses from Wien
#FS: 2020-10-31
#FS: 2022-11-03
import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import codecs
import datetime
import time
import json

jnlfilename = 'THESES-TUWIEN-%s' % (ejlmod3.stampoftoday())

publisher = 'Vienna, Tech. U.'

hdr = {'User-Agent' : 'Magic Browser'}

rpp = 20
pages = 20
boringinstitutes = ['E360', 'E017', 'E017', 'E105', 'E120', 'E163', 'E164', 'E165',
                    'E186', 'E187', 'E188', 'E194', 'E259', 'E311', 'E315', 'E322',
                    'E330', 'E317', 'E166', 'E253', 'E192', 'E193', 'E280', 'E251',
                    'E253', 'E259', 'E260', 'E264', 'E280', 'E285', 'E299', 'E202',
                    'E204', 'E206', 'E207', 'E208', 'E212', 'E220', 'E222', 'E226',
                    'E230', 'E234', 'E249', 'E352', 'E353', 'E354', 'E355', 'E222',
                    'E360', 'E362', 'E370', 'E371', 'E372', 'E373', 'E376',
                    'E384', 'E388', 'E399', 'E235', 'E210', 
                    'E120', 'E122', 'E127', 'E128', 'E129', 'E153', 'E163', 'E164',
                    'E165', 'E166', 'E174', 'E179', 'E187', 'E188', 'E193', 'E302',
                    'E305', 'E307', 'E308', 'E311', 'E315', 'E317', 'E322', 'E325',
                    'E329', 'E330', 'E340', 'E349', 'E183', 'E185']

boringdegrees = ['Diploma']

prerecs = []
hdls = []
for page in range(pages):
    tocurl = 'https://repositum.tuwien.at/handle/20.500.12708/5?sort_by=2&order=DESC&offset=' + str(page*rpp) + '&rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for tr in tocpage.body.find_all('tr'):
        for a in tr.find_all('a'):
            if a.has_attr('href') and re.search('handle\/20.500', a['href']):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : [], 'keyw' : [], 'oa' : False}
                rec['hdl'] = re.sub('.*?(20.500.*)', r'\1', a['href'])
                rec['artlink'] = 'https://repositum.tuwien.at' + a['href']
                for img in tr.find_all('img', attrs = {'title' : 'Open Access'}):
                    rec['oa'] = True
                if not rec['hdl'] in hdls:
                    hdls.append(rec['hdl'])
                    if ejlmod3.ckeckinterestingDOI(rec['hdl']):
                        prerecs.append(rec)
                        
    print('   %4i records so far' % (len(prerecs)))
    time.sleep(4)

i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]]) 
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(4)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'citation_title', 'DCTERMS.issued', 'DCTERMS.abstract',
                                        'citation_pdf_url', 'DC.language', 'citation_doi', 'DC.format'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #supervisor
            if meta['name'] == 'DC.contributor':
                rec['supervisor'] = [[ meta['content'] ]]
            #keywords
            elif meta['name'] == 'citation_keywords':
                for keyw in re.split('[,;] ', meta['content']):
                    if not keyw in ['Thesis', 'Hochschulschrift']:
                        rec['keyw'].append(keyw)
            #type
            elif meta['name'] == 'DC.type':
                if meta['content'] in boringdegrees:
                    print('  skip "%s"' % (meta['content']))
                    keepit = False
                elif not meta['content'] in ['Thesis', 'Hochschulschrift']:
                    rec['note'].append(meta['content'])
    for div in artpage.body.find_all('div', attrs = {'class' : 'metadata-row'}):
        for th in div.find_all('div', attrs = {'class' : 'metadataFieldLabel'}):
            metadataFieldLabel = th.text.strip()
        for td in div.find_all('div', attrs = {'class' : 'metadataFieldValue'}):
            #ORCID of author
            if metadataFieldLabel == 'Authors:':
                for a in td.find_all('a'):
                    if a.has_attr('href') and re.search('orcid.org', a['href']):
                        rec['autaff'][-1].append(re.sub('.*\/', 'ORCID:', a['href']))
            #ORCID of supervisor
            elif metadataFieldLabel == 'Advisor:':
                for a in td.find_all('a'):
                    if a.has_attr('href') and re.search('orcid.org', a['href']):
                        rec['supervisor'][-1].append(re.sub('.*\/', 'ORCID:', a['href']))
            #institute
            elif metadataFieldLabel == 'Organisation:':
                institute = td.text.strip()
                if institute[:4] in boringinstitutes:
                    print('  skip "%s"' % (institute[:4]))
                    keepit = False
                elif institute[:4] in ['E138']:
                    rec['fc'] = 'f'
                elif institute[:4] in ['E104', 'E107']:
                    rec['fc'] = 'm'
                else:
                    rec['note'].append(institute)
    #author's affiliation
    rec['autaff'][-1].append(publisher)    
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
