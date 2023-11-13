# -*- coding: utf-8 -*-
#program to harvest journals from OSA publishing
# FS 2018-09-20

import sys
import os
import ejlmod3
import re
import codecs
from bs4 import BeautifulSoup
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

publisher = 'OSA Publishing'
typecode = 'P'
bunchsize = 10
jnl = sys.argv[1]
vol = sys.argv[2]
issue = sys.argv[3]
skipalreadyharvested = True
cnum = False
if (jnl == 'oe'): 
    jnlname = 'Opt.Express'
elif (jnl == 'ao'): 
    jnlname = 'Appl.Opt.'
elif (jnl == 'ol'):
    jnlname = 'Opt.Lett.'
elif (jnl == 'josaa'): 
    jnlname = 'J.Opt.Soc.Am.'
    vol = 'A' + sys.argv[2]
elif (jnl == 'josab'): 
    jnlname = 'J.Opt.Soc.Am.'
    vol = 'B' + sys.argv[2]
elif (jnl == 'optica'):
    jnlname = 'Optica'
elif (jnl == 'aop'):
    jnlname = 'Adv.Opt.Photon.'
else:
    print(' do not know "%s"' % (jnl))
    sys.exit(0)
    
jnlfilename = 'OSA_%s%s.%s_%s' % (jnl, vol, issue, ejlmod3.stampoftoday())
if len(sys.argv) > 4:
    cnum = sys.argv[4]
    jnlfilename += '_' + cnum
    typecode = 'C'

urltrunk = 'https://www.osapublishing.org/%s/issue.cfm?volume=%s&issue=%s' % (jnl, vol, issue)
urltrunk = 'https://opg.optica.org/%s/issue.cfm?volume=%s&issue=%s' % (jnl, vol, issue)
print(urltrunk)

downloadpath = '/tmp'
pdfpath = '/afs/desy.de/group/library/publisherdata/pdf'

options = uc.ChromeOptions()
#options.headless=True
#options.binary_location='/usr/bin/chromium-browser'
#options.binary_location='/afs/desy.de/user/l/library/tmp/chromedriver109.0.5414.74'
options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
####options.add_argument('--headless')
#options.add_argument("--no-sandbox")
#options.add_argument("--incognito")
#options.add_argument("--user-data-dir=/home/library/chrome")
#options.add_argument("--disable-gpu")
#options.add_argument("--disable-setuid-sandbox")
#options.add_argument("--disable-extensions")
#options.add_argument('--disable-application-cache')
#options.add_argument('--disable-gpu')
#options.add_argument("--no-sandbox")
#options.add_argument("--disable-setuid-sandbox")
#options.add_argument("--disable-dev-shm-usage")
options.add_experimental_option("prefs", {"download.prompt_for_download": False, "plugins.always_open_pdf_externally": True, "download.default_directory": downloadpath})
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
#driver = uc.Chrome(options=options)

driver.get(urltrunk)
tocpage = BeautifulSoup(driver.page_source, features="lxml")
time.sleep(10)

done = ['https://www.osapublishing.org/josab/abstract.cfm?uri=josab-36-7-E112']
if skipalreadyharvested:
    for identifier in ejlmod3.getalreadyharvested(jnlfilename):
        done.append(re.sub('\-\-$', '', identifier))
(level0note, level1note) = (False, False)
prerecs = []
year = False
for h2 in tocpage.find_all('h2', attrs = {'class' : 'heading-block-header'}):
    if re.search(' 20\d\d', h2.text):
        year = re.sub('.* (20\d\d).*', r'\1', re.sub('[\n\t\r]', '', h2.text.strip()))
divs = tocpage.body.find_all('div', attrs = {'class' : 'osap-accordion'})
if not divs:
    divs = tocpage.find_all('body')
for div in divs:
    for label in div.find_all('label'):
        level0note = label.text.strip()
    for div2 in div.find_all('div', attrs = {'class' : ['row', 'col-md-12']}):
        for h2 in div2.find_all('h2'):
            level1note = h2.text.strip()
        for p in div2.find_all('p', attrs = {'class' : 'article-title'}):
            rec = {'jnl' : jnlname, 'vol' : vol, 'issue' : issue, 'tc' : typecode,
                   'note' : [], 'keyw' : [], 'autaff' : [], 'refs' : []}
            if cnum:
                rec['cnum'] = cnum
            if level0note:
                rec['note'].append(level0note)
            if level1note:
                rec['note'].append(level1note)
            if year:
                rec['year'] = year
            for a in p.find_all('a'):
                rec['tit'] = p.text.strip()
                rec['artlink'] = 'https://opg.optica.org' + a['href']
            if rec['artlink'] in done:
                print('   %s in done' % (rec['artlink']))
            else:
                prerecs.append(rec)
                rec['note'].append('URLDOC='+rec['artlink'])
                done.append(rec['artlink'])
        #pages
        for p in div2.find_all('p', attrs = {'style' : 'color: #999'}):
            pt = re.sub('[\n\t\r]', '', p.text.strip()) 
            if re.search('\), \d+\-\d+', pt):
                rec['p1'] = re.sub('.*\), (\d+)\-.*', r'\1', pt)
                rec['p2'] = re.sub('.*\), \d+\-(\d+).*', r'\1', pt)
        #authors
        for p in div2.find_all('p', attrs = {'class' : 'article-authors'}):
            rec['auts'] = []
            for aut in re.split('(,| and) ', p.text.strip()):
                rec['auts'].append(re.sub('^and ', '', aut))
time.sleep(5)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']]])
    try:
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        print('   try again in 60s...')
        time.sleep(60)
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    if len(artpage.find_all('meta')) < 10:
        print('  -- try again after 180 s  --  ')
        time.sleep(180)
        try:
            driver.get(rec['artlink'])
            artpage = BeautifulSoup(driver.page_source, features="lxml")
        except:
            print('   try again in 60s...')
            time.sleep(60)
            driver.get(rec['artlink'])
            artpage = BeautifulSoup(driver.page_source, features="lxml")
        if len(artpage.find_all('meta')) < 10:
            print('  -- try again after 300 s  --  ')
            time.sleep(300)
            try:
                driver.get(rec['artlink'])
                artpage = BeautifulSoup(driver.page_source, features="lxml")
            except:
                print('   try again in 60s...')
                time.sleep(60)
                driver.get(rec['artlink'])
                artpage = BeautifulSoup(driver.page_source, features="lxml")
        
        
    print('   read meta tags')
    ejlmod3.metatagcheck(rec, artpage, ['dc.description', 'citation_doi', 'dc.subject',
                                        'citation_firstpage', 'citation_lastpage',
                                        'citation_online_date'])
    #ORCIDs
    orciddict = {}
    for div in artpage.find_all('div', attrs = {'id' : 'authorAffiliations'}):        
        for tr in div.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) == 2 and re.search('orcid.org', tds[1].text):
                author = tds[0].text.strip()
                orcid = re.sub('.*orcid.org\/', 'ORCID:', tds[1].text.strip())
                if author in orciddict:
                    orciddict[author] = False #if author name is not unique
                else:
                    orciddict[author] = orcid
    for meta in artpage.find_all('meta'):
        if meta.has_attr('name'):
            #print meta['name']
            if meta['name'] == 'citation_author':                
                rec['autaff'].append([ meta['content'] ])
                if meta['content'] in orciddict and orciddict[meta['content']]:
                    rec['autaff'][-1].append(orciddict[meta['content']])
            elif meta['name'] == 'citation_author_institution':
                rec['autaff'][-1].append(meta['content'])
            elif meta['name'] == 'citation_author_orcid':
                orcid = re.sub('.*\/', '', meta['content'])
                rec['autaff'][-1].append('ORCID:%s' % (orcid))
            elif meta['name'] == 'citation_author_email':
                email = meta['content']
                rec['autaff'][-1].append('EMAIL:%s' % (email))    
            elif meta['name'] == 'citation_publication_date':
                rec['year'] = meta['content'][:4]
            elif meta['name'] == 'citation_pdf_url':
                if jnl in ['oe', 'boe', 'optica', 'ome', 'osac']:
                    rec['FFT'] = meta['content']
    #references
    j = 0
    for ol in artpage.find_all('ol', attrs = {'id' : 'referenceById'}):
        lis = ol.find_all('li')
        print('   read %i references' % (len(lis)))
        for li in lis:
            j += 1
            for a in li.find_all('a'):
                if re.search('Crossref', a.text):
                    alink = a['href']
                    a.replace_with(re.sub('.*doi.org\/', ', DOI: ', alink))
                elif not re.search('osa\.org\/abstract', a['href']):
                    a.replace_with('')
            ref = re.sub('[\n\t]', ' ', li.text.strip())
            ref = '[%i] %s' % (j, re.sub('\. *, DOI', ', DOI', ref))
            rec['refs'].append([('x', ref)])
    if not rec['autaff']:
        del rec['autaff']
    
    recs.append(rec)
    ejlmod3.printrecsummary(rec)
    #store pdf - but only for QIS as OSA likes to block
    for rec2 in recs:
        if 'FFT' in rec2 and 'fc' in rec2 and 'k' in rec2['fc']:
            targetfilename = '%s/%s/%s.pdf' % (pdfpath, re.sub('\/.*', '', rec2['doi']), re.sub('[\(\)\/]', '_', rec2['doi']))
            if os.path.isfile(targetfilename):
                print('     %s already exists' % (targetfilename))
            else:
                savedfilename = '%s/%s.pdf' % (downloadpath, re.sub('.*uri=(.*)&.*', r'\1', rec2['FFT']))
                if not os.path.isfile(savedfilename):            
                    print('     get %s from %s' % (savedfilename, rec2['FFT']))
                    driver.get(rec2['FFT'])
                    time.sleep(30)
                if os.path.isfile(savedfilename):
                    print('     mv %s to %s' % (savedfilename, targetfilename))
                    os.system('mv %s %s' % (savedfilename, targetfilename))
                    time.sleep(300)
                else:
                    print('     COULD NOT DOWNLOAD PDF')




    ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize))
    time.sleep(40-i/10)

