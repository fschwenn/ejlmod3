# -*- coding: utf-8 -*-
#harvest UPenn, Philadelphia
#FS: 2022-11-10
#FS: 2023-11-23

import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

publisher = 'UPenn, Philadelphia'
pages = 6
rpp = 40
skipalreadyharvested = True
boring = ['City & Regional Planning', 'Romance Languages', 'Cell & Molecular Biology',
          'History of Art', 'Applied Economics', 'Accounting', 'Africana Studies', 'Anthropology', 'Architecture',
          'Art & Archaeology of Mediterranean World', 'Biochemistry & Molecular Biophysics', 'Bioengineering',
          'Biology', 'Chemical and Biomolecular Engineering', 'Chemistry', 'Classical Studies', 'Communication',
          'Comparative Literature and Literary Theory', 'Demography', 'Economics', 'Education', 'English',
          'Epidemiology & Biostatistics', 'Finance', 'Genomics & Computational Biology',
          'Health Care Management & Economics', 'History and Sociology of Science', 'History', 'Immunology',
          'Legal Studies & Business Ethics', 'Linguistics', 'Management', 'Marketing', 'Chemistry',
          'Materials Science & Engineering', 'Mechanical Engineering & Applied Mechanics', 'Music', 'Neuroscience',
          'Nursing', 'Operations & Information Management', 'Pharmacology', 'Political Science', 'Psychology',
          'Social Welfare', 'Sociology', 'South Asia Regional Studies', 'History and Sociology of Science',
          'Immunology', 'Ancient History', 'Criminology', 'East Asian Languages & Civilizations',
          'Germanic Languages and Literature', 'Managerial Science and Applied Economics',
          'Near Eastern Languages & Civilizations', 'Philosophy', 'Religious Studies', 'City and Regional Planning',
          'Earth & Environmental Science', 'Healthcare Systems', 'Insurance & Risk Management',
          'Art and Archaeology of the Mediterranean World', 'Biochemistry and Molecular Biophysics',
          'Cell and Molecular Biology', 'Chief Learning Officer', 'East Asian Languages and Civilizations',
          'Epidemiology and Biostatistics', 'Ethics and Legal Studies', 'Genomics and Computational Biology',
          'Materials Science and Engineering', 'Mechanical Engineering and Applied Mechanics',
          'Operations, Information and Decisions']

jnlfilename = 'THESES-UPENN-%s' % (ejlmod3.stampoftoday())


if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

prerecs = []
date = False
for page in range(pages):
    tocurl = 'https://repository.upenn.edu/search?scope=34a5f2e5-48bc-428c-adf2-e3b1e2609515&configuration=diss-thesis-search&spc.page=' + str(page+1) + '&spc.sf=dc.date.accessioned&spc.sd=DESC&spc.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(7)
    except:
        print("retry %s in 180 seconds" % (tocurl))
        time.sleep(180)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    for article in tocpage.find_all('ds-truncatable', attrs={'class': 'ng-star-inserted'}):
        for a in article.find_all('a', attrs={'target' : '_self'}):
            if a.has_attr('href'):
                rec = {'jnl' : 'BOOK', 'tc' : 'T', 'date' : date, 'note' : [],
                       'supervisor' : [], 'keyw' : []}
                rec['link'] = "https://repository.upenn.edu%s" % (a['href'])
                if ejlmod3.checkinterestingDOI(rec['link']):
                    prerecs.append(rec)
    print('  ', len(prerecs),'records so far')

i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        driver.get(rec['link'] + '/full')
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(7)
        ejlmod3.metatagcheck(rec, artpage, ['citation_pdf_url', 'citation_title', 'citation_author'])
        rec['autaff']
    except:
        print("retry %s in 180 seconds" % (rec['link']))
        time.sleep(180)
        driver.get(rec['link'] + '/full')
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        ejlmod3.metatagcheck(rec, artpage, ['citation_pdf_url', 'citation_title', 'citation_author'])
        time.sleep(1)
    for tr in artpage.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) == 3:
            th = tds[0].text.strip()
            td = tds[1].text.strip()
        # Get the author name
        if th == 'dc.contributor.author':
            rec['autaff'] = [[td]]
        # Get the issued date
        elif th == 'dc.date.issued':
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
        elif th in ['supervisor', 'dc.contributor.supervisor', 'dc.contributor.advisor']:
            rec['supervisor'].append([td])
        # pages
        elif th in ['dc.extent']:
            rec['pages'] = td
        # Check if it is a PhD
        elif th == 'dc.description.degree':
            if td != 'Doctor of Philosophy (PhD)':
                if td in ['M.Sc.', 'B.Sc.', 'D.Sc.', 'M.A.', 'B.A.', "Master's degree",
                          'Master of Applied Positive Psychology', 'Doctor of Social Work (DSW)',
                          'Master of Science in Animal Welfare and Behavior (MSc AWB)',
                          'Master of Science in Historic Preservation (MSHP)']:
                    print('\tskip "%s"' % (td))
                    keepit = False
                else:
                    rec['note'].append('DEGREE:::' + td)
        #department
        elif th in ['dc.contributor.department', 'upenn.graduate.group']:
            if td in boring:
                keepit = False
            elif td == 'Computer and Information Science':
                rec['fc'] = 'c'
            elif td == 'Statistics':
                rec['fc'] = 's'
            elif td in ['Mathematics and Statistics', 'Mathematics',
                        'Applied Mathematics and Computational Science']:
                rec['fc'] = 'm'
            else:
                rec['note'].append('GROUP:::'+td)
        #license
        elif th == 'dc.rights.uri':
            if re.search('creativecommons', td):
                rec['license'] = {'url' : td}
        #embargo
        elif th == 'dc.embargo.liftdate':
            rec['embargo'] = td
            
    if keepit:
        if 'autaff' in rec:
            if len(rec['autaff'][-1]) == 1:
                rec['autaff'][-1].append(publisher)
            if skipalreadyharvested and '20.2000/LINK/' + re.sub('\W', '', rec['link'][4:]) in alreadyharvested:
                pass
            elif skipalreadyharvested and 'hdl' in rec and rec['hdl'] in alreadyharvested:
                pass
            else:
                ejlmod3.printrecsummary(rec)
                recs.append(rec)
        else:
            print('   not able to harvest')
    else:
        ejlmod3.adduninterestingDOI(rec['link'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
