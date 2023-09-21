# -*- coding: UTF-8 -*-
#program to crawl Springer
# FS 2017-02-22
# FS 2022-09-26

import os
import ejlmod3
import re
import sys
import unicodedata
import string
import codecs 
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup


publisher = 'Springer'
toclink = sys.argv[1]
jnl = sys.argv[2]
vol = sys.argv[3]
issue = sys.argv[4]
#cnum = sys.argv[5]
#fc = sys.argv[6]

boring = ['Editorial', 'Comment', 'Q&A', 'News & Views', 'Obituary',
          'News Q&A', 'Correspondence', 'News And Views', 'Career Q&A',
          'Career News', 'Outlook', 'Technology Feature', 'Book Review', 'Obituary', 'News',
          'Books And Arts', 'World View', 'Seven Days', 'Career Column', 'Career Brief',
          'research-highlight', 'Research Highlight', 'Research Briefing', 'Meeting Report',
          'Futures', 'Where I Work', 'Books & Arts', 'Expert Recommendation', 'Measure for Measure',
          'News Round-up', 'News & Views', 'Q&a', 'q-and-a', 'Nature Index', 'nature-index',
          'News and views', 'Career Feature', 'News and Views']

if re.search('springer', toclink):
    urltrunc = 'https://link.springer.com'
else:
    urltrunc = 'https://www.nature.com'

jnlfilename = re.sub(' ', '_', "%s%s.%s" % (jnl, vol, issue))
if len(sys.argv) > 5:
    cnum = sys.argv[5]
    jnlfilename += '_' + cnum


print("%s %s, Issue %s" % (jnl, vol, issue))
print("get table of content... from %s" % (toclink))


def get_records(url):
    global jnlfilename
    recs = []
    print(('get_records:'+url))
    try:
        page = urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(url)
        pages = {url : BeautifulSoup(page, features="lxml")}
        time.sleep(7)
    except:
        print(('failed to open %s' % (url)))
        sys.exit(0)
    #booktitle
    if jnl == 'BOOK':
        for h1 in pages[url].find_all('h1', attrs = {'data-test' : 'book-title'}):
            booktitle = h1.text.strip()
            print('BOOK: %s' % (booktitle))
            jnlfilename = re.sub('\W', '_', booktitle)
            for p in pages[url].find_all('p', attrs = {'data-test' : 'book-subtitle'}):
                booktitle += ': ' + p.text.strip()
            rec = {'jnl' : jnl, 'tit' : booktitle, 'tc' : 'B', 'isbns' : []}
            if len(sys.argv) > 5:
                rec['cnum'] = cnum
                rec['tc'] = 'K'
            ejlmod3.metatagcheck(rec, pages[url], ['doi'])
            #editors
            for div in pages[url].find_all('div', attrs = {'data-test' : 'editor-info'}):
                rec['autaff'] = []
                for li in div.find_all('li', attrs = {'class': 'c-article-authors-listing__item'}):
                    for span in li.find_all('span', attrs = {'class': 'c-article-authors-search__title'}):
                        rec['autaff'].append([span.text.strip() + ' (Ed.)'])
                    for p in li.find_all('p', attrs = {'class': 'c-article-author-affiliation__address'}):
                        rec['autaff'][-1].append(p.text.strip())
            #ISBNS, pages[url]s
            for li in pages[url].find_all('li', attrs = {'class': 'c-bibliographic-information__list-item'}):
                for span2 in li.find_all('span', attrs = {'class': 'c-bibliographic-information__value'}):
                    span2t = span2.text.strip()
                for span in li.find_all('span', attrs = {'class': 'u-text-bold'}):
                    spant = span.text.strip()
                    if spant == 'Hardcover ISBN':
                        rec['isbns'].append([('a', re.sub('[^X\d]', '', span2t)),
                                             ('b', 'hardcover')])
                    elif spant == 'Softcover ISBN':
                        rec['isbns'].append([('a', re.sub('[^X\d]', '', span2t)),
                                             ('b', 'softcover')])
                    elif spant == 'eBook ISBN':
                        rec['isbns'].append([('a', re.sub('[^X\d]', '', span2t)),
                                             ('b', 'online')])
                    elif spant == 'Number of Pages':
                        rec['pages'] = re.sub('\D', '', span2t)
                    elif spant == 'Series Title':
                        rec['bookseries'] =  [('a', span2t)]
                    elif spant == 'Copyright Information':
                        rec['date'] = re.sub('.*([12]\d\d\d).*', r'\1', span2t)
            recs.append(rec)
    else:
        booktitle = False   
    #content spread over several pages?
    numpag = pages[url].body.findAll('span', attrs={'class': 'number-of-pages'})
    print('numpage=', numpag)
    if len(numpag) > 0:
        if re.search('^\d+$', numpag[0].string):
            for i in range(int(numpag[0].string)):
                tocurl = '%s?page=%i' % (re.sub('#toc$', '', url), i+1)  + '#toc'
                if not tocurl in list(pages.keys()):
                    print(tocurl)
                    try:
                        page = urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl)
                        pages[tocurl] = BeautifulSoup(page, features="lxml")
                        time.sleep(7)
                    except:
                        time.sleep(20)
                        page = urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl)
                        pages[tocurl] = BeautifulSoup(page, features="lxml")
                        time.sleep(10)
#                except:
#                    tocurl = '%s/page=%i' % (url, i+1) 
#                    if not tocurl in list(pages.keys()):
#                        print(tocurl)
#                        page = urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl)
#                        pages[tocurl] = BeautifulSoup(page, features="lxml")
        else:
            print(("number of pages %s not an integer" % (numpag[0].string)))
    else:
        inpts = pages[url].body.findAll('input', attrs={'class': 'c-pagination__input'})
        print('%i input-fields' % (len(inpts)))
        for inpt in inpts:
            if re.search('^\d+$', inpt['max']):
                maxpage = int(inpt['max'])
            print('maxpage=', maxpage)
            for i in range(maxpage):
                tocurl = '%s?page=%i' % (re.sub('#toc$', '', url), i+1)  + '#toc'
                if not tocurl in list(pages.keys()):
                    print(tocurl)
                    page = urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl)
                    pages[tocurl] = BeautifulSoup(page, features="lxml")
                    time.sleep(1)
        if not inpts:
            dp = 0
            for li in pages[url].body.findAll('li', attrs={'class': 'c-pagination__item'}):
                if li.has_attr('data-page'):
                    if re.search('^\d$', li['data-page']):
                        dp = int(li['data-page'])
            for i in range(dp-1):
                tocurl = '%s&page=%i' % (re.sub('#toc$', '', url), i+2)
                if not tocurl in list(pages.keys()):
                    print(tocurl)
                    page = urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl)
                    pages[tocurl] = BeautifulSoup(page, features="lxml")
                    time.sleep(1)
        

#    links = []
#    for tocurl in list(pages.keys()):
#        page = pages[tocurl]
#        newlinks = []
#        newlinks += page.body.findAll('p', attrs={'class': 'title'})
#        newlinks += page.body.findAll('h3', attrs={'class': ['title', 'c-card__title']})
#        links += newlinks
#        print(('a) %i potential links in %s' % (len(newlinks), tocurl)))
#    if not links:
#        for tocurl in list(pages.keys()):
#            if tocurl == url and len(pages) > 1: continue
#            page = pages[tocurl]
#            newlinks = page.body.findAll('div', attrs={'class': 'content-type-list__title'})        
#            links += newlinks
#            print(('b) %i potential links in %s' % (len(newlinks), tocurl)))
#    if not links:
#        for tocurl in list(pages.keys()):
#            page = pages[tocurl]
#            newlinks = page.body.findAll('p', attrs={'class': 'item__title'})
#            links += newlinks
#            print(('a) %i potential links in %s' % (len(newlinks), tocurl)))
#            #urltrunc = 'https://materials.springer.com'
#    artlinks = []
#    #print links
#    for link in links:
    artlinks = []
    for (i, tocurl) in enumerate(list(pages.keys())):
        page = pages[tocurl]
        foundsection = False
        print(foundsection)
        for section in page.body.find_all('section', attrs = {'data-title' : 'book-toc'}):
            for li in section.find_all('li', attrs = {'class' : 'c-card'}):                
                for h3 in li.find_all('h3', attrs = {'data-title' : 'part-title'}):
                    foundsection = True
                    print('    ', h3.text.strip())
                    note = h3.text.strip()
                    for h4 in li.find_all('h4'):
                        rec = {'jnl' : jnl, 'autaff' : [], 'note' : [note]}
                        rec['tit'] = h4.text.strip()
                        print('      ', rec['tit'])
                        if booktitle:
                            rec['note'].append(booktitle)
                            if 'isbns' in recs[0] and recs[0]['isbns']:
                                rec['motherisbn'] = recs[0]['isbns'][0][0][1]
                        for a in h4.find_all('a'):
                            if a.has_attr('href'):
                                if re.search('https?:', a['href']):
                                    rec['artlink'] = a['href']
                                else:
                                    rec['artlink'] = urltrunc + a['href']
                                if rec['artlink'] in artlinks:
                                    print('   %s alredady in list' % (rec['artlink']))
                                else:
                                    recs.append(rec)
                                    artlinks.append(rec['artlink'])
        if not foundsection:
            for h3 in page.find_all('h3', attrs = {'class' : 'c-card__title'}):
                print('    ', h3.text.strip())
                rec = {'jnl' : jnl, 'autaff' : [], 'note' : []}
                rec['tit'] = h3.text.strip()
                for a in h3.find_all('a'):
                    if a.has_attr('href'):
                        if re.search('https?:', a['href']):
                            rec['artlink'] = a['href']
                        else:
                            rec['artlink'] = urltrunc + a['href']
                        if rec['artlink'] in artlinks:
                            print('   %s alredady in list' % (rec['artlink']))
                        else:
                            recs.append(rec)
                            artlinks.append(rec['artlink'])            
        ejlmod3.printprogress('+', [[i+1, len(pages)], [tocurl], [len(recs)]])
    return recs 





prerecs = get_records(toclink)
i = 0
recs = []
for rec in prerecs:
    i += 1
    keepit = True
    if not 'artlink' in rec:
        ejlmod3.printprogress('-', [[i, len(prerecs)], [len(recs)]])
        ejlmod3.printrecsummary(rec)
        continue
    if issue != '0':
        rec['issue'] = issue
    if vol == '0':
        rec['tc'] = 'S'
    else:
        rec['vol'] = vol
    if len(sys.argv) > 5:
        rec['cnum'] = cnum
        rec['tc'] = 'C'
    elif vol == '0' or jnl == 'BOOK':
         rec['tc'] = 'S'
    else:
        rec['tc'] = 'P'
    if len(sys.argv) > 6:
        rec['fc'] = sys.argv[6]
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(10)
    except:
        print('  wait 120s to try again')
        time.sleep(120)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(20)
    ejlmod3.metatagcheck(rec, artpage, ['citation_firstpage', 'citation_lastpage', 'citation_doi', 'citation_author',
                                        'citation_author_institution', 'citation_author_email', 'citation_author_orcid',
                                        'description', 'dc.description', 'citation_cover_date', 'citation_article_type',
                                        'prism.publicationDate'])
    if jnl in ['npj Quantum Inf.']:
        for p in artpage.find_all('p', attrs = {'class' : 'c-article-info-details'}):
            for span in p.find_all('span', attrs = {'data-test' : 'article-number'}):
                rec['p1'] = span.text.strip()
                if 'p2' in rec:
                    del rec['p2']
    #article type
    if 'citation_article_type' in rec:
        for at in rec['citation_article_type']:
            if at[24:] in boring:
                keepit = False                
            elif not at[24:] in ['Article', 'Letter', 'Review Article', 'Publisher Correction']:
                rec['note'].append(at)
    #license
    for a in artpage.body.find_all('a', attrs = {'rel' : 'license'}):
        if a.has_attr('href') and re.search('creativecomm', a['href']):
            rec['license'] = {'url' : a['href']}
            ejlmod3.metatagcheck(rec, artpage, ['citation_pdf_url'])
    #date
    if not 'date' in list(rec.keys()):
        for  meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_publication_date'}):
            rec['date'] = meta['content']
    if not 'date' in list(rec.keys()):
        for span in artpage.body.find_all('span', attrs = {'class' : 'bibliographic-information__value', 'id' : 'copyright-info'}):
            if re.search('[12]\d\d\d', span.text):
                rec['date'] = re.sub('.*?([12]\d\d\d).*', r'\1', span.text.strip())
    if not 'date' in rec:
        for a in artpage.body.find_all('a', attrs = {'data-track-action' : 'publication date'}):
            for dt in a.find_all('time'):
                rec['date'] = dt['datetime']
    #Abstract
    for section in artpage.body.find_all('section', attrs = {'class' : 'Abstract'}):
        abstract = ''
        for p in section.find_all('p'):
            abstract += p.text.strip() + ' '
        if not 'abs' in rec or len(abstract) > len(rec['abs']):
            rec['abs'] = abstract
    #Keywords
    for div in artpage.body.find_all('div', attrs = {'class' : 'KeywordGroup'}):
        rec['keyw'] = []
        for span in div.find_all('span', attrs = {'class' : 'Keyword'}):
            rec['keyw'].append(span.text.strip())
    if not 'keyw' in rec:
        rec['keyw'] = []
        for li in artpage.body.find_all('li', attrs = {'class' : 'c-article-subject-list__subject'}):
            rec['keyw'].append(li.text.strip())            
    #References
    references = artpage.body.find_all('ol', attrs = {'class' : ['BibliographyWrapper', 'c-article-references']})
    if not references:
        references = artpage.body.find_all('ul', attrs = {'class' : ['BibliographyWrapper', 'c-article-references']})
    for ol in references:
        rec['refs'] = []
        for li in ol.find_all('li'):
            for a in li.find_all('a'):
                if a.text.strip() in ['Google Scholar', 'MathSciNet', 'ADS']:
                    a.replace_with(' ')
                elif a.text.strip() in ['CrossRef' ,'Article']:
                    rdoi = re.sub('.*doi.org\/', '', a['href'])
                    rdoi = re.sub('%2F', '/', rdoi)
                    a.replace_with(', DOI: %s' % (rdoi))
            rec['refs'].append([('x', li.text.strip())])


        
    #SPECIAL CASE LANDOLT-BOERNSTEIN
    if not rec['autaff']:
        del rec['autaff']
        #date
        #rec['tc'] = 'S'
        if not 'date' in list(rec.keys()):
            rec['date'] = re.sub('.* (\d\d\d\d) *$', r'\1', rec['abs'])
        for dl in artpage.body.find_all('dl', attrs = {'class' : 'definition-list__content'}):
            chapterDOI = False
            #ChapterDOI
            for child in dl.children:
                try:
                    child.name
                except:
                    continue
                if re.search('Chapter DOI', child.text):
                    chapterDOI = True
                elif chapterDOI:
                    rec['doi'] = child.text.strip()
                    chapterDOI = False
            #Authors and Email
            for dd in dl.find_all('dd', attrs = {'id' : 'authors'}):
                rec['auts'] = []
                for li in dd.find_all('li'):
                    email = False
                    for sup in li.find_all('sup'):
                        aff = re.sub('.*\((.*)\).*', r'\1', sup.text.strip())
                        sup.replace_with(',,=Aff%s' % (aff))
                    for a in li.find_all('a'):
                        for img in a.find_all('img'):
                            if re.search('@', img['title']):
                                email = img['title']
                                a.replace_with('') 
                    autaff = re.split(' *,, *', re.sub('[\n\t]', '', li.text.strip()))
                    author = autaff[0]
                    if email:
                         rec['auts'].append(re.sub(' *(.*) (.*)', r'\2, \1', author) + ', EMAIL:%s' % (email))
                    else:
                         rec['auts'].append(re.sub(' *(.*) (.*)', r'\2, \1', author))
                    if len(autaff) > 1:
                        rec['auts'] += autaff[1:]
            #Affiliations
            for dd in dl.find_all('dd', attrs = {'class' : 'definition-description author-affiliation'}):
                rec['aff'] = []
                for li in dd.find_all('li'):
                    aff = re.sub('[\n\t]', ' ', li.text.strip())
                    aff = re.sub('  +', ' ', aff).strip()
                    rec['aff'].append(re.sub('^(\d.*?) (.*)', r'Aff\1= \2', aff))
        #Abstract
        if not 'abs' in list(rec.keys()):
            for div in artpage.body.find_all('div', attrs = {'class' : 'section__content'}):
                for p in div.find_all('p'):
                    rec['abs'] = p.text.strip()
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
        

                
ejlmod3.writenewXML(recs, publisher, jnlfilename, retfilename='retfiles_special')
