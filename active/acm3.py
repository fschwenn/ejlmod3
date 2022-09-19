# -*- coding: UTF-8 -*-
#program to harvest journals from Association for Computing Machinery'
# FS 2021-02-26
#FS: 2022-09-05

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
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import datetime

recs = []
rpp = 30

publisher = 'Association for Computing Machinery'
jnl = sys.argv[1]
if jnl == 'proceedings':
    procnumber = sys.argv[2]
    jnlname = 'BOOK'
    tc = 'C'
    if len(sys.argv) > 3:
        cnum = sys.argv[3]
        jnlfilename = "acm_%s%s_%s" % (jnl, procnumber, cnum)    
    else:
        cnum = False
        jnlfilename = "acm_%s%s" % (jnl, procnumber)    
    tocurl = 'https://dl.acm.org/doi/proceedings/10.1145/' + procnumber
else:
    year = sys.argv[2]
    vol = sys.argv[3]
    issue = sys.argv[4]
    tc = 'P'
    if (jnl == 'tqc'): 
        jnlname = 'ACM Trans.Quant.Comput.'
    elif (jnl == 'toms'): 
        jnlname = 'ACM Trans.Math.Software'
    elif (jnl == 'cacm'): 
        jnlname = 'Commun.ACM'
    elif (jnl == 'jacm'): 
        jnlname = 'J.Assoc.Comput.Machinery'
    elif (jnl == 'tocs'): 
        jnlname = 'ACM Trans.Comp.Syst.'
    elif (jnl == 'csur'): 
        jnlname = 'ACM Comput.Surveys'
    elif (jnl == 'tog'): 
        jnlname = 'ACM Trans.Graph.'
    elif (jnl == 'tomacs'): 
        jnlname = 'ACM Trans.Model.Comput.Simul.'
    elif (jnl == 'trets'): 
        jnlname = 'ACM Trans.Reconf.Tech.Syst.'

    jnlfilename = "acm_%s%s.%s" % (jnl, vol, issue)
    tocurl = 'https://dl.acm.org/toc/%s/%s/%s/%s' % (jnl, year, vol, issue)

    print("%s, Volume %s, Issue %s" % (jnlname, vol, issue))

print("get table of content... from %s" % (tocurl))

options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/chromium-browser'
options.add_argument('--headless')
driver = uc.Chrome(version_main=103, options=options)
driver.implicitly_wait(300)

driver.get(tocurl)
tocpages = [BeautifulSoup(driver.page_source, features="lxml")]

for span in tocpages[0].body.find_all('span', attrs = {'class' : 'in-progress'}):
    jnlfilename = "acm_%s%s.%s_in_progress_%s" % (jnl, vol, issue, ejlmod3.stampoftoday())

if jnl == 'proceedings':
    #year
    for div in tocpages[0].find_all('div', attrs = {'class' : 'coverDate'}):
        year = div.text.strip()
    #Hauptaufnahme
    rec = {'jnl' : jnlname, 'tc' : 'K', 'auts' : [], 'year' : year, 'fc' : 'c', 'note' : []}
    rec['doi'] = '10.1145/' + procnumber
    for div in tocpages[0].body.find_all('div', attrs = {'class' : 'colored-block__title'}):
        if not 'tit' in list(rec.keys()):
            rec['tit'] = div.text.strip()
            if cnum:
                rec['cnum'] = cnum
            for divr in div.find_all('div', attrs = {'class' : 'item-meta-row'}):
                for divh in divr.find_all('div', attrs = {'class' : 'item-meta-row'}):
                    divht = div.text.strip()
                for divc in divr.find_all('div', attrs = {'class' : 'item-meta-row__value'}):
                    #ISBN
                    if divht == 'ISBN:':
                        rec['isbn'] = divc.text.strip()
                    #details
                    elif divht == 'Conference:':
                        rec['note'].append(divc.text.strip())
            #authors
            for ul in tocpages[0].body.find_all('ul', attrs = {'title' : 'list of authors'}):
                for a in ul.find_all('a'):
                    if not re.search('\+ *\d', a.text):
                        rec['auts'].append(re.sub('(.*) (.*)', r'\2, \1 (ed.)', a.text.strip()))
            recs = [rec]


totalnumber = 1
for button in tocpages[0].find_all('button', attrs = {'class' : 'showAllProceedings'}):
    totalnumber = int(re.sub('\D', '', button.text))+rpp
    print(totalnumber-rpp, 'more articles expected')
    incomplete = True
for i in range(totalnumber//rpp):
    if incomplete:
        incomplete = False
        for button in tocpages[-1].find_all('button', attrs = {'class' : 'showMoreProceedings'}):
            tocurl = 'https://dl.acm.org/doi/proceedings/%s?id=%s' % (button['data-doi'], button['data-id'])
            ejlmod3.printprogress('=', [[i+2, totalnumber//rpp+1], [tocurl]])
            driver.get(tocurl)
            tocpages.append(BeautifulSoup(driver.page_source, features="lxml"))
            incomplete = True
        
    
for tocpage in tocpages:
    for div in tocpage.body.find_all('div', attrs = {'class' : 'issue-item__content'}):
        if jnl == 'proceedings':
            rec = {'jnl' : jnlname, 'tc' : tc, 'year' : year, 'fc' : 'c', 'note' : []}
            if cnum:
                rec['cnum'] = cnum
        else:
            rec = {'jnl' : jnlname, 'tc' : tc, 'vol' : vol, 'issue' : issue, 'year' : year, 'fc' : 'c', 'note' : []}
        for h5 in div.find_all('h5', attrs = {'class' : 'issue-item__title'}):
            for a in h5.find_all('a'):
                rec['artlink'] = 'https://dl.acm.org' + a['href']
                rec['doi'] = re.sub('.*?\/(10\..*)', r'\1', rec['artlink'])
                rec['tit'] = a.text.strip()
        for div2 in div.find_all('div', attrs = {'class' : 'issue-item__detail'}):
            div2t = div2.text.strip()
            #pages
            if re.search(' pp \d+\D\d+', div2t):
                pages = re.split('\D', re.sub('.*pp (\d+\D\d+).*', r'\1', div2t))
                rec['pages'] = str(int(pages[1]) - int(pages[0]))
            #p1
            if re.search('(Paper|Article) No\.: \d+', div2t):
                rec['p1'] = re.sub('.*(Paper|Article) No\.: (\d+).*', r'\2', div2t)            
        recs.append(rec)

print(' %3i recs from TOC' % (len(recs)))

for tocpage in tocpages:
    for div in tocpage.body.find_all('div', attrs = {'class' : ['toc_section accordion-tabbed__tab',
                                                                'toc__section accordion-tabbed_tab js--open',
                                                                'toc__section accordion-tabbed__tab',
                                                                'toc__section accordion-tabbed__tab js--open']}):
        section = div.text.strip()
        inps = div.find_all('input', attrs = {'class' : 'section--dois'})
        ndois = 0 
        for inp in inps:
            if inp.has_attr('value'):
                for doi in re.split(',', inp['value']):
                    if jnl == 'proceedings':
                        rec = {'jnl' : jnlname, 'tc' : tc, 'year' : year, 'note' : [section], 'fc' : 'c'}
                        if cnum:
                            rec['cnum'] = cnum
                    else:
                        rec = {'jnl' : jnlname, 'tc' : tc, 'vol' : vol, 'issue' : issue, 'year' : year, 'note' : [section], 'fc' : 'c'}
                    rec['doi'] = doi
                    rec['artlink'] = 'https://dl.acm.org/doi/' + doi
                    recs.append(rec)
                    ndois += 1
        if ndois:
            print(' %3i additional recs from %i section %s' % (ndois, len(inps), section))

i = 0
for rec in recs:
    i += 1
    if not 'artlink' in rec:
        continue
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['artlink']]])
    time.sleep(10)
    driver.get(rec['artlink'])
    artpage = BeautifulSoup(driver.page_source, features="lxml")

    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #keywords
            if meta['name'] == 'dc.Subject':
                rec['keyw'] = re.split(' *; *', meta['content'])
            #date
            elif meta['name'] == 'dc.Date':
                rec['date'] = re.sub('.*?(\d\d\d\\d\-\d+\-\d+)$', r'\1', meta['content'])
            #type
            elif meta['name'] == 'dc.Type':
                rec['note'].append(meta['content'])
            #article no
            elif meta['name'] == 'dc.Identifier':
                if meta.has_attr('scheme') and meta['scheme'] == 'article-no':
                    rec['p1'] = meta['content']
    #tile
    for h1 in artpage.find_all('h1', attrs = {'class' : 'citation__title'}):
        rec['tit'] = h1.text.strip()
    #authors
    for ul in artpage.find_all('ul', attrs = {'ariaa-label' : 'authors'}):
        rec['autaff'] = []
        for li in ul.find_all('li'):
            for span in li.find_all('span', attrs = {'class' : 'loa__author-name'}):
                rec['autaff'].append([span.text.strip()])
            for span in li.find_all('span', attrs = {'class' : 'loa_author_inst'}):
                rec['autaff'][-1].append(span.text.strip())
    #abstract
    for div in artpage.find_all('div', attrs = {'class' : 'abstractInFull'}):
        for sup in div.find_all('sup'):
            supt = sup.text.strip()
            sup.replace_with('$^{%s}$' % (supt))
        for sub in div.find_all('sub'):
            subt = sub.text.strip()
            sub.replace_with('$_{%s}$' % (subt))
        rec['abs'] = div.text.strip()
    #references
    for ol in artpage.find_all('ol', attrs = {'class' : 'references__list'}):
        rec['refs'] = []
        for li in ol.find_all('li'):
            refno = ''
            if li.has_attr('id'):
                refno = '[%s] ' % (re.sub('^0*', '', re.sub('\D', '', li['id'])))
            for a in li.find_all('a'):
                if a.has_attr('href') and re.search('doi=10.*key=10', a['href']):
                    rdoi = re.sub('.*key=', '', a['href'])
                    rdoi = re.sub('%28', '(', rdoi)
                    rdoi = re.sub('%29', ')', rdoi)
                    rdoi = re.sub('%2F', '/', rdoi)
                    rdoi = re.sub('%3A', ':', rdoi)
                    a.replace_with(', DOI: %s' % (rdoi))
                else:
                    a.decompose()
            rec['refs'].append([('x', refno + li.text.strip())])
    #pages
    for div in artpage.find_all('div', attrs = {'class' : 'pageRange'}):
        rec['p1'] = re.sub('\D.*?(\d+).*', r'\1', div.text.strip())
        rec['p2'] = re.sub('.*\D(\d+).*', r'\1', div.text.strip())
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
