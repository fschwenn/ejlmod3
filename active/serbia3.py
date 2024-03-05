# -*- coding: utf-8 -*-
#program to harvest from doiSerbia
# FS 2019-10-25
# FS 2023-04-25

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time
import ssl
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

tmpdir = '/tmp'

jnl = sys.argv[1]
issueid = sys.argv[2]

if jnl == 'facta':
    jnlname = 'Facta Univ.Ser.Phys.Chem.Tech.'
    typecode = 'P'
    issn = '0354-4656'
    publisher = 'Nis U.'
elif jnl == 'filomat':
    jnlname = 'Filomat'
    typecode = 'P'
    issn = '0354-5180'
    publisher = 'Nis U.'
else:
    print('journal unknown')
    sys.exit(0)

    
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


host = os.uname()[1]
if host == 'l00schwenn':
    options = uc.ChromeOptions()
    options.binary_location='/usr/bin/chromium'
    chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
    driver = uc.Chrome(version_main=chromeversion, options=options)
else:
    options = uc.ChromeOptions()
    options.headless=True
    options.add_argument('--headless')
    driver = uc.Chrome(version_main=chromeversion, options=options)



toclink = 'https://www.doiserbia.nb.rs/issue.aspx?issueid=%s' % (issueid)
tocfile = '/tmp/%s%s' % (jnl, issueid)

print(toclink)
#if not os.path.isfile(tocfile):
#    os.system('lynx -source "%s" > %s' % (toclink, tocfile))
#inf = open(tocfile, 'r')
#tocpage = BeautifulSoup(''.join(inf.readlines()), features="lxml")
#inf.close()

#req = urllib.request.Request(toclink, headers=hdr)
#tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")

tocpages = []
complete = False
i = 0
driver.get(toclink)
time.sleep(10)
while not complete:
    i += 1
    print(' tocpage', i)
    time.sleep(3)
    tocpages.append(BeautifulSoup(driver.page_source, features="lxml"))
    complete = True
    for a in tocpages[-1].find_all('a', attrs = {'class' : 'cc'}):
        if a.text.strip() == str(i+1):
            complete = False
            driver.find_element(By.LINK_TEXT, str(i + 1)).click()
            time.sleep(3)




time.sleep(4)

              
recs = []
#for div in tocpage.body.find_all('div', attrs = {'id' : 'ContentRight'}):
#    for a in div.find_all('a'):
for tocpage in tocpages:
    for a in tocpage.body.find_all('a'):
        if re.search('Details', a.text.strip()):
            rec = {'jnl' : jnlname, 'tc' : typecode, 'auts' : []}
            rec['artlink'] = 'http://www.doiserbia.nb.rs/' + a['href']
            #rec['artlink'] =  a['href']
            recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['artlink']]])
    req = urllib.request.Request(rec['artlink'], headers=hdr)
    artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    time.sleep(4)
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_author', 'citation_keywords',
                                        'citation_year', 'citation_volume', 'citation_issue',
                                        'citation_firstpage',  'citation_lastpage',
                                        'citation_abstract', 'citation_pdf_url'])
    #authors
    if not 'autaff' in rec or not rec['autaff']:
        rec['autaff'] = []
        for span in artpage.find_all('span', attrs = {'id' : 'ContentPlaceHolder1_ArticleDetails2_labelArticleAuthors'}):
            for br in span.find_all('br'):
                br.replace_with('XXX_AUT')
            for span2 in span.find_all('span'):
                span2t = span2.text.strip()
                span2.replace_with(span2t + 'YYY_AUT')
        for author in re.split(' *XXX_AUT *', re.sub('[\n\t\r]', '', span.text)):
            if re.search('YYY_AUT', author):
                rec['autaff'].append([re.sub(' *YYY_AUT.*', '', author)])
                rec['autaff'][-1].append(re.sub('.*YYY_AUT *', '', author))
    for a in artpage.find_all('a'):
        if a.has_attr('href') and re.search('doi.org.10', a['href']):
            rec['doi'] = re.sub('.*doi.org.(10\..*)', r'\1', a['href'])
    #references
    for div in artpage.find_all('div', attrs = {'id' : 'RptRef'}):
        rec['refs'] = []
        for hr in div.find_all('hr'):
            hr.replace_with('XXX_REF')
        divt = div.text.strip()
        divt = re.sub('[\n\t\r]', ' ', divt)
        for ref in re.split(' *XXX_REF *', divt):
            rec['refs'].append([('x', ref)])
    ejlmod3.printrecsummary(rec)
    
jnlfilename = '%s%s.%s_%s' % (jnl, rec['vol'], rec['issue'], ejlmod3.stampoftoday())
ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
