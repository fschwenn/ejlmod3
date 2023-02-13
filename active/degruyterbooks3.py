# -*- coding: UTF-8 -*-
#program to harvest PDe Gruyter Book series
# FS 2016-01-03
# FS 2023-02-08

import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
import time
import undetected_chromedriver as uc

from bs4 import BeautifulSoup

urltrunc = 'https://www.degruyter.com'
publisher = 'De Gruyter'

serial = sys.argv[1]
skipalreadyharvested = True

options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/chromium-browser'
options.add_argument('--headless')
chromeversion = int(re.sub('Chro.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


jnlfilename = 'dg' + serial + ejlmod3.stampoftoday()
if serial == 'GSTMP':
    jnl = "De Gruyter Stud.Math.Phys."
    tocurl = 'https://www.degruyter.com/view/serial/GSTMP-B?contents=toc-59654'
    tocurl = 'https://www.degruyter.com/serial/GSTMP-B/html#volumes'

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

print(tocurl)

driver.get(tocurl)
tocpage = BeautifulSoup(driver.page_source, features="lxml")
print(tocpage.text)
#get volumes
recs = []
i = 0
divs = tocpage.body.find_all('div', attrs = {'class' : 'resultTitle'})
for div in divs:
    for a in div.find_all('a'):
        i += 1
        rec = {'tc' : 'B', 'jnl' : jnl, 'auts' : []}
        rec['artlink'] = urltrunc + a['href']
        ejlmod3.printprogress('-', [[i, len(divs)], [rec['artlink']]])
        #DOI
        rec['doi'] = re.sub('.*doi\/(10.1515.*)\/html', r'\1', rec['artlink'])        
        if skipalreadyharvested and 'doi' in alreadyharvested:
            continue
        #get details
        artfilename = '/tmp/dg%s' % (re.sub('[\(\)\/]', '_', rec['doi']))
        if not os.path.isfile(artfilename):
            time.sleep(10)
            os.system("wget -T 300 -t 3 -q -O %s %s" % (artfilename, rec['artlink']))
        inf = open(artfilename, 'r')
        volpage = BeautifulSoup(''.join(inf.readlines()), features="lxml")
        inf.close()
        ejlmod3.metatagcheck(rec, volpage, ['citation_title', 'citation_keywords', 'citation_isbn',
                                            'citation_publication_date', 'dc.identifier',
                                            'citation_author', 'og:description'])
        #volume
        for div in volpage.find_all('div', attrs = {'class' : 'font-content '}):
            for a in div.find_all('a', attrs = {'class' : 'c-Button--primary"'}):
                atext = a.text.strip()
                if re.search('\d$', atext):
                    rec['vol'] = re.sub('.*\D', '', atext)
        #pages
        for dd in volpage.find_all('dd', attrs = {'class' : 'pagesarabic'}):
            rec['pages'] = re.sub('[\n\t\r]', '', dd.text.strip())
        if not 'pages' in list(rec.keys()):
            for li in volpage.find_all('li', attrs = {'class' : 'pageCounts'}):
                rec['pages'] = 0
                for li2 in li.find_all('li'):
                    rec['pages'] += int(re.sub('\D', '', li2.text.strip()))
        #ISBNS
        for dd in volpage.find_all('dd', attrs = {'class' : 'publisherisbn'}):
            if 'isbn' in list(rec.keys()):
                del rec['isbn']
            if 'isbns' in list(rec.keys()): 
                rec['isbns'].append([('a', re.sub('[\n\t\r\-]', '', dd.text.strip()))])
            else:
                rec['isbns'] = [[('a', re.sub('[\n\t\r\-]', '', dd.text.strip()))]]
        for li in volpage.find_all('li', attrs = {'class' : 'isbn'}):
            if 'isbn' in list(rec.keys()):
                del rec['isbn']
            if 'isbns' in list(rec.keys()):
                rec['isbns'].append([('a', re.sub('\D', '', li.text.strip()))])
            else:
                rec['isbns'] = [[('a', re.sub('\D', '', li.text.strip()))]]
        #authors
        if not rec['auts']:
            for div in volpage.find_all('div', attrs = {'class' : 'content-box'}):
                for h2 in div.find_all('h2'):
                    if re.search('Author', h2.text):
                        for strong in div.find_all('strong'):
                            rec['auts'].append(strong.text.strip())
        if not rec['auts']:
            for div in volpage.find_all('div', attrs = {'class' : 'productInfo'}):
                for h2 in div.find_all('h2'):
                    if re.search('Author', h2.text):
                        for strong in div.find_all('strong'):
                            rec['auts'].append(strong.text.strip())
                        if not rec['auts']:
                            h2.decompose()
                            rec['auts'].append(re.sub(',*', '', div.text.strip()))
        if not rec['auts']:
            del(rec['auts'])
            rec['autaff'] = []
            for div in volpage.find_all('div', attrs = {'class' : 'productInfo'}):
                for h3 in div.find_all('h3'):
                    if re.search('[Aa]uthor information', h3.text):
                        for div2 in div.find_all('div', attrs = {'class' : 'metadataInfoFont'}):
                            for s in div2.find_all('strong'):
                                rec['autaff'].append([s.text.strip()])
                                s.decompose()
                            if rec['autaff']:
                                rec['autaff'][-1].append(div2.text.strip())
                            else:
                                rec['autaff'] = [re.split(',', div2.text.strip(), 1)]
            #print rec['autaff']
        if 'date' in list(rec.keys()):
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
        else:
            print('  no date!')
            ejlmod3.printrec(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
