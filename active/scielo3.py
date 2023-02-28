# -*- coding: UTF-8 -*-
#program to harvest scielo.org
# FS 2021-06-18
# FS 2023-02-28

import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup
import ssl

jnl = sys.argv[1]
year = sys.argv[2]
skipalreadyharvested = True

typecode = 'P'

if   (jnl == 'rbef'): 
    trunc = 'http://www.scielo.br'
    issn = '1806-1117'
    jnlname = 'Rev.Bras.Ens.Fis.'
    vol = str(int(year) - 1978)
    publisher = 'Sociedade Brasileira de Fisica'
    #despite its name it does not contain reviews
    #typecode = 'R'
#elif (jnl == 'rmaa'):
#    trunc = 'http://www.scielo.org.mx'
#    issn = '0185-1101'
#    jnlname = 'Rev.Mex.Astron.Astrofis.'
#    publisher = 'National Autonomous University of Mexico'
else:
    print('Dont know journal %s!' % (jnl))
    sys.exit(0)

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}


tocurl = '%s/j/%s/i/%s.v%s' % (trunc, jnl, year, vol)
print("get table of content of %s%s via %s ..." %(jnlname, year, tocurl))
req = urllib.request.Request(tocurl, headers=hdr)
tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")

note = ''
prerecs = []



jnlfilename = '%s%s_%s' % (jnl, year, ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)


alldois = []
for ul in tocpage.body.find_all('ul', attrs = {'class' : 'articles'}):
    for li in ul.find_all('li'):
        arturl = False
        absurl = False
        rec = {'jnl' : jnlname, 'year' : year, 'vol' : vol, 'tc' : typecode,
               'autaff' : [], 'refs' : [], 'note' : []}
        for h2 in li.find_all('h2'):
            #title and document type
            for span in h2.find_all('span'):
                rec['note'].append(span.text)
                span.decompose()
            rec['tit'] = h2.text
            for li2 in li.find_all('li'):
                #PDF                
                if re.search('PDF', li2.text):
                    for a in li2.find_all('a'):
                        rec['FFT'] = trunc + a['href']
                        #language
                        if re.search('Portu', a['title']):
                            rec['language'] = 'Portuguese'
                        elif re.search('(Spanish|Espa)', a['title']):
                            rec['language'] = 'Portuguese'
                #article link
                elif re.search('Text', li2.text):
                    for a in li2.find_all('a'):
                        rec['artlink'] = trunc + a['href']
            prerecs.append(rec)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        req = urllib.request.Request(rec['artlink'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(3)
    except:
        print('      wait 5 minutes to get', rec['artlink'])
        time.sleep(300)
        artpage = BeautifulSoup(urllib.request.urlopen(rec['artlink']))
    ejlmod3.metatagcheck(rec, artpage, ['citation_doi', 'citation_publication_date', 'citation_pdf_url'])
    #authors
    for div in artpage.body.find_all('div', attrs = {'class' : 'contribGroup'}):
        for span in div.find_all('span', attrs = {'class' : 'dropdown'}):
            for span2 in span.find_all('span'):
                rec['autaff'].append([span2.text.strip()])
                span2.decompose()
            for a in span.find_all('a'):
                if a.has_attr('href'):
                    if re.search('orcid.org', a['href']):
                        rec['autaff'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', a['href']))
                    elif re.search('mailto:', a['href']):
                        rec['autaff'][-1].append(re.sub('.*mailto:', 'EMAIL:', a['href']))
                    a.decompose()
            rec['autaff'][-1].append(re.sub('[\n\t\r]', ' ', span.text.strip()))
    #translated title
    if 'language' in list(rec.keys()):
        for h2 in artpage.body.find_all('h2', attrs = {'class' : 'article-title'}):
            rec['transtit'] = h2.text.strip()
    #abstract and keywords
    for div in artpage.body.find_all('div', attrs = {'data-anchor' : 'Abstract'}):
        for h1 in div.find_all('h1'):
            h1.decompose()
        divt = re.sub('[\n\t\r]', ' ', div.text.strip())
        if re.search('Keywords:', divt):
            rec['keyw'] = re.split('; ', re.sub('.*Keywords: *', '', divt))
            divt = re.sub(' *Keywords:.*', '', divt)
        rec['abs'] = divt
    if not 'abs' in list(rec.keys()):
        abslink = re.sub('(.*)\/.*', r'\1', rec['artlink']) + '/abstract/?lang=en'
        time.sleep(2)
        try:
            req = urllib.request.Request(abslink, headers=hdr)
            abspage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
            for article in abspage.find_all('article'):
                articlet = re.sub('[\n\t\r]', ' ', article.text.strip())
                if re.search('Keywords:', articlet):
                    rec['keyw'] = re.split('; ', re.sub('.*Keywords: *', '', articlet))
                    articlet = re.sub(' *Keywords:.*', '', articlet)
                rec['abs'] = articlet
        except:
            print('  could not get abstract page')
    if not 'abs' in list(rec.keys()):
        for div in artpage.body.find_all('div', attrs = {'data-anchor' : 'Resumos'}):
            for h1 in div.find_all('h1'):
                h1.decompose()
            divt = re.sub('[\n\t\r]', ' ', div.text.strip())
            if re.search('Palavros:', divt):
                rec['keyw'] = re.split('; ', re.sub('.*Palavros: *', '', divt))
                divt = re.sub(' *Palavros:.*', '', divt)
            rec['abs'] = divt
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    #references
    for ul in artpage.body.find_all('ul', attrs = {'class' : 'refList'}):
        for li in ul.find_all('li'):
            rec['refs'].append([('x', li.text.strip())])
    #articleID
    if jnl == 'rbef':
        rec['p1'] = re.sub('\-', '', re.sub('.*RBEF', 'e', rec['doi']))
    if skipalreadyharvested and rec['doi'] in alreadyharvested:
        print('   %s already in backup' % (rec['doi']))
    else:        
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
