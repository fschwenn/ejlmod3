# -*- coding: utf-8 -*-
#harvest theses from different italian universities
#FS: 2020-02-20
#
#repository not very up-to-date

import sys
import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time




universities = {'milanbicocca' : ('Milan Bicocca U.', 'https://boa.unimib.it', '/handle/10281/9145', 8),
                'trento' : ('Trento U.', 'https://iris.unitn.it', '/handle/11572/237822', 10),
                'pavia' : ('Pavia U.', 'https://iris.unipv.it', '/handle/11571/1198268', 10),
                'turinpoly' : ('Turin Polytechnic', 'https://iris.polito.it', '/handle/11583/2614423', 10),
                'milan' : ('Milan U.', 'https://air.unimi.it', '/handle/2434/146884', 20),
                'udine' : ('Udine U.', 'https://air.uniud.it', '/handle/11390/1123314', 7),
                'genoa' : ('Genoa U.', 'https://iris.unige.it', '/handle/11567/928192', 15),
                'ferrara' : ('Ferrara U.', 'https://iris.unife.it', '/handle/11392/2380873', 4),
                'trieste' : ('Trieste U', 'https://arts.units.it', '/handle/11368/2907477', 10),
                'siena' : ('Siena U.', 'https://usiena-air.unisi.it', '/handle/11365/973085', 5),
                'verona' : ('Verona U.', 'https://iris.univr.it', '/handle/11562/924246', 7),
                'cagliari' : ('Cagliari U.', 'https://iris.unica.it', '/handle/11584/207612', 8),
                'sns' : ('Pisa, Scuola Normale Superiore', 'https://ricerca.sns.it', '/handle/11384/78634', 5),
                'cagliarieprints' : ('Cagliari U.', 'https://iris.unica.it', '/handle/11584/265854', 8),
                'parma' : ('Parma U.', 'https://www.repository.unipr.it', '/handle/1889/636', 1)}

uni = sys.argv[1]
publisher = universities[uni][0]
pages = universities[uni][3]
jnlfilename = 'THESES-%s-%s' % (uni.upper(), ejlmod3.stampoftoday())
years = 2

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for page in range(pages):
    tocurl = '%s%s?offset=%i&sort_by=-1&order=DESC' % (universities[uni][1], universities[uni][2], 20*page)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    recsfound = False
    for tr in tocpage.body.find_all('tr'):
        rec = False
        for td in tr.find_all('td', attrs = {'headers' : 't1'}):
            for a in td.find_all('a'):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : []}
                rec['artlink'] = universities[uni][1] + a['href'] + '?mode=full.716'
                rec['hdl'] = re.sub('.*handle\/', '', a['href'])
        if not rec:
            for td in tr.find_all('td', attrs = {'headers' : 't3'}):
                for a in td.find_all('a'):
                    rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : []}
                    rec['artlink'] = universities[uni][1] + a['href'] + '?mode=full.716'
                    rec['hdl'] = re.sub('.*handle\/', '', a['href'])
        if rec:
            recsfound = True
            for td in tr.find_all('td', attrs = {'headers' : 't2'}):
                if re.search('[12]\d\d\d', td.text):
                    rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', td.text.strip())
                    if int(rec['year']) >= ejlmod3.year(backwards=years):
                        prerecs.append(rec)
                else:
                    print('(YEAR?)', td.text)
                    prerecs.append(rec)
    if not recsfound:
        for a in tocpage.find_all('a', attrs = {'class' : 'list-group-item-action'}):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : []}
            rec['artlink'] = universities[uni][1] + a['href']
            rec['hdl'] = re.sub('.*handle\/', '', a['href'])
            for p in a.find_all('p'):
                if re.search('[12]\d\d\d', p.text):
                    rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', p.text.strip())
                    if int(rec['year']) >= ejlmod3.year(backwards=years):
                        prerecs.append(rec)
                else:
                    print('(YEAR?)', p.text)
    print('     %3i records so far' % (len(prerecs)))
    time.sleep(5)
                    

i = 0
recs = []
for rec in prerecs:
    interesting = True
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs), len(recs)], [rec['artlink']]])
    if not ejlmod3.ckeckinterestingDOI(rec['hdl']):
        continue
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_author_email', 'citation_author_orcid', 'citation_pdf_url', 'citation_doi',
                                        'citation_title', 'citation_publication_date', 'citation_language', 'DC.subject', 'citation_keywords',
                                        'citation_date'])
    for meta in artpage.find_all('meta'):
        if meta.has_attr('name') and meta.has_attr('content'):
            #pages
            if meta['name'] == 'citation_lastpage':
                if re.search('^\d+$', meta['content']):
                    rec['pages'] = meta['content']
            #abstract
            elif meta['name'] == 'DCTERMS.abstract':
                if re.search(' (the|of|and) ', meta['content']):
                    rec['abs'] = meta['content']
            #thesis type
            #elif meta['name'] == 'DC.type':
            #    if len(meta['content']) > 5:
            #        rec['note'].append(meta['content'])
            #department
            elif meta['name'] == 'citation_keywords':
                section = re.sub('Settore ', '', meta['content'])
                if re.search('^[A-Z][A-Z][A-Z]', section):
                    interesting = False
                    if section[:3] in ['FIS', 'INF', 'ING', 'MAT']:
                        rec['note'].append(section)
                        interesting = True
                    else:
                        print('  skip', section)
    if not 'autaff' in list(rec.keys()):
        for meta in artpage.find_all('meta', attrs = {'name' : 'DC.creator'}):
            rec['autaff'] = [[ meta['content'] ]]
    # :( meta-tags now hidden in JavaScript
    for table in artpage.body.find_all('table', attrs = {'class' : 'itemTagFields'}):
        for tr in table.find_all('tr'):
            for td in tr.find_all('td', attrs = {'class' : 'metadataFieldLabel'}):
                tdlabel = td.text.strip()
            for td in tr.find_all('td', attrs = {'class' : 'metadataFieldValue'}):
                #author
                if re.search('^Autori', tdlabel):
                    if not 'autaff' in list(rec.keys()):
                        rec['autaff'] = [[td.text.strip()]]
                #supervisor
                elif re.search('^Tutore', tdlabel):
                    if not 'supervisor' in list(rec.keys()):
                        rec['supervisor'] = [[td.text.strip()]]
                #title
                elif re.search('^Titolo', tdlabel):
                    if not 'tit' in list(rec.keys()):
                        rec['tit'] = td.text.strip()
                #date
                elif re.search('^Data di', tdlabel):
                    if not 'date' in list(rec.keys()):
                        rec['date'] = re.sub('.*(\d\d\d\d).*', r'\1', td.text.strip())
                #abstract
                elif re.search('^Abstract', tdlabel):
                    if not 'abs' in list(rec.keys()):
                        if re.search(' the ', td.text):
                            rec['abs'] = td.text.strip()
                #language
                elif re.search('^Lingua', tdlabel):
                    if not 'language' in list(rec.keys()):
                        if re.search('Ital', td.text.strip()):
                            rec['language'] = 'italian'
                #keywords
                elif re.search('^Parole.*Inglese', tdlabel):
                    if not 'keyw' in list(rec.keys()):
                        rec['keyw'] = re.split('; ', td.text.strip())
                #section
                elif re.search('^Settore', tdlabel):
                    section = re.sub('Settore ', '', td.text.strip())
                    if re.search('^[A-Z][A-Z][A-Z]', section):
                        interesting = False
                        if section[:3] in ['FIS', 'INF', 'ING', 'MAT']:
                            rec['note'].append(td.text.strip())
                            interesting = True
                        else:
                            print('  skip', section)
        #FFT
        if not 'FFT' in list(rec.keys()):
            for div in artpage.body.find_all('div', attrs = {'class' : 'itemTagBitstreams'}):
                for span in div.find_all('span', attrs = {'class' : 'label'}):
                    if re.search('Open', span.text):
                        for a in div.find_all('a'):
                            if re.search('pdf$', a['href']):
                                rec['FFT'] = universities[uni][1] + a['href']
    if 'autaff' in list(rec.keys()):
        rec['autaff'][-1].append(publisher)
        #year might be the year of deposition
        if 'date' in list(rec.keys()) and not 'year' in list(rec.keys()):
            rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])
        if 'year' in list(rec.keys()) and not 'date' in list(rec.keys()):
            rec['date'] = rec['year']
        #license
        ejlmod3.globallicensesearch(rec, artpage)
        #abstract
        if not 'abs' in list(rec.keys()):
            for p in artpage.body.find_all('p', attrs = {'class' : 'abstractEng'}):
                rec['abs'] = p.text.strip()
        #abstract
        if not 'abs' in list(rec.keys()):
            for p in artpage.find_all('p', attrs = {'class' : 'abstractIta'}):
                rec['abs'] = p.text.strip()
        #link
        if not 'doi' in list(rec.keys()) and not 'hdl' in list(rec.keys()):
            rec['link'] = rec['artlink']
        if interesting:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
        else:
            ejlmod3.adduninterestingDOI(rec['hdl'])
    else:
        print('---[ NO AUTHOR! ]---  ')

ejlmod3.writenewXML(recs, publisher, jnlfilename)
