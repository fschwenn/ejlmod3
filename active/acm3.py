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


sample = {'10.1145/1015330.1015435' : {'all' : 14 , 'core' : 14},
          '10.1145/1465482.1465560' : {'all' : 21 , 'core' : 21},
          '10.1145/1390156.1390294' : {'all' : 18 , 'core' : 18},
          '10.1145/276698.276708' : {'all' : 21 , 'core' : 21},
          '10.1145/258533.258579' : {'all' : 22 , 'core' : 22},
          '10.1145/167088.167097' : {'all' : 25 , 'core' : 25},
          '10.1145/800157.805047' : {'all' : 30 , 'core' : 30},
          '10.1145/237814.237866' : {'all' : 498 , 'core' : 498},
          '10.1145/301250.301349' : {'all' : 10 , 'core' : 10},
          '10.1145/3341302.3342072' : {'all' : 11 , 'core' : 11},
          '10.1145/380752.380757' : {'all' : 21 , 'core' : 21},
          '10.1145/3055399.3055454' : {'all' : 14 , 'core' : 14},
          '10.1145/3311790.3396656' : {'all' : 20 , 'core' : 20},
          '10.1145/3453483.3454061' : {'all' : 12 , 'core' : 12},
          '10.1145/3519939.3523433' : {'all' : 12 , 'core' : 12},
          '10.1145/130385.130401' : {'all' : 17 , 'core' : 17},
          '10.1145/3345312.3345497' : {'all' : 16 , 'core' : 16},
          '10.1145/380752.380758' : {'all' : 26 , 'core' : 26},
          '10.1145/2807591.2807623' : {'all' : 17 , 'core' : 17},
          '10.1145/3387940.3391459' : {'all' : 14 , 'core' : 14},
          '10.1145/3295500.3356155' : {'all' : 16 , 'core' : 16},
          '10.1145/3313276.3316378' : {'all' : 16 , 'core' : 16},
          '10.1145/3123939.3123952' : {'all' : 16 , 'core' : 16},
          '10.1145/780542.780545' : {'all' : 24 , 'core' : 24},
          '10.1145/3287624.3287704' : {'all' : 18 , 'core' : 18},
          '10.1145/3386367.3431293' : {'all' : 22 , 'core' : 22},
          '10.1145/3406325.3451005' : {'all' : 19 , 'core' : 19},
          '10.1145/2591796.2591870' : {'all' : 21 , 'core' : 21},
          '10.1145/3149526.3149531' : {'all' : 22 , 'core' : 22},
          '10.1145/3316781.3317888' : {'all' : 19 , 'core' : 19},
          '10.1145/780542.780546' : {'all' : 23 , 'core' : 23},
          '10.1145/2597917.2597939' : {'all' : 21 , 'core' : 21},
          '10.1145/3387514.3405853' : {'all' : 25 , 'core' : 25},
          '10.1145/3352460.3358287' : {'all' : 22 , 'core' : 22},
          '10.1145/3126908.3126947' : {'all' : 27 , 'core' : 27},
          '10.1145/3352460.3358265' : {'all' : 25 , 'core' : 25},
          '10.1145/3233188.3233224' : {'all' : 28 , 'core' : 28},
          '10.1145/3352460.3358313' : {'all' : 28 , 'core' : 28},
          '10.1145/3385412.3386007' : {'all' : 28 , 'core' : 28},
          '10.1145/3352460.3358257' : {'all' : 30 , 'core' : 30},
          '10.1145/2897518.2897544' : {'all' : 40 , 'core' : 40},
          '10.1145/3009837.3009894' : {'all' : 32 , 'core' : 32},
          '10.1145/780542.780552' : {'all' : 47 , 'core' : 47},
          '10.1145/2491956.2462177' : {'all' : 32 , 'core' : 32},
          '10.1145/3341302.3342070' : {'all' : 39 , 'core' : 39},
          '10.1145/2591796.2591854' : {'all' : 38 , 'core' : 38},
          '10.1145/3188745.3188802' : {'all' : 44 , 'core' : 44},
          '10.1145/3168822' : {'all' : 37 , 'core' : 37},
          '10.1145/3313276.3316310' : {'all' : 52 , 'core' : 52},
          '10.1145/3183895.3183901' : {'all' : 47 , 'core' : 47},
          '10.1145/1993636.1993682' : {'all' : 88 , 'core' : 88},
          '10.1145/3313276.3316366' : {'all' : 88 , 'core' : 88},
          '10.1145/1806689.1806711' : {'all' : 10 , 'core' : 10},
          '10.1145/3477206.3477464' : {'all' : 10 , 'core' : 10},
          '10.18653/v1/N19-1423' : {'all' : 19 , 'core' : 19},
          '10.1145/3338517' : {'all' : 12 , 'core' : 12},
          '10.1145/3411466' : {'all' : 11 , 'core' : 11},
          '10.1145/322248.322255' : {'all' : 13 , 'core' : 13},
          '10.1145/792538.792543' : {'all' : 13 , 'core' : 13},
          '10.1145/992287.992296' : {'all' : 17 , 'core' : 17},
          '10.1145/2049662.2049669' : {'all' : 14 , 'core' : 14},
          '10.1145/3360546' : {'all' : 12 , 'core' : 12},
          '10.1145/3441309' : {'all' : 15 , 'core' : 15},
          '10.1145/2491533.2491549' : {'all' : 16 , 'core' : 16},
          '10.1145/2331130.2331138' : {'all' : 57 , 'core' : 57},
          '10.1145/2885493' : {'all' : 24 , 'core' : 24},
          '10.1145/1219092.1219096' : {'all' : 19 , 'core' : 19},
          '10.1145/3406306' : {'all' : 21 , 'core' : 21},
          '10.1145/79505.79507' : {'all' : 41 , 'core' : 41},
          '10.1145/1968.1972' : {'all' : 31 , 'core' : 31},
          '10.1145/3386162' : {'all' : 23 , 'core' : 23},
          '10.1145/502090.502098' : {'all' : 27 , 'core' : 27},
          '10.1145/3402192' : {'all' : 33 , 'core' : 33},
          '10.1145/502090.502097' : {'all' : 36 , 'core' : 36},
          '10.1145/3428218' : {'all' : 27 , 'core' : 27},
          '10.1145/581771.581773' : {'all' : 43 , 'core' : 43},
          '10.1145/321356.321357' : {'all' : 31 , 'core' : 31},
          '10.1145/1568318.1568324' : {'all' : 41 , 'core' : 41},
          '10.1145/279232.279236' : {'all' : 57 , 'core' : 57},
          '10.1145/3106700.3106710' : {'all' : 34 , 'core' : 34},
          '10.1145/3434318' : {'all' : 32 , 'core' : 32},
          '10.1145/3326362' : {'all' : 36 , 'core' : 36},
          '10.1145/272991.272995' : {'all' : 77 , 'core' : 77},
          '10.1145/3065386' : {'all' : 80 , 'core' : 80},
          '10.1145/359168.359176' : {'all' : 69 , 'core' : 69},
          '10.1145/382780.382781' : {'all' : 58 , 'core' : 58},
          '10.1145/227683.227684' : {'all' : 74 , 'core' : 74},
          '10.1145/359340.359342' : {'all' : 124 , 'core' : 124},
          '10.1145/3474222' : {'all' : 8 , 'core' : 8},
          '10.1145/1008908.1008920' : {'all' : 117 , 'core' : 117},
          '10.1145/3446776' : {'all' : 12 , 'core' : 12},
          '10.1145/35078.35080' : {'all' : 9 , 'core' : 9}}

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
        jnlname = 'J.Assoc.Comput.Machinery'
    elif (jnl == 'csur'): 
        jnlname = 'ACM Comput.Surveys'
    elif (jnl == 'sigsam-cca'):
        jnlname = 'ACM Commun.Comp.Alg.'

    elif (jnl == 'tocs'): 
        jnlname = 'ACM Trans.Comp.Syst.'
    elif (jnl == 'tog'): 
        jnlname = 'ACM Trans.Graph.'
    elif (jnl == 'tomacs'): 
        jnlname = 'ACM Trans.Model.Comput.Simul.'
    elif (jnl == 'trets'): 
        jnlname = 'ACM Trans.Reconf.Tech.Syst.'
    elif (jnl == 'jacm'):
        jnlname = 'J.Assoc.Comput.Machinery'
        

    jnlfilename = "acm_%s%s.%s" % (jnl, vol, re.sub('\/', '_', issue))
    tocurl = 'https://dl.acm.org/toc/%s/%s/%s/%s' % (jnl, year, vol, issue)

    print("%s, Volume %s, Issue %s" % (jnlname, vol, issue))

print("get table of content... from %s" % (tocurl))

options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
#options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
driver.implicitly_wait(300)

driver.get(tocurl)
tocpages = [BeautifulSoup(driver.page_source, features="lxml")]

for span in tocpages[0].body.find_all('span', attrs = {'class' : 'in-progress'}):
    jnlfilename = "acm_%s%s.%s_in_progress_%s" % (jnl, vol, issue, ejlmod3.stampoftoday())

if jnl == 'proceedings':
    year= False
    #year
    for div in tocpages[0].find_all('div', attrs = {'class' : 'coverDate'}):
        year = div.text.strip()
    if not year:   
        tocurl = 'https://dl.acm.org/doi/proceedings/10.5555/' + procnumber
        print("get table of content... from %s instead" % (tocurl))
        time.sleep(2)
        driver.get(tocurl)
        tocpages = [BeautifulSoup(driver.page_source, features="lxml")]
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
        
dois = []
    
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
                if a.has_attr('href'):
                    rec['artlink'] = 'https://dl.acm.org' + a['href']
                    rec['doi'] = re.sub('.*?\/(10\..*)', r'\1', rec['artlink'])
                    rec['tit'] = a.text.strip()
                else:
                    print('???', a)
        for div2 in div.find_all('div', attrs = {'class' : 'issue-item__detail'}):
            div2t = div2.text.strip()
            #p1
            if re.search('(Paper|Article) No\.: \d+', div2t):
                rec['p1'] = re.sub('.*(Paper|Article) No\.: (\d+).*', r'\2', div2t)            
            #pages
            if re.search(' pp \d+\D\d+', ' '+div2t):
                pages = re.split('\D', re.sub('.*pp (\d+\D\d+).*', r'\1', div2t))
                if jnl in ['sigsam-cca', 'cacm'] or not 'p1' in rec:
                    rec['p1'] = pages[0]
                    rec['p2'] = pages[1]
                else:
                    rec['pages'] = str(int(pages[1]) - int(pages[0]))
                    
        if not rec['doi'] in dois:
            recs.append(rec)
            dois.append(rec['doi'])

print(' %3i recs from TOC' % (len(recs)))

for tocpage in tocpages:
    for div in tocpage.body.find_all('div', attrs = {'class' : ['toc_section accordion-tabbed__tab',
                                                                'toc__section accordion-tabbed_tab js--open',
                                                                'toc__section accordion-tabbed__tab',
                                                                'toc__section accordion-tabbed__tab js--open']}):
        section = div.text.strip()
        inps = div.find_all('input', attrs = {'class' : 'section--dois'})
        ndois = 0
        if not section in ['DEPARTMENT: Departments', 'DEPARTMENT: Career Paths in Computing',   
                           'DEPARTMENT: Letters to the Editor', 'DEPARTMENT: BLOG@CACM',
                           'COLUMN: Last Byte', 'COLUMN: News', 'COLUMN: Legally Speaking',
                           'COLUMN: Privacy', 'COLUMN: Viewpoint', 'DEPARTMENT: Career paths in computing',
                           'DEPARTMENT: Letters to the editor', 'COLUMN: Legally speaking', 'COLUMN: Education',
                           'COLUMN: Last byte', "DEPARTMENT: Cerf's up", 'COLUMN: Inside risks',
                           'COLUMN: Technology strategy and management', 'COLUMN: Broadening participation',
                           'COLUMN: Kode Vicious', 'COLUMN: Historical reflections', 'editorial']:
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
                        if not doi in dois:
                            recs.append(rec)
                            dois.append(doi)
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
        if not 'refs' in rec:
            rec['refs'] = []
            lis = ol.find_all('li')
        for li in lis:
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
    #FFT
    for li in artpage.find_all('li', attrs = {'class' : 'pdf-file'}):
        for a in li.find_all('a', attrs = {'title' : 'PDF'}):
            rec['hidden'] = 'https://dl.acm.org' + a['href']
    #pages
    for div in artpage.find_all('div', attrs = {'class' : 'pageRange'}):
        rec['p1'] = re.sub('\D.*?(\d+).*', r'\1', div.text.strip())
        rec['p2'] = re.sub('.*\D(\d+).*', r'\1', div.text.strip())
    if not 'p1' in rec:
        for span in artpage.find_all('span', attrs = {'class' : 'epub-section__pagerange'}):
            div2t = span.text.strip()
            if re.search(' pp +\d+\D\d+', ' '+div2t):
                pages = re.split('\D', re.sub('.*pp +(\d+\D\d+).*', r'\1', div2t))
                rec['p1'] = pages[0]
                rec['p2'] = pages[1]








    if rec['doi'] in sample:        
        rec['note'] += ['reharvest_based_on_refanalysis',
                        '%i citations from INSPIRE papers' % (sample[rec['doi']]['all']),
                        '%i citations from CORE INSPIRE papers' % (sample[rec['doi']]['core'])]
        print('   reharvest_based_on_refanalysis %i | %o' % (sample[rec['doi']]['all'], sample[rec['doi']]['core']))
                
    ejlmod3.printrecsummary(rec)
    if 'refs' in rec:
        print('       %i references found' % (len(rec['refs'])))

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
