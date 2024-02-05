# -*- coding: utf-8 -*-
#harvest Connecticut U. theses
#FS: 2023-04-18

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Connecticut U.'
jnlfilename = 'THESES-CONNECTICUT-%s' % (ejlmod3.stampoftoday())

pages = 20
skipalreadyharvested = True
years = 2 

boringdepartments = ['Biomedical Science', 'Kinesiology', 'Communication Sciences',
                     'Psychology', 'Nursing', 'Business Administration', 'Philosophy',
                     'Agricultural and Resource Economics', 'Animal Science', 'Anthropology',
                     'Biomedical Engineering', 'Chemical Engineering', 'Chemistry',
                     'Civil Engineering', 'Curriculum and Instruction', 'Educational Leadership',
                     'Ecology and Evolutionary Biology', 'Economics', 'Italian', 'History',
                     'Educational Psychology', 'Electrical Engineering', 'English',
                     'Genetics and Genomics', 'Geography', 'Geological Sciences', 'German', 
                     'Human Development and Family Studies', 'Educational Leadership (Ed.D.)',
                     'Learning, Leadership, and Education Policy', 'Linguistics',
                     'Literatures, Languages, and Cultures', 'Materials Science and Engineering',
                     'Materials Science', 'Mechanical Engineering', 'Medieval Studies',
                     'Molecular and Cell Biology', 'Natural Resources: Land, Water, and Air',
                     'Nutritional Science', 'Oceanography', 'Pharmaceutical Science',
                     'Physiology and Neurobiology', 'Plant Science', 'Political science',
                     'Polymer Science', 'Social Work', 'Sociology', 'Education Administration',
                     'Adult Learning', 'Biochemistry', 'Cell Biology',
                     'Comparative Literary and Cultural Studies', 'Educational Technology',
                     'Environmental Engineering', 'French', 'Microbiology', 'Music',
                     'Natural Resources: Land, Water, and Air', 'Pathobiology', 'Public Health',
                     'Spanish', 'Special Education', 'Structural Biology and Biophysics',
                     'Speech, Language, and Hearing Sciences']

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

for page in range(pages):
    tocurl = 'https://collections.ctdigitalarchive.org/islandora/object/20002%3AUniversityDissertations?page=' + str(page) + '&sort=fgs_createdDate_dt%20desc&islandora_solr_search_navigation=0'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for div in tocpage.body.find_all('div', attrs = {'class' : 'islandora-solr-search-results'}):
        for dl in div.find_all('dl', attrs = {'class' : 'solr-grid-field'}):
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : []}
            keepit = True
            for div2 in dl.find_all('div', attrs = {'class' : 'solr-value dc-date'}):
                year = div2.text.strip()
                if re.search('^[12]\d\d\d$', year):
                    rec['year'] = year
                    if int(rec['year']) <= ejlmod3.year(backwards=years):
                        print('    %s too old' % (rec['year']))
                        keepit = False
            for dt in dl.find_all('dt'):
                for a in dt.find_all('a'):
                    rec['link'] = 'https://collections.ctdigitalarchive.org' + a['href']
                    if keepit:
                        if ejlmod3.checkinterestingDOI(rec['link']):
                            prerecs.append(rec)
                        else:
                            print('    %s uninteresting' % (rec['link']))
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(5)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(4)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    for dl in artpage.find_all('dl', attrs = {'class' : 'islandora-inline-metadata'}):
        for child in dl.children:
            try:
                name = child.name
            except:
                continue
            if name == 'dt':
                dtt = child.text.strip()
            elif name == 'dd':
                #field of study
                if dtt == 'Field of Study':
                    fos = child.text.strip()
                    if fos in boringdepartments:
                        keepit = False
                        print('   skip "%s"' % (fos))
                    else:
                        rec['note'].append('FOS:::'+fos)
                #abstract
                elif dtt == 'Description':
                    rec['abs'] = child.text.strip()
                #Date
                elif dtt == 'Date':
                    rec['date'] = child.text.strip()
                #HDL
                elif dtt == 'Link':
                    for a in child.find_all('a'):
                        if a.has_attr('href') and re.search('handle.net', a['href']):
                            rec['hdl'] = re.sub('.*handle.net\/', '', a['href'])
                #Degree Level
                elif dtt == 'Degree Level':
                    if child.text.strip() != 'Doctoral':
                        rec['note'].append('LEVEL:::'+child.text.strip())
                #Genre
                elif dtt == 'Genre':
                    if child.text.strip() != 'doctoral dissertations':
                        rec['note'].append('GENRE:::'+child.text.strip())
                #Contributors
                elif dtt == 'Contributor':
                    for a in child.find_all('a'):
                        if re.search('\(Creator', a.text):
                            rec['autaff'] = [[re.sub(' *\(.*', '', a.text.strip()), publisher]]
                        elif re.search('\(Major Adviso', a.text):
                            rec['supervisor'].append([re.sub(' *\(.*', '', a.text.strip())])
    if keepit:
        if not skipalreadyharvested or not 'hdl' in rec or not rec['hdl'] in alreadyharvested:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
