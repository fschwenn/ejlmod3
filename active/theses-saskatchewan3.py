# -*- coding: utf-8 -*-
#harvest theses from Saskatchewan U.
#FS: 2020-09-25
#FS: 2023-04-17

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time


publisher = 'Saskatchewan U.'
jnlfilename = 'THESES-SASKATCHEWAN-%s' % (ejlmod3.stampoftoday())

rpp = 50
pages = 5
skipalreadyharvested = False
boring = ['Chemistry', 'Veterinary Biomedical Sciences', 'English', 'Educational Foundations',
          'History', 'School of Environment and Sustainability', 'Soil Science',
          'Agricultural and Resource Economics', 'Archaeology and Anthropology',
          'Biomedical Engineering', 'Chemical and Biological Engineering',
          'Educational Administration', 'Electrical and Computer Engineering',
          'Interdisciplinary Centre for Culture and Creativity', 'Interdisciplinary Studies',
          'Johnson-Shoyama Graduate School of Public Policy', 'Nursing', 'Pharmacology',
          'School of Public Health', 'Veterinary Pathology', 'Toxicology Centre',
          'Animal and Poultry Science', 'Biology', 'Civil and Geological Engineering',
          'Community Health and Epidemiology', 'Geography and Planning',
          'Large Animal Clinical Sciences', 'Law', 'Mechanical Engineering', 'Medicine',
          'Microbiology and Immunology', 'Psychology', 'Sociology', 'Veterinary Microbiology',
          'Anatomy and Cell Biology', 'Art and Art History', 'Biochemistry', 'Curriculum Studies',
          'Food and Bioproduct Sciences', 'Geological Sciences', 'Kinesiology',
          'Bioresource Policy, Business and Economics', 'Environmental Engineering',
          'Nutrition', 'Pathology and Laboratory Medicine', 'Western College of Veterinary Medicine',
          'Pharmacy and Nutrition', 'Physiology', 'Plant Sciences', 'School of Physical Therapy']
boring += ['Master of Science (M.Sc.)', 'Master of Education (M.Ed.)', 'Master of Arts (M.A.)',
           'Master of Nursing (M.N.)', 'Master of Public Policy (M.P.P.)',
           'Master of Laws (LL.M.)', 'Master of Fine Arts (M.F.A.)']
boringdegrees = []
for b in boring:
    boringdegrees.append(re.sub(' ', '+', re.sub('\(', '%28', re.sub('\)', '%29', b))))

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []


hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for page in range(pages):
    tocurl = 'https://harvest.usask.ca/handle/10388/381/discover?sort_by=dc.date.issued_dt&order=desc&rpp=' + str(rpp) + '&page=' + str(page+1)
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    prerecs += ejlmod3.getdspacerecs(tocpage, 'https://harvest.usask.ca', alreadyharvested=alreadyharvested, boringdegrees=boringdegrees)
    print('  %4i records so far' % (len(prerecs)))

i = 0
recs = []
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'DC.subject',
                                        'DCTERMS.abstract', 'citation_pdf_url'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'DC.creator':
                if re.search('\d{4}\-\d{4}\-', meta['content']):
                    rec['autaff'][-1].append('ORCID:' + meta['content'])
                else:
                    rec['autaff'] = [[  meta['content'] ]]
    rec['autaff'][-1].append(publisher)
    for div in artpage.body.find_all('div', attrs = {'class' : 'table'}):
        for h5 in div.find_all('h5'):
            h5t = h5.text.strip()
            h5.decompose()
            #degree
            if h5t == 'Degree':
                rec['degree'] = div.text.strip()
                rec['note'].append(rec['degree'])
                if rec['degree'] in boring:
                    print('   skip "%s"' % (rec['degree']))
                    keepit = False
            #Department
            elif h5t == 'Department':
                rec['department'] = div.text.strip()
                rec['note'].append(rec['department'])
                if rec['department'] in boring:
                    print('   skip "%s"' % (rec['department']))
                    keepit = False
            #supervisor
            elif h5t == 'Supervisor':
                for span in div.find_all('span'):
                    for sv in re.split('; ', span.text.strip()):
                        if re.search('@', sv):
                            email = re.sub('.* (.*?@[\w\.]+).*', r'EMAIL:\1', sv)
                            sv = re.sub(' .*?@.*', '', sv)
                            rec['supervisor'].append([sv, email])
                        else:
                            rec['supervisor'].append([sv])
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
