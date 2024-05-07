# -*- coding: utf-8 -*-
# harvest theses from Queen's University at Kingston
# JH: 2022-04-09
# FS: 2023-04-25

from bs4 import BeautifulSoup
from time import sleep
import time
import os
import sys
import ejlmod3
import re
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

Scheiss Javascript

publisher = "Queen's U., Kingston"
jnlfilename = 'THESES-QUEENSUKINGSTON-%s' % (ejlmod3.stampoftoday())

skipalreadyharvested = True
pages = 10
rpp = 50 
boring = ['Art History', 'Civil Engineering', 'Environmental Studies', 'Rehabilitation Science',
          'Geological Sciences and Geological Engineering', 'Mechanical and Materials Engineering',
          'Political Studies', 'Aging and Health', 'Biology', 'Biomedical and Molecular Sciences',
          'Business', 'Chemical Engineering', 'Cultural Studies', 'Economics', 'Education',
          'English Language and Literature', 'Geography and Planning', 'History', 'Neuroscience Studies',
          'Kinesiology and Health Studies', 'Law', 'Mining Engineering', 'Nursing', 'Psychology', 
          'Pathology and Molecular Medicine', 'Philosophy', 'Sociology', 'Public Health Sciences',
          'Chemistry', 'Electrical and Computer Engineering', 'Gender Studies', 'French Studies',
          'Anatomy and Cell Biology', 'Biochemistry', 'Community Health and Epidemiology', 'English',
          'French', 'Geography', 'German', 'Management', 'Microbiology and Immunology',
          'Pharmacology and Toxicology', 'Physiology', 'Translational Medicine',
          'School of Architecture, Design and Planning,', 'School of Biology & Environmental Science,',
          'School of Communication and Arts ,', 'School of Design,',
          'School of Psychology & Counselling,', 'The School of Music,',
          'UQ Centre for Clinical Research,']
          
recs = []


options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
#options.binary_location='/usr/bin/chromium'
#options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

urlswithoutauthors = []

def get_subsite(url):
    if ejlmod3.checkinterestingDOI(url):
        print("    [%s] --> Harversting data" % url)
        rec = {'tc': 'T', 'jnl': 'BOOK', 'link': url, 'note' : [], 'keyw' : [],
               'supervisor' : []}
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        sleep(5)
    else:        
        print("    [%s]     uninteresting" % url)
        return

    ejlmod3.metatagcheck(rec, soup, ['citation_pdf_url', 'citation_publication_date',
                                    'citation_language'])
    for tr in soup.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) == 3:
            th = tds[0].text.strip()
            td = tds[1].text.strip()
        # Get the author name
        if th == 'dc.contributor.author':
            rec['autaff'] = [[td, publisher]]
        # Get the issued date
        elif th == 'date.issued':
            rec['date'] = td
        # Get the handle
        elif th in ['dc.identifier.uri', 'identifier.uri']:
            rec['hdl'] =re.sub('.*handle\/', '', td)
            # Get the abstract
        elif th in ['dc.description.abstract', 'abstract']:
            rec['abs'] = td
        # Get the keywords
        elif th in ['dc.subject', 'subject']:
            rec['keyw'].append(td)
        # Get the title
        elif th in ['dc.title', 'title']:
            rec['tit'] = td
        # Get the supervisor
        elif th in ['supervisor', 'dc.contributor.supervisor']:
            rec['supervisor'].append([td])
        # Check if it is a PhD
        elif th == 'dc.description.degree':
            if td != 'PhD':
                if td in ['M.Sc.', 'B.Sc.', 'D.Sc.', 'M.A.', 'B.A.']:
                    print('\tskip "%s"' % (td))
                else:
                    print('\tskip "%s" ?!?!' % (td))                    
                ejlmod3.adduninterestingDOI(url)
                return
            #print "\t[PhD Check] PhD detected --> Saving"
        #department
        elif th == 'dc.contributor.department':
            if td in boring:
                print('\tskip "%s"' % (td))
                ejlmod3.adduninterestingDOI(url)
                return
            elif td == 'Computing':
                rec['fc'] = 'c'
            elif td == 'Mathematics and Statistics':
                rec['fc'] = 'm'
            else:
                rec['note'].append(td)
        #license
        elif th == 'dc.rights.uri':
            rec['license'] = {'url' : td}
        #embargo
        elif th == 'dc.embargo.liftdate':
            rec['embargo'] = td

    #check embargo
    if 'license' in rec and 'pdf_url' in rec and 'embargo' in rec:
        if rec['embargo'] > ejlmod3.stampoftoday():
            del rec['pdf_url']
            print('   Embargo until %s :-(' % (rec['embargo']))


    #authors:
    if url == 'https://qspace.library.queensu.ca/items/b29b74bd-4e63-4f3a-ac0a-a872cbd6e962/full':
        rec['autaff'] = [['Benjamin Sum Ki Tam', publisher]]
    elif url == 'https://qspace.library.queensu.ca/items/50e68a83-21b1-49d1-ad8a-61d8f357843a/full':
        rec['autaff'] = [['Poushimin, Rana', publisher]]
    elif url == 'https://qspace.library.queensu.ca/items/065182a7-fad7-48ad-9f28-89753485d6c4/full':
        rec['autaff'] = [['Dongze Wang', publisher]]
    elif url == 'https://qspace.library.queensu.ca/items/b2ade516-b03a-4444-b1b9-b838422833cf/full':
        rec['autaff'] = [['Sarakbi, Diana', publisher]]
    elif url == 'https://qspace.library.queensu.ca/items/2e11f607-1685-4ee2-93dc-e768330ce805/full':
        rec['autaff'] = [['Lebedev, Dmitry', publisher]]
    

    if not skipalreadyharvested or not 'hdl' in rec or not rec['hdl'] in alreadyharvested:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
        if not 'autaff' in rec:
            urlswithoutauthors.append(url)
    else:
        ejlmod3.printrecsummary(rec)



for page in range(pages):
    tocurl = 'https://qspace.library.queensu.ca/handle/1974/290/discover?order=desc&rpp=' + str(rpp) + '&sort_by=dc.date.available_dt&order=desc&page=' + str(page+1) + '&group_by=none&etal=0'
    tocurl = 'https://qspace.library.queensu.ca/collections/28264e28-1843-437c-abca-776a363a1c1c?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp) 
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    driver.get(tocurl)
    WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CLASS_NAME, 'ng-star-inserted')))
    tocpage = BeautifulSoup(driver.page_source, 'lxml')
    articles = tocpage.find_all('ds-truncatable', attrs={'class': 'item-list-title'})
    if not articles:
        sleep(3)
        driver.get(tocurl)
        WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CLASS_NAME, 'ng-star-inserted')))
        tocpage = BeautifulSoup(driver.page_source, 'lxml')
        articles = tocpage.find_all('ds-truncatable', attrs={'class': 'item-list-title'})
    if articles:
        for article in articles:
            print(article)
            for a in article.find_all('a', attrs={'target' : '_self'}):
                if a.has_attr('href'):
                    href = "https://qspace.library.queensu.ca%s/full" % (a['href'])
                    get_subsite(href)
    else:
        print(tocpage.text)
    print('\n  %4i/%4i/%4i records so far\n' % (len(recs), (page+1)*rpp, pages*rpp))
    sleep(10)

ejlmod3.writenewXML(recs, publisher, jnlfilename)

if urlswithoutauthors:
    print(urlswithoutauthors)
