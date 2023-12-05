# -*- coding: UTF-8 -*-
#program to harvest Cambridge-Books
# FS 2017-08-22
# FS 2023-02-15

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup

skipalreadyharvested = True
pages = 1

publisher = 'Cambridge University Press'

sections = [('physics', 'https://www.cambridge.org/core/what-we-publish/books/listing?sort=canonical.date%3Adesc&aggs%5BproductTypes%5D%5Bfilters%5D=BOOK&aggs%5BproductDate%5D%5Bfilters%5D=Last+12+months&aggs%5BproductSubject%5D%5Bfilters%5D=DBFB610E9FC5E012C011430C0573CC06&searchWithinIds=0C5182F27A492FDC81EDF8D3C53266B5'),
            ('math', 'https://www.cambridge.org/core/what-we-publish/books/listing?sort=canonical.date%3Adesc&aggs%5BproductTypes%5D%5Bfilters%5D=BOOK&aggs%5BproductDate%5D%5Bfilters%5D=Last+12+months&aggs%5BproductSubject%5D%5Bfilters%5D=FA1467C44B5BD46BB8AA6E58C2252153&searchWithinIds=0C5182F27A492FDC81EDF8D3C53266B5')]
sections = [('', 'DBFB610E9FC5E012C011430C0573CC06'),
            ('m', 'FA1467C44B5BD46BB8AA6E58C2252153'),
            ('c', 'A57E10708F64FB69CE78C81A5C2A6555')]

jnlfilename = 'CambridgeBooks__%s' % (ejlmod3.stampoftoday())
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

def formatreference(content):
    if re.search('citation_title', content):
        citationdict = {}
        for part in re.split('; citation_', content[9:]):
            subparts = re.split('=', part, 1)
            if subparts[0] in list(citationdict.keys()):
                citationdict[subparts[0]].append(subparts[1])
            else:
                citationdict[subparts[0]] = [subparts[1]]
        if 'author' in list(citationdict.keys()):
            ref = ', '.join(citationdict['author'])
        else:
            ref = ''
        if 'title' in list(citationdict.keys()):
            ref += ': "%s"' % (citationdict['title'][0])
        if 'journal_title' in list(citationdict.keys()):
            ref += ', ' + citationdict['journal_title'][0]
        elif 'inbook' in list(citationdict.keys()):
            ref += ' in: ' + citationdict['inbook'][0]
        if 'volume' in list(citationdict.keys()):
            ref += ' ' + citationdict['volume'][0]
        if 'firstpage' in list(citationdict.keys()):
            ref += ', ' + citationdict['firstpage'][0]
        if 'lastpage' in list(citationdict.keys()):
            ref += '-'  + citationdict['lastpage'][0]
        if 'publication_date' in list(citationdict.keys()):
            ref += ' (%s)' % (citationdict['publication_date'][0])
        if 'doi' in list(citationdict.keys()):
            ref += ', doi: ' + citationdict['doi'][0]
        return [('x', ref)]
    else:
        return [('x', content)]
        

prerecs = []
for (fc, sec) in sections:
    for page in range(pages):
        ejlmod3.printprogress("=", [[fc, sec], [page+1, pages]])
        tocurl = 'https://www.cambridge.org/core/publications/books/listing?sort=canonical.date%3Adesc&aggs%5BproductTypes%5D%5Bfilters%5D=BOOK&aggs%5BproductDate%5D%5Bfilters%5D=Last%2012%20months&aggs%5BproductSubject%5D%5Bfilters%5D=' + sec + '&pageNum=' + str(page+1) + '&searchWithinIds=0C5182F27A492FDC81EDF8D3C53266B5'
        tocreq = urllib.request.Request(tocurl, headers={'User-Agent' : "Magic Browser"}) 
        toc = BeautifulSoup(urllib.request.urlopen(tocreq), features="lxml")
        lis = toc.body.find_all('li', attrs = {'class' : 'title'})
        if not lis:
            lis = toc.body.find_all('div', attrs = {'class' : 'product-listing-with-inputs-content'})
        for li in lis:
            for a in li.find_all('a', attrs = {'class' : 'part-link'}):
                rec = {'tit' : a.text.strip(), 'note' : [], 'autaff' : [],
                       'tc' : 'B', 'jnl' : 'BOOK'}
                if fc: rec['fc'] = fc
                rec['artlink'] = 'https://www.cambridge.org' + a['href']
                prerecs.append(rec)
        print('    %i recors so far' % (len(prerecs)))

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    artreq = urllib.request.Request(rec['artlink'], headers={'User-Agent' : "Magic Browser"}) 
    artpage = BeautifulSoup(urllib.request.urlopen(artreq), features="lxml")
    haseditor = False
    refs = []
    rec['doi'] = '20.2000/CambridgeBooks/' + re.sub('\W', '', rec['artlink'][10:])
    ejlmod3.metatagcheck(rec, artpage, ['citation_doi', 'citation_isbn', 'citation_author', 'citation_editor',
                                        'citation_author_institution', 'citation_editor_institution',
                                        'citation_online_date', 'citation_abstract'])
    if skipalreadyharvested and rec['doi'] in alreadyharvested:
        print('  already in backup')
    else:
        for meta in artpage.head.find_all('meta'):
            if meta.has_attr('name'):
                #references
                if meta['name'] == 'citation_reference':
                    if not meta['content'] in refs:
                        refs.append(meta['content'])
                #year
                elif meta['name'] == 'citation_publication_date':
                    rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', meta['content'])
        for author in rec['autaff']:
            if re.search('\(Ed', author[0]):
                haseditor = True
                break
        if haseditor:
            rec['note'].append('ggf. Einzelaufnahmen!')
        else:
            rec['refs'] = list(map(formatreference, refs))
        for ul in artpage.body.find_all('ul', attrs = {'class' : 'spec'}):
            for li in ul.find_all('li'):
                for span in li.find_all('span', attrs = {'class' : 'medium-4'}):
                    spant = span.text.strip()
                for span in li.find_all('span', attrs = {'class' : 'medium-8'}):
                    #keywords
                    if spant == 'Subjects:':
                        rec['keyw'] = []
                        for a in span.find_all('a'):
                            rec['keyw'].append(a.text.strip())
                    #book series
                    elif spant == 'Series:':
                        rec['bookseries'] = [('a', span.text.strip())]
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    time.sleep(10 + i % 5)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
