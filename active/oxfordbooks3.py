# -*- coding: UTF-8 -*-
#!/usr/bin/python
#program to harvest Oxford University Press Books
# FS 2017-08-22

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
import urllib.parse
import time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

skipalreadyharvested = True

publisher = 'Oxford University Press'
urltrunc = 'https://global.oup.com/academic/category/science-and-mathematics'
jnlfilename = 'OxfordBooks_%s' % (ejlmod3.stampoftoday())

serieses = ['physics/astronomy-and-astrophysics',
            'physics/atomic-molecular-and-optical-physics',
            'physics/condensed-matter-physics',
            'physics/mathematical-and-statistical-physics',
            'physics/nuclear-physics',
            'physics/particles-and-fields',
            'physics/quantum-physics',
            'physics/relativity-and-gravitation',
            'mathematics/mathematical-analysis',
            'mathematics/numerical-and-computational-mathematics']

facetsandsort = '?cc=de&lang=en&prevSortField=8&facet_narrowbytype_facet=Academic+Research&facet_narrowbytype_facet=Books+for+Courses&sortField=8&resultsPerPage=20&start=0'


options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
options.add_argument("--enable-javascript")
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

driver.get('https://global.oup.com/academic/')
time.sleep(180)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

#scan serieses
isbnsdone = []
prerecs = []
reisbn = re.compile('.*\D(978\d+X?)\?prev.*')
for series in serieses:
    toclink = '%s/%s/%s' % (urltrunc, series, facetsandsort)
    subject = re.sub('.*\/', '', series)
    ejlmod3.printprogress('=', [ [series], [toclink] ])
    #tocreq = urllib.request.Request(toclink, headers={'User-Agent' : "Magic Browser"})
    #toc = BeautifulSoup(urllib.request.urlopen(tocreq), features="lxml")
    driver.get(toclink)
    toc = BeautifulSoup(driver.page_source, features="lxml")
    #print(toc.text)
    for td in toc.body.find_all('td', attrs = {'class' : 'result_biblio'}):
        for h2 in td.find_all('h2'):
            for a in h2.find_all('a'):
                artlink = 'https://global.oup.com' + a['href']
                rec = {'tit' : a.text.strip(), 'artlink' : artlink, 'note' : [ subject ],
                       'tc' : 'B', 'jnl' : 'BOOK', }
#                if not artlink in ['https://global.oup.com/academic/product/quantum-fields--from-the-hubble-to-the-planck-scale-9780192873491?prevSortField=8&facet_narrowbytype_facet=Academic%20Research&sortField=8&resultsPerPage=20&start=0&lang=en&cc=de']:
                if skipalreadyharvested and reisbn.search(artlink):
                    isbn = reisbn.sub(r'\1', artlink)
                    if isbn in alreadyharvested:
                        print('    %s already in backup' % (isbn))
                    else:
                        print('    %s not in backup' % (isbn))
                        prerecs.append(rec)
                else:
                    print('    %s' % (artlink))
                    prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(130)

#scan individual book pages
i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    #artreq = urllib.request.Request(rec['artlink'], headers={'User-Agent' : "Magic Browser"})
    #art = BeautifulSoup(urllib.request.urlopen(artreq), features="lxml")
    driver.get(rec['artlink'])
    art = BeautifulSoup(driver.page_source, features="lxml")
    #abstract and ISBN
    for meta in art.head.find_all('meta'):
        if meta.has_attr('property'):
            if meta['property'] == 'og:description':
                rec['abs'] = meta['content']
        elif meta.has_attr('name'):
            if meta['name'] == 'WT.pn_sku':
                rec['isbns'] = [ [('a', meta['content']), ('b', 'print')] ]
    #authors
    for h3 in art.body.find_all('h3', attrs = {'class' : 'product_biblio_author'}):
        rec['auts'] = re.split(', ', re.sub(' and ', ', ', h3.text))
    #book series
    for h3 in art.body.find_all('h3', attrs = {'class' : 'product_biblio_series_heading'}):
        rec['bookseries'] = [('a', h3.text)]
    #pages, date, further ISBNs
    for div in art.body.find_all('div', attrs = {'class' : ['content_right', 'product_sidebar']}):
        for p in div.find_all('p'):
            ptext = p.text.strip()
            if re.search('Published:', ptext):
                rec['date'] = re.sub('Published: *', '', ptext)
                rec['year'] = re.sub('.* (\d\d\d\d).*', r'\1', ptext)
            elif re.search('^ *\d+ Pages', ptext):
                rec['pages'] = re.sub(' *(\d+) Pages.*', r'\1', ptext)
            elif 'isbns' not in rec and re.search('ISBN'):
                rec['isbns'] = [ [('a', re.sub('ISBN: *([0-9X]+).*', r'\1', ptext)), ('b', 'print')] ]
        for div2 in div.find_all('div', attrs = {'class' : 'product_available_modal'}):
            for img in div2.find_all('img'):
                if img.has_attr('src'):
                    if re.search('Ebook', div2.text):
                        isbn = [('a', re.sub('.*\/', '', img['src'])), ('b', 'ebook')]
                    else:
                        isbn = [('a', re.sub('.*\/', '', img['src'])), ('b', 'print')]
                        if not isbn in rec['isbns']:
                            rec['isbns'].append(isbn)
    time.sleep(20)
    addrecord = True
    #check if too new
    if 'date' in rec and re.search('Estimated', rec['date']):
        print('   [%2i/%2i] delete "%s" because date=%s' % (i, len(prerecs), rec['tit'], rec['date']))
        addrecord = False
        continue
    #check if already in other subject
    if 'isbns' in rec:
        for isbn in rec['isbns']:
            if addrecord:
                if isbn in isbnsdone:
                    print('   already under other subject or with other ISBN')
                    addrecord = False
                elif skipalreadyharvested and '20.2000/ISBNS/' + isbn[0][1] in alreadyharvested:
                    print('   already in backup')
                    addrecord = False
            isbnsdone.append(isbn)
    if addrecord:
        #print('   [%2i/%2i] added "%s"' % (i, len(prerecs), rec['tit']))
        recs.append(rec)
        ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
