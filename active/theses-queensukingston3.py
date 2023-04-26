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
          'Pharmacology and Toxicology', 'Physiology']
          
recs = []


options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)



def get_subsite(url):
    if ejlmod3.checkinterestingDOI(url):
        print("    [%s] --> Harversting data" % url)
        rec = {'tc': 'T', 'jnl': 'BOOK', 'link': url, 'note' : []}

        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        sleep(5)
    else:        
        print("    [%s]     uninteresting" % url)
        return

    # Read out the table
    table_section = soup.find_all('div', attrs={'class': 'ds-table-responsive'})
    if len(table_section) != 1:
        return

    table = table_section[0]
    rows = table.find_all('tr')

    if len(rows) <= 0:
        return

    for row in rows:
        cols = row.find_all('td')
        if len(cols) <= 0:
            continue

        row_header = cols[0].text
        row_data = cols[1].text
        
        # Get the author name
        if row_header.find('author') != -1:
            rec['autaff'] = [[row_data]]
        elif row_header.find('date.issued') != -1:
            # Get the issued date
            rec['date'] = row_data
        elif row_header.find('identifier.uri') != -1:
            # Get the handle
            splitted_handle_link = row_data.split('/')
            handle = "%s/%s" % (splitted_handle_link[-2], splitted_handle_link[-1])
            rec['hdl'] = handle
        elif row_header.find('abstract') != -1:
            # Get the abstract
            rec['abs'] = row_data
        elif row_header.find('language') != -1:
            # Get the Language
            rec['lang'] = row_data.upper()
        elif row_header.find('subject') != -1:
            # Get the keywords
            if 'keyw' in list(rec.keys()):
                rec['keyw'].append(row_data)
            else:
                rec['keyw'] = [row_data]
        elif row_header.find('title') != -1:
            # Get the title
            rec['tit'] = row_data
        elif row_header.find('supervisor') != -1:
            # Get the supervisor
            if 'supervisor' in list(rec.keys()):
                rec['supervisor'].append([row_data])
            else:
                rec['supervisor'] = [[row_data]]
        elif row_header.find('degree') != -1 and row_header.find('grantor') == -1:
            # Check if it is a PhD
            if row_data.find('PhD') == -1:
                print("\t[PhD Check] This is not a PhD! --> Skipping")
                ejlmod3.adduninterestingDOI(url)
                return
            #print "\t[PhD Check] PhD detected --> Saving"
        elif row_header.find('dc.contributor.department') != -1:
            if row_data in boring:
                print('\tskip "%s"' % (row_data))
                ejlmod3.adduninterestingDOI(url)
                return
            elif row_data == 'Computing':
                rec['fc'] = 'c'
            elif row_data == 'Mathematics and Statistics':
                rec['fc'] = 'm'
            else:
                rec['note'].append(row_data)

    # Get the pdf link
    for meta in soup.find_all('meta', attrs={'name' : 'citation_pdf_url'}):
        rec['pdf_link'] = meta['content']

    #license
    for meta in soup.find_all('meta', attrs={'name' : 'DC.rights'}):
        if re.search('creativecommons.org', meta['content']):
            rec['license'] = {'url' : meta['content']}
    if 'pdf_link' in list(rec.keys()):
        if 'license' in list(rec.keys()):
            rec['FFT'] = rec['pdf_link']
        else:
            rec['hidden'] = rec['pdf_link']

    #date
    if not 'date' in rec:
        for meta in soup.find_all('meta', attrs={'name' : 'citation_date'}):
            rec['date'] = meta['content'][:10] 

    if not skipalreadyharvested or not 'hdl' in rec or not rec['hdl'] in alreadyharvested:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)



for page in range(pages):
    tocurl = 'https://qspace.library.queensu.ca/handle/1974/290/discover?order=desc&rpp=' + str(rpp) + '&sort_by=dc.date.available_dt&order=desc&page=' + str(page+1) + '&group_by=none&etal=0'
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    driver.get(tocurl)
    articles = BeautifulSoup(driver.page_source, 'lxml').find_all('div', attrs={'class': 'ds-artifact-item'})
    for article in articles:
        article_link = article.find_all('a')
        if len(article_link) == 2:
            if article_link[0].get('href') is not None:
                href = "https://qspace.library.queensu.ca%s?show=full" % article_link[0].get('href')
                get_subsite(href)
    sleep(10)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
