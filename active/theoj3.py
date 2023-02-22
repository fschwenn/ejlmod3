# -*- coding: UTF-8 -*-
#!/usr/bin/python
#program to harvest from theoj.org
# FS 2020-01-06

import os
import ejlmod3
import re
import sys
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time


publisher = 'publisher'
jnl = sys.argv[1]
if jnl == 'joss':
    jnlname = 'J.Open Source Softw.'
    numberofpages = 15
#needs firefox!
#elif jnl == 'astro': 
#    jnlname = 'Open J.Astrophys.'
#    numberofpages = 1

jnlfilename = 'theoj_%s_%s' % (jnl, ejlmod3.stampoftoday())

options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
options.add_argument('--headless')
options.add_argument("--no-sandbox")
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


#check already done articles
ejldir = '/afs/desy.de/user/l/library/dok/ejl'
def tfstrip(x): return x.strip()
done = []
done =  list(map(tfstrip,os.popen("grep '^3.*DOI' %s/backup/*theoj_%s*doki |sed 's/.*=//'|sed 's/;//'" % (ejldir, jnl))))
done +=  list(map(tfstrip,os.popen("grep '^3.*DOI' %s/backup/%4d/*theoj_%s*doki |sed 's/.*=//'|sed 's/;//'" % (ejldir, ejlmod3.year(backwards=1), jnl))))
print('already done:', len(done))


hdr = {'User-Agent' : 'Mozilla/5.0'}
artlinks = []
driver.implicitly_wait(30)
for pagenr in range(numberofpages):
    tocurl = 'http://%s.theoj.org/papers/published?page=%i' % (jnl, pagenr+1)
    ejlmod3.printprogress('=', [[pagenr+1, numberofpages], [tocurl]])
    driver.get(tocurl)
    tocpage =  BeautifulSoup(driver.page_source, features="lxml")
    for h2 in tocpage.body.find_all('h2', attrs = {'class' : 'paper-title'}):
        for a in h2.find_all('a'):            
            doi = re.sub('.*papers\/', '', a['href'])
            if not doi in done:
                artlinks.append(a['href'])
    print('    %i recs so far' % (len(artlinks)))
    time.sleep(10)

#done = []


i=0
recs = []
for artlink in artlinks:
    i += 1 
    rec = {'jnl' : jnlname, 'tc' : 'P', 'keyw' : [], 'autaff' : [], 'notes' : ['Vorsicht, kein Abstract!']}
    #doi
    rec['doi'] = re.sub('.*papers\/', '', artlink)
    if rec['doi'] in done:
        print('  %s already in done')
    else:
        ejlmod3.printprogress('-', [[i, len(artlinks)], [artlink]])
    #get detailed page
    try:
        driver.get(artlink)
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(5)
    except:
        print('   ... wait 15 minutes')
        time.sleep(900)
        driver.get(artlink)
        artpage = BeautifulSoup(driver.page_source,features="lxml" )
    for div in artpage.find_all('div', attrs = {'class' : 'paper-sidebar'}):
        for child in div.children:
            try:
                child.name
            except:
                continue
            if child.name == 'div':
                divt = child.text.strip()
            elif child.name == 'p':
                #license
                if divt == 'License':
                    for a in child.find_all('a'):
                        if a.has_attr('href') and re.search('creativecommons.org', a['href']):
                            rec['license'] = {'url' : a['href']}
                #tags
                elif divt == 'Tags':
                    for a in child.find_all('a'):
                        rec['keyw'].append(a.text.strip())
                #authors
                elif divt == 'Authors':
                    for a in child.find_all('a'):
                        #ORCID
                        if a.has_attr('href') and re.search('orcid.org', a['href']):
                            rec['autaff'][-1].append(re.sub('.*\/', 'ORCID:', a['href']))
                        #name
                        else:
                            rec['autaff'].append([a.text.strip()])
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_publication_date', 'citation_volume',
                                        'citation_issue', 'citation_firstpage', 'citation_pdf_url',
                                        'citation_doi'])
    if not rec['doi'] in done:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
driver.quit()
