# -*- coding: UTF-8 -*-
#program to harvest journals from the AGU journals
# FS 2019-03-26
# FS 2022-12-12

import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
import time
import os
from bs4 import BeautifulSoup
import cloudscraper
import random

publisher = 'AGU'
tc = 'P'
jnl = sys.argv[1]
vol = sys.argv[2]
issue = sys.argv[3]

if   (jnl == 'jgrsp'):
    jnlname = 'J.Geophys.Res.Space Phys.'
    toclink = 'https://agupubs.onlinelibrary.wiley.com/toc/21699402/%i/%s/%s' % (int(vol)+1895, vol, issue)
elif (jnl == 'jgrp'):
    jnlname = 'J.Geophys.Res.Planets'
    toclink = 'https://agupubs.onlinelibrary.wiley.com/toc/21699100/%i/%s/%s' % (int(vol)+1895, vol, issue)
elif (jnl == 'jgra'):
    jnlname = 'J.Geophys.Res.Atmos.'
    toclink = 'https://agupubs.onlinelibrary.wiley.com/toc/21698996/%i/%s/%s' % (int(vol)+1895, vol, issue)
elif (jnl == 'jgrse'):
    jnlname = 'J.Geophys.Res.Solid Earth'
    toclink = 'https://agupubs.onlinelibrary.wiley.com/toc/21699356/%i/%s/%s' % (int(vol)+1895, vol, issue)
elif (jnl == 'jgro'):
    jnlname = 'J.Geophys.Res.Oceans'
    toclink = 'https://agupubs.onlinelibrary.wiley.com/toc/21699291/%i/%s/%s' % (int(vol)+1895, vol, issue)
elif (jnl == 'grl'):
    jnlname = 'Geophys.Res.Lett.'
    toclink = 'https://agupubs.onlinelibrary.wiley.com/toc/19448007/%i/%s/%s' % (int(vol)+1895, vol, issue)


scraper = cloudscraper.create_scraper(captcha={'provider': 'anticaptcha', 'api_key': '2871055371ae80947cdd89f4a09b0657'})

if len(sys.argv) > 4:
    cnum = sys.argv[4]
    tc = 'C'
    jnlfilename = '%s%s.%s_%s' % (jnl, vol, issue, cnum)
else:
    jnlfilename = '%s%s.%s' % (jnl, vol, issue)

print(toclink)
#tocpage = BeautifulSoup(urllib2.build_opener(urllib2.HTTPCookieProcessor).open(toclink))
#tocfilename = '/tmp/%s.toc' % (jnlfilename)
#if not os.path.isfile(tocfilename):
#    os.system('wget -T 300 -t 3 -q -O %s "%s"' % (tocfilename, toclink))
#inf = open(tocfilename, 'r')
#tocpage = BeautifulSoup(''.join(inf.readlines()))
#inf.close()
tocpage = BeautifulSoup(scraper.get(toclink).text, features="lxml")


(note1, note2) = (False, False)
prerecs = []
for div in tocpage.body.find_all('div', attrs = {'class' : ['card', 'issue-items-container']}):
    for child in div.children:
        try:
            child.name
        except:
            continue
        if child.name == 'h3':
            note1 = child.text.strip()
            print('=====[ %s ]=====' % (note1))
        elif child.name == 'div':
            for child2 in child.children:
                try:
                    child2.name
                except:
                    continue
                if child2.name == 'h4':
                    note2 = child2.text.strip()
                    print('-----[ %s ]-----' % (note2))
                elif child2.name == 'div':
                    at = child2.find_all('a', attrs = {'class' : 'issue-item__title'})
                    if not at:
                        at = child2.find_all('a', attrs = {'class' : ['issue-item__title', 'visitable']})
                    for a in at:
                        rec = {'jnl' : jnlname, 'vol' : vol, 'issue' : issue, 'year' : '%i' % (int(vol)+1895),
                               'tc' : tc, 'note' : [], 'autaff' : [], 'keyw' : []}
                        if len(sys.argv) > 4:
                            rec['cnum'] = cnum
                        if re.search('\/10\.', a['href']):
                            rec['doi'] = re.sub('.*\/(10\..*)', r'\1', a['href'])
                            rec['artlink'] = 'https://agupubs.onlinelibrary.wiley.com' + a['href']
                            if note1:
                                rec['note'].append(note1)
                            if note2:
                                rec['note'].append(note2)
                            print('    a)', rec['doi'])
                            prerecs.append(rec)
                elif child2.name == 'a':
                    if child2.has_attr('class') and ('issue-item__title' in child2['class'] or 'issue-item__title visitable' in child2['class']):
                        rec = {'jnl' : jnlname, 'vol' : vol, 'issue' : issue, 'year' : '%i' % (int(vol)+1895),
                               'tc' : tc, 'note' : [], 'autaff' : [], 'keyw' : []}
                        if len(sys.argv) > 4:
                            rec['cnum'] = cnum
                        if re.search('\/10\.', child2['href']):
                            rec['doi'] = re.sub('.*\/(10\..*)', r'\1', child2['href'])
                            rec['artlink'] = 'https://agupubs.onlinelibrary.wiley.com' + child2['href']
                            if note1:
                                rec['note'].append(note1)
                            if note2:
                                rec['note'].append(note2)
                            print('    b)', rec['doi'])
                            prerecs.append(rec)




i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']]])
    time.sleep(random.randint(30,90))
    #artpage = BeautifulSoup(urllib2.build_opener(urllib2.HTTPCookieProcessor).open(rec['artlink']))
#    artfilename = '/tmp/%s.%s' % (jnlfilename, re.sub('\W', '', rec['artlink'][8:]))
#    print(artfilename)
#    if not os.path.isfile(artfilename):
#        time.sleep(10)
#        os.system('wget -T 300 -t 3 -q -O %s "%s"' % (artfilename, rec['artlink']))
#    if int(os.path.getsize(artfilename)) == 0:
#        time.sleep(10)
#        os.system('wget -T 300 -t 3 -q -O %s "%s"' % (artfilename, rec['artlink']))        
#    inf = open(artfilename, 'r')
#    artpage = BeautifulSoup(''.join(inf.readlines()))
#    inf.close()
    artpage = BeautifulSoup(scraper.get(rec['artlink']).text, features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_keywords', 'citation_firstpage',
                                        'citation_lastpage', 'citation_publication_date',
                                        'citation_author', 'citation_author_institution',
                                        'citation_author_orcid', 'citation_author_email'])
    #articleID
    if not 'p1' in list(rec.keys()):
        for meta in artpage.head.find_all('meta', attrs = {'name' : 'article_references'}):
            if re.search('http', meta['content']):
                rec['p1'] = re.sub('.*, (.*?)\. http.*', r'\1', meta['content'])
    #abstract
    for div in artpage.body.find_all('div', attrs = {'class' : ['article-section__content', 'en', 'main']}):
        rec['abs'] = div.text.strip()
    #references
    for section in artpage.body.find_all('section', attrs = {'id' : 'references-section'}):
        rec['refs'] = []
        refswithdoi = 0
        for li in section.find_all('li'):
            if not li.has_attr('data-bib-id'):
                continue
            refno = re.sub('.*\-', '', li['data-bib-id'])
            rdoi = False
            for a in li.find_all('a'):
                if a.text in ['CrossRef', 'Crossref']:
                    rdoi = re.sub('.*=', '', a['href'])
                    rdoi = re.sub('%28', '(', rdoi)
                    rdoi = re.sub('%29', ')', rdoi)
                    rdoi = re.sub('%2F', '/', rdoi)
                    rdoi = re.sub('%3A', ':', rdoi)
                    a.replace_with('')
                elif a.text in ['Wiley Online Library']:
                    rdoi = re.sub('.*\/doi\/', '', a['href'])
                    a.replace_with('')
                else:
                    a.replace_with('')
            if rdoi:
                lit = re.sub('\.? *$', ', DOI: %s' % (rdoi), li.text.strip())
                refswithdoi += 1
            else:
                lit = li.text.strip()
            ref = '[%s] %s' % (refno, lit)
            #print '         ', ref
            rec['refs'].append([('x', ref)])
        print('        %i references found (%i with DOI)' % (len(rec['refs']), refswithdoi))
    if not rec['autaff'] and rec['tit'] in ['Issue Information']:
        pass
    else:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
