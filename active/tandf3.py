#!/usr/bin/python
# -*- coding: UTF-8 -*-
#program to harvest Taylor and Francis
# FS 2016-06-27.
# FS 2022-12-09

import os
import sys
import ejlmod3
import re
#import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import cloudscraper
import cookiecache
import requests
import random

def tfstrip(x): return x.strip()

publisher = 'Taylor and Francis'
jnl = sys.argv[1]
vol = sys.argv[2]
issue = sys.argv[3]

if   (jnl == 'tnst20'):
    jnlname = 'J.Nucl.Sci.Tech.'
elif (jnl == 'tcph20'):
    jnlname = 'Contemp.Phys.'
elif (jnl == 'tmop20'):
    jnlname = 'J.Mod.Opt.'
elif (jnl == 'gaat20'):
    jnlname = 'Astron.Astrophys.Trans.'
elif (jnl == 'ggaf20'):
    jnlname = 'Geophys.Astrophys.Fluid Dynamics'
elif (jnl == 'gsrn20'):
    jnlname = 'Synchrotron Radiat.News'
elif (jnl == 'tadp20'):
    jnlname = 'Adv.Phys.'
elif (jnl == 'tphm20'):
    jnlname = 'Phil.Mag.'
elif (jnl == 'gnpn20'):
    jnlname = 'Nucl.Phys.News'
elif (jnl == 'tnmp20'):
    jnlname = 'J.Nonlin.Math.Phys.'
elif (jnl == 'tapx20'):
    jnlname = 'Adv.Phys.X'
elif (jnl == 'uexm20'):
    jnlname = 'Exper.Math.'
elif (jnl == 'gitr20'):
    jnlname = 'Integral Transform.Spec.Funct.'
elif (jnl == 'glma20'):
    jnlname = 'Linear Multilinear Alg.'

if jnl in ['tapx20']:
    jnlfilename = "%s.%s.%s.%s" % (jnl, vol, issue, ejlmod3.stampoftoday())
else:
    jnlfilename = "%s.%s.%s" % (jnl, vol, issue)


#options = uc.ChromeOptions()
#options.headless=True
#options.binary_location='/usr/bin/chromium-browser'
#options.add_argument('--headless')
#driver = uc.Chrome(version_main=103, options=options)


tocurl = 'http://www.tandfonline.com/toc/%s/%s/%s' % (jnl, vol, issue)
print('get table of content from', tocurl)
#driver.get(tocurl)
#page = BeautifulSoup(driver.page_source, features="lxml")
hdr = {'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:106.0) Gecko/20100101 Firefox/106.0',
       'Accept' : 'test/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Referer' : 'http://www.google.com/',
       'Accept-Encoding' : 'br, gzip, deflate',
       'Accept-Language' : 'en-gb'}
cookies = cookiecache.load(domain="tandfonline.com")
for dm in ["google.com", "mozilla.com", "df.eu"]:    
    cookies2 = cookiecache.load(domain=dm)
    for k in cookies2:
        cookies[k] = cookies2[k]
#print(cookies)
session = requests.session()
session.get('http://www.desy.de', headers = hdr, cookies=cookiecache.flatten_cookies(cookies))
#scraper = cloudscraper.create_scraper(sess=session)

scraper = cloudscraper.create_scraper(captcha={'provider': 'anticaptcha', 'api_key': '2871055371ae80947cdd89f4a09b0657'})
page = BeautifulSoup(scraper.get(tocurl).text, features="lxml")
              
#get year
for div in page.body.find_all('div', attrs = {'class' : 'hd prevNextLink'}):
    year = re.sub('.* ([21]\d\d\d) .*', r'\1', re.sub('\n', ' ', div.text.strip()))


prerecs = []
inputs = page.body.find_all('input', attrs = {'name' : 'doi'})
tc = 'P'
for adoi in page.body.find_all('a'):
    if not adoi.has_attr('href'):
        continue
    if not re.search('^PDF', adoi.text):
        continue
    if jnl == 'tcph20':
        tc = 'IR'
    elif jnl in ['gnpn20', 'gsrn20']:
        tc = ''
    rec = {'jnl' : jnlname, 'tc' : tc, 'vol' : vol, 'issue' : issue, 'autaff' : [], 'note' : []}
    rec['doi'] = re.sub('.*\/(10\..*)', r'\1', adoi['href'])
    prerecs.append(rec)
recs = []
for (i, rec) in enumerate(prerecs):
    time.sleep(random.randint(30,170))
    ejlmod3.printprogress('-', [[i+1, len(prerecs)], [rec['doi']]])
    try:
        #driver.get('http://www.tandfonline.com/doi/ref/%s' % (rec['doi']))
        #apage = BeautifulSoup(driver.page_source, features="lxml")
        apage = BeautifulSoup(scraper.get('http://www.tandfonline.com/doi/full/%s' % (rec['doi'])).text, features="lxml")
        time.sleep(random.randint(20,100))
        rpage = BeautifulSoup(scraper.get('http://www.tandfonline.com/doi/ref/%s' % (rec['doi'])).text, features="lxml")
    except:
        print('try without references')
        time.sleep(random.randint(50,90))
        #driver.get('http://www.tandfonline.com/full/ref/%s' % (rec['doi']))
        #apage = BeautifulSoup(driver.page_source, features="lxml")
        apage = BeautifulSoup(scraper.get('http://www.tandfonline.com/full/ref/%s' % (rec['doi'])).text, features="lxml")
        rpage = apage
    if re.search('Cloudflare', apage.text):
        print('Cloudflare :(')
        sys.exit(0)
    #cnum
    if len(sys.argv) > 4:
        rec['tc'] = 'C'
        rec['cnum'] = sys.argv[4]
    ejlmod3.metatagcheck(rec, apage, ['dc.Title', 'dc.Date', 'keywords'])
    #article type
    for div in apage.body.find_all('div', attrs = {'class' : 'toc-heading'}):
        for h3 in div.find_all('h3'):
            rec['note'].append(h3.text.strip())
        for h2 in div.find_all('h2'):
            rec['note'].append(h3.text.strip())
    #year
    for h2 in apage.body.find_all('h2'):
        if re.search('Volume \d.* \d\d\d\d', h2.text):
            rec['year'] = re.sub('.* (\d\d\d\d).*', r'\1', re.sub('\n', ' ', h2.text.strip()))
    #pdf
    #authorstructure
    for span in apage.body.find_all('div', attrs = {'class' : 'hlFld-ContribAuthor'}):
        for div in span.find_all('div', attrs = {'class' : 'entryAuthor'}):
            #author's name
            for a in div.find_all('a', attrs = {'class' : 'author'}):
                rec['autaff'].append([ re.sub('(.*) (.*)', r'\2, \1', a.text.strip()) ])
            #ORCID
            for a in div.find_all('a', attrs = {'class' : 'orcid-author'}):
                rec['autaff'][-1].append(re.sub('.*org\/', 'ORCID:', a['href']))
            for affspan in div.find_all('span', attrs = {'class' : 'overlay'}):
                #EMAIL
                for a in affspan.find_all('a'):
                    if a.has_attr('href') and re.search('@[a-z]', a['href']):
                        rec['autaff'][-1].append(re.sub('.*mailto:', 'EMAIL:', a['href']))
                    a.decompose()
                #correspondance/funding note 
                for corr in div.find_all('span', attrs = {'class' : 'corr-sec'}):
                    corr.decompose()
                for fund in div.find_all('a', attrs = {'class' : 'author-extra-info'}):
                    fund.decompose()
                #AFFILLIATION
                rec['autaff'][-1].append(affspan.text.strip())
    #abstract
    for div in apage.body.find_all('div', attrs = {'class' : 'abstractInFull'}):
        rec['abs'] = div.text.strip()
    #pages
    for span in apage.body.find_all('span', attrs = {'class' : 'contentItemPageRange'}):
        pages = re.sub('[Pp]ages? *', '', span.text).strip()
        try:
            [rec['p1'], rec['p2']] = re.split('\-', pages)
        except:
            rec['p1'] = re.sub('Article: ', '', pages)

    #references
    for ul in rpage.body.find_all('ul', attrs = {'class' : 'references numeric-ordered-list'}):
        rec['refs'] = []
        for li in ul.find_all('li'):
            rdoi = ''
            for a in li.find_all('a'):                
                if a.has_attr('href'):
                    if re.search('Cross[rR]ef', a.text):
                        rdoi = re.sub('.*=', ', DOI: ', a['href'])
                        a.replace_with('')
                    elif re.search('Web of Science', a.text):
                        if not rdoi:
                            rdoi = re.sub('.*doi=', ', DOI: ', a['href'])
                            rdoi = re.sub('\&.*', '', rdoi)
                        a.replace_with('')
                    elif re.search('(PubMed|Taylor|Google Scholar)', a.text):
                        a.replace_with('')                        
            lit = re.sub('\. *$', '', li.text)
            lit = re.sub('\xa0', ' ', li.text)
            lit = re.sub('[\n\t]', ' ', lit)
            lit = re.sub(',\s*,', ',', lit)
            lit = re.sub(',\s*,', ',', lit)
            lit = re.sub('; *(\d)', r', \1', lit)
            if rdoi:
                rdoi = re.sub('%2F', '/', rdoi)
                rdoi = re.sub('%28', '(', rdoi)
                rdoi = re.sub('%29', ')', rdoi)
                rec['refs'].append([('x',  re.sub(',\s*,', ',', lit + rdoi))])
            else:
                rec['refs'].append([('x', lit)])
    if 'note' in rec and rec['note'] and rec['note'][0] in ['Book reviews', 'Essay reviews']:
        continue
    elif 'note' in rec and rec['note'] and rec['note'][0] in ['Review Article']:
        rec['tc'] += 'R'
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
