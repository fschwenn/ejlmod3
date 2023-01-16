# -*- coding: UTF-8 -*-
#program to harvest World  Scientific Books
# FS 2017-08-22

import sys
import os
import ejlmod3
import re
import codecs
import time
from bs4 import BeautifulSoup
import undetected_chromedriver as uc

publisher = 'World Scientific'
jnlfilename = 'WSPBooks_%s' % (ejlmod3.stampoftoday())

startdate = str(ejlmod3.year(backwards=1)) + '0401'
stopdate = re.sub('\-', '', ejlmod3.stampoftoday())

tuples = []
dois = []


options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/chromium-browser'
options.add_argument('--headless')
chromeversion = int(re.sub('Chro.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


for (conceptid, subject, fc) in [('130338', 'Applied and Technical Physics', ''),
                                 ('130339', 'Astrophysics / Astronomy / Cosmology / Geophysics', 'a'),
                                 ('130340', 'Atomic and Molecular Physics', ''),                                 
                                 ('130341', 'Classical Mechanics, Continuum Physics, Acoustics', 'q'),
                                 ('130342', 'Computational, Mathematical and Theoretical Physics', ''),
                                 ('130343', 'Condensed Matter Physics', 'f'),
                                 ('130355', 'Electromagnetism and Plasma Physics', ''),
                                 ('130354', 'General Physics', 'q'),
                                 ('130353', 'Interdisciplinary Physics', ''),
                                 ('130347', 'Optics and Laser Physics', ''),
                                 ('130346', 'Particle Physics/High Energy Physics, Quantum Fields', ''),
                                 ('130344', 'Popular Physics', ''),
                                 ('130350', 'Quantum Mechanics and Quantum Information', 'k'),
                                 ('130356', 'Relativity and Gravitation', 'g'),
                                 ('130351', 'Statistical Physics, Complexity and Nonlinear Dynamical Systems', 's'),
                                 ('130199', 'Computer Science', 'c'),
                                 ('130191', 'Mathematics', 'm')]:
    ejlmod3.printprogress('=', [[subject], [conceptid]])
    tocurl = 'Ppub=%5B' + startdate + '+TO+' + stopdate + '%5D&PubType=book&sortBy=Earliest&startPage=&rel=nofollow&pageSize=50&ConceptID=' +  conceptid
    fulltocurl = 'https://www.worldscientific.com/action/showPublications?' + tocurl
    print('     ' + fulltocurl)
    driver.get(fulltocurl)
    toc = BeautifulSoup(driver.page_source, features="lxml")
    for a in toc.body.find_all('a'):
        if a.has_attr('href') and re.search('worldscibooks.10.1142', a['href']):
            doi = re.sub('.*worldscibooks.', '', a['href'])
            if not doi in dois:
                tuples.append((subject, doi, fc))
                dois.append(doi)
    print('       %3i' % (len(tuples)))


i = 0
recs = []
for tuplet in tuples:
    (subject, doi, fc) = tuplet
    i += 1
    ejlmod3.printprogress('-', [[i, len(tuples)], [len(recs)], [subject], [doi]])
    tc ='B'
    bookfilename = '/tmp/wspbooks.%s' % (re.sub('\W', '', doi))
    if not os.path.isfile(bookfilename):
        time.sleep(20)
        os.system('wget -q -O %s "http://www.worldscientific.com/worldscibooks/%s"' % (bookfilename, doi))
    bookf = open(bookfilename, 'r')
    book = BeautifulSoup(''.join(bookf.readlines()), features="lxml")
    bookf.close()
    rec = {'doi' : doi, 'isbns' : [], 'autaff' : [], 'note' : [ subject ], 'jnl' : 'BOOK'}
    if fc: rec['fc'] = fc
    for meta in book.head.find_all('meta'):
        if meta.has_attr('property'):
            #abstract
            if meta['property'] == 'og:description':
                rec['abs'] = re.sub('\-\->.*', '', re.sub('^\-*> *', '', meta['content']))
            #title
            elif meta['property'] == 'og:title':
                rec['tit'] = meta['content']
    #title
    for h1 in book.body.find_all('h1', attrs = {'class' : 'meta__title'}):
        rec['tit'] = h1.text.strip()
    #subtitle
    for h2 in book.body.find_all('h2', attrs = {'class' : 'normalSubtitle'}):
        rec['note'].append(h2.text.strip())
    #ISBNs
    for span in book.body.find_all('span', attrs = {'class' : 'text'}):
        spant = span.text.strip()
        if re.search('ISBN.*978', spant):
            isbn = re.sub('\D', '', spant)
            if re.search('cover', spant):
                rec['isbns'].append([('a', isbn), ('b', 'print')])
            elif re.search('ebook', spant):
                rec['isbns'].append([('a', isbn), ('b', 'ebook')])
    #pages
    for span in book.body.find_all('span', attrs = {'class' : 'pagecount'}):
        rec['pages'] = re.sub('\D', '', span.text.strip())
    #date
    for span in book.body.find_all('span', attrs = {'class' : 'cover-date'}):
        rec['date'] = span.text.strip()
        rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])
    #authors
    for ul in book.body.find_all('ul', attrs = {'title' : 'list of authors'}):
        ult = ul.text.strip()
        #<span class="hlFld-ContribAuthor">
        if re.search('^By .author', ult):
            for li in ul.find_all('li'):
                for a in li.find_all('a'):
                    rec['autaff'].append([a.text])
                    a.decompose()
                rec['autaff'][-1].append(re.sub('^\((.*)\)$', r'\1', li.text.strip()))
        elif re.search('^Edited', ult):
            for li in ul.find_all('li'):
                for a in li.find_all('a'):
                    rec['autaff'].append([a.text+ ' (Ed.)'])
                    a.decompose()
                rec['autaff'][-1].append(re.sub('^\((.*)\)$', r'\1', li.text.strip()))
    #abstract
    for div in  book.body.find_all('div', attrs = {'id' : 'aboutBook'}):
        rec['abs'] = re.sub('Sample Chapte.*', '', re.sub('[\n\t\r]', ' ', div.text.strip()))
    #license
    ejlmod3.globallicensesearch(rec, book)
    for span in book.body.find_all('span', attrs = {'class' : 'badge-oa'}):
        rec['FFT'] = 'https://www.worldscientific.com/doi/pdf/%s?download=true' % (doi)
    for note in rec['note']:
        if re.search('Proceedings of', note):
            tc = 'K'
    rec['tc'] = tc
    recs.append(rec)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
driver.quit()
