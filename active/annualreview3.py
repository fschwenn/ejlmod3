#!/usr/bin/python
#program to harvest Annual Reviews
# FS 2017-01-18
# FS 2022-09-11

import os
import ejlmod3
import re
import sys
import unicodedata
import undetected_chromedriver as uc
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import codecs
import time
import cloudscraper

tmpdir = '/tmp'
def tfstrip(x): return x.strip()

publisher = 'Annual Reviews'
jnl = sys.argv[1]
vol = sys.argv[2]

jnlfilename = jnl+vol

if   (jnl == 'arnps'): 
    jnlname = 'Ann.Rev.Nucl.Part.Sci.'
    urltrunk = 'http://www.annualreviews.org/toc/nucl/%s/1' % (vol)
elif (jnl == 'araa'):
    jnlname = 'Ann.Rev.Astron.Astrophys.'
    urltrunk = 'http://www.annualreviews.org/toc/astro/%s/1' % (vol)
elif (jnl == 'arcmp'):
    jnlname = 'Ann.Rev.Condensed Matter Phys.'
    urltrunk = 'http://www.annualreviews.org/toc/conmatphys/%s/1' % (vol)


options = uc.ChromeOptions()
#options.headless=True
options.binary_location='/usr/bin/chromium'
#options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
#chromeversion = 108
driver = uc.Chrome(version_main=chromeversion, options=options)
#scraper = cloudscraper.create_scraper()


print("get table of content of %s%s ... via %s" %(jnlname,vol, urltrunk))
driver.get(urltrunk)
tocpage = BeautifulSoup(driver.page_source, features="lxml")
#tocpage = BeautifulSoup(scraper.get(urltrunk).text, features="lxml")
time.sleep(3)

recs = []
doisdone = []
for div in tocpage.find_all('article', attrs = {'class' : 'teaser'}):
    #right colume??
    volume = re.sub('.*Vol\. (\d+).*', r'\1', re.sub('[\n\t]', ' ', div.text.strip()))
    print(volume, vol)
    if volume != vol:
        continue
    rec = {'vol' : vol, 'tc' : 'R', 'jnl' : jnlname, 'auts' : [], 'aff' : []}
    #doi
    for a in div.find_all('a'):
        if a.has_attr('href'):
            ahref= a['href']
            if re.search('doi.*10', ahref):
                doi = re.sub('.*?(10\..*)', r'\1', a['href'])
                if not re.search('#', doi):
                    rec['doi'] = doi
                    rec['artlink'] = 'http://www.annualreviews.org/doi/full/' + rec['doi']
    if rec['doi'] in doisdone:
        continue
    else:
        doisdone.append(rec['doi'])
    print(rec['doi'], rec['artlink'])
    driver.get(rec['artlink'])
    artpage = BeautifulSoup(driver.page_source, features="lxml")
    #artpage = BeautifulSoup(scraper.get(rec['artlink']).text, features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['dc.Title', 'dc.Subject', 'keywords', 'dc.Description'])
#    print(artpage.text)
    #Abstract
    for div in artpage.body.find_all('div', attrs = {'class' : 'abstractInFull'}):
        rec['abs'] = div.text.strip() 
    #pubnote
    for div in artpage.body.find_all('div', attrs = {'class' : 'article-header'}):
        divtext = re.sub('[\n\t]', ' ', div.text.strip())
        if re.search('.*?Vol. \d+:\d+\-\d+', divtext):
            rec['p1'] = re.sub('.*?Vol. \d+:(\d+)\-.*', r'\1', divtext)
            rec['p2'] = re.sub('.*?Vol. \d+:\d+\-(\d+).*', r'\1', divtext)
        rec['year'] = re.sub('.*Volume.*? (20\d\d).*', r'\1', divtext)
        if re.search('Advance', divtext):
            if re.search('Advance on [A-Za-z]+ \d+, \d+', divtext):
                rec['date'] = re.sub('.*Advance on ([A-Za-z]+) (\d+), (\d+).*', r'\2 \1 \3', divtext)
            else:
                rec['date'] = re.sub('.*Advance.* (20\d\d).*', r'\1', divtext)
    for div in artpage.body.find_all('div', attrs = {'class' : 'hlFld-ContribAuthor'}):
        #Authors
        for p in div.find_all('p', attrs = {'class' : 'name'}):
            for sup in p.find_all('sup'):
                afftext = ''
                for aff in re.split(',', sup.text):
                    afftext += '; =Aff%s' % (aff)
                sup.replace_with(afftext + '; ')
            ptext = re.sub(',', '', p.text.strip())
            ptext = re.sub(' and ', '; ', ptext)
            for aut in re.split('; ', ptext):
                if len(aut.strip()) > 2:
                    rec['auts'].append(aut.strip())
        #Affiliations
        for p in div.find_all('p'):
            if p.has_attr('class'): continue
            for sup in p.find_all('sup'):
                afftext = 'Aff%s= ' % (sup.text)
                sup.replace_with(afftext)
            rec['aff'].append(re.sub(' email.*', '', p.text.strip()))
    #License
    for div in artpage.body.find_all('div', attrs = {'class' : 'article-tools'}):
        for a in div.find_all('a'):
            if a.has_attr('href'):
                if re.search('creativecommons.org', a['href']):
                    rec['license'] = {'url' : a['href']}
                elif re.search('doi\/pdf', a['href']):
                    rec['FFT'] = 'https://www.annualreviews.org' + a['href']
    #Reference
    for div in artpage.body.find_all('div', attrs = {'class' : 'lit-cited'}):
        for ul in div.find_all('ul', attrs = {'class' : 'otherReviewsList'}):
            ul.replace_with('')
        rec['refs'] = []
        for li in div.find_all('li'):
            if not li.has_attr('refid'): continue
            refdoi = False
            for a in li.find_all('a'):
                if re.search('Crossref', a.text):
                    refdoi = re.sub('.*key=', '', a['href'])
                    refdoi = re.sub('%2F', '/', refdoi)
                    refdoi = re.sub('%28', '(', refdoi)
                    refdoi = re.sub('%29', ')', refdoi)
                    refdoi = re.sub('%3A', ':', refdoi)
                    refdoi = re.sub('%5B', '[', refdoi)
                    refdoi = re.sub('%5D', ']', refdoi)
                a.replace_with('')
            reftext = li.text.strip()
            if refdoi:
                reftext = '%s, DOI: %s' % (reftext, refdoi)
            rec['refs'].append([('x', reftext)])
    ejlmod3.printrecsummary(rec)
    recs.append(rec)
    time.sleep(3)

if not recs:
    print(tocpage.text)


ejlmod3.writenewXML(recs, publisher, jnlfilename)
