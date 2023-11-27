# -*- coding: utf-8 -*-
#harvest theses from Rice University
#JH+FS: 2021-11-04
#FS: 2023-01-10



#https://hdl.handle.net/1911/13110
#https://repository.rice.edu/search?scope=5aa4da72-3dd6-4196-9ca2-0eb55538e94e&spc.page=1&f.degreelevel=Doctoral,equals&spc.sf=dc.date.issued&spc.sd=DESC&spc.rpp=100

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from time import sleep
import ejlmod3
import os
import getopt
import sys
import re

pages = 3
rpp = 100
skipalreadyharvested = True

publisher = 'Rice U.'
jnlfilename = 'THESES-RICE-%s' % (ejlmod3.stampoftoday())

boring = ['Humanities', 'History', 'Chemistry', 'Biochemistry+and+Cell+Biology',
          'Bioengineering', 'Chemical+and+Biomolecular+Engineering',
          'Civil+and+Environmental+Engineering', 'Music', 'Political+Science',
          'Psychology', 'Social+Sciences', 'Ecology+and+Evolutionary+Biology',
          'Systems%2C+Synthetic+and+Physical+Biology', 'Business']

# Initilize Webdriver
options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

# In this variable all the data is saved
recs = []

# The function that opens the subsite
def get_subsite(rec):
    ejlmod3.printprogress('-', [[rec['link']], [len(recs)]])
    if rec['hdl'] in alreadyharvested:
        print('    %s already in backup' % (rec['hdl']))
        return
    elif not ejlmod3.checkinterestingDOI(rec['hdl']):
        print('    %s is uninteresting' % (rec['hdl']))
        return
    for degree in rec['degrees']:
        if degree in boring:
            print('    skip "%s"' % (degree))
            ejlmod3.adduninterestingDOI(rec['hdl'])
            return
        elif degree in ['Computer+Science']:
            rec['fc'] = 'c'
        elif degree in ['Mathematics']:
            rec['fc'] = 'm'
        elif degree in ['Statistics']:
            rec['fc'] = 's'
    driver.get(rec['link'])
    soup = BeautifulSoup(driver.page_source, 'lxml')
    ejlmod3.metatagcheck(rec, soup, ['citation_pdf_url', 'DC.subject', 'citation_date',
                                     'DCTERMS.abstract', 'citation_title', 'citation_author'])
    # Check if it is a Master Thesis
    for degree_div in soup.find_all('div', attrs={'class': 'simple-item-view-degree'}):
        if re.search('Master', degree_div.text):
            print("["+ rec['link']  +"] is not a PhD thesis! --> Skipping this thesis")
            ejlmod3.adduninterestingDOI(hdl)
            return None

    # author's affiliation
    rec['autaff'][-1].append(publisher)

    # Ge the advisor name
    advisor_div = soup.find_all('div', attrs={'class': 'simple-item-view-advisor'})
    if len(advisor_div) == 1:
        rec['supervisor'] = []
        advisors = advisor_div[0].text.split('\n')[2].split(';')
        for advisor in advisors:
            rec['supervisor'].append([advisor])

    recs.append(rec)
    ejlmod3.printrecsummary(rec)
    sleep(10)
    return

for page in range(pages):
    # Get Index Page
    url = 'https://scholarship.rice.edu/handle/1911/13110/discover?rpp=' + str(rpp) + '&etal=0&scope=&group_by=none&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc&filtertype_0=degreelevel&filter_relational_operator_0=equals&filter_0=Doctoral'
    ejlmod3.printprogress("=", [[page+1, pages], [url]])
    driver.get(url)
    tocpage = BeautifulSoup(driver.page_source, 'lxml')
    # Get all the articles
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://scholarship.rice.edu'):
        get_subsite(rec)
    sleep(10)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
driver.close()
