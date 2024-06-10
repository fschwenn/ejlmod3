# -*- coding: UTF-8 -*-
#!/usr/bin/python
#program to harvest individual DOIs from Cambridge-journals
# FS 2023-12-12

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse,http.cookiejar
import time
from bs4 import BeautifulSoup

publisher = 'Cambridge University Press'

tc = 'P'
skipalreadyharvested = False
bunchsize = 10
corethreshold = 15

jnlfilename = 'CAMBRIDGE_QIS_retro.' + ejlmod3.stampoftoday()
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)


sample = {'10.1017/S0305004100013554' : {'all' : 263 , 'core' : 263},
          '10.1017/S0305004100023197' : {'all' : 36 , 'core' : 36},
          '10.1017/hpl.2016.34' : {'all' : 50 , 'core' : 50},
          '10.1017/S0960129504004256' : {'all' : 28 , 'core' : 28},
          '10.1017/S0305004100021150' : {'all' : 140 , 'core' : 140},
          '10.1017/S0962492900002841' : {'all' : 32 , 'core' : 32},
          '10.1017/S0305004100009580' : {'all' : 74 , 'core' : 74},
          '10.1017/S0027763000005304' : {'all' : 32 , 'core' : 32},
          '10.1017/S0305004100019137' : {'all' : 100 , 'core' : 100},
          '10.1017/hpl.2019.36' : {'all' : 137 , 'core' : 137},
          '10.1017/fmp.2018.3' : {'all' : 26 , 'core' : 26}}
sample = {'10.1017/S0305004100009580' : {'all' : 86, 'core' : 36},
          '10.1017/S0305004100021162' : {'all' : 32, 'core' : 23}}


reref = re.compile('^reference\-\d')
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}



i = 0
recs = []
missingjournals = []
for doi in sample:
    if missingjournals:
        print('\nmissing journals:', missingjournals, '\n')

    i += 1
    ejlmod3.printprogress('-', [[i, len(sample)], [doi, sample[doi]['all'], sample[doi]['core']], [len(recs)]])
    if sample[doi]['core'] < corethreshold:
        print('   too, few citations')
        continue
    if skipalreadyharvested and doi in alreadyharvested:
        print('   already in backup')
        continue
    rec = {'tc' : 'P', 'artlink' : 'https://doi.org/' + doi, 'doi' : doi,
           'refs' : [], 'note' : []}
    req = urllib.request.Request(rec['artlink'], headers=hdr)
    try:
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(8)
    except:
        if 'artlink2' in list(rec.keys()):
            print('wait 3 minutes befor trying %s instead of %s' % (rec['artlink2'], rec['artlink']))
            time.sleep(180)
            req = urllib.request.Request(rec['artlink2'], headers=hdr)
        else:
            print('wait 3 minutes befor trying  again')
            time.sleep(180)
            req = urllib.request.Request(rec['artlink'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(2)
    for meta in artpage.find_all('meta', attrs = {'name' : 'citation_journal_title'}):
        if meta['content'] == 'Acta Numerica':
            rec['jnl'] = 'Acta Numer.'
        elif meta['content'] == 'Mathematical Proceedings of the Cambridge Philosophical Society':
            rec['jnl'] = 'Math.Proc.Cambridge Phil.Soc.'
        elif meta['content'] == 'High Power Laser Science and Engineering':
            rec['jnl'] = 'High Power Laser Sci.Eng.'
        elif meta['content'] == 'Mathematical Structures in Computer Science':
            rec['jnl'] = 'Math.Struct.Comput.Sci.'
        elif meta['content'] == 'Nagoya Mathematical Journal':
            rec['jnl'] = 'Nagoya Math.J.'
        elif meta['content'] == 'Forum of Mathematics, Pi':
            rec['jnl'] = 'Forum Math.Pi'


    if not 'jnl' in rec:
        missingjournals.append(meta['content'])
        continue
        
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_firstpage', 'citation_lastpage',
                                        'citation_doi', 'citation_author', 'citation_author_institution',
                                        'citation_author_email', 'citation_author_orcid',
                                        'citation_online_date', 'citation_keywords',
                                        'citation_pdf_url', 'citation_volume', 'citation_issue'])
#    for meta in artpage.head.find_all('meta'):
#        if 'name' in meta.attrs:
#            #pubnote
#            if meta['name'] == 'citation_volume':
#                if jid == 'IAU':
#                    rec['vol'] = vol
#                else:
#                rec['vol'] = meta['content']
#            elif meta['name'] == 'citation_issue':
#                if not jid == 'IAU':
#                    rec['issue'] = meta['content']
#            elif meta['name'] == 'citation_publication_date':
#                rec['year'] = meta['content'][:4]
    #article-ID
    if not 'p1' in list(rec.keys()):
        for dl in artpage.body.find_all('dl', attrs = {'class' : 'article-details'}):
            for div in dl.find_all('div', attrs = {'class' : 'content__journal'}):
                for span in div.find_all('span'):
                    rec['p1'] = re.sub('^ *,? *', '', span.text.strip())
    #articleID
    if 'p1' not in rec:
        for ul in artpage.body.find_all('ul', attrs = {'class' : 'title-volume-issue'}):
            for li in ul.find_all('li', attrs = {'class' : 'published'}):
                rec['p1'] = re.sub('.*, ', '', re.sub('\n', ' ', li.text.strip()))
    #abstract
    for div in artpage.body.find_all('div', attrs = {'class' : 'abstract'}):
        for tit in div.find_all('title'):
            tit.replace_with('')
        rec['abs'] = div.text.strip()
        rec['abs'] = re.sub('[\n\t\r]', ' ', rec['abs'])
        rec['abs'] = re.sub('  +', ' ', rec['abs'])
    #references (only with DOI)
    for div in artpage.body.find_all('div', attrs = {'id' : 'references'}):
        for child in div.children:
            try:
                child.name
            except:
                continue
            if child.name == 'div':
                reference = child.text.strip()
            elif child.name == 'ul':
                for a in child.find_all('a'):
                    if a.text == 'CrossRef':
                        refdoi = re.sub('.*doi.org.', '', a['href'])
                        reference += ', DOI: ' + refdoi
            elif child.name == 'hr':
                rec['refs'].append([('x', reference)])
        #(new/other) references
        if not rec['refs']:
            for div2 in div.find_all('div', attrs = {'class' : 'ref'}):
                rec['refs'].append([('x', div2.text.strip())])
    if not rec['refs']:
        refdivs = []
        for div in artpage.body.find_all('div'):
            if div.has_attr('id') and reref.search(div['id']):
                refdivs.append(div)
        for div in refdivs:
            reference = ''
            refnum = re.sub('\D', '', div['id'])
            for a in div.find_all('a'):
                if a.text == 'CrossRef':
                    refdoi = re.sub('.*doi.org.', '', a['href'])
                    reference += ', DOI: ' + refdoi
                    a.decompose()
                elif a.text in ['Google Scholar', 'Pubmed']:
                    a.decompose()
            rec['refs'].append([('x', '[%s] %s%s' % (refnum, re.sub('\. *$', '', div.text.strip()), reference))])
    #licence
    for div in artpage.body.find_all('div', attrs = {'class' : 'description'}):
        for div2 in div.find_all('div', attrs = {'class' : 'margin-top'}):
            div2text = div2.text.strip()
            if re.search('creativecommons.org', div2text):
                rec['licence'] = {'url' : re.sub('.*(http.*?creativecommons.*?0).*', r'\1', div2text)}                

    #sample note
    rec['note'] = ['reharvest_based_on_refanalysis',
                   '%i citations from INSPIRE papers' % (sample[doi]['all']),
                   '%i citations from CORE INSPIRE papers' % (sample[doi]['core'])]
    ejlmod3.printrecsummary(rec)
    recs.append(rec)
    ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize), retfilename='retfiles_special')

