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
import undetected_chromedriver as uc

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
#    vol = str(int(year) - 1964)
#    publisher = 'National Autonomous University of Mexico'
else:
    print('Dont know journal %s!' % (jnl))
    sys.exit(0)
    
options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
    
tocurl = '%s/j/%s/i/%s.v%s' % (trunc, jnl, year, vol)
print("get table of content of %s%s via %s ..." %(jnlname, year, tocurl))
driver.get(tocurl)
tocpage = BeautifulSoup(driver.page_source, features="lxml")

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
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(3)
    except:
        print('      wait 5 minutes to get', rec['artlink'])
        time.sleep(300)
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_doi', 'citation_publication_date', 'citation_pdf_url',
                                        'citation_firstpage', 'citation_abstract', 'citation_keywords',
                                        'citation_author', 'citation_author_orcid', 'citation_author_affiliation'])
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
    if 'language' in rec:
        abslink = re.sub('(.*)\/.*', r'\1', rec['artlink']) + '/abstract/?lang=en'
        time.sleep(2)
        try:
            req = urllib.request.Request(abslink, headers=hdr)
            abspage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
            for h1 in abspage.find_all('h1'):
                rec['transtit'] = h1.text.strip()
            for article in abspage.find_all('article'):
                articlet = re.sub('[\n\t\r]', ' ', article.text.strip())
                if re.search('Keywords:', articlet):
                    rec['keyw'] = re.split('; ', re.sub('.*Keywords: *', '', articlet))
                    articlet = re.sub(' *Keywords:.*', '', articlet)
                rec['abs'] = articlet
        except:
            print('  could not get abstract page')
    #abstract and keywords
    for article in artpage.body.find_all('article'):
        for div in article.find_all('div'):
            for p in div.find_all('p'):
                for strong in p.find_all('strong'):
                    if strong.text.strip() == 'Keywords:':
                        strong.decompose()
                        rec['keyw'] = re.split('; ', re.sub('.*Keywords: *', '', p.text.strip()))
                        p.decompose()
                        rec['abs'] = div.text.strip()
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
