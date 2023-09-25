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

publisher = "Queen's U., Kingston"
jnlfilename = 'THESES-QUEENSUKINGSTON-%s' % (ejlmod3.stampoftoday())

skipalreadyharvested = True
pages = 50
rpp = 10 
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
          'Pharmacology and Toxicology', 'Physiology', 'Translational Medicine']
          
recs = []


options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)



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
        elif th == 'identifier.uri':
            rec['hdl'] =re.sub('.*handle\/', '', td)
            # Get the abstract
        elif th == 'abstract':
            rec['abs'] = td
        # Get the keywords
        elif th == 'subject':
            rec['keyw'].append(td)
        # Get the title
        elif th == 'title':
            rec['tit'] = td
        # Get the supervisor
        elif th == 'supervisor':
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

    if not skipalreadyharvested or not 'hdl' in rec or not rec['hdl'] in alreadyharvested:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.printrecsummary(rec)



for page in range(pages):
    tocurl = 'https://qspace.library.queensu.ca/handle/1974/290/discover?order=desc&rpp=' + str(rpp) + '&sort_by=dc.date.available_dt&order=desc&page=' + str(page+1) + '&group_by=none&etal=0'
    tocurl = 'https://qspace.library.queensu.ca/collections/28264e28-1843-437c-abca-776a363a1c1c?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp) 
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    driver.get(tocurl)
    articles = BeautifulSoup(driver.page_source, 'lxml').find_all('ds-truncatable', attrs={'class': 'ng-star-inserted'})
    for article in articles:
        for a in article.find_all('a', attrs={'target' : '_self'}):
            if a.has_attr('href'):
                href = "https://qspace.library.queensu.ca%s/full" % (a['href'])
                get_subsite(href)
    print('\n  %4i/%4i/%4i records so far\n' % (len(recs), (page+1)*rpp, pages*rpp))
    sleep(10)

ejlmod3.writenewXML(recs, publisher, jnlfilename)

