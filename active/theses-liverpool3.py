# -*- coding: utf-8 -*-
#harvest Liverpool Theses
#FS: 2020-02-03
#FS: 2022-09-27

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'U. Liverpool (main)'
hdr = {'User-Agent' : 'Magic Browser'}

departmentstoskip = ["Chemistry", "Archaeology, Classics and Egyptology", "Archaeology",  "Architecture",  "Biochemistry",
                     "Biological Sciences",  "Biology",  "Biostatistics",  "Business Administration",
                     "Cellular & Molecular Physiology",  "Cellular and Molecular Physiology",
                     "Centre for Higher Education Studies",  "Child Health",  "Civil Engineering and Industrial Design",
                     "Clinical Infection, Microbiology and Immunology",  "Clinical Psychology",  "Dentistry",
                     "Department of Archaeology, Classics and Egyptology",  "Department of Biostatistics",
                     "Department of Cellular and Molecular Physiology",
                     "Department of Clinical Infection, Microbiology and Immunology",
                     "Department of Electrical Engineering & Electronics",
                     "Department of Molecular and Clinical Cancer Medicine",
                     "Department of Molecular and Clinical Pharmacology",  "Department of Psychological Sciences",
                     "Department of Sociology, Social Policy and Criminology",
                     "Department of Women's and Children's Health",  "Earth, Ocean and Ecological Sciences",
                     "Economics and Finance",  "Economics",  "Education",  "Electrical Eng & Electronics",
                     "Electrical Engineering & Electronics",  "Engineering",  "English",  "Environmental Sciences",
                     "Evolution, Ecology and Behaviour",  "Eye and Vision Science",  "Functional and Comparative Genomics",
                     "Gastroenterology",  "Geography and Planning",  "Health Services Research",  "History",
                     "Infection & Immunity",  "Infection and Global Health",  "Infection Biology",
                     "Institute of Ageing and Chronic Disease",  "Institute of Infection & Global Health",
                     "Institute of Infection and Global Health",  "Institute of Integrative Biology",
                     "Institute of Irish Studies",  "Institute of Psychology, Health & Society",
                     "Institute of Psychology, Health and Society",  "Institute of Translational Medicine",  "Law",
                     "Liverpool Law School",  "Management School",  "Management",
                     "Mechanical, Materials and Aerospace Engineering",  "Medicine",  "Microbiology",
                     "Modern Languages and Cultures",  "Molecular and Clinical Cancer Medicine",
                     "Molecular and Clinical Pharmacology",  "Musculoskeletal Biology 1",  "Musculoskeletal Biology II",
                     "Musculoskeletal Biology",  "Music",  "Ocular Oncology",  "Operations and Supply Chain Management",
                     "Pharmacology",  "Politics",  "Psychological Sciences",  "Psychology",  "School of Biological Sciences",
                     "School of Chemistry",  "School of Dentistry",  "School of Education",
                     #"School of Electrical Engineering, Electronics and Computer Science",
                     "School of Engineering",
                     "School of Environmental Sciences",  "School of Management",  "School of Psychology",
                     "School of Tropical Medicine",  "Sociology, Social Policy and Criminology",  "Sociology",
                     "Strategy, International Business and Entrepreneurship",  "Surgery and Oncology",  "Tropical medicine",
                     "Tropical Medicine",  "Veterinary Science",  "Work, Organisation and Management", "Applied Health Research", 
                     "Archaeology (Arts)", "Biological and Medical Sciences", "Cancer Biology", "Cancer Medicine", 
                     "Cellular & Molecular Physiology", "Cellular &Molecular Physiology", "Communications and Media", 
                     "Department of Communication and Media", "Department of Electrical Engineering & Electronics",
                     "Department of Epidemiology and Population Health", "Department of Functional and Comparative Genomics",
                     "Department of Infection Biology", "Department of Musculoskeletal Biology", "Egyptology",
                     "Electrical Eng & Electronics", "Electrical Engineering & Electronics", "Endodontics",
                     "Epidemiology & Population Health", "Epidemiology & Population Hlth",
                     "Epidemiology and Population Health", "Epidemiology", "Eye & Vision Science", "Geography",
                     "Haematology & Leukaemia", "Health Psychlogy", "Higher Education (EdD)", "Higher Education",
                     "Infect & Global Hlth(Vet)", "Infection & Global Health (Medicine)", "Infection & Immunity",
                     "Infection and Global Health Veterinary", "Infectious Diseases", "Institute of Veterinary Science",
                     "Irish Studies", "Management Studies", "Medical Imaging", "Medical Microbiology",
                     "Musculoskeletal Biol(Medicine)", "Obesity & Endocrinology(Med)", "Orthodontics", "Pancreatology",
                     "Pharmacology & Therapeutics", "Psychiatry", "Psychology (Science)", "Public Health", "SACE",
                     "School of Histories, Languages and Cultures", "Veterinary Immunology", "Veterinary Parasitology",
                     "Veterinary Pathology", "Virology", "Women and Children's Health",
                     "Archives & Record Management", "Cellular & Molecular Physiology", "Cellular &Molecular Physiology",
                     "Chester & Hope", "Civic Design", "Educational Development", "Electrical & Electronic Engineering",
                     "Electrical Eng & Electronics", "Electrical Engineering & Electronics", "Endocrinology",
                     "Epidemiology & Population Hlth", "Eye & Vision Science", "Haematology & Leukaemia",
                     "Health Services Resarch", "Hispanic Studies", "Immunology", "Infect & Global Hlth(Medicine)",
                     "Infect & Global Hlth(Vet)", "Infection & Immunity", "Medical Education", "Molecular Virology",
                     "Musculoskeletal Biol(Vet)", "Obesity & Endocrinology(Med)", "One Health (Veterinary)", "Pathology",
                     "Pharmacology & Therapeutics", "Sociolinguistics", "Veterinary Epidemiology",
                     "Veterinary Microbiology", "Women&apos;s Health", "School of Architecture",
                     "Institute of infection and Global health", "School of Medical Education", "Infection & Immunity",
                     "Latin American Studies", "Haematology", "Obesity Biology", "Clinical Engineering",
                     #"Computer Sciences",
                     "Critical Care", "Department of Clinical and Molecular", "Department of Eye and Vision Science",
                     "Electrical Engineering & Electronics", "Electrical Engineering and Electronics", "Eye & Vision Science",
                     "German", "Obesity & Endocrinology(Med)", "Pathophysiology", "Perinatal & Reproductive Med",
                     "Pharmacology & Therapeutics", "Infect & Global Hlth(Vet)", "Infection & Immunity",
                     "Neurological Science", "Ophthalmology", "Haematology & Leukaemia", "Infect & Global Hlth(Medicine)",
                     "Accounting and Finance", "Biochemistry and Systems Biology", "Cellular & Molecular Physiology",
                     "Cellular &Molecular Physiology", "Department of Biochemistry and Systems Biology",
                     "Department of Chemistry", "Department of English", "Department of Health Services Research",
                     "Department of History", "Department of Music", "Department of Pharmacology and Therapeutics",
                     "Doctor of Clinical Psychology thesis, University of Liverpool.",
                     "Doctor of Education thesis, University of Liverpool.",
                     "Doctor of Engineering thesis, University of Liverpool.",
                     "Doctor of Medicine thesis, University of Liverpool.",
                     "Doctor of Philosophy thesis, University of Liverpool.", "Doctor of Philosophy thesis, Unspecified.",
                     "Electrical Eng & Electronics", "Electrical Engineering & Electronics", "Equine Clinical Science",
                     "Eye & Vision Science", "Faculty of Health and Life Sciences", "Health Data Science",
                     "Infection and Microbiome", "Institute of Infection, Veterinary and Ecological Sciences",
                     "Institute of Life Course and Medical Sciences", "Institute of Life Courses and Medical Sciences",
                     "Institute of Population Health", "Institute of Systems, Molecular and Integrative Biology",
                     "Liverpool School of Tropical Medicine", "Livestock and One Health",
                     "Molecular Physiology and Cell Signaling", "Musculoskeletal & Ageing Science",
                     "Musculoskeletal Biology I", "Obesity & Endocrinology(Med)", "Pharmacology & Therapeutics",
                     "Philosophy", "Primary Care & Mental Health", "Public Health and Policy",
                     "School of Electrical Engineering, Electronics and Computer Science",
                     "School of Histories, Languages and Culture", "School of Law and Social Justice",
                     "School of Medicine", "Stem Cells & Regenerative Med", "Women&apos;s Health"]


reboring = re.compile('(Master of Philosophy|Doctor of Business Administration|Doctor of Education thesis|Doctor of Dental Science|Doctor of Medicine|Doctor of Clinical Psychology)')
for year in [ejlmod3.year(backwards=1), ejlmod3.year()]:
    prerecs = []
    jnlfilename = 'THESES-LIVERPOOL-%s_%i' % (ejlmod3.stampoftoday(), year)
    tocurl = 'https://livrepository.liverpool.ac.uk/view/doctype/thesis/%i.html' % (year)
    print(tocurl)
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(2)
    for p in tocpage.find_all('p'):
        for a in p.find_all('a'):
            if a.has_attr('href') and re.search('livrepository.liverpool.ac.uk', a['href']):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'link' : a['href'], 'year' : str(year), 'supervisor' : []}
                rec['tit'] = a.text.strip()
                a.replace_with('XXX')
                pt = re.sub('.*XXX', '', re.sub('[\n\r\t]', '', p.text.strip()))
                if not reboring.search(pt) and ejlmod3.ckeckinterestingDOI(rec['link']):
                    rec['note'] = [ pt ]
                    prerecs.append(rec)

    recs = []
    for (i, rec) in enumerate(prerecs):
        keepit = True
        ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
        try:
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
            time.sleep(3)
        except:
            try:
                print('retry %s in 180 seconds' % (rec['link']))
                time.sleep(180)
                artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
            except:
                print('no access to %s' % (rec['link']))
                continue
        ejlmod3.metatagcheck(rec, artpage, ['eprints.creators_name', 'eprints.keywords', 'eprints.abstract', #'eprints.creators_orcid', 
                                            'eprints.date', 'eprints.doi', 'eprints.pages', 'eprints.document_url'])
        for meta in artpage.head.find_all('meta', attrs = {'name' : 'eprints.creators_orcid'}):
            orcid = meta['content'][:19]
            rec['autaff'][-1].append('ORCID:'+orcid)
        #department
        for meta in artpage.head.find_all('meta', attrs = {'name' : 'eprints.department'}):
            department = meta['content']
            if department in ['Department of Mathematical Sciences', 'Mathematical Sciences']:
                rec['fc'] = 'm'
            elif department in ['Department of Computer Sciences', 'Computer Science']:
                rec['fc'] = 'c'
            elif department in departmentstoskip:
                keepit = False
            else:
                rec['note'].append(department)
        #supervisor
        for tr in artpage.body.find_all('tr'):
            for th in tr.find_all('th'):
                tht = th.text.strip()
                if tht in ['Supervisors:', 'Supervisor:']:
                    for li in tr.find_all('li', attrs = {'class' : 'person_item'}):
                        for span in li.find_all('span', attrs = {'class' : 'person_name'}):
                            rec['supervisor'].append([span.text.strip()])
                        for span in li.find_all('span', attrs = {'class' : 'orcid-tooltip'}):
                            rec['supervisor'][-1].append(re.sub(' ', '', span.text.strip()))	  
        if keepit:
            if not 'doi' in rec:
                rec['doi'] = '20.2000/Liverpool/' + re.sub('\D', '', a['href'])
            recs.append(rec)
            rec['autaff'][-1].append(publisher)
            ejlmod3.printrecsummary(rec)
        else:
            ejlmod3.adduninterestingDOI(rec['link'])
    ejlmod3.writenewXML(recs, publisher, jnlfilename)

