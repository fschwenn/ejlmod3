# -*- coding: utf-8 -*-
#harvest theses from Oklahoma
#FS: 2019-11-06
#FS: 2022-09-20

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import codecs
import time

numopages = 5
articlesperpage = 50
skipalreadyharvested = True

boring = ['Agricultural+Economics', 'Animal+Science', 'Applied+Educational+Studies', 'Biomedical+Sciences',
          'Business+Administration', 'Chemistry', 'Civil+Engineering', 'Comparative+Biomedical+Sciences',
          'Curriculum+Studies', 'Educational+Leadership+and+Policy+Studies', 'Educational+Psychology',
          'Education', 'English', 'Forensic+Science', 'Geology', 'Health+and+Human+Performance', 'History',
          'Human+Sciences', 'Industrial+Engineering+and+Management', 'Integrative+Biology',
          'Language%2C+Literacy+and+Culture', 'Mechanical+Engineering', 'Psychology', 'Sociology',
          'Natural+Resource+Ecology+and+Management', 'School+Administration', 'School+Psychology',
          'Biosystems+and+Agricultural+Engineering', 'Crop+Science', 'Education+Leadership+and+Policy+Studies',
          'Fire+and+Emergency+Management', 'Fire+and+Emergency+Management+Administration',
          'Educational+Administration', 'Food+Science', 'Mathematics+Education',
          'Microbiology+and+Molecular+Genetics', 'Nutritional+Sciences', 'Plant+Pathology',
          'Human+Development+and+Family+Science', 'Learning%2C+Design+and+Technology',
          'Microbiology%2C+Cell+and+Molecular+Biology', 'Plant+Biology', 'Zoology',
          'Agricultural+Education', 'Biochemistry+and+Molecular+Biology', 'Chemical+Engineering',
          'Clinical+Psychology', 'Counseling+Psychology', 'Economics', 'Electrical+Engineering',
          'Entomology+and+Plant+Pathology', 'Environmental+Science', 'Geography',
          'Biosystems+Engineering', 'Counseling', 'Educational+Leadership+Studies',
          'Educational+Technology', 'Education+in+Workforce+and+Adult+Education', 'Education+Leadership',
          'Entomology', 'Fungal+Biology', 'Higher+Education', 'Hospitality+Administration',
          'Human+Development+and+Family+Sciences', 'Leisure', 'Materials+Science+and+Engineering',
          'Microbial+Ecology', 'Microbiology+and+Molecular+biology', 'Organic+Chemistry', 'Plant+Science',
          'Professional+Education+Studies', 'Professional+Writing', 'Science+Education',
          'Social+Foundations+of+Education', 'Veterinary+Biomedical+Science', 'Workforce+and+Adult+Education',
          'Health%2C+Leisure+and+Human+Performance', 'Interior+Design', 'Mechanical+and+Aerospace+Engineering',
          'Soil+Science', 'Statistics', 'Veterinary+Biomedical+Sciences']
boring += ['Weitzenhoffer Family College of Fine Arts::School of Music',
           'Dodge Family College of Arts and Sciences::Department of Chemistry and Biochemistry',
           'College of Atmospheric and Geographic Sciences::Department of Geography and Environmental Sustainability',
           'College of Atmospheric and Geographic Sciences::School of Meteorology',
           'Dodge Family College of Arts and Sciences::Department of Anthropology',
           'Dodge Family College of Arts and Sciences::Department of Biology',
           'Dodge Family College of Arts and Sciences::Department of Communication',
           'Dodge Family College of Arts and Sciences::Department of Economics',
           'Dodge Family College of Arts and Sciences::Department of English',
           'Dodge Family College of Arts and Sciences::Department of Health and Exercise Science',
           'Dodge Family College of Arts and Sciences::Department of Philosophy',
           'Dodge Family College of Arts and Sciences::Department of Political Science',
           'Dodge Family College of Arts and Sciences::Department of Psychology',
           'Gallogly College of Engineering::School of Aerospace and Mechanical Engineering',
           'Gallogly College of Engineering::School of Civil Engineering and Environmental Science',
           'Gallogly College of Engineering::School of Electrical and Computer Engineering',
           'Gallogly College of Engineering::School of Industrial and Systems Engineering',
           'Gallogly College of Engineering::Stephenson School of Biomedical Engineering',
           'Jeannine Rainbolt College of Education::Department of Educational Leadership and Policy Studies',
           'Jeannine Rainbolt College of Education::Department of Educational Psychology',
           'Mewbourne College of Earth and Energy::Mewbourne School of Petroleum and Geological Engineering',
           'Michael F. Price College of Business', 'Christopher C. Gibbs College of Architecture',
           'College of Arts and Sciences::Department of Anthropology',
           'College of Arts and Sciences::Department of Biology',
           'College of Arts and Sciences::Department of Chemistry and Biochemistry',
           'College of Arts and Sciences::Department of Communication',
           'College of Arts and Sciences::Department of Economics',
           'College of Arts and Sciences::Department of English',
           'College of Arts and Sciences::Department of Health and Exercise Science',
           'College of Arts and Sciences::Department of History of Science',
           'College of Arts and Sciences::Department of History',
           'College of Arts and Sciences::Department of Microbiology and Plant Biology',
           'College of Arts and Sciences::Department of Modern Languages, Literatures, and Linguistics',
           'College of Arts and Sciences::Department of Philosophy',
           'College of Arts and Sciences::Department of Political Science',
           'College of Arts and Sciences::Department of Psychology',
           'College of Arts and Sciences::Department of Sociology',
           'Dodge Family College of Arts and Sciences:: Department of Chemistry and Biochemistry',
           'Dodge Family College of Arts and Sciences::Department of History of Science',
           'Dodge Family College of Arts and Sciences::Department of History of Science, Technology, and Medicine',
           'Dodge Family College of Arts and Sciences::Department of History',
           'Dodge Family College of Arts and Sciences::Department of Microbiology and Plant Biology',
           'Dodge Family College of Arts and Sciences::Department of Modern Languages, Literatures, and Linguistics',
           'Gallogly College of Engineering::School of Chemical, Biological and Materials Engineering',
           'Gallogly College of Engineering', 'Gaylord College of Journalism and Mass Communication',
           'Jeannine Rainbolt College of Education::Department of Instructional Leadership and Academic Curriculum',
           'Mewbourne College of Earth and Energy::School of Geosciences',
           'Christopher C. Gibbs College of Architecture',
           'College of Arts and Sciences', 'Jeannine Rainbolt College of Education',
           'Mewbourne College of Earth and Energy::Conoco Phillips School of Geology and Geophysics',
           'Mewbourne College of Earth and Energy', 'Weitzenhoffer Family College of Fine Arts',
           'Weitzenhoffer Family College of Fine Arts::School of Visual Arts',
           'Nutritional+Science,Oklahoma+State+University',
           'Teaching%2C+Learning+and+Leadership,Oklahoma+State+University',
           'Petroleum+Engineering,Oklahoma+State+University',
           'Applied+Educational+Studies--Aviation+and+Space+Option,Oklahoma+State+University']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested('THESES-OKLAHOMA')
else:
    alreadyharvested = []

hdr = {'User-Agent' : 'Magic Browser'}
for uni in [('Oklahoma U.', '11244/10476'), ('Oklahome State U.', '11244/10462')]:
    publisher = uni[0]
    jnlfilename = 'THESES-%s-%s' % (re.sub('\W', '', uni[0].upper()), ejlmod3.stampoftoday())
    prerecs = []
    for i in range(numopages):
        tocurl = 'https://shareok.org/handle/%s/browse?rpp=%i&sort_by=2&type=dateissued&offset=%i&etal=-1&order=DESC' % (uni[1], articlesperpage, articlesperpage*i)
        ejlmod3.printprogress('=', [[uni[0]], [i+1, numopages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        for rec in ejlmod3.getdspacerecs(tocpage, 'https://shareok.org'):
            keepit = True
            if 'degrees' in rec:
                for degree in rec['degrees']:
                    if degree in boring:
                        keepit = False
                    elif degree in ['Computer+Science']:
                        rec['fc'] = 'c'
                    elif degree in ['Mathematics']:
                        rec['fc'] = 'm'
            if keepit:
                if rec['hdl'] in alreadyharvested:
                    print('    %s already in backup' % (rec['hdl']))
                else:
                    prerecs.append(rec)
        print ('  %4i records so far' % (len(prerecs)))
        time.sleep(10)
    i = 0
    recs = []
    for rec in prerecs:
        keepit = True
        i += 1
        ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
        try:
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+'?show=full'), features="lxml")
            time.sleep(3)
        except:
            try:
                print("retry %s in 180 seconds" % (rec['link']))
                time.sleep(180)
                artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+'?show=full'), features="lxml")
            except:
                print("no access to %s" % (rec['link']))
                continue
        ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'DC.subject', 'DCTERMS.abstract', 'DC.rights', 'citation_pdf_url'])
        for meta in artpage.head.find_all('meta'):
            if meta.has_attr('name'):
                #author
                if meta['name'] == 'DC.creator':
                    author = re.sub(' *\[.*', '', meta['content'])
                    rec['autaff'] = [[ author ]]
                    rec['autaff'][-1].append(publisher)
        for tr in artpage.body.find_all('tr', attrs = {'class' : 'ds-table-row'}):
            (label, word) = ('', '')
            for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
                label = td.text.strip()
            for td in tr.find_all('td', attrs = {'class' : 'word-break'}):
                word = td.text.strip()
            #ORCID
            if re.search('shareok.orcid', label):
                rec['autaff'] = [[ author, 'ORCID:' + re.sub('.*.org/', '', word), publisher ]]
            #supervisor
            elif re.search('dc.contributor.advisor', label):
                rec['supervisor'] = [[ word, publisher ]]
            #department
            elif re.search('ou.group', label):
                if word in boring:
                    keepit = False
                elif word in ['Dodge Family College of Arts and Sciences::Department of Mathematics',
                              'College of Arts and Sciences::Department of Mathematics',
                              'College of Arts and Sciences::Department of Mathematics']:
                    rec['fc'] = 'm'
                elif word == 'Gallogly College of Engineering::School of Computer Science':
                    rec['fc'] = 'c'
                else:
                    rec['note'].append('DEPARTMENT:%s' % (word))
        if keepit:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
        else:
            ejlmod3.adduninterestingDOI(rec['hdl'])
    ejlmod3.writenewXML(recs, publisher, jnlfilename)

