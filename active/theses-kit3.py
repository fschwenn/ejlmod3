# -*- coding: utf-8 -*-
#program to harvest theses from Karlsruhe Insitute of Technolgy
# FS 2020-01-13

import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import time 
import undetected_chromedriver as uc


publisher = 'KIT, Karlsruhe'
jnlfilename = 'THESES-KIT-%s' % (ejlmod3.stampoftoday())
pages = 4 


options = uc.ChromeOptions()
options.headless=True
#options.binary_location='/opt/google/chrome/google-chrome'
##options.binary_location='/opt/google/chrome/chrome'
options.binary_location='/usr/bin/chromium-browser'
options.add_argument('--headless')
driver = uc.Chrome(version_main=103, options=options)
#driver = uc.Chrome(browser_executable_path='/usr/bin/chromedriver', options=options)
#driver = uc.Chrome(options=options)


recs = []
for page in range(pages):
    tocurl = 'https://primo.bibliothek.kit.edu/primo-explore/search?query=any,contains,*&tab=kit&sortby=date&vid=KIT&facet=local5,include,istHochschulschrift&mfacet=local3,include,istFachPhys,1&mfacet=local3,include,istFachMath,1&mode=simple&offset=' + str(10*page) + '&fn=search'
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    newrecs = []
    try:
        driver.get(tocurl)
        time.sleep(15)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(4)
    except:
        print("retry %s in 300 seconds" % (tocurl))
        time.sleep(300)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    for div in tocpage.find_all('div', attrs = {'class' : 'list-item-wrapper'}):
        for div2 in div.find_all('div', attrs = {'class' : 'list-item-primary-content'}):
            rec = {'jnl' : 'BOOK', 'tc' : 'T', 'note' : [], 'keyw' : [], 'supervisor' : []}
            rec['data-recordid'] = div2['data-recordid']
            rec['artlink'] = 'https://primo.bibliothek.kit.edu/primo-explore/fulldisplay?docid=' + div2['data-recordid']+ '&context=L&vid=KIT&lang=de_DE'
            recs.append(rec)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['artlink']]])
    isbns = []
    try:
        driver.get(rec['artlink'])
        time.sleep(4)
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(4)
    except:
        print("retry %s in 300 seconds" % (tocurl))
        time.sleep(300)
        driver.get(rec['artlink'])
        time.sleep(4)        
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    tabelle = {}
    for div in artpage.body.find_all('div', attrs = {'class' : 'full-view-inner-container'}):
        for div2 in div.find_all('div', attrs = {'class' : 'standorte'}):
            for div3 in div2.find_all('div', attrs = {'class' : 'item-details-element-container'}):
                rec['keyw'] += re.split(' \/ ', div3.text.strip())
        for div2 in div.find_all('div', attrs = {'class' : 'full-view-section-content'}):
            for div3 in div2.find_all('div', attrs = {'class' : 'layout-block-xs'}):
                for span in div3.find_all('span', attrs = {'class' : 'bold-text'}):
                    for span2 in div3.find_all('span', attrs = {'class' : 'ng-binding'}):
                        if span.text.strip() in list(tabelle.keys()):
                            tabelle[span.text.strip()].append(span2.text.strip())
                        else:
                            tabelle[span.text.strip()] = [span2.text.strip()]
    if 'Titel' in list(tabelle.keys()):
        rec['tit'] = re.sub(' *\/ von.*', '', tabelle['Titel'][0])
    if 'Jahr' in list(tabelle.keys()):
        rec['year'] = tabelle['Jahr'][0]
    if 'Sprache' in list(tabelle.keys()):
        if tabelle['Sprache'][0] == 'Deutsch':
            rec['language'] = 'German'
    if 'Verfasser' in list(tabelle.keys()):
        rec['autaff'] = [[ re.sub(' *\[.*', '', tabelle['Verfasser'][0]), publisher ]]
    if 'Auflage / Umfang' in list(tabelle.keys()):
        if re.search('\d\d+ Seiten', tabelle['Auflage / Umfang'][0]):
            rec['pages'] = re.sub('.*?(\d\d+) Seiten.*', r'\1', tabelle['Auflage / Umfang'][0])
    if 'Identifikator' in list(tabelle.keys()):
        for ide in tabelle['Identifikator']:
            if re.search('DOI: 10', ide):
                rec['doi'] = re.sub('.*?(10.*)', r'\1', ide)
            elif re.search('\D978.?\d.?\d.?\d', ide):
                isbn = re.sub('\-', '', re.sub('.*?(978.*[\dX]).*', r'\1', ide))
                if not isbn in isbns:
                    isbns.append(isbn)
    if 'doi' in list(rec.keys()):
        if re.search('^10.5445', rec['doi']):
            print('   checking primo-page')
            try:
                time.sleep(10)
                artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open('https://doi.org/'+rec['doi']), features="lxml")
            except:
                try:
                    print("retry %s in 180 seconds" % ('https://doi.org/'+rec['doi']))
                    time.sleep(180)
                    artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open('https://doi.org/'+rec['doi']), features="lxml")
                except:
                    pass
            for meta in artpage.head.find_all('meta'):
                if meta.has_attr('name'):
                    #abstract
                    if meta['name'] == 'citation_abstract':
                        rec['abs'] = meta['content']
                    #ISBN
                    elif meta['name'] == 'citation_isbn':
                        isbn = re.sub('\-', '', meta['content'])
                        if not isbn in isbns:
                            isbns.append(isbn)
                    #fulltext
                    elif meta['name'] == 'citation_pdf_url':
                        rec['FFT'] = meta['content']
            for table in artpage.body.find_all('table', attrs = {'class' : 'table'}):
                for tr in table.find_all('tr'):
                    tds = tr.find_all('td')
                    if len(tds) == 2:
                        #Keywords
                        if re.search('Schlagw', tds[0].text.strip()):
                            for keyw in re.split(', ', tds[1].text.strip()):
                                if not keyw in rec['keyw']:
                                    rec['keyw'].append(keyw)
                        #Language
                        elif tds[0].text.strip() == 'Sprache':
                            if tds[1].text.strip() != 'Englisch':
                                if tds[1].text.strip() == 'Deutsch':
                                    rec['language'] = 'german'
                                else:
                                    rec['language'] = tds[1].text.strip()
                        #pages
                        elif tds[0].text.strip() == 'Umfang':
                            if re.search('\d\d\d', tds[1].text.strip()):
                                rec['pages'] = re.sub('.*?(\d\d\d+).*', r'\1', tds[1].text.strip())
                        #supervisor
                        elif re.search('Betreuer', tds[0].text):
                            for br in tds[1].find_all('br'):
                                br.replace_with(';;;')
                            for sv in re.split(' *;;; *', tds[1].text.strip()):
                                rec['supervisor'].append([ re.sub('Prof\. ', '', re.sub('Dr\. ', '', sv)) ])
                        #date
                        elif re.search('Pr.fungsdatum', tds[0].text):
                            rec['MARC'] = [ ['500', [('a', 'Presented on ' + re.sub('(\d\d).(\d\d).(\d\d\d\d)', r'\3-\2-\1', tds[1].text.strip()))] ] ]
                        #institue
                        elif tds[0].text.strip() == 'Institut':
                            rec['note'].append(tds[1].text.strip())
                        #urn
                        elif tds[0].text.strip() == 'Identifikator':
                            for br in tds[1].find_all('br'):
                                br.replace_with('#')
                            for tdt in re.split('#',  re.sub('[\n\t\r]', '#', tds[1].text.strip())):
                                if re.search('urn:nbn', tdt):
                                    rec['urn'] = re.sub('.*?(urn:nbn.*)', r'\1', tdt.strip())
            #license
            for a in artpage.body.find_all('a', attrs = {'class' : 'with-popover'}):
                if a.has_attr('data-content'):
                    adc = a['data-content']
                    if re.search('creativecommons.org', adc):
                        rec['license'] = {'url' : re.sub('.*(http.*?) target.*', r'\1', adc)}
            #english abstract
            for div in artpage.body.find_all('div', attrs = {'id' : 'KIT_KITopen_abstract_eng'}):
                for span in div.find_all('span', attrs = {'class' : 'kit_link_on_white_background'}):
                    span.decompose()
                    rec['abs'] = div.text.strip()
    else:
        rec['doi'] = '20.2000/KIT/'+rec['data-recordid']
        rec['link'] = rec['artlink']
    if isbns:
        rec['isbns'] = []
        for isbn in isbns:
            rec['isbns'].append([('a', isbn)])
    
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
driver.quit()
