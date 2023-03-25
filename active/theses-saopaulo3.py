# -*- coding: utf-8 -*-
#harvest theses from Sao Paulo U.
#FS: 2019-10-29
#FS: 2023-03-25


import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

pagestocheck = 2
skipalreadyharvested = True

publisher = 'U. Sao Paulo (main) '
jnlfilename = 'THESES-SAOPAULO-%s' % (ejlmod3.stampoftoday())    

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []
prerecs = []
for year in [ejlmod3.year(backwards=1), ejlmod3.year()]:
    tocurl = 'https://teses.usp.br/index.php?option=com_jumi&fileid=19&Itemid=87&lang=en&g=4&b0=Physics&c0=c&o0=AND&b1=%i&c1=a&o1=AND&pagina=' % (year)
    ejlmod3.printprogress("=", [[year], [tocurl]])
    tocfilename = '/tmp/theses-saopaulo-%s_%i_1' % (ejlmod3.stampoftoday(), year)
    if not os.path.isfile(tocfilename):
        os.system('wget -T 300 -t 3 -q  -O %s "%s%i"' % (tocfilename, tocurl, 1)) 
    inf = open(tocfilename, 'r')
    tocpages = [BeautifulSoup(''.join(inf.readlines()), features='lxml')]
    inf.close()
    #check how many pages per year there are
    for div in tocpages[0].body.find_all('div', attrs = {'class' : 'dadosLinha'}):
        divt = div.text.strip()
        if re.search('Displaying.*of \d', divt):
            numofpages = int(re.sub('.*of (\d+).*', r'\1', divt))
    #get TOC pages
    for i in range(numofpages-1):
        ejlmod3.printprogress("=", [[year], [i+2, numofpages], [tocurl+str(i+2)]])
        tocfilename = '/tmp/theses-saopaulo-%s_%i_%i' % (ejlmod3.stampoftoday(), year, i+2)
        if not os.path.isfile(tocfilename):
            os.system('wget -T 300 -t 3 -q  -O %s "%s%i"' % (tocfilename, tocurl, i+2)) 
            time.sleep(10)
        inf = open(tocfilename, 'r')
        tocpages.append(BeautifulSoup(''.join(inf.readlines()), features='lxml'))
        inf.close()
    #check TOC pages for links
    for tocpage in tocpages:
        for div in tocpage.body.find_all('div', attrs = {'class' : 'dadosDocNome'}):
            for a in div.find_all('a'):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'keyw' : []}
                rec['link'] = re.sub('(.*)\/.*', r'\1', a['href'])
                prerecs.append(rec)
#checl individual theses
i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    artfilename = '/tmp/theses-saopaulo-%s_%i_art%04i' % (ejlmod3.stampoftoday(), year, i)
    if not os.path.isfile(artfilename):
        os.system('wget -T 300 -t 3 -q   -O %s "%s"' % (artfilename, rec['link'])) 
        time.sleep(20)
    inf = open(artfilename, 'r')
    artpage = BeautifulSoup(''.join(inf.readlines()), features='lxml')
    inf.close()        
    #language and title
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.language'}):
        lang = meta['content']
        if lang == 'por':
            rec['language'] = 'portuguese'
            for meta2 in artpage.head.find_all('meta', attrs = {'name' : 'DC.title'}):
                if meta2['xml:lang'] == 'en':
                    rec['transtit'] = meta2['content']
                else:
                    rec['tit'] = meta2['content']
        else:
            for meta2 in artpage.head.find_all('meta', attrs = {'name' : 'DC.title'}):
                if meta2['xml:lang'] == 'en':
                    rec['tit'] = meta2['content']
    #other metadata
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'citation_publication_date', 'DC.subject',
                                        'DCTERMS.abstract', 'DC.contributor', 'DC.identifier',
                                        'citation_pdf_url'])
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_dissertation_institution'}):
        rec['autaff'][-1].append(meta['content'] + ', Brazil')
    if not 'doi' in rec:
        rec['doi'] = '20.2000/' + re.sub('\W', '', rec['link'][11:])
    if len(rec['autaff'][-1]) == 1:
        rec['autaff'][-1].append('U. Sao Paulo (main)')
    if skipalreadyharvested and rec['doi'] in alreadyharvested:
        print('  already in backup')
    elif skipalreadyharvested and rec['doi'][4:] in alreadyharvested:
        print('  already in backup')
    else:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
