# -*- coding: utf-8 -*-
# program to harvest Journal of Holography Applications in Physics (JHAP)
#FS: 2022-09-22

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
import codecs
from bs4 import BeautifulSoup
import time
import ssl


publisher = 'Damghan University'
tocurl = sys.argv[1]

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}
try:
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (tocurl))
    time.sleep(180)
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")

recs = []
for h5 in tocpage.body.find_all('h5'):
#    for a in h5.find_all('a', attrs = {'class' : 'tag_a'}):
    for a in h5.find_all('a', attrs = {'class' : 'citation_title'}):
        rec = {'jnl' : 'JHAP', 'tc' : 'P', 'auts' : [], 'aff' : []}
        rec['artlink'] = 'http://jhap.du.ac.ir/' + a['href']
        recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['artlink']]])
    try:
        time.sleep(3)
        req = urllib.request.Request(rec['artlink'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    except:
        print("retry %s in 180 seconds" % (rec['artlink']))
        time.sleep(180)
        req = urllib.request.Request(rec['artlink'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_date', 'citation_title',
                                        'citation_doi', 'citation_volume', 'citation_issue',
                                        'citation_firstpage', 'citation_lastpage', 'citation_pdf_url',
                                        'citation_abstract'])#'citation_author_institution', 'citation_author',
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'keywords'}):
        if meta['content'] != 'Journal of Holography Applications in Physics,JHAP':
            rec['keyw'] = re.split(',', meta['content'])
    #ORCIDs
    for p in artpage.find_all('div', attrs = {'class' : 'col-lg-9'}):
        for strong in p.find_all('strong'):
            if strong.text[:6] == 'Author':
                for ul in p.find_all('ul'):
                    if not rec['auts']:
                        for li in ul.find_all('li'):
                            (orcid, mail) = (False, False)
                            for sup in li.find_all('sup'):
                                for a in sup.find_all('a'):
                                    if a.has_attr('href'):
                                        if re.search('mailto:', a['href']):
                                            mail = re.sub('mailto:', ', EMAIL:', a['href'])
                                            sup.decompose()
                                        elif re.search('orcid.org', a['href']):
                                            orcid = re.sub('.*orcid.org\/', ', ORCID:', a['href'])
                                            sup.decompose()
                                        else:
                                            aff = a['href'][1:]
                                            sup.replace_with(';='+aff)
                            author = re.split(';', re.sub('[\n\t\r]', '', li.text.strip()))
                            if orcid:
                                rec['auts'].append(author[0] + orcid)
                            elif mail:
                                rec['auts'].append(author[0] + mail)
                            else:
                                rec['auts'].append(author[0])
                            rec['auts'] += author[1:]
                            li.decompose()
                #print('-->', rec['auts'])
                for p2 in p.find_all('p', attrs = {'class' : 'margin-bottom-3'}):
                    if p2.has_attr('id'):
                        for sup in p2.find_all('sup'):
                            aff = sup.text
                            sup.replace_with('aff%s=' % (aff))
                        rec['aff'].append(re.sub('  +', ' ', re.sub('[\n\t\r]', '', p2.text)).strip())
                #print('-->', rec['aff'])                                                        
    ejlmod3.printrecsummary(rec)

jnlfilename = 'jhap%s.%s_%s' % (rec['vol'], rec['issue'], ejlmod3.stampoftoday())
ejlmod3.writenewXML(recs, publisher, jnlfilename)
