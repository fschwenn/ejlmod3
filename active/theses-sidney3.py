# -*- coding: utf-8 -*-
#harvest theses from Sydney U. 
#FS: 2019-12-11


import sys
import os
import urllib.request, urllib.error, urllib.parse
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Sydney U.'
jnlfilename = 'THESES-SIDNEY-%s' % (ejlmod3.stampoftoday())

rpp = 100
pages = 4
skipalreadyharvested = True
        
boring = ['Faculty of Medicine and Health, The University of Sydney School of Pharmacy',
          'Faculty of Arts and Social Sciences, School of Languages and Cultures',
          'Faculty of Arts and Social Sciences, School of Literature, Art and Media',
          'Faculty of Engineering, School of Biomedical Engineering',
          'Faculty of Medicine and Health, School of Medical Sciences',
          'Faculty of Science, School of Psychology',
          'Faculty of Arts and Social Sciences, School of Philosophical and Historical Inquiry',
          'Faculty of Arts and Social Sciences, School of Social and Political Sciences',
          'Faculty of Arts and Social Sciences',
          'Faculty of Arts and Social Sciences, Sydney School of Education and Social Work',
          'Faculty of Engineering, School of Aerospace Mechanical and Mechatronic Engineering',
          'Faculty of Engineering, School of Chemical and Biomolecular Engineering',
          'Faculty of Engineering, School of Civil Engineering',
          'Faculty of Medicine and Health, Central Clinical School',
          'Faculty of Medicine and Health, Children&apos;s Hospital Westmead Clinical School',
          'Faculty of Medicine and Health, Nepean Clinical School',
          'Faculty of Medicine and Health, Northern Clinical School',
          'Faculty of Medicine and HealthPublic Health',
          'Faculty of Medicine and Health, School of Health Sciences', 'Faculty of Medicine and Health',
          'Faculty of Medicine and Health, The University of Sydney School of Dentistry',
          'Faculty of Medicine and Health, The University of Sydney School of Public Health',
          'Faculty of Medicine and Health, The University of Sydney Susan Wakil School of Nursing and Midwifery',
          'Faculty of Science, School of Chemistry', 'Faculty of Science, School of Geosciences',
          'Faculty of Science, School of History and Philosophy of Science',
          'Faculty of Science, School of Life and Environmental Sciences',
          'Faculty of Science, Sydney Institute of Veterinary Science',
          'Sydney Conservatorium of Music', 'Sydney School of Architecture, Design and Planning',
          'The University of Sydney Business School, Discipline of Accounting',
          'The University of Sydney Business School, Discipline of Business Analytics',
          'The University of Sydney Business School, Discipline of Business Law',
          'The University of Sydney Business School, Discipline of Marketing',
          'The University of Sydney Business School, Discipline of Strategy, Innovation and Entrepreneurship',
          'The University of Sydney Business School', 'The University of Sydney Law School',
          'Faculty of Arts and Social Sciences, School of Art, Communication and English',
          'Faculty of Arts and Social Sciences, School of Economics',
          'Faculty of Arts and Social Sciences, School of Humanities',
          'Faculty of EngineeringSchool of Aerospace, Mechanical, and Mechatronic Engineering',
          'Faculty of EngineeringSchool of Electrical and Information Engineering',
          'Faculty of Medicine and HealthCentral Clinical School',
          'Faculty of Medicine and Health, Children&apos;s Hospital Westmead Clinical School',
          'Faculty of Medicine and Health, Concord Clinical School',
          'Faculty of Medicine and Health, NHMRC Clinical Trials Centre',
          'Faculty of Medicine and Health, Save Sight Institute',
          'Faculty of Medicine and Health, Sydney Medical School',
          'Faculty of Medicine and Health, Sydney Pharmacy School',
          'Faculty of Medicine and Health, Sydney School of Health Sciences',
          'Faculty of Medicine and Health, Sydney School of Public Health',
          'Faculty of Medicine and Health, The Matilda Centre for Research in Mental Health and Substance Use',
          'Faculty of Medicine and Health, Westmead Clinical School',
          'School of Languages and Cultures', 'School of Philosophical and Historical Inquiry',
          'The University of Sydney Business School, Discipline of Business Information Systems',
          'The University of Sydney Business School, Discipline of Finance',
          'Faculty of Arts and Social SciencesSchool of Social and Political Sciences',
          'Faculty of Arts and Social Sciences, Sydney College of the Arts',
          "Faculty of Medicine and Health, Children's Hospital Westmead Clinical School",
          'Faculty of Medicine and HealthNorthern Clinical School',
          'Faculty of Medicine and Health, Sydney Dental School',
          'The University of Sydney Business School, Institute of Transport and Logistics Studies (ITLS)',
          'The University of Sydney School of Architecture, Design and Planning',
          'Faculty of Engineering, School of Project Management', 'Faculty of Engineering',
          'Faculty of Medicine and HealthSydney Medical School',
          'Faculty of Medicine and Health, The University of Sydney School of Medicine',
          'Faculty of Arts and Social SciencesSchool of Economics']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

hdr = {'User-Agent' : 'Magic Browser'} 
options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

prerecs = []
for j in range(pages):
    tocurl = 'https://ses.library.usyd.edu.au/handle/2123/35/browse?rpp=' + str(rpp) + '&sort_by=3&type=dateissued&offset=' + str(j*rpp) + '&etal=-1&order=DESC'
    ejlmod3.printprogress('=', [[j+1, pages], [tocurl]])
    #req = urllib.request.Request(tocurl, headers=hdr)
    #tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    driver.get(tocurl)
    tocpage = BeautifulSoup(driver.page_source, features="lxml")
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://ses.library.usyd.edu.au', alreadyharvested=alreadyharvested):
        if ejlmod3.checkinterestingDOI(rec['hdl']):
            prerecs.append(rec)
    print('        %4i records so far' % (len(prerecs)))
    time.sleep(10)

i = 0
recs = []
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        #artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        driver.get(rec['link'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 18 seconds" % (rec['link']))
            time.sleep(18)
            #artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
            driver.get(rec['link'])
            artpage = BeautifulSoup(driver.page_source, features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'DC.subject', 'DCTERMS.abstract',
                                        'citation_pdf_url'])
    #author
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.creator'}):
        if re.search('\d\d\d\d\-\d\d\d\d',  meta['content']):
            rec['autaff'][-1].append('ORCID:' + meta['content'])
        else:
            author = re.sub(' *\[.*', '', meta['content'])
            rec['autaff'] = [[ author ]]
    rec['autaff'][-1].append(publisher)
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    if not 'pdf_url' in rec:
        for div in artpage.find_all('div'):
            for a in div.find_all('a'):
                if a.has_attr('href') and re.search('bistream.*\.pdf', a['href']):
                    divt = div.text.strip()
                    if re.search('Restricted', divt):
                        print(divt)
                    else:
                        rec['pdf_url'] = 'https://ses.library.usyd.edu.au' + re.sub('\?.*', '', a['href'])
    #faculty
    for div in artpage.find_all('div', attrs = {'class' : 'item-page-field-wrapper'}):
        for h3 in div.find_all('h3'):
            if h3.text == 'Faculty/School':
                h3.decompose()
                faculty = div.text.strip()
                if faculty in boring:
                    keepit = False
                    ejlmod3.adduninterestingDOI(rec['hdl'])
                else:
                    rec['note'].append(faculty)
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
                
ejlmod3.writenewXML(recs, publisher, jnlfilename)
