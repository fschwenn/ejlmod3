# -*- coding: UTF-8 -*-
#program to harvest MIT Books
# FS 2022-06-02
# FS 2023-01-08

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup

publisher = 'MIT Press'
urltrunc = 'https://mitpress.mit.edu/search-result-list/?category='
jnlfilename = 'MITBooks_%s' % (ejlmod3.stampoftoday())

serieses = [('MAT', 'm', 3), ('COM', 'c', 10), ('SCI057000', 'k', 1),
            ('SCI061000', 'g', 1), ('SCI005000', 'a', 1), ('SCI074000', 'q', 1),
            ('SCI055000', 'q', 1), ('SCI004000', 'a', 2), ('SCI015000', 'a', 1),
            ('SCI098000', 'a', 1), ('SCI040000', '', 1), ('SCI051000', '', 1),
            ('SCI103000', '', 1)]
years = 2
skipalreadyharvested = True

#scan serieses
linksdone = []
prerecs = []
i = 0
for (series, fc, pages) in serieses:
    i += 1
    for page in range(pages):
        toclink = '%s%s&supapress_order=publishdate-desc&page_number=%i' % (urltrunc, series, page+1)
        ejlmod3.printprogress("=", [[i, len(serieses)], [series], [page+1, pages], [toclink]])
        tocreq = urllib.request.Request(toclink, headers={'User-Agent' : "Magic Browser"})
        toc = BeautifulSoup(urllib.request.urlopen(tocreq), features="lxml")
        for div in toc.body.find_all('div', attrs = {'class' : 'book-wrapper'}):
            for div2 in div.find_all('div', attrs = {'class' : 'information-wrapper'}):
                for p in div2.find_all('p', attrs = {'class' : 'sp__the-publication-date'}):
                    year = int(re.sub('.*([12]\d\d\d).*', r'\1', p.text.strip()))
                    if year > ejlmod3.year(backwards=years) and ejlmod3.year() >= year:
                        for h3 in div2.find_all('h3'):
                            for a in h3.find_all('a'):
                                rec = {'tit' : a.text.strip(), 'link' : 'https://mitpress.mit.edu' + a['href'], 'note' : [],
                                       'tc' : 'B', 'jnl' : 'BOOK', 'auts' : [], 'date' : str(year), 'isbns' : []}
                                if fc: rec['fc'] = fc
                                if not a['href'] in linksdone:
                                    prerecs.append(rec)
                                    linksdone.append(a['href'])
                                    #print(' ', rec['tit'])
        print('  %4i records so far' % (len(prerecs)))
        time.sleep(10)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

#scan individual book pages
i = 0
recs = []
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    artreq = urllib.request.Request(rec['link'], headers={'User-Agent' : "Magic Browser"})
    artpage = BeautifulSoup(urllib.request.urlopen(artreq), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['og:title'])
    #abstract
    for div in artpage.body.find_all('div', attrs = {'class' : 'tabs__panel--description'}):
        rec['abs'] = div.text.strip()
    #authors
    for span in artpage.body.find_all('p', attrs = {'class' : 'sp__the-author'}):
        for a in span.find_all('a'):
            rec['auts'].append(a.text)
    #ISBN
    for ul in artpage.body.find_all('ul'):
        (isbn, ft) = ('', 'print')
        for li in ul.find_all('li', attrs = {'class' : 'sp__isbn13'}):
            isbn = li.text
            if skipalreadyharvested and '20.2000/ISBNS/'+isbn in alreadyharvested:
                keepit = False
        for li in ul.find_all('li', attrs = {'class' : 'sp__format'}):
            if li.text in ['eBook']:
                ft = 'online'
            elif li.text in ['Hardcover']:
                ft = 'hardcover'
            elif li.text in ['Softcover', 'Paperback']:
                ft = 'softcover'
            elif isbn:
                print(li)
        if isbn:
            rec['isbns'].append([('a', isbn), ('b', ft)])
    #pages
    for span in artpage.body.find_all('span', attrs = {'class' : 'sp__the-pages'}):
        rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', span.text)
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    time.sleep(4)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
