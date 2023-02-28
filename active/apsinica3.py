# -*- coding: utf-8 -*-
#program to harvest Acta Phys.Sin.
# FS 2020-02-23
# FS 2023-02-28

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time
import ssl


publisher = 'Chinese Academy of Sciences'
year = sys.argv[1]
issue = sys.argv[2]
jnlfilename = 'actaphyssin%s.%s' % (year, issue)
#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}

urltrunk = 'http://wulixb.iphy.ac.cn/en/custom/%s/%s' % (year, issue)
try:
    print(urltrunk)
    req = urllib.request.Request(urltrunk, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (urltrunk))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(urltrunk), features="lxml")

recs = []
section = False
for div in tocpage.body.find_all('div', attrs = {'class' : 'main-right'}):
    for child in div.children:
        try:
            child.name
        except:
            continue
        if child.name == 'h6':
            section = child.text.strip()
        elif child.name == 'div':
            for div in child.find_all('div', attrs = {'class' : 'article-list-title'}):
                for a in div.find_all('a'):
                    rec = {'jnl' : 'Acta Phys.Sin.', 'tc' : 'P', 'auts' : [], 'aff' : [],
                           'note' : [], 'issue' : issue, 'refs' : []}
                    if section:
                        rec['note'].append(section)
                    if re.search('^http:', a['href']):
                        rec['artlink'] = a['href']
                    else:
                        rec['artlink'] = 'http:' + a['href']
                    rec['tit'] = a.text.strip()
                    if not a['href'] in ['http://wulixb.iphy.ac.cn:80/en/article/doi/10.7498/aps.70.20201347']:
                        recs.append(rec)
time.sleep(3)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    try:
        req = urllib.request.Request(rec['artlink'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(13)
    except:
        print("retry %s in 180 seconds" % (rec['artlink']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_doi', 'citation_date', 'dc.description',
                                        'citation_volume', 'citation_firstpage', 'citation_lastpage',
                                        'citation_pdf_url', 'dc.rights', 'dc.keywords'])
    #references
    for li in artpage.body.find_all('li', attrs = {'id' : 'References'}):
        for table in li.find_all('table', attrs = {'class' : 'reference-tab'}):
            for tr in table.find_all('tr'):
                for a in tr.find_all('a'):
                    if a.has_attr('href') and re.search('doi.org\/10', a['href']):
                        rdoi = re.sub('.*doi.org\/', ', DOI: ', a['href'])
                        a.replace_with(rdoi)
                rec['refs'].append([('x', tr.text.strip())])
    #PACS
    for inp in artpage.body.find_all('input', attrs = {'id' : 'pcas_txt'}):
        rec['pacs'] = re.split(' *[;,] *', inp['value'])
    #authors
    for ul in artpage.body.find_all('ul', attrs = {'class' : 'article-author'}):
        for sup in ul.find_all('sup'):
            affs = ''
            for aff in re.split(',', sup.text.strip()):
                affs += ', =Aff' + aff
            sup.replace_with(affs)
        ult = re.sub('[\n\t\r]', ' ', ul.text.strip())
        for part in re.split(' *, *', ult):
            if len(part) > 3:
                rec['auts'].append(part)
    #affiliations
    for li in artpage.body.find_all('li', attrs = {'class' : 'article-author-address'}):
        for span in li.find_all('span'):
            spant = re.sub('[\n\t\r]', '', span.text.strip())
            spant = re.sub('(\d+).*', r'Aff\1= ', spant)
            span.replace_with(spant)
        rec['aff'].append(li.text.strip())
    #pages
    if re.search('\d+\-1', rec['p1']) and re.search('\d+\-\d', rec['p2']):
        rec['pages'] = re.sub('.*\-', '', rec['p2'])
        rec['p1'] = re.sub('\-.*', '', rec['p2'])
        del rec['p2']
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
