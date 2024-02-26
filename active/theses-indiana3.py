# -*- coding: utf-8 -*-
#harvest theses Indiana U., Bloomington (main)
#FS: 2020-05-13
#FS: 2023-04-28
#FS: 2024-02-26

import sys
import os
from bs4 import BeautifulSoup
import re
import undetected_chromedriver as uc
import ejlmod3
import time

publisher = 'Indiana U., Bloomington (main)'
jnlfilename = 'THESES-INDIANABLOOMINGTON-%s' % (ejlmod3.stampoftoday())

skipalreadyharvested = True
rpp = 60
pages = 2
boring = ['Anthropology/University Graduate School', 'Department of Anthropology',
          'Department of Biology School of Informatics Computing Engineering/University Graduate School',
          'Department of Communication Culture', 'Department of Earth Atmospheric Sciences',
          'Department of English/University Graduate School', 'Department of Folklore Ethnomusicology',
          'Department of History', 'Department of Linguistics',
          'Department of Linguistics the Department of Second Language Studies',
          'Department of Psychological Brain Sciences',
          'Department of Psychological Brain Sciences/College of Arts Sciences',
          'Department of Psychological Brain Sciences Program in Neuroscience',
          'Department of Psychological Brain Sciences the Cognitive Science Program',
          'Department of Psychological Brain Sciences the Program in Neural Science',
          'Department of Psychological Brain Sciences the Program in Neuroscience',
          'Department of Psychological Brain Sciences/University Graduate School',
          'Department of Spanish Portuguese', 'Department of Speech Hearing Sciences',
          'History Philosophy of Science Medicine/University Graduate School',
          'Jacobs School of Music', 'Kelley School of Business',
          'Linguistics/University Graduate School', 'Department of Biology',
          'Media School/University Graduate School',
          'Musicology/Jacobs School of Music', 'School of Education',
          'School of Education/University Graduate School',
          'School of Optometry', 'School of Public Environmental Affairs',
          'School of Public Health', 'School of Public Health/University Graduate School',
          'Anthropology', 'Biochemistry', 'Biochemistry Molecular Biology',
          'Biology', 'Business', 'Cellular Integrative Physiology',
          'Central Eurasian Studies', 'Chemistry', 'Classical Studies',
          'Cognitive Science', 'Cognitive Science Program',
          'Cognitive Science/Psychological Brain Sciences',
          'Communication Culture', 'Comparative Literature', 'Criminal Justice',
          'Department of Biochemistry Molecular Biology',
          'Department of Biology School of Informatics Computing Engineering/University Graduate School',
          'Department of Central Eurasian Studies', 'Department of English',
          'Department of Folklore Ethnomusicology', 'Department of French Italian',
          'Department of Psychological Brain Sciences',
          'Department of Psychological Brain Sciences Program in Neuroscience',
          'Department of Psychological Brain Sciences the Department of Biology',
          'Department of Psychological Brain Sciences the Program in Neuroscience',
          'Department of Sociology', 'East Asian Languages Cultures',
          'East Asian Languages Cultures (EALC', 'Ecology Evolutionary Biology',
          'Economics', 'Education', 'Educational Leadership',
          'Educational Leadership Policy Studies', 'English', 'Environmental Science',
          'Fine Arts', 'Folklore Ethnomusicology', 'French',
          'Geography', 'Geological Sciences', 'Germanic Studies',
          'Health Rehabilitation Sciences', 'History', 'History/American Studies',
          'History of Art', 'History Philosophy of Science', 'Italian',
          'Journalism', 'Linguistics', 'Linguistics Central Eurasian Studies',
          'Linguistics/Second Language Studies', 'Mass Communications/Telecommunications',
          'Microbiology', 'Microbiology Immunology', 'Molecular Cellular Developmental Biology',
          'Music', 'Near Eastern Languages Cultures', 'Neuroscience',
          'Nursing Science', 'Optometry', 'Pharmacology Toxicology',
          'Philanthropic Studies', 'Philosophy', 'Political Science',
          'Psychological Brain Sciences',
          'sychological Brain Sciences/Cognitive Science',
          'Psychological Brain Sciences/Cognitive Sciences',
          'Psychological Brain Sciences the Cognitive Science Program',
          'Psychology', 'Public Affairs', 'Public Health', 'Public Policy',
          'School of Health Physical Education Recreation',
          'Sociology', 'Spanish', 'Spanish Portuguese', 'Speech Hearing']
boring += ['Department of Germanic Studies', 'Department of Spanish &a; Portuguese',
           'Department of Spanish and Portuguese/Department of Linguistics.',
           'School of Music', 'Biology/University Graduate School',
           'Department of Art History', 'Department of Communication and Culture',
           'Department of Biology and School of Informatics, Computing, and Engineering/University Graduate School',
           'Department of Education Leadership and Policy Studies',
           'Department of Folklore &a; Ethnomusicology', 'Department of Folklore and Ethnomusicology',
           'Department of French and Italian', 'Department of Geography',
           'Department of Linguistics and the Department of Second Language Studies',
           'Department of Medical Sciences', 'Department of Middle Eastern Languages and Cultures',
           'Department of Psychological &a; Brain Sciences and Program in Neuroscience',
           'Department of Psychological &a; Brain Sciences and the Cognitive Science Program',
           'Department of Psychological &a; Brain Sciences',
           'Department of Psychological and Brain Sciences and the Cognitive Science Program',
           'Department of Psychological and Brain Sciences and the Program in Neural Science',
           'Department of Psychological and Brain Sciences, and the Program in Neuroscience',
           'Department of Psychological and Brain Sciences/College of Arts and Sciences',
           'Department of Psychological and Brain Sciences', 'Folklore',
           'Department of Psychological and Brain Sciences/University Graduate School',
           'Department of Psychology and Brain Sciences and the Cognitive Science Program',
           'Department of Philosophy', 'Department of Psychology and Brain, Sciences',
           'Department of Second Language Studies', 'Department of Spanish and Portuguese',
           'Department of Speech, Language, and Hearing Sciences',
           'Department of Theatre, Drama, and Contemporary Dance/University Graduate School',
           'Department of the History of Art', 'Maurer School of Law',
           'Departments of Comparative Literature and Religious Studies',
           'Departments of Linguistics and Spanish &a; Portuguese',
           'Earth and Atmospheric Sciences', 'Folklore/Ethnomusicology',
           'History and Philosophy of Science and Medicine/University Graduate School',
           'O’Neill School of Public and Environmental Affairs',
           'Paul H. O&s;Neill School of Public and Environmental Affairs',
           'School of Public and Environmental Affairs/University Graduate School',
           'Cinema and Media Studies/The Media School', 'Department of Jewish Studies',
           'Department of Musicology', 'Department of Speech and Theatre',
           'dep:::Cognitive Science/Psychological &a; Brain Sciences',
           'Communication and Culture', 'Department of Earth and Atmospheric Sciences',
           'Department of Gender Studies', 'Educational Leadership and Policy Studies',
           'Department of Molecular and Cellular Biochemistry',
           'Department of Psychological and Brain Sciences and the Department of Biology',
           'Folklore &a; Ethnomusicology', 'Folklore and Ethnomusicology',
           'History and Philosophy of Science', 'Library and Information Science',
           'Linguistics and Central Eurasian Studies',
           'Psychological and Brain Sciences and the Cognitive Science Program',
           'Psychological and Brain Sciences/Cognitive Sciences',
           'Psychological and Brain Sciences', 'School of Public and Environmental Affairs',
           'Spanish &a; Portuguese', 'Spanish and Portuguese']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []


baseurl = 'https://scholarworks.iu.edu'

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
driver.get(baseurl)
time.sleep(3)

recs = []
redep = re.compile('DC.DESCRIPTION=.*Indiana University, (.*), *[12]\d\d\d')
remaster = re.compile('DC.DESCRIPTION=Thesis \((M\.S\.|M\. S\.|M\.A\.|M\. A\.|Master|Bachelor)')
for page in range(pages):
    tocurl = baseurl + '/dspace/collections/bb2e61e3-fb2c-46dd-91b5-67d5a6f63b36?cp.page=' + str(page+1) + '&cp.sd=DESC&cp.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.contributor.author',
                                               'dc.date.issued', 'dc.description.abstract',
                                               'dc.identifier.uri', 'dc.language.iso',
                                               'dc.subject', 'dc.title'], boring=boring, alreadyharvested=alreadyharvested):
        keepit = True
        for note in rec['note']:
            if redep.search(note):
                dep = redep.sub(r'\1', note)
                if dep in ['Mathematics.', 'Department of Mathematics',
                           'University Graduate School/Mathematics',
                           'Mathematics']:
                    rec['fc'] = 'm'
                elif dep == 'Department of Statistics':
                    rec['fc'] = 's'
                elif dep in ['Department of Astronomy', 'Astronomy']:
                    rec['fc'] = 'a'
                elif dep in ['Informatics and Computing,',
                             'School of Informatics and Computing']:
                    rec['fc'] = 'c'
                elif dep in boring:
                    print('   skip "%s"' % (dep))
                    keepit = False
                elif not dep in ['Department of Mathematics and the Department of Computer Science',
                                 'Physics', 'Department of Physics/University Graduate School',
                                 'Luddy School of Informatics, Computing, and Engineering/University Graduate School',
                                 'Luddy School of Informatics,, Computing, and Engineering',
                                 'School of Informatics, Computing, &a; Engineering',
                                 'School of Informatics, Computing and Engineering',
                                 'School of Informatics, Computing, and Engineering',
                                 'University Graduate School/Luddy School of Informatics, Computing, and Engineering',
                                 'Luddy School of Informatics, Computing, and Engineering',
                                 'Informatics, Computing, and Engineering/University Graduate School',
                                 'Department of Physics']:
                    rec['note'].append('dep:::' + dep)
            if remaster.search(note):
                print('   skip "%s"' % (note))
                keepit = False
        if keepit:
            #print(rec['thesis.metadata.keys'])
            rec['autaff'][-1].append(publisher)
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
        else:
            ejlmod3.adduninterestingDOI(rec['hdl'])
    time.sleep(20)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
