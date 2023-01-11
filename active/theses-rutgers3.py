# -*- coding: utf-8 -*-
#harvest theses from Rutgers
#FS: 2019-09-15
#FS: 2022-08-23


import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

pages = 10
rpp = 50
years = 10
skipalreadyharvested = True

publisher = 'Rutgers U.'
jnlfilename = 'THESES-RUTGERS-%s' % (ejlmod3.stampoftoday())

prerecs = []
hdr = {'User-Agent' : 'Magic Browser'}

boring = ['Civil and Environmental Engineering', 'Microbiology and Molecular Genetics', 'Political Science',
          'ProgramManagement', 'Behavioral and Neural Sciences', 'History', 'Chemical and Biochemical Engineering',
          'Psychoogy', 'Cell and Developmental Biology', 'Plant Biology']
boring += ["Graduate School of Education Electronic Theses and Dissertations", "School of Health Professions ETD Collection",
           "School of Nursing (RBHS) DNP Projects", "Clinical psychology", "Continuing education", "Higher education",
           "International relations", "LGBTQ studies", "Literature", "Management", "Mental health", "Nursing",
           "Political science", "Psychobiology", "Psychology", "Public policy", "Teacher education", "Women's studies",
           "Graduate School of Applied and Professional Psychology", "Graduate School of Education", "RBHS School of Nursing",
           "School of Health Professions"]
boring += ["Accounting", "American history", "Animal sciences", "Biochemistry", "Bioengineering", "Biological oceanography", 
           "Biomedical engineering", "Biophysics", "Cellular biology", "Chemical oceanography", "Chemistry",
           "Civil engineering", "Computational chemistry", "Computer engineering", "Creative writing", "Biomechanics",
           "Developmental psychology", "English literature", "Environmental science", "European history", "Food science",
           "Genetics", "Geology", "Geophysics", "Industrial engineering", "Journalism", "Marketing", "Mechanical engineering",
           "Microbiology", "Molecular biology", "Neurosciences", "Nutrition", "Operations research", "Pharmaceutical sciences",
           "Philosophy", "Physiology", "Plant sciences", "Public administration", "Robotics", "Systems science", "Theater",
           "Toxicology", "Transportation"]
boring += ["Acoustics", "Aerospace engineering", "African studies", "Agriculture", "Analytical chemistry",
           "Area planning & development", "Asian American studies", "Atmospheric sciences", "Banking", "Biology",
           "Biostatistics", "Black studies", "Chemical engineering", "Climate change", "Cultural resources management",
           "Ecology", "Economics", "Education", "Energy", "Entomology", "Environmental economics", "Epistemology",
           "Evolution & development", "Finance", "Forestry", "French literature", "Gender studies", "Geobiology", "Geography",
           "Health sciences", "Horticulture", "Landscape architecture", "Law enforcement", "Linguistics", "Music history",
           "Natural resource management", "Optics", "Organic chemistry", "Particle physics", "Pharmacology",
           "Physical anthropology", "Physical oceanography", "Public health education", "Public health", "Remote sensing",
           "Social psychology", "Social research", "Sociology", "South Asian studies", "Special education", "Sustainability",
           "Systematic biology", "Theater history", "Urban forestry", "Water resources management"]
boring += ["School of Public Health ETD Collection", "African literature", "American literature", "American studies",
           "Anthropology", "Art History", "Biogeochemistry", "Biomedical Engineering", "Caribbean literature",
           "Chemistry and Chemical Biology", "Childhood Studies", "Classics", "Cognitive psychology", "Comparative Literature",
           "Creative Writing", "Criminal Justice", "Criminology", "Cultural anthropology", "Ecology and Evolution",
           "Economic theory", "English", "Environmental Geology", "Environmental Science", "Epidemiology",
           "Food and Business Economics", "Food Science", "Forensic Science", "Geochemistry", "Geological Sciences",
           "Global Affairs", "Higher Education", "Immunology", "Industrial and Systems Engineering",
           "Industrial Relations and Human Resources", "Italian", "Jazz History and Research", "Kinesiology and Applied Physiology",
           "Labor economics", "Landscape Architecture", "Latin American history", "Latin American studies", "Liberal Studies",
           "Literatures in English", "Medicinal Chemistry", "Medieval literature", "Microbial Biology", "Music", "Neuroscience",
           "Nutritional Sciences", "Oceanography", "Oncology", "Organizational behavior", "Performing arts",
           "Pharmaceutical Science", "Pharmacology, Cellular and Molecular", "Physiology and Integrative Biology",
           "Planning and Public Policy", "Polymer chemistry", "Public Administration (SPAA)", "Public Health",
           "Quantitative Biomedicine", "Religion", "Social work", "Urban Systems", "Women's and Gender Studies",
           "Women`s and Gender Studies", "World history"]
boring += ["American Studies", "Art history", "Artificial intelligence", "Atmospheric Science", "Biomedical Sciences",
           "Business and Science", "Computational and Integrative Biology", "Developmental biology",
           "Endocrinology and Animal Biosciences", "Environmental health", "Environmental Sciences", "Fluid mechanics", "French",
           "Geological engineering", "German", "Music Education", "Operations Research", "Public Affairs",
           "Religious Studies", "Sedimentary geology", "Social Work", "Spanish", "Urban planning"]

dokidir = '/afs/desy.de/user/l/library/dok/ejl/backup'
alreadyharvested = []
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    filenametrunc = re.sub('\d.*', '*doki', jnlfilename)
    alreadyharvested = list(map(tfstrip, os.popen("cat %s/*%s %s/%i/*%s | grep URLDOC | sed 's/.*=//' | sed 's/;//' " % (dokidir, filenametrunc, dokidir, ejlmod3.year(backwards=1), filenametrunc))))
    print('%i records in backup' % (len(alreadyharvested)))
    
for page in range(pages):
    tocurl = 'https://rucore.libraries.rutgers.edu/search/results/?orderby=datedesc&ppage=' + str(rpp) + '&numresults=' + str(rpp) + '&key=ETD-RU&start=%i' % (rpp*page + 1)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(3)
    for div in tocpage.body.find_all('div', attrs = {'class' : 'result__result-entry brief'}):
        keepit = True
        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'keyw' : [], 'note' : []}
        for div2 in div.find_all('div', attrs = {'class' : 'result__result-field brief'}):
            for span in div2.find_all('span', attrs = {'class' : 'resultBrief__result-title'}):
                fieldtitle = span.text.strip()
            for span in div2.find_all('span', attrs = {'class' : 'resultBrief__result-text'}):
                fieldtext = span.text.strip()
            if fieldtitle in ['Collection', 'School', 'Graduate Program']:
                if fieldtext in boring:
                    keepit = False                    
                else:
                    if fieldtext == 'Computer Science':
                        rec['fc'] = 'c'
                    elif fieldtext == 'Condensed matter physics':
                        rec['fc'] = 'f'
                    elif fieldtext == 'Quantum physics':
                        rec['fc'] = 'k'
                    elif fieldtext == 'Statistics':
                        rec['fc'] = 's'
                    elif fieldtext in ['Applied mathematics', 'Mathematics']:
                        rec['fc'] = 'm'
                    elif fieldtext in ['Astronomy', 'Astrophysics']:
                        rec['fc'] = 'a'
                    else:
                        rec['note'].append('%s=%s' % (fieldtitle, fieldtext))
            elif fieldtitle == 'Date Created':
                if re.search('^[12]\d\d\d$', fieldtext):
                    if int(fieldtext) < ejlmod3.year() - years:
                        keepit = False
        for a in div.find_all('a'):            
            rec['artlink'] = 'https://rucore.libraries.rutgers.edu' + a['href']
            if ejlmod3.checkinterestingDOI(rec['artlink']) and keepit:
                prerecs.append(rec)
    print('     %i/%i/%i records so far' % (len(prerecs), (page+1)*rpp, pages*rpp))

i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue      
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_date', 'citation_keywords', 'citation_doi', 'citation_pdf_url'])
    #author
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_author'}):
        author = re.sub(' *\[.*', '', meta['content'])
        rec['autaff'] = [[ author ]]
        rec['autaff'][-1].append('Rutgers U., Piscataway (main)')
    for div in artpage.body.find_all('div', attrs = {'class' : 'result__result-field full'}):
        for span in div.find_all('span', attrs = {'class' : 'resultFull__result-title'}):
            #abstract
            if span.text == 'Description':
                for span2 in div.find_all('span', attrs = {'class' : 'resultFull__result-text'}):
                    rec['abs'] = span2.text.strip()
            #program
            elif span.text in ['Graduate Program', 'School', 'Collection', 'Genre']:
                for span2 in div.find_all('span', attrs = {'class' : 'resultFull__result-text'}):
                    span2text = span2.text.strip()
                    if span2text in boring:
                        keepit = False
                    else:
                        rec['note'].append('%s=%s' % (span.text, span2text))                       
            #pages
            elif span.text == 'Extent':
                for span2 in div.find_all('span', attrs = {'class' : 'resultFull__result-text'}):
                    if re.search('\d\d+ pages', span2.text):
                        rec['pages'] = re.sub('.*?(\d\d+) pages.*', r'\1', span2.text)
            #date fallback
            elif span.text == 'Other Date':
                for span2 in div.find_all('span', attrs = {'class' : 'resultFull__result-text'}):
                    st = span2.text.strip()
                    if not 'date' in list(rec.keys()):
                        rec['date'] = re.sub('.*?([12]\d\d.*\d).*', r'\1', st)
                    elif re.search('degre', span2.text):
                        rec['date'] = re.sub('.*?([12]\d\d.*\d).*', r'\1', st)
    if keepit:
        if re.sub('^doi:', '', rec['doi']) in alreadyharvested:
            print('    %s already in backup' % (rec['doi']))
        else:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
