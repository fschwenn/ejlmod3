# -*- coding: utf-8 -*-
#harvest theses from Cornell
#FS: 2019-12-09
#FS: 2022-11-07
#FS: 2023-11-27


import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json
import undetected_chromedriver as uc

publisher = 'Cornell U.'
jnlfilename = 'THESES-CORNELL-%s' % (ejlmod3.stampoftoday())

rpp = 10
yearstocover = 2
pages = 30

hdr = {'User-Agent' : 'Magic Browser'}
options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
options.binary_location='/usr/bin/google-chrome'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

    
allhdls = []
recs = []
boring = ['Architecture', 'Industrial and Labor Relations', 'Hotel Administration',
          'Natural Resources', 'Fiber Science and Apparel Design', 
          'Chemistry and Chemical Biology', 'Systems Engineering', 'Human Development',
          'Asian Studies', 'Aerospace Engineering', 'Animal Science',
          'Anthropology', 'Applied Economics and Management', 'Architecture',
          'Asian Literature, Religion and Culture', 
          'Atmospheric Science', 'Biochemistry, Molecular and Cell Biology',
          'Biological and Environmental Engineering', 'Biomedical and Biological Sciences',
          'Biomedical Engineering', 'Biophysics', 'Chemical Engineering',
          'Chemistry and Chemical Biology', 'City and Regional Planning',
          'Civil and Environmental Engineering', 'Computational Biology',
          'Design and Environmental Analysis', 'Ecology and Evolutionary Biology',
          'Economics', 'English Language and Literature', 'Entomology',
          'Fiber Science and Apparel Design', 'Food Science and Technology',
          'Genetics, Genomics and Development', 'Geological Sciences',
          'Germanic Studies', 'Government', 'Horticulture', 'Human Development',
          'Information Science', 'Linguistics', 'Management', 'Plant Biology',
          'Plant Breeding', 'Policy Analysis and Management', 'Romance Studies',
          'Science and Technology Studies', 'Systems Engineering',
          'Materials Science and Engineering', 'Mechanical Engineering',
          'Medieval Studies', 'Microbiology', 'Music', 'Natural Resources',
          'Neurobiology and Behavior', 'Nutrition', 'Philosophy',          
          'Operations Research and Information Engineering', 'Performing and Media Arts', 
          'History of Art, Archaeology, and Visual Studies', 'History',
          'Africana Studies', 'Archaeology', 'Art', 'Classics', 'Communication',
          'Comparative Literature', 'Development Sociology', 'Global Development',
          'Law', 'Plant Pathology and Plant-Microbe Biology', 'Psychology',
          'Regional Science', 'Sociology', 'Soil and Crop Sciences']

for page in range(pages):
    tocurl = 'https://ecommons.cornell.edu/collections/5893a6ea-7af3-41d7-abc6-04bcd26ab5df?cp.page=' + str(page+1)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    #req = urllib.request.Request(tocurl, headers=hdr)
    #tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    try:
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        prerecs = ejlmod3.ngrx(tocpage, 'https://ecommons.cornell.edu', ['dc.description', 'dc.identifier.uri', 'dc.title',
                                                                          'dc.contributor.author', 'dc.description.abstract',
                                                                          'dc.identifier.doi', 'dc.identifier.other',
                                                                          'dc.subject', 'dc.title', 'dcterms.license',
                                                                          'thesis.degree.discipline', 'thesis.degree.grantor',
                                                                          'thesis.degree.level', 'thesis.degree.name',
                                                                          'dc.date.issued', 'thesis.degree.discipline',
                                                                          'dc.rights.uri', 'dc.description.embargo'], boring=boring)
    except:
        time.sleep(120)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        prerecs = ejlmod3.ngrx(tocpage, 'https://ecommons.cornell.edu', ['dc.description', 'dc.identifier.uri', 'dc.title',
                                                                          'dc.contributor.author', 'dc.description.abstract',
                                                                          'dc.identifier.doi', 'dc.identifier.other',
                                                                          'dc.subject', 'dc.title', 'dcterms.license',
                                                                          'thesis.degree.discipline', 'thesis.degree.grantor',
                                                                          'thesis.degree.level', 'thesis.degree.name',
                                                                          'dc.date.issued', 'thesis.degree.discipline',
                                                                          'dc.rights.uri', 'dc.description.embargo'], boring=boring)
    for rec in prerecs:                        
        keepit = True
        for note in rec['note']:
            if note == 'THESIS.DEGREE.DISCIPLINE=Statistics':
                rec['fc'] = 's'
            elif note in ['THESIS.DEGREE.DISCIPLINE=Mathematics', 'THESIS.DEGREE.DISCIPLINE=Applied Mathematics']:
                rec['fc'] = 'm'
            elif note in ['THESIS.DEGREE.DISCIPLINE=Computer Science']:
                rec['fc'] = 'c'
            elif re.search('^[MB]\.[AS]\.,', note) or note[:6] in ['M.F.A.', 'D.M.A.']:
                print('   skip "%s"' % (note))
                keepit = False
        if 'embargo' in rec:
            if re.search('^\d\d\d\d\-\d\d\-\d\d', rec['embargo']):
                if rec['embargo'] > ejlmod3.stampoftoday():
                    print('   embargo', rec['embargo'], ':-(')
                    if 'pdf_url' in rec:
                        del(rec['pdf_url'])
                else:
                    print('   embargo', rec['embargo'], ':-)')
        if keepit:
            recs.append(rec)
    print('               %i records so far ' % (len(recs)))
    time.sleep(15)

       
ejlmod3.writenewXML(recs, publisher, jnlfilename)
