# -*- coding: utf-8 -*-
#harvest Hong Kong U. Sci. Tech. theses
#FS: 2021-12-21
#FS: 2022-10-24

import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

publisher = 'Hong Kong U. Sci. Tech.'

pages = 1
skipalreadyharvested = True

jnlfilename = 'THESES-HongKongUSciTech-%s' % (ejlmod3.stampoftoday())

options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
#options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

if skipalreadyharvested:    
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for (dep, fc) in [('Computer+Science', 'c'), ('Physics', ''), ('Mathematics', 'm')]:
    for i in range(pages):
        tocurl = 'http://lbezone.ust.hk/rse/?paged=' + str(i+1) + '&s=%2A&sort=pubyear&order=desc&fq=degree_cc_Ph.D._ss_department_cc_' + dep + '&scopename=electronic-theses&show_result_ui=list'
        ejlmod3.printprogress('=', [[dep], [i+1, pages], [tocurl]])
        try:
            driver.get(tocurl)
            tocpage = BeautifulSoup(driver.page_source, features="lxml")
            time.sleep(3)
        except:
            print("retry %s in 180 seconds" % (tocurl))
            time.sleep(180)
            driver.get(tocurl)
            tocpage = BeautifulSoup(driver.page_source, features="lxml")
        for li in tocpage.body.find_all('li', attrs = {'class' : 'thumbnails_li'}):
            for a in li.find_all('a'):
                rec = {'jnl' : 'BOOK', 'tc' : 'T', 'note' : [], 'supervisor' : [], 'keyw' : []}
                rec['artlink'] = a['href']
                rec['doi'] = '30.3000/HongKongUSciTech/' + re.sub('\W', '', a['href'][10:])
                if fc:
                    rec['fc'] = fc
                if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                    prerecs.append(rec)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (rec['artlink']))
        time.sleep(180)
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    #informations at top of page
    for div in artpage.body.find_all('div', attrs = {'id' : 'content-full'}):
        #title
        for h3 in div .find_all('h3', attrs = {'class' : 'post-title'}):
            rec['tit'] = h3.text.strip()
            h3.decompose()
        #author
        for h3 in div .find_all('h3'):
            if not 'autaff' in list(rec.keys()):
                rec['autaff'] = [[ re.sub('^by ', '', h3.text.strip()), publisher ]]
    #abstract
    for div2 in artpage.body.find_all('div', attrs = {'class' : 'abstract_content'}):
        for strong in div2.find_all('strong'):
            if strong.text == 'Abstract':
                strong.decompose()
        rec['abs'] = re.sub(' *\[ *Hide abstract.*', '', div2.text.strip())
        div2.replace_with('XXXABSTRACTXXX')
    #information at bottom of page
    for table in artpage.body.find_all('table', attrs = {'class' : 'table-striped'}):
        for tr in table.find_all('td'):
            for child in tr.children:
                try:
                    child.name
                except:
                    pass
                if child.name == 'strong':
                    ult = child.text.strip()
                elif child.name == 'ul':
                    #supervisor
                    if ult == 'Supervisors':
                        for li in child.find_all('li'):
                            rec['supervisor'].append([ li.text.strip() ])
                    #keywords
                    elif ult == 'Subjects':
                        for li in child.find_all('li'):
                            rec['keyw'].append(li.text.strip())
                    #language
                    elif ult == 'Language':
                        language = child.text.strip()
                        if language != 'English':
                            rec['language'] = language
                    #DOI
                    elif ult == 'DOI':
                        rec['doi'] = child.text.strip()
    #pages, year
    divt = re.sub('[\n\t\r]', ' ', div.text.strip())
    divt = re.sub('XXXABSTRACTXXX.*', '', divt)
    rec['date'] = re.sub('.*THESIS *([12]\d\d\d).*', r'\1', divt)
    if re.search('\d pages', divt):
        rec['pages'] = re.sub('.*?(\d+) pages.*', r'\1', divt)   
    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
driver.quit()
