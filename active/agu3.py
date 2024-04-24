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
#import cloudscraper
import undetected_chromedriver as uc
import random

publisher = 'AGU'
bunchsize = 10
tc = 'P'
jnl = sys.argv[1]
vol = sys.argv[2]
issue = sys.argv[3]
skipalreadyharvested = True
pdfpath = '/afs/desy.de/group/library/publisherdata/pdf'
downloadpath = '/tmp'

if   (jnl == 'jgrsp'):
    year = str(int(vol)+1895)
    jnlname = 'J.Geophys.Res.Space Phys.'
    toclink = 'https://agupubs.onlinelibrary.wiley.com/toc/21699402/%s/%s/%s' % (year, vol, issue)
elif (jnl == 'jgrp'):
    year = str(int(vol)+1895)
    jnlname = 'J.Geophys.Res.Planets'
    toclink = 'https://agupubs.onlinelibrary.wiley.com/toc/21699100/%s/%s/%s' % (year, vol, issue)
elif (jnl == 'jgra'):
    year = str(int(vol)+1895)
    jnlname = 'J.Geophys.Res.Atmos.'
    toclink = 'https://agupubs.onlinelibrary.wiley.com/toc/21698996/%s/%s/%s' % (year, vol, issue)
elif (jnl == 'jgrse'):
    year = str(int(vol)+1895)
    jnlname = 'J.Geophys.Res.Solid Earth'
    toclink = 'https://agupubs.onlinelibrary.wiley.com/toc/21699356/%s/%s/%s' % (year, vol, issue)
elif (jnl == 'jgro'):
    year = str(int(vol)+1895)
    jnlname = 'J.Geophys.Res.Oceans'
    toclink = 'https://agupubs.onlinelibrary.wiley.com/toc/21699291/%s/%s/%s' % (year, vol, issue)
elif (jnl == 'grl'):
    year = str(int(vol)+1895)
    jnlname = 'Geophys.Res.Lett.'
    toclink = 'https://agupubs.onlinelibrary.wiley.com/toc/19448007/%s/%s/%s' % (year, vol, issue)
elif (jnl == 'agua'):
    year = str(int(vol)+2019)
    jnlname = 'AGU Adv.'
    toclink = 'https://agupubs.onlinelibrary.wiley.com/toc/2576604x/%s/%s/%s' % (year, vol, issue)
    


#scraper = cloudscraper.create_scraper(captcha={'provider': 'anticaptcha', 'api_key': '2871055371ae80947cdd89f4a09b0657'})
host = os.uname()[1]
options = uc.ChromeOptions()
options.add_experimental_option("prefs", {"download.prompt_for_download": False, "plugins.always_open_pdf_externally": True, "download.default_directory": downloadpath})
if host == 'l00schwenn':
    options.binary_location='/usr/bin/chromium'
else:
    options.headless=True
    options.binary_location='/usr/bin/google-chrome'
    options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

if len(sys.argv) > 4:
    cnum = sys.argv[4]
    tc = 'C'
    jnlfilename = '%s%s.%s_%s_%s' % (jnl, vol, issue, cnum, ejlmod3.stampoftoday())
else:
    jnlfilename = '%s%s.%s_%s' % (jnl, vol, issue, ejlmod3.stampoftoday())

print(toclink)
#tocpage = BeautifulSoup(urllib2.build_opener(urllib2.HTTPCookieProcessor).open(toclink))
#tocfilename = '/tmp/%s.toc' % (jnlfilename)
#if not os.path.isfile(tocfilename):
#    os.system('wget -T 300 -t 3 -q -O %s "%s"' % (tocfilename, toclink))
#inf = open(tocfilename, 'r')
#tocpage = BeautifulSoup(''.join(inf.readlines()))
#inf.close()
#tocpage = BeautifulSoup(scraper.get(toclink).text, features="lxml")
try:
    driver.get(toclink)
    tocpage = BeautifulSoup(driver.page_source, features="lxml")
    divs = tocpage.body.find_all('div', attrs = {'class' : ['card', 'issue-items-container']})
    divs[1]
except:
    print('try again')
    time.sleep(60)
    driver.get(toclink)
    tocpage = BeautifulSoup(driver.page_source, features="lxml")
    divs = tocpage.body.find_all('div', attrs = {'class' : ['card', 'issue-items-container']})
    divs[1]
    
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

(note1, note2) = (False, False)
dois = []
prerecs = []
for div in divs:
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
                        rec = {'jnl' : jnlname, 'vol' : vol, 'issue' : issue, 'year' : year,
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
                            if rec['doi'] in dois:
                                print(' [  a)', rec['doi'] + ']')
                            elif not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                                if a.text.strip() in ['Issue Information']:
                                    print('    -)', rec['doi'])
                                else:
                                    print('    a)', rec['doi'])
                                    prerecs.append(rec)                                
                            else:
                                print('      ', rec['doi'])
                            dois.append(rec['doi'])
                elif child2.name == 'a':
                    if child2.has_attr('class') and ('issue-item__title' in child2['class'] or 'issue-item__title visitable' in child2['class']):
                        rec = {'jnl' : jnlname, 'vol' : vol, 'issue' : issue, 'year' : year,
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
                            if rec['doi'] in dois:
                                print(' [  a)', rec['doi'] + ']')
                            elif not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                                if child2.text.strip() in ['Issue Information']:
                                    print('    -)', rec['doi'])
                                else:
                                    print('    b)', rec['doi'])
                                    prerecs.append(rec)
                            else:
                                print('      ', rec['doi'])
                            dois.append(rec['doi'])



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
    #artpage = BeautifulSoup(scraper.get(rec['artlink']).text, features="lxml")
    driver.get(rec['artlink'])
    artpage  = BeautifulSoup(driver.page_source, features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_keywords', 'citation_firstpage',
                                        'citation_lastpage', 'citation_publication_date',
                                        'citation_author', 'citation_author_institution',
                                        'citation_author_orcid', 'citation_author_email'])
    ejlmod3.globallicensesearch(rec, artpage)
    if 'license' in rec:
        #print('check citation_pdf_url')
        ejlmod3.metatagcheck(rec, artpage, ['citation_pdf_url'])
        #print(rec.keys())
            
        targetfilename = '%s/%s/%s.pdf' % (pdfpath, re.sub('\/.*', '', rec['doi']), re.sub('[\(\)\/]', '_', rec['doi']))
        if os.path.isfile(targetfilename):
            print('     %s already exists' % (targetfilename))
            rec['FFT'] = '%s.pdf' % (re.sub('[\(\)\/]', '_', rec['doi']))
        else:
            pdfurl = re.sub('\/doi', '/doi/pdf', rec['artlink'])
            pdfurl = rec['pdf_url']
            savedfilereg = re.compile('%s . %s.*.pdf$' % (re.sub('.* ', '', rec['autaff'][0][0]), re.sub(' .*', '', rec['tit'])))
            print('     get PDF from %s' % (pdfurl))
            driver.get(pdfurl)
            time.sleep(30)
            print('        looking for *%s . %s*pdf' % (re.sub('.* ', '', rec['autaff'][0][0]), re.sub(' .*', '', rec['tit'])))
            for datei in os.listdir(downloadpath):
                if savedfilereg.search(datei):
                    savedfilename = '%s/%s' % (downloadpath, datei)
                    print('     mv %s to %s' % (savedfilename, targetfilename))
                    os.system('mv "%s" %s' % (savedfilename, targetfilename))
                    rec['FFT'] = '%s.pdf' % (re.sub('[\(\)\/]', '_', rec['doi']))
                    time.sleep(300)
            if not os.path.isfile(targetfilename):
                pdfurl = re.sub('\/doi', '/doi/pdfdirect', rec['artlink'])
                print('     get PDF from %s' % (pdfurl))
                driver.get(pdfurl)
                time.sleep(30)
                for datei in os.listdir(downloadpath):
                    if savedfilereg.search(datei):
                        savedfilename = '%s/%s' % (downloadpath, datei)
                        print('     mv %s to %s' % (savedfilename, targetfilename))
                        os.system('mv "%s" %s' % (savedfilename, targetfilename))
                        rec['FFT'] = '%s.pdf' % (re.sub('[\(\)\/]', '_', rec['doi']))
                        time.sleep(300)


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
                    if a.has_attr('href'):
                        if re.search('doi.(org|pangea.de)\/10', a['href']):
                            rdoi = re.sub('.*?\/(10\..*)', r'\1', a['href'])
#                        elif not rdoi:
#                            print('       referencelink:', a['href'])
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
        ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize))

