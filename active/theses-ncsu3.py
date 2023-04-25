# -*- coding: utf-8 -*-
#harvest theses from North Carolina State U.
#FS: 2021-09-07
#FS: 2023-04-18

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'North Carolina State U.'

rpp = 100
pages = 2
skipalreadyharvested = True

hdr = {'User-Agent' : 'Firefox'}
jnlfilename = 'THESES-NCSU-%s' % (ejlmod3.stampoftoday())

boringdisciplines = ['Mechanical Engineering', 'Electrical Engineering', 'Biology', 'Biomedical Engineering',
                     'Chemical Engineering', 'Civil Engineering', 'Educational Adm & Supervision',
                     'Fish, Wildlife, and Con Bio', 'Forestry and Environmental Res', 'Horticultural Science',
                     'Psychology', 'Aerospace Engineering', 'Chemistry', 'Comm, Rhetoric & Digital Media',
                     'Computer Engineering', 'Economics', 'Ed Leadership Policy Human Dev',
                     'Fiber & Polymer Science', 'Food Science', 'Forest Biomaterials', 'Genetics',
                     'Learning and Teaching in STEM', 'Material Science & Engineering', 'Public History',
                     'Sociology', 'Soil Science', 'Statistics', 'Teacher Educ and Learning Sci',
                     'Materials Science & Engineering', 'Plant Biology', 'Plant Pathology',
                     'Animal Sci & Poultry Sci', 'Bioinformatics', 'Biological & Agri Engineering',
                     'Applied Mathematics', 'Counseling & Counselor Educ', 'Crop Science',
                     'Ed Research & Policy Analysis', 'Mathematics Education', 'Microbiology',
                     'Adult and Community College Education', 'Adult and Higher Education',
                     'Agricultural and Extension Education', 'Agricultural Education', 'Animal and Poultry Science',
                     'Animal SciencePoultry ScienceFunctional Genomics', 'Animal SciencePoultry Science',
                     'Animal Science', 'Biochemistry', 'BioinformaticsStatistics', 'Botany', 'ChemistryStatistics',
                     'Comm Rhetoric & Digital Media', 'Communication, Rhetoric, and Digital Media',
                     'Comparative Biomedical Sciences',
                     #'Computer ScienceComputer Science', 'Computer Science',
                     'Counseling and Counselor Education', 'Counselor Education', 'Curriculum and Instruction',
                     'Curriculum Studies', 'EconomicsStatistics', 'EdD', 'Educational Administration and Supervision',
                     'Educational Psychology', 'Educational Research and Policy Analysis', 'Engineering',
                     'Extension Education', 'Fiber and Polymer ScienceBiomedical Engineering',
                     'Fiber and Polymer ScienceElectrical Engineering', 'ForestryNatural Resources', 'Forestry',
                     'Functional Genomics', 'Geospatial Analytics', 'Higher Education Administration', 'Immunology',
                     'Industrial EngineeringIndustrial Engineering', 'Marine, Earth and Atmospheric Sciences',
                     'Materials Science and Engineering', 'Math, Science and Technology Education',
                     'NutritionAnimal Science', 'Occupational Education', 'Operations ResearchComputer Science',
                     'Operations ResearchElectrical Engineering', 'Parks, Recreation and Tourism Management',
                     'Physiology', 'Plant PathologyCrop Science', 'Poultry Science', 'School Counseling',
                     'Technology Education', 'Textiles', 'Training and Development', 'Wood and Paper Science',
                     'Fiber and Polymer ScienceWood and Paper Science', 'Fisheries and Wildlife Sciences',
                     'Fisheries, Wildlife, and Conservation Biology', 'Forestry and Environmental Resources', 
                     'Fiber and Polymer ScienceMaterials Science and Engineering', 'Fiber and Polymer Science', 
                     'Curriculum and Instruction, English Education', 'Curriculum and Instruction, Reading', 
                     'Biological and Agricultural Engineering', 'Biomedical EngineeringFiber and Polymer Science',                     
                     'Science Education', 'Biomathematics', 'Comm, Rhetoric & Digital Media',
                     'Comparative Biomedical Sci', 'Nutrition', 'Parks, Rec and Tourism Mgmt',
                     'Curriculum & Instruction', 'Design', 'Entomology', 'Fiber & Polymer Science',
                     'Industrial Engineering', 'Marine, Earth & Atmos Sciences', 'Zoology',
                     'Material Science & Engineering', 'Materials Science & Engineering',
                     'Operations Research', 'Public Administration', 'Toxicology', 'Textile Technology Management',
                     'Biological+%26+Agri+Engineering']
boringdegrees = ['Doctor+of+Education', 'Master+of+Science']
for b in boringdisciplines:
    boringdegrees.append(re.sub(' ', '+', re.sub('\(', '%28', re.sub('\)', '%29', re.sub('&', '%26', b)))))
                                                 
if skipalreadyharvested:
    alreadyharvested = []
    for doi in ejlmod3.getalreadyharvested(jnlfilename):
        alreadyharvested.append(doi)
        alreadyharvested.append(re.sub('.*NCSU\/184020', '30.3000/httpsrepositorylibncsuedu/1840.20/', doi))

prerecs = []
for page in range(pages):
    tocurl = 'https://repository.lib.ncsu.edu/handle/1840.20/24/discover?rpp=' + str(rpp) + '&etal=0&group_by=none&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    tocfilename = '/tmp/NCSU.%s.%04i.html' % (ejlmod3.stampoftoday(), page)
    if not os.path.isfile(tocfilename):
        os.system('wget -q -O  %s "%s"' % (tocfilename, tocurl))
        time.sleep(5)
    inf = open(tocfilename, 'r')
    tocpage = BeautifulSoup(''.join(inf.readlines()))
    inf.close()
    prerecs += ejlmod3.getdspacerecs(tocpage,  'https://repository.lib.ncsu.edu', fakehdl=True, alreadyharvested=alreadyharvested, boringdegrees=boringdegrees)
    print('   %i recs so far' % (len(prerecs)))

recs = []
i = 0
for rec in prerecs:
    discipline = False
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    artfilename = '/tmp/NCSU.%s.thesis' % (re.sub('\D', '', rec['link']))
    if not os.path.isfile(artfilename):
        os.system('wget -q -O %s "%s"' % (artfilename, rec['link']))
        time.sleep(5)
    inf = open(artfilename, 'r')
    artpage = BeautifulSoup(''.join(inf.readlines()))
    inf.close()
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.title', 'DCTERMS.issued',
                                        'DC.subject', 'citation_pdf_url', 'DCTERMS.abstract'])
    rec['autaff'][-1].append(publisher)
    for tr in artpage.body.find_all('tr'):
        tdt = False
        for td in tr.find_all('td'):
            if tdt:
                if tdt == 'Discipline:':
                    discipline = td.text.strip()
                    tdt == False
            else:
                for span in td.find_all('span', attrs = {'class' : 'bold'}):
                    tdt = span.text.strip()
    if discipline and discipline in boringdisciplines:
        print('  skip', discipline)
        ejlmod3.adduninterestingDOI(rec['link'])
    else:
        rec['note'].append('DISCIPLINE:::'+discipline)
        recs.append(rec)
        ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
