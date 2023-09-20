#-*- coding: utf-8 -*-
#harvest theses from Florida U.
#FS: 2021-04-29

import os
import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import time
import ejlmod3
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

publisher = 'Florida U.'

rpp = 24
pages = 15+40
skipalreadyharvested = True
startyear = ejlmod3.year(backwards=1)
stopyear = ejlmod3.year()
boring = ['aerodynamics', 'birds', 'disease', 'religion', 'archaeology', 'hormones',
          'biocollections', 'dental', 'aircraft', 'rhetoric', 'potato', 'paleontology',
          'aegypti', 'aerosol', 'agarose', 'andes', 'anthropocene', 'antimicrobial',
          'aquaculture', 'artists', 'autism', 'bacteria', 'biomarker', 'brain',
          'burnout', 'cardiovascular', 'caregivers', 'crispr', 'diabetes', 'drugs',
          'emotion', 'everglades', 'fiction', 'fish', 'fungicide', 'geography',
          'healthcare', 'implant', 'mammal', 'medical', 'microbiology', 'microbiome',
          'middle-school', 'mitochondria', 'nutrition', 'odor', 'organic', 'orthodontic',
          'painting', 'peanut', 'pediatric', 'peru', 'phylogenetic', 'poems', 'poverty',
          'psychology', 'queer', 'renewable', 'soil', 'spanish', 'stigma', 'telehealth',
          'terpenoids', 'terrorism', 'therapy', 'tuberculosis', 'urbanization', 'urban',
          'wetlands', 'wildlife', 'womanism', 'women', 'zika', 'art', 'citrus', 'disease',
          'literature', 'workplace', 'tourism', 'world-war-ii', 'voronoi', 'urban planning',
          'sports', 'spanish', 'shipwrecks', 'satire', 'reimbursement', 'hellenistic',
          'parkinsons', 'lionfish', 'alzheimers', 'vitamins', 'vernacular-architecture',
          'veterinary-dermatology', 'vegetable', 'ancomycin', 'usambara', 'urban planning',
          'migration', 'technology', 'agriculture', 'america', 'ecology', 'equity',
          'feminism', 'food', 'hiv', 'pain', 'perceptions', 'poetry', 'social', 'teachers',
          'teacher', 'cancer', 'gender', 'genetics', 'health', 'obesity', 'psychosocial',
          'violence', 'children', 'rural', 'climate', 'education', 'tomato', 'sustainability',
          'Soil science', 'Cultured cells', 'music', 'marketing', 'Human organs', 'Genetic mutation',
          'Consumer research', 'Agonists', 'The Everglades', 'Resins', 'Phenotypic traits',
          'hydrogels', 'Gender roles', 'Disease risks', 'Dehydrogenases', 'Cognitive impairment',
          'beef', 'ATP binding cassette transporters', 'African American studies', 'Vegetation canopies',
          'trauma', 'Textual collocation', 'Symptomatology', 'Soil temperature regimes',
          'osteoarthritis', 'Modern art', 'Miami-Dade County', 'metabolism', 'Korean culture',
          'herbicide', 'habitat', 'Chinese culture', 'Cell lines', 'anthropology', 'African art',
          'fishermen', 'graffiti', 'literacy']

boring += ["Accounting", "Advertising", "Aerospace Engineering", "Agricultural and Biological Engineering",
           "Agricultural Education and Communication", "Agronomy", "Animal Molecular and Cellular Biology",
           "Animal Sciences", "Anthropology", "Applied Physiology and Kinesiology", "Architecture",
           "Art and Art History", "Art History", "Behavioral Science and Community Health",
           "Biochemistry and Molecular Biology", "Biochemistry and Molecular Biology (IDP)", "Biology",
           "Biomedical Engineering", "Biostatistics", "Botany", "Building Construction", "Geology",
           "Business Administration", "Chemical Engineering", "Chemistry", "Civil and Coastal Engineering",
           "Civil Engineering", "Classical Studies", "Classics", "Clinical and Health Psychology",
           "Communication Sciences and Disorders",
           #"Computer and Information Science and Engineering",
           "Counseling and Counselor Education", "Counseling Psychology", "Creative Writing",
           "Criminology, Law, and Society", "Curriculum and Instruction", "Curriculum and Instruction (CCD)",
           "Curriculum and Instruction (CUI)", "Curriculum and Instruction (ISC)", "Dental Sciences",
           "Dentistry", "Design, Construction and Planning", "Design, Construction, and Planning",
           "Design, Construction, and Planning Doctorate", "Digital Arts and Sciences", "Geological Sciences",
           "Early Childhood Education", "Economics", "Educational Leadership", "Educational Psychology",
           "Electrical and Computer Engineering", "English", "English Education", "Entomology and Nematology",
           "Environmental and Global Health", "Environmental Engineering Sciences", "Environmental Horticulture",
           "Clinical Investigation (IDP)", "Coastal and Oceanographic Engineering", "Epidemiology",
           "Family, Youth and Community Sciences", "Finance, Insurance and Real Estate", "Genetics (IDP)",
           "Fisheries and Aquatic Sciences", "Food and Resource Economics", "Food Science", "Geography",
           "Food Science and Human Nutrition", "Forest Resources and Conservation", "French and Francophone Studies",
           #"Computer Engineering", "Computer Science",
           "Construction Management", "Genetics and Genomics",
           "German", "Health and Human Performance", "Health Education and Behavior", "Health Services Research",
           "Health Services Research, Management, and Policy", "Higher Education Administration",
           "Historic Preservation", "History", "Horticultural Sciences", "Human-Centered Computing",
           "Human Development and Organizational Studies in Education", "Immunology and Microbiology (IDP)",
           "Industrial and Systems Engineering", "Information Systems and Operations Management", "Marketing",
           "Interdisciplinary Ecology", "Interior Design", "Journalism and Communications", "Landscape Architecture",
           "Language, Literature and Culture", "Latin", "Latin American Studies", "Linguistics", "Management",
           "Marriage and Family Counseling", "Mass Communication", "Materials Science and Engineering",
           "Mechanical and Aerospace Engineering", "Mechanical Engineering", "Medical Sciences", "French",
           "Medicinal Chemistry", "Medicine", "Mental Health Counseling", "Microbiology and Cell Science",
           "Molecular Cell Biology (IDP)", "Molecular Genetics and Microbiology", "Museology", "Music",
           "Music Education", "Neuroscience (IDP)", "Nuclear and Radiological Engineering", "Religion",
           "Nuclear Engineering Sciences", "Nursing", "Nursing Sciences", "Nutritional Sciences",
           "Pharmaceutical Outcomes and Policy", "Pharmaceutical Sciences", "Pharmaceutics", "Pharmacodynamics",
           "Pharmacology and Therapeutics (IDP)", "Pharmacotherapy and Translational Research", "Philosophy",
           "Physiology and Functional Genomics (IDP)", "Physiology and Pharmacology (IDP)", "Sociology",
           "Plant Molecular and Cellular Biology", "Plant Pathology", "Political Science", "Statistics",
           "Political Science - International Relations", "Psychology", "Public Health", "Sport Management",
           "Recreation, Parks and Tourism", "Recreation, Parks, and Tourism", "Rehabilitation Science",
           "Research and Evaluation Methodology", "Romance Languages", "School Psychology", "Science Education",
           "Sociology and Criminology &amp; Law", "Soil and Water Science", "Soil and Water Sciences", "Spanish",
           "Spanish and Portuguese Studies", "Special Education", "Speech, Language and Hearing Sciences",
           "Special Education, School Psychology and Early Childhood Studies", "Sustainable Construction",
           "Teaching and Learning", "Tourism and Recreation Management", "Tourism, Hospitality, & Event Management",
           "Tourism, Recreation, and Sport Management", "Urban and Regional Planning", "Veterinary Medical Sciences",
           "Veterinary Medicine", "Wildlife Ecology and Conservation", "Women's Studies", "Zoology",
           "Occupational Therapy", "Romance Languages and Literatures"]
boring += ['Ed.D.', 'M.A.M.C.', 'M.A.', 'M.H.P.', 'M.S.C.M.', 'M.S.', 'M.U.R.P.', 'B.S.', 'M.D.P.', 'D.B.A.', 'B.L.A', 'M.L.A.']
reboringdegree = re.compile(' (M\.S\.|Ed\.D\.|M\.A\.|M\.H\.P\.|M\.U\.R\.P\.|B\.S\.|M\.D\.P\.|D\.B\.A\.|B\.L\.A\.|M\.L\.A\.)')
boring += ['Plant Pathology Thesis, Ph.D.', 'Animal Sciences Thesis, Ph.D.', 'Art History Thesis, Ph.D.',
           'Counseling and Counselor Education Thesis, Ph.D.', 'Curriculum and Instruction Thesis, Ph.D.',
           'Design, Construction, and Planning Thesis, Ph.D.', 'Fisheries and Aquatic Sciences Thesis, Ph.D.',
           'Food and Resource Economics Thesis, Ph.D.', 'Geography Thesis, Ph.D.', 'English Thesis, Ph.D.', 
           'Higher Education Administration Thesis, Ph.D.', 'Human-Centered Computing Thesis, Ph.D.',
           'Industrial and Systems Engineering Thesis, Ph.D.', 'Interdisciplinary Ecology Thesis, Ph.D.',
           'Mass Communication Thesis, Ph.D.', 'Microbiology and Cell Science Thesis, Ph.D.',
           'Pharmaceutical Sciences Thesis, Ph.D.', 'Public Health Thesis, Ph.D.', 'Special Education Thesis, Ph.D.',
           'Youth Development and Family Science Thesis, Ph.D.', 'Zoology Thesis, Ph.D.', 
           'Agricultural and Biological Engineering Thesis, Ph.D.', 'Counseling Psychology Thesis, Ph.D.',
           'Food Science Thesis, Ph.D.', 'Forest Resources and Conservation Thesis, Ph.D.',
           'Health and Human Performance Thesis, Ph.D.', 'Materials Science and Engineering Thesis, Ph.D.',
           'Soil and Water Sciences Thesis, Ph.D.', 'Agronomy Thesis, Ph.D.', 'Entomology and Nematology Thesis, Ph.D.',
           'Nutritional Sciences Thesis, Ph.D.', 'School Psychology Thesis, Ph.D.', 'Chemistry Thesis, Ph.D.',
           'Veterinary Medical Sciences Thesis, Ph.D.', 'Business Administration Thesis, Ph.D.', 
           'Psychology Thesis, Ph.D.', 'Horticultural Sciences Thesis, Ph.D.', 'Medical Sciences Thesis, Ph.D.',
           'Aerospace Engineering Thesis, Ph.D.', 'Agricultural Education and Communication Thesis, Ph.D.',
           'Anthropology Thesis, Ph.D.', 'Chemical Engineering Thesis, Ph.D.', 'Epidemiology Thesis, Ph.D.',
           'Genetics and Genomics Thesis, Ph.D.', 'Geology Thesis, Ph.D.', 'Linguistics Thesis, Ph.D.',
           'Music Education Thesis, Ph.D.', 'Romance Languages Thesis, Ph.D.', 'Sociology Thesis, Ph.D.',
           'Wildlife Ecology and Conservation Thesis, Ph.D.', 'Business', 'Theatre',
           'Sustainable Development Practice field practicum report, M.D.P.',
           'Business Administration dissertation, D.B.A.', 'Theatre and Dance',
           'Sustainable Development Practice field practicum report M.D.P.']


jnlfilename = 'THESES-FloridaU-%s' % (ejlmod3.stampoftoday())

options = uc.ChromeOptions()
#options.add_argument('--headless')
options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
options.add_argument("--enable-javascript")
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
driver.implicitly_wait(60)

prerecs = []
uninteresting = []
backup = []
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

driver.get('https://ufdc.ufl.edu/')
time.sleep(120)
for page in range(pages):
    tocurl = 'https://ufdc.ufl.edu/results?datehi=' + str(stopyear) + '-31-12&datelo=' + str(startyear) + '-01-01&filter=type%3Atheses&sort=desc&page=' + str(page+1)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        #WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'BriefView_container__2e-2g')))
#        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'BriefView_title__31xSy')))
        time.sleep(5)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        #print(tocpage)
        sections = tocpage.find_all('article')
        for section in sections:
            for div in section.find_all('div'):
                if div.has_attr('class') and re.search('BriefView_title__', div['class'][0]):
                    for a in div.find_all('a'):
                        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : [], 'restricted' : False, 'autaff' : []}
                        rec['link'] =  'https://ufdc.ufl.edu' + a['href']
                        #marc xml works only for some records
                        rec['artlink'] =  re.sub('^\/(..)(..)(..)(..)(..)\/(.*)\/citation', r'https://ufdcimages.uflib.ufl.edu/\1/\2/\3/\4/\5/\6/marc.xml', a['href'])
                        rec['doi'] = '20.2000/FloridaU' + re.sub('\/citation', '', a['href'])
                        rec['tit'] = a.text.strip()
                        for p in section.find_all('p'):
                            spans = p.find_all('span')
                            spant = spans[0].text.strip()
                            if spant == 'Creator:':
                                rec['autaff'] = [[ spans[1].text.strip(), publisher ]]
                            elif spant == 'Publication Date:':
                                rec['date'] = spans[1].text.strip()

                        if ejlmod3.checkinterestingDOI(rec['doi']):
                            if skipalreadyharvested and rec['doi'] in alreadyharvested:
                                backup.append(rec['doi'])
                            else:
                                prerecs.append(rec)
                                print('  - ', rec['doi'])
                        else:
                            uninteresting.append(rec['doi'])
        print('\n  %4i records so far (%4i uninteresting, %4i already in backup)\n' % (len(prerecs), len(uninteresting), len(backup)))
    except:
        print(' could not load "%s"' % (tocurl))
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        print(tocpage.text)
        break
    time.sleep(10)

i = 0
recs = []
for rec in prerecs:
    i += 1
    keepit = True
    embargo = False
    ejlmod3.printprogress('-', [[len(recs), i, len(prerecs)], [rec['artlink']]])
    #TRY MARC XML
    artfilename = '/tmp/florida_%s' % (re.sub('\W', '', rec['artlink']))
    if not os.path.isfile(artfilename):
        os.system('wget -O %s -q "%s"' % (artfilename, rec['artlink']))
        time.sleep(5)
    inf = open(artfilename, 'r')
    lines = inf.readlines()
    inf.close()
    artpage = BeautifulSoup(''.join(lines), features="lxml")
    #author
    for df in artpage.find_all('datafield', attrs = {'tag' : '100'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            rec['autaff'] = [[ re.sub('\.$', '', sf.text.strip()) ]]
    #title
    for df in artpage.find_all('datafield', attrs = {'tag' : '245'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            rec['tit'] = sf.text.strip()
    #date
    for df in artpage.find_all('datafield', attrs = {'tag' : '260'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'c'}):
            rec['date'] = re.sub('\.$', '', sf.text.strip())
    #keywords
    for df in artpage.find_all('datafield', attrs = {'tag' : '653'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            rec['keyw'].append(sf.text.strip())
    #pages
    for df in artpage.find_all('datafield', attrs = {'tag' : '300'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            sft = sf.text.strip()
            if re.search('\d+ pages', sft):
                rec['pages'] = re.sub('.*?(\d+) pages.*', r'\1', sft)
            elif  re.search('\d+ p\.\)', sft):
                rec['pages'] = re.sub('.*?(\d+) p\..*', r'\1', sft)
    #abstract
    for df in artpage.find_all('datafield', attrs = {'tag' : '520'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            rec['abs'] = sf.text.strip()
    #department
    for df in artpage.find_all('datafield', attrs = {'tag' : '690'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            dep = re.sub('(.*) thesis,.*', r'\1', sf.text.strip())
            if dep in boring:
                keepit = False
                print('   skip "%s"' % (dep))
            else:
                rec['note'].append(dep)
    #500
    for df in artpage.find_all('datafield', attrs = {'tag' : ['500', '590']}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            sft = sf.text.strip()
            #supervisor
            if re.search('^Advis[oe]r:', sft):
                rec['supervisor'].append([re.sub('.*: *(.*).?$', r'\1', sft)])
            #department
            elif re.search('^Major department:', sft):
                dep = re.sub('Major department: *', '', sft)
                dep = re.sub('\.$', '', dep).strip()
                if dep in boring:
                    keepit = False
                    print('   skip "%s"' % (dep))
                else:
                    rec['note'].append(dep)
    #degree
    for df in artpage.find_all('datafield', attrs = {'tag' : '502'}):
        for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
            if re.search('Thesis \(', sf.text):
                degree = re.sub('Thesis \((.*?)\).*', r'\1', sf.text.strip())
                if degree in boring:
                    print('   skip "%s"' % (degree))
                    keepit = False
                elif degree != 'Ph.D.':
                    rec['note'].append(degree)
    #complete
    dfs = artpage.find_all('datafield')
    #for df in dfs:
    #    for sf in df.find_all('subfield'):
    #        rec['note'].append('[MARC] %s%s : %s' % (df['tag'], sf['code'], sf.text.strip()))
    #IF MARC XML DOES NOT WORK
    if not dfs:
        time.sleep(1)
        print('     try', rec['link'])
        try:
            driver.get(rec['link'])
            #WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'my-3')))
            artpage = BeautifulSoup(driver.page_source, features="lxml")
            #print(artpage)


            #scheiss JavaScript
            
            print(artpage.text)
            time.sleep(5)
            #title
            for h1 in artpage.find_all('h1'):
                rec['tit'] = h1.text
            for a in artpage.body.find_all('a'):
                if a.has_attr('href'):
                    #author
                    if re.search('results\?creator=', a['href']):
                        author = re.sub('.*results\?creator= *"?(.*)"?$', r'\1', a['href'])
                        author = re.sub('"', '', author)
                        rec['autaff'] = [[ author ]]
                    #date
                    elif re.search('publication_date=', a['href']):
                        rec['date'] = a.text.strip()
            #pages
            for div in artpage.find_all('div', attrs = {'class' : 'my-3'}):
                if re.search('\d+ pages\)', div.text):
                    rec['pages'] = re.sub('.*?(\d+) pages.*', r'\1', div.text.strip())
                elif re.search('\(\d+ p\.\)', div.text):
                    rec['pages'] = re.sub('.*?(\d+) p\..*', r'\1', div.text.strip())
            #supervisor
            for span in artpage.find_all('span'):
                if re.search('^Advis[oe]r:', span.text):
                    sv = re.sub('.*: *(.*).?$', r'\1', span.text.strip())
                    sv = re.sub('.... Show more', '', sv)
                    sv = re.sub(', *', ', ', sv)
                    rec['supervisor'].append([sv])
                    span.decompose()
            for li in artpage.find_all('li'):                    
                for p in li.find_all('p', attrs = {'class' : 'my-3'}):
                    pt = p.text.strip()
                    p.decompose()
                    #abstract
                    if pt == 'Abstract:':
                        rec['abs'] = li.text.strip()                
            #department
            for div in artpage.body.find_all('div', attrs = {'class' : 'content-css'}):
                for span in div.find_all('span'):
                    spant = span.text.strip()
                    if re.search('Major department: ', spant):
                        print(artpage)
                        dep = re.sub('Major department: ', '', spant)
                        dep = re.sub('\.$', '', dep).strip()
                        if dep in boring:
                            keepit = False
                            print('   skip "%s"' % (dep))
                        else:
                            rec['note'].append(dep)
            #subjects
            for div in artpage.find_all('div', attrs = {'class' : 'citation-module'}):
                for span in div.find_all('span', attrs = {'class' : 'identifier'}):
                    if re.search('Subjects', span.text):
                        for li in div.find_all('li'):
                            subject = li.text.strip()
                            if subject in boring:
                                keepit = False
                                print('   skip "%s"' % (subject))
                            elif reboringdegree.search(subject):
                                keepit = False
                                print('   skip "%s"' % (subject))                                
                            else:
                                rec['note'].append(subject)     
            ejlmod3.printrecsummary(rec)                           
            if not 'tit' in rec or not rec['autaff']:
                embargo = True
                print('    failed to extract author or title')
        except:
            embargo = True
            print('    failed')
    if keepit:
        if not embargo and rec['autaff']:
            rec['autaff'][-1].append(publisher)
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['doi'])


ejlmod3.writenewXML(recs, publisher, jnlfilename)
driver.quit()
