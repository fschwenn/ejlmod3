# -*- coding: utf-8 -*-
#harvest theses from Purdue U.
#FS: 2020-03-16
#FS: 2023-01-27

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Purdue U.'

startyear = ejlmod3.year(backwards=1)

uninterestingsubjects = ['Chemistry', 'Biochemistry', 'Organic chemistry',
                         'Clinical psychology', 'Social research', 'Disability studies',
                         'Individual & family studies', 'Social psychology',
                         'Asian Studies', 'Personality psychology', "Accounting", "Acoustics",
                         "Aerospace engineering", "African American Studies", "African history",
                         "African literature", "Agricultural economics", "Agricultural education",
                         "Agricultural engineering", "Agriculture", "Agronomy", "Alternative Energy",
                         "American history", "American literature", "American studies",
                         "Analytical chemistry", "Animal Diseases", "Animal sciences",
                         "Architectural engineering", "Art education", "Artificial intelligence",
                         "Asian literature", "Asian studies", "Atmospheric Chemistry",
                         "Atmospheric sciences", "Atomic physics", "Audiology", "Automotive engineering",
                         "Behavioral psychology", "Behavioral Sciences", "Bioengineering",
                         "Biogeochemistry", "Bioinformatics", "Biology", "Biomechanics",
                         "Biomedical engineering", "Biophysics", "Botany", "British & Irish literature",
                         "British and Irish literature", "Business administration", "Cellular biology",
                         "Chemical engineering", "Civil engineering", "Classical Studies",
                         "Climate Change", "Cognitive psychology", "Communication",
                         "Comparative literature", "Computational chemistry",
                         "Computer Engineering", "Conservation biology",
                         "Counseling Psychology", "Creative writing", "Criminology",
                         "Cultural anthropology", "Curriculum development", "Design",
                         "Developmental biology", "Ecology", "Economics", "Educational administration",
                         "Educational evaluation", "Educational leadership", "Educational psychology",
                         "Educational sociology", "Educational technology", "Educational tests & measurements",
                         "Education finance", "Education philosophy", "Education policy", "Education Policy",
                         "Education", "Electrical engineering", "Elementary education", "Energy", "Engineering",
                         "Entomology", "Entrepreneurship", "Environmental economics", "Environmental education",
                         "Environmental engineering", "Environmental health", "Environmental Health",
                         "Environmental science", "Epidemiology", "Epistemology", "Ethics", "Ethnic studies",
                         "European history", "Evolution and Development", "Experimental psychology",
                         "Film studies", "Finance", "Fine arts", "Fluid mechanics", "Food science",
                         "Food Science", "Forestry", "French literature", "Gender studies", "Genetics",
                         "Geographic information science", "Geology", "Geophysics", "German literature",
                         "Gerontology", "Gifted Education", "Health care management", "Health sciences",
                         "Higher Education Administration", "Higher education", "Hispanic American studies",
                         "History", "Holocaust Studies", "Horticulture", "Hydraulic engineering",
                         "Hydrologic sciences", "Immunology", "Industrial engineering", "Information science",
                         "Information technology", "Information Technology", "Inorganic chemistry",
                         "Instructional Design", "International Relations", "Kinesiology", "Labor economics",
                         "Language", "Latin American history", "Latin American literature",
                         "Latin American Studies", "Law enforcement", "Law", "LGBTQ studies", "Linguistics",
                         "Literature", "Low Temperature Physics", "Macroecology", "Management", "Marketing",
                         "Mass communications", "Materials science", "Mathematics education", 
                         "Mechanical engineering", "Mechanics", "Medical imaging", "Medicine",
                         "Medieval literature", "Mental health", "Meteorology", "Microbiology",
                         "Middle Eastern history", "Middle School education", "Molecular biology",
                         "Molecular physics", "Multicultural Education", "Multimedia Communications",
                         "Museum studies", "Music history", "Nanoscience", "Nanotechnology",
                         "Native American studies", "Neurosciences", "Nuclear engineering", "Nutrition",
                         "Oncology", "Operations research", "Optics", "Organizational behavior",
                         "Organization Theory", "Particle physics", "Pathology", "Pedagogy",
                         "Pharmaceutical sciences", "Pharmacology", "Philosophy of religion", "Philosophy",
                         "Physical chemistry", "Physical education", "Physiology", "Plant Pathology",
                         "Plant sciences", "Plasma physics", "Plastics", "Political science", "Polymer chemistry",
                         "Psychology", "Public administration", "Public Health Education", "Public health",
                         "Public policy", "Quantum physics", "Religion", "Remote sensing", "Rhetoric", "Robotics",
                         "Romance literature", "Science education", "Science history", "Secondary education",
                         "Sedimentary Geology", "Social studies education", "Sociolinguistics", "Sociology",
                         "Soil sciences", "Speech therapy", "Sports Management", "Statistics", "Sustainability",
                         "Systems science", "Teacher education", "Technical Communication", "Theater", "Therapy",
                         "Thermodynamics", "Toxicology", "Transportation", "Urban planning", "Veterinary services",
                         "Virology", "Water Resource Management", "Web Studies", "Wildlife Conservation",
                         "Wildlife Management", "Women's studies", "Womens studies", "Zoology",
                         "Aesthetics", "Aging", "Agricultural chemicals", "Agriculture, Forestry and Wildlife",
                         "Agriculture, Plant Culture", "American Studies", "Applied Mechanics", "Aquatic sciences",
                         "Archaeology", "Architectural", "Architecture", "Art Criticism", "Art history",
                         "Artificial Intelligence", "Arts Management", "Bilingual education", "Biology, Botany",
                         "Biology, Cell", "Biology, Ecology", "Biology, General", "Biology, Genetics",
                         "Biology, Microbiology", "Biology, Neuroscience", "Biology, Veterinary Science",
                         "Biophysics, Biomechanics", "Biophysics, General", "Business Administration, Management",
                         "Business Administration, Marketing", "Caribbean Studies", "Chemistry, Analytical",
                         "Chemistry, Biochemistry", "Chemistry, General", "Chemistry, Nuclear", "Cinematography",
                         "Commerce-Business", "Computer engineering", "Design and Decorative Arts",
                         "Developmental psychology", "Early childhood education", "Economics, General",
                         "Economic theory", "Education, Administration", "Education, Continuing",
                         "Education, Curriculum and Instruction", "Education, Higher",
                         "Education, Language and Literature", "Education, Policy", "Education, Religious",
                         "Electromagnetics", "Engineering, Biomedical", "Engineering, Chemical",
                         "Engineering, Computer", "Engineering, Electronics and Electrical",
                         "Engineering, Industrial", "Engineering, Materials Science", "Engineering, Mechanical",
                         "Engineering, Nuclear", "Engineering, Robotics", "English as a Second Language",
                         "Environmental management", "European Studies", "Fine Arts", "Foreign Language",
                         "Forensic anthropology", "Gender Studies", "Geochemistry", "Geomorphology", "Geotechnology",
                         "Germanic literature", "Health education", "Health Sciences, Audiology",
                         "Health Sciences, General", "Health Sciences, Health Care Management",
                         "Health Sciences, Nutrition", "Health Sciences, Occupational Health and Safety",
                         "Health Sciences, Pharmacology", "Health Sciences, Pharmacy",
                         "Health Sciences, Public Health", "Health Sciences, Recreation",
                         "Health Sciences, Speech Pathology", "Hispanic American Studies",
                         "History, Asia, Australia and Oceania", "History, European", "History of Oceania",
                         "History, United States", "Home economics", "Industrial arts education",
                         "Information Science", "Islamic Studies", "Labor relations", "Land Use Planning",
                         "Language arts", "Language, Rhetoric and Composition", "Literacy",
                         "Literature, African", "Literature, American", "Literature, English",
                         "Literature, General", "Literature, Latin American", "Literature, Modern",
                         "Literature of Oceania", "Medieval history", "Middle Eastern Studies",
                         "Military history", "Military Studies", "Modern literature", "Molecular chemistry",
                         "Natural Resource Management", "Occupational health", "Occupational psychology",
                         "Occupational safety", "Occupational Therapy", "Operations Research", "Pacific Rim Studies",
                         "Packaging", "Parasitology", "Petroleum engineering", "Pharmacy sciences",
                         "Physical anthropology", "Physiological psychology", "Planetology", "Plant biology",
                         "Political Science, International Law and Relations", "Military studies",
                         "Political Science, International Relations", "Psychobiology", "Psychology, Cognitive",
                         "Psychology, General", "Psychology, Industrial", "Reading instruction", "Recreation",
                         "Religion, History of", "Religious history", "School administration", "School counseling",
                         "Social structure", "Sociology, Organizational", "Sociology, Organization Theory",
                         "Sociology, Public and Social Welfare", "South Asian Studies", "Special education",
                         "Speech Communication", "Systematic biology", "Theater History", "Theology",
                         "Transportation planning", "Vocational education", "Wood sciences"]


prerecs = []
jnlfilename = 'THESES-PURDUE-%s' % (ejlmod3.stampoftoday())
hdr = {'User-Agent' : 'Magic Browser'}

tocurl = 'https://docs.lib.purdue.edu/dissertations/'
req = urllib.request.Request(tocurl, headers=hdr)
tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")

prerecs = []
tooold = False
for p in tocpage.body.find_all('p'):
    rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : [], 'supervisor' : [] }
    for strong in p.find_all('strong'):
        rec['autaff'] = [[ strong.text.strip() ]]
        rec['autaff'][-1].append(publisher)
    for a in p.find_all('a'):
        rec['link'] = a['href']
        if re.search('dissertations\/...', a['href']):
            rec['doi'] = '20.2000/Purdue/' + re.sub('.*\/', '', a['href'])
            rec['tit'] = a.text.strip()
            if re.search('\([12]\d\d\d', p.text):
                rec['year'] = re.sub('.*\(([12]\d\d\d).*', r'\1', p.text.strip())
                if int(rec['year']) < startyear:
                    #print '  %s too old' % (rec['year'])
                    tooold = True
                else:
                    prerecs.append(rec)
            else:
                print('  unknown year?!')
                if tooold:
                    pass
                else:
                    prerecs.append(rec)
           
i = 0
recs = []
for rec in prerecs:
    i += 1
    interesting = True
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
    ejlmod3.metatagcheck(rec, artpage, ['description'])

    for div in artpage.body.find_all('div', attrs = {'id' : 'alpha'}):
        h4t = False
        for child in div.children:
            try:
                child.name
            except:
                continue
            if child.name == 'h4':
                h4t = child.text.strip()
            elif child.name == 'p':
                if h4t:
                    #supervsor
                    if h4t == 'Advisors':
                        rec['supervisor'].append([re.sub(',.*', '', child.text.strip())])
                    #subjects
                    elif h4t == 'Subject Area':
                        for subj in re.split('\|', child.text.strip()):
                            if subj in uninterestingsubjects:
                                print('   skip "%s"' % (subj))
                                interesting = False
                            elif subj in ["Computational physics", "Computer science"]:
                                rec['fc'] = 'c'
                            elif subj in ["Mathematics"]:
                                rec['fc'] = 'm'
                            elif subj in ["Astronomy"]:
                                rec['fc'] = 'a'
                            else:
                                rec['note'].append(subj)
    #license           
    for table in artpage.body.find_all('table', attrs = {'class' : 'ep_block'}):
        for a in table.find_all('a'):
            if a.has_attr('href') and re.search('creativecommons.org', a['href']):
                rec['licence'] = {'url' : a['href']}
    if interesting:
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
