# -*- coding: utf-8 -*-
#harvest theses from Liege U.
#FS: 2022-10-27

import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

publisher = 'Liege U.'

pages = 1
rpp = 10
years = 2
skiptooold = True
skipalreadyharvested = True

jnlfilename = 'THESES-LIEGE-%s' % (ejlmod3.stampoftoday())

options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for (degree, authority1) in [('PhD', 'DSO%2FF03'), ('Habilitation', 'DSO%2FF04')]:
    for (fc, authority2) in [('m', 'G03'), ('', 'G04'), ('a', 'G05'), ('c', 'C05')]:
        for page in range(pages):
            tocurl = 'https://orbi.uliege.be/simple-search?query=&filter_1=type%3A%3Aauthority%3A%3A' + authority1 + '&filter=classification%3A%3Aauthority%3A%3A' + authority2 + '&sort_by=available_dt&order=desc&rpp=' + str(rpp) + '&start=' + str(rpp*page)
            ejlmod3.printprogress('=', [[degree, authority2], [page+1, pages], [tocurl]])
            try:
                driver.get(tocurl)
                tocpage = BeautifulSoup(driver.page_source, features="lxml")
                time.sleep(3)
            except:
                print("retry %s in 180 seconds" % (tocurl))
                time.sleep(180)
                driver.get(tocurl)
                tocpage = BeautifulSoup(driver.page_source, features="lxml")                
            for div in tocpage.body.find_all('div', attrs = {'class' : 'card-result'}):
                for a in div.find_all('a', attrs = {'class' : 'stretched-link'}):
                    if a.has_attr('href') and re.search('handle', a['href']):
                        rec = {'jnl' : 'BOOK', 'tc' : 'T', 'supervisor' : [], 'keyw' : [], 'autaff' : []}
                        rec['artlink'] = 'https://orbi.uliege.be' + a['href']
                        rec['hdl'] = re.sub('.*le\/', '', a['href'])
                        rec['degree'] = degree
                        if fc:
                            rec['fc'] = fc
                        if skiptooold and not ejlmod3.checknewenoughDOI(rec['hdl']):
                            print('    %s too old ' % (rec['hdl']))
                        elif not skipalreadyharvested or not rec['hdl'] in alreadyharvested:
                            prerecs.append(rec)
            print('    %3i records so far' % (len(prerecs)))

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        ejlmod3.metatagcheck(rec, artpage, ['citation_title'])
        rec['tit']
        time.sleep(3)        
    except:
        print("retry %s in 180 seconds" % (rec['artlink']))
        time.sleep(180)
        driver.get(rec['artlink'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_date', 'citation_pdf_url', 'citation_keywords',
                                        'citation_language', 'DCTERMS.abstract', 'DCTERMS.extent'])
    #persons
    for div in artpage.body.find_all('div', attrs = {'class' : 'row'}):
        for th in div.find_all('div', attrs = {'class' : 'col-md-3'}):
            tht = th.text.strip()
            if re.search('(Author|Promot)', tht):
                if re.search('Author', tht):
                    marc = 'autaff'
                else:
                    marc = 'supervisor'
                for td in div.find_all('div', attrs = {'class' : 'col-md-9'}):
                    for person in td.find_all('div'):
                        (orcid, aff) = (False, False)
                        for sup in person.find_all('sup'):
                            for a in sup.find_all('a'):
                                if a.has_attr('href') and re.search('orcid', a['href']):
                                    orcid = re.sub('.*org\/', 'ORCID:', a['href'])
                            sup.decompose()
                        for span in person.find_all('span', attrs = {'class' : 'text-muted'}):
                            aff = span.text.strip()
                            span.decompose()
                        rec[marc].append([re.sub(';', '', person.text).strip()])
                        if orcid: rec[marc][-1].append(orcid)
                        if marc == 'autaff':
                            rec[marc][-1].append(publisher)
                        elif aff:                            
                            rec[marc][-1].append(aff)


        #author
        for h3 in div .find_all('h3'):
            if not 'autaff' in list(rec.keys()):
                rec['autaff'] = [[ re.sub('^by ', '', h3.text.strip()), publisher ]]                        
    #non PhD
    year = re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])
    if int(year) > ejlmod3.year(backwards=years):
        rec['MARC'] = [('502', [('b', rec['degree']), ('c', publisher), ('d', year)])]
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.addtoooldDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
driver.quit()
