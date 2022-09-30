# -*- coding: utf-8 -*-
#!/usr/bin/python
#program to harvest Andromeda-journals
# FS 2015-02-11
# FS 2022-09-29

import sys
import os
import ejlmod3
import re
import urllib.parse
from bs4 import BeautifulSoup
import time

pdfdir = '/afs/desy.de/group/library/publisherdata/pdf'
tmpdir = '/tmp'

publisher = 'Andromda'
typecode = 'P'

jnl = sys.argv[1]
issuenumber = sys.argv[2]

if jnl == 'lhep':
    jnlname = 'LHEP'
    tocurl = 'http://journals.andromedapublisher.com/index.php/LHEP/issue/view/' + issuenumber
elif jnl == 'jmlfs':
    jnlname = 'JMLFS'
    tocurl = 'http://journals.andromedapublisher.com/index.php/JMLFS/issue/view/' + issuenumber
elif jnl == 'jais':
    jnlname = 'JAIS'
    tocurl = 'http://journals.andromedapublisher.com/index.php/JAIS/issue/view/' + issuenumber
elif jnl == 'acp':    
    jnlname = 'BOOK'
    tocurl = ' http://main.andromedapublisher.com/ACP/' + issuenumber
    typecode = 'C'

print(tocurl)
try:
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
    time.sleep(3)
except:
    print("retry %s in 180 seconds" % (tocurl))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")

recs = []
for div in tocpage.find_all('div', attrs = {'class' : 'title'}):
    for a in div.find_all('a'):
        rec = {'jnl': jnlname, 'tc' : typecode, 'autaff' : [], 'keyw' : []}
        rec['tit'] = a.text.strip()
        rec['artlink'] = a['href']
        recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['artlink']]])
    try:
        print(rec['artlink'])
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['artlink']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_author_institution', 'citation_date', 'citation_volume', 'citation_issue', 'citation_doi', 'citation_keywords', 'citation_pdf_url', 'DC.Description', 'DC.Rights'])
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.Identifier'}):
        rec['p1'] = meta['content']
    #year as volume for LHEP and JAIS
    if not 'vol' in rec or not rec['vol']:
        if jnl in ['lhep', 'jais']:
            rec['vol'] = re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])
    #licence
    if not 'license' in list(rec.keys()):
        for a in artpage.body.find_all('a', attrs = {'rel' : 'license'}):
            rec['license'] = {'url' : a['href']}
    #references
    for div in artpage.body.find_all('div', attrs = {'class' : 'item references'}):
        rec['refs'] = []
        for div2 in div.find_all('div'):
            for br in div2.find_all('br'):
                br.replace_with('_TRENNER_')
            div2t = re.sub('\. *\[(\d+)\] ', r'._TRENNER_[\1] ', div2.text)
            for ref in re.split('_TRENNER_', div2t):
                rec['refs'].append([('x', ref)])    
    #get PDF to extract DOI !!!
    if not 'doi' in list(rec.keys()):
        if not os.path.isfile('/tmp/%s.%s.%i.pdf' % (rec['jnl'], ejlmod3.stampoftoday() ,i)):
            os.system('wget -O /tmp/%s.%s.%i.pdf "%s"' % (rec['jnl'], ejlmod3.stampoftoday() ,i, rec['FFT']))
        os.system('pdftotext /tmp/%s.%s.%i.pdf /tmp/%s.%s.%i.txt' % (rec['jnl'], ejlmod3.stampoftoday(), i, rec['jnl'], ejlmod3.stampoftoday() ,i))
        inf = open('/tmp/%s.%s.%i.txt' % (rec['jnl'], ejlmod3.stampoftoday() ,i), 'r')
        for line in inf.readlines():
            if re.search('DOI.*(10\.31526\/)', line) and 'doi' not in rec:
                rec['doi'] = re.sub('.*?(10\.31526\/.*)', r'\1', line.strip())
                rec['doi'] = re.sub(' .*', '', rec['doi'])
                os.system('cp /tmp/%s.%s.%i.pdf %s/10.31526/%s' % (rec['jnl'], ejlmod3.stampoftoday() ,i, pdfdir, re.sub('\/', '_', rec['doi'])))
        inf.close()
    ejlmod3.printrecsummary(rec)


if recs:
    if 'issue' in list(rec.keys()):
        jnlfilename = '%s%s.%s_%s' % (jnl, rec['vol'], rec['issue'], ejlmod3.stampoftoday())
    else:
        jnlfilename = '%s%s_%s' % (jnl, rec['vol'], ejlmod3.stampoftoday())
elif jnl in ['acp']:
    recs = []
    jnlfilename = '%s%s_%s' % (jnl, issuenumber, ejlmod3.stampoftoday())
    for div in tocpage.find_all('div', attrs = {'class' : 'col-md-8'}):
        for div2 in div.find_all('div', attrs = {'class' : 'container'}):
            rec = {'jnl': jnlname, 'tc' : typecode, 'auts' : [], 'aff' : []}
            #year
            rec['year'] = sys.argv[3]
            #cnum
            if len(sys.argv) > 4:
                rec['cnum'] = sys.argv[4]
            #title
            for h2 in div2.find_all('h2', attrs = {'class' : 'text-primary'}):
                rec['tit'] = h2.text.strip()
            #abstract
            for div3 in div2.find_all('div', attrs = {'class' : 'collapse'}):
                for p in div3.find_all('p'):
                    rec['abs'] = p.text.strip()
                div3.decompose()
            #authors
            for h2 in div2.find_all('h2', attrs = {'class' : 'text-secondary'}):
                for sup in h2.find_all('sup'):
                    aff = sup.text
                    sup.replace_with(', =Aff%s, ' % (aff))
                for aut in re.split(' *, *', re.sub('[\n\t\r]', ' ', h2.text.strip())):
                    if re.search('\w', aut):
                        rec['auts'].append(aut)
            #affiliations
            for p in div2.find_all('p'):
                for sup in p.find_all('sup'):
                    aff = sup.text
                    sup.replace_with(' XXX Aff%s= ' % (aff))
                rec['aff'] = re.split(' +XXX +', re.sub('[\n\t\r]', ' ', p.text))[1:]
            #fulltext
            for a in div2.find_all('a'):
                if a.has_attr('href') and re.search('\.pdf', a['href']):
                    rec['FFT'] = 'http://main.andromedapublisher.com' + a['href'].strip()
                    rec['link'] = 'http://main.andromedapublisher.com' + a['href'].strip()
                    rec['doi'] = '20.2000/Andromeda/' + re.sub('\W', '', a['href'].strip()[10:])
            if rec['auts']:
                ejlmod3.printrecsummary(rec)
                recs.append(rec)
                    
ejlmod3.writenewXML(recs, publisher, jnlfilename)
