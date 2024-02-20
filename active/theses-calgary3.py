# -*- coding: utf-8 -*-
#harvest theses from Calgary
#FS: 2020-11-21
#FS: 2023-11-28

from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc
import os


publisher = 'Calgary U.'
rpp = 40
pages = 10
skipalreadyharvested = True

jnlfilename = 'THESES-CALGARY-%s' % (ejlmod3.stampoftoday())
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

boring = ['Biological Sciences', 'Chemistry', 'Geoscience', 'Psychology – Clinical', 'Economics', 'Medicine – Neuroscience']
boring += ['Biological+Sciences', 'Chemistry', 'Geoscience', 'Psychology+%E2%80%93+Clinical', 'Medicine+%E2%80%93+Neuroscience']
boring += ['Archaeology', 'Communication and Media Studies', 'Medicine – Immunology',
           'Education Graduate Program – Educational Psychology',
           'Education Graduate Program – Educational Research', 'Engineering – Biomedical',
           'Engineering – Chemical &a; Petroleum', 'Engineering – Civil', 'Engineering – Geomatics',
           'Engineering – Mechanical &a; Manufacturing', 'English', 'Kinesiology',
           'Languages, Literatures and Cultures', 'Law', 'Linguistics',
           'Medicine – Biochemistry and Molecular Biology', 'Medicine – Community Health Sciences',
           'Medicine – Gastrointestinal Sciences', 'Medicine – Medical Sciences',
           'Medicine – Microbiology &a; Infectious Diseases', 'Military &a; Strategic Studies',
           'Music', 'Nursing', 'Political Science', 'Psychology', 'Social Work', 'Sociology',
           'Veterinary Medical Sciences', 'Urban and Regional Planning', 'Geography',
           'Business, Haskayne School of Business', 'Computational Media Design',
           'Environmental Design', 'Haskayne School of Business: Management', 'History',
           'Religious Studies', 'Accounting', 'Bioinformatics', 'Business Administration--Management',
           'Economics--Agricultural', 'Education--Business', 'Education--Health', 'Education--Religious',
           'Education--Technology', 'History--African', 'History--European', 'History--Modern', 'Theater',
           'Urban and Regional Planning', 'Anthropology', 'French, Italian and Spanish',
           'Medicine – Cardiovascular/Respiratory Science', 'Biology--Bioinformatics', 'Biology--Cell',
           'Biology--Molecular', 'Biology', 'Biophysics--Medical', 'Economics--Finance',
           'Education--Bilingual and Multicultural', 'Education--Sciences', 'Education',
           'Engineering--Biomedical', 'Environmental Sciences', 'Geography', 'Geophysics', 'Immunology',
           'Language', 'Oncology', 'Psychology--Industrial', 'Virology', 'Biochemistry',
           'Biological Sciences', 'Biology', 'Chemistry', 'Disaster Risk and Resilience', 'Ecology',
           'Environmental Chemistry', 'Environmental Sciences', 'Psychology',
           'Speech and Language Sciences', 'Water Resource Management', 'Biophysics',
           'Biostatistics', 'Educational Psychology', 'Education--Social Sciences',
           'History--Ancient', 'Microbiology', 'Neuroscience']

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

recs = []
for page in range(pages):
    tocurl = 'https://prism.ucalgary.ca/collections/16fe099b-62b7-45bd-9a99-5fc465f0d04d?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    baseurl = 'https://prism.ucalgary.ca'
    
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.contributor.author', 'dc.date.issued', 'dc.title', 'dc.identifier.uri', 'dc.description.abstract', 'dc.identifier.uri', 'dc.language.iso', 'dc.rights', 'dc.subject', 'dc.subject.classification', 'thesis.degree.discipline', 'thesis.degree.name'], boring=boring, alreadyharvested=alreadyharvested):
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        #print(rec['thesis.metadata.keys'])
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
