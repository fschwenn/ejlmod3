# -*- coding: utf-8 -*-
#harvest theses from City University New York
#FS: 2022-08-29

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'CUNY, Graduate School - U. Ctr.'
jnlfilename = 'THESES-CUNY-%s' % (ejlmod3.stampoftoday())
years = 2
pages = 5
boring = ['M.A.', 'B.A.', 'M.S.', 'D.M.A.', 'Au.D.', 'D.P.T.', 'D.P.H.']
boring += ['American Politics', 'Environmental Studies', 'International Relations',
           'African American Studies', 'History of Art, Architecture, and Archaeology',
           "Women's Studies", 'Industrial and Organizational Psychology', 'Nursing Administration',
           'Educational Assessment, Evaluation, and Research', 'Political Science',
           'Accounting', "Acting", "Aesthetics", "African American Studies", "Africana Studies",
           "African Languages and Societies", "African Studies", "American Art and Architecture",
           "American Literature", "American Material Culture", "American Politics",
           "American Popular Culture", "American Studies", "Analytical Chemistry",
           "Animal Experimentation and Research", "Anthropological Linguistics and Sociolinguistics",
           "Anthropology", "Applied Ethics", "Arabic Language and Literature",
           "Archaeological Anthropology", "Art Education", "Artificial Intelligence and Robotics",
           "Arts and Humanities", "Asian American Studies", "Atomic, Molecular and Optical Physics",
           "Audio Arts and Acoustics", "Bacteriology", "Basque Studies", "Behavioral Neurobiology",
           "Behavior and Behavior Mechanisms", "Behavior and Ethology", "Educational Psychology",
           "Bilingual, Multilingual, and Multicultural Education", "Biochemistry", "Education",
           "Biochemistry, Biophysics, and Structural Biology", "Biodiversity", "Biogeochemistry",
           "Bioinformatics", "Biological and Chemical Physics", "Biological and Physical Anthropology",
           "Biological Engineering", "Biological Psychology", "Biology", "Biophysics", "Botany",
           "Cell Biology", "Cellular and Molecular Physiology", "Celtic Studies", "Economics",
           "Central American Studies", "Chemistry", "Classical Literature and Philology",
           "Clinical Psychology", "Cognition and Perception", "Cognitive Neuroscience",
           "Cognitive Psychology", "Cognitive Science", "Community Health and Preventive Medicine",
           "Comparative Literature", "Comparative Methodologies and Theories", "Comparative Politics",
           "Comparative Psychology", "Composition", "Computational Biology", "Constitutional Law",
           "Contemporary Art", "Continental Philosophy", "Corporate Finance", "Criminology",
           "Criminology and Criminal Justice", "Critical and Cultural Studies", "Cultural History",
           "Curriculum and Instruction", "Curriculum and Social Inquiry", "Dance",  "Econometrics",
           "Databases and Information Systems", "Developmental Psychology", "Development Studies",
           "Diagnosis", "Digital Humanities", "Diplomatic History", "Disability Studies",
           "Dramatic Literature, Criticism and Theory", "Dutch Studies", "Early Childhood Education",
           "Educational Assessment, Evaluation, and Research", "Educational Methods",
            "Educational Sociology", "Education Economics", "Elementary Education and Teaching",
           "Endocrine System Diseases", "Engineering Physics", "English Language and Literature",
           "Environmental Health", "Environmental Sciences", "Environmental Studies", "Epistemology",
           "Ethics and Political Philosophy", "European History", "European Languages and Societies",
           "Evolution", "Experimental Analysis of Behavior", "Feminist, Gender, and Sexuality Studies",
           "Film and Media Studies", "Finance", "Finance and Financial Management", "Fine Arts",
           "Forest Management", "French and Francophone Language and Literature", "Geropsychology",
           "French and Francophone Literature", "Gender and Sexuality", "Genetics", "Genomics",
           "Geographic Information Sciences", "Geography", "Geometry and Topology", "German Literature",
           "Graphic Communications", "Graphics and Human Computer Interfaces", "Growth and Development",
           "Health Information Technology", "Health Psychology", "Higher Education", "History",
           "History of Art, Architecture, and Archaeology", "History of Gender", "History of Religion",
           "History of Science, Technology, and Medicine", "Holocaust and Genocide Studies",  "Legal",
           "Human Geography", "Human Resources Management", "Immunopathology", "Income Distribution",
           "Indigenous Education", "Indigenous Studies", "Industrial and Organizational Psychology",
           "Inequality and Stratification", "Intellectual History", "Interdisciplinary Arts and Media",
           "International and Area Studies", "International and Comparative Education", "Law and Politics",
           "International Economics", "International Relations", "Islamic Studies",  "Law and Society",
           "Islamic World and Near East History", "Italian Literature", "Language and Literacy Education",
           "Language Interpretation and Translation", "Latin American History",  "Latina/o Studies",
           "Latin American Languages and Societies", "Latin American Literature", "Latin American Studies",
            "Legal History", "Lesbian, Gay, Bisexual, and Transgender Studies", "Linguistic Anthropology",
           "Literature in English, British Isles", "Literature in English, North America", "Microbiology",
           "Literature in English, North America, Ethnic and Cultural Minority", "Materials Chemistry",
           "Longitudinal Data Analysis and Time Series", "Macroeconomics", "Marine Biology", "Marketing",
           "Maternal, Child Health and Neonatal Nursing", "Medicine and Health", "Migration Studies",
           "Medicine and Health Sciences", "Medieval Studies", "Mental Disorders", "Metaphysics",
            "Military History", "Models and Methods", "Modern Art and Architecture", "Modern Languages",
           "Modern Literature", "Molecular and Cellular Neuroscience", "Molecular Biology",
           "Molecular, Genetic, and Biochemical Nutrition", "Music Education", "Musicology",
           "Music Pedagogy", "Music Performance", "Music Practice", "Music Theory", "Nanomedicine",
           "National Security Law", "Nature and Society Relations", "Near and Middle Eastern Studies",
           "Near Eastern Languages and Societies", "Nonfiction", "Nursing", "Nursing Administration",
           "Nutritional and Metabolic Diseases", "Online and Distance Education", "Optics",
           "Organic Chemistry", "Organizational Behavior and Theory", "Other Communication",
           "Other Computer Engineering", "Other Computer Sciences", "Other Engineering", "Other Nursing",
           "Other Ecology and Evolutionary Biology", "Other Feminist, Gender, and Sexuality Studies",
           "Other Film and Media Studies", "Other Immunology and Infectious Disease", "Other Music",
           "Other Nutrition", "Other Psychiatry and Psychology", "Other Psychology",
           "Other Public Affairs, Public Policy and Public Administration", "Other Sociology",
           "Other Spanish and Portuguese Language and Literature", "Pathogenic Microbiology",
           "Performance Studies", "Personality and Social Contexts", "Philosophy of Language",
           "Philosophy of Science", "Physical and Environmental Geography", "Physiology",
           "Place and Environment", "Poetry", "Political Economy", "Political History", "Political Science",
           "Political Theory", "Politics and Social Change", "Population Biology",
           "President/Executive Department", "Psychiatry and Psychology", "Public Policy",
           "Psychological Phenomena and Processes", "Psychology", "Public Health and Community Nursing",
           "Quantitative, Qualitative, Comparative, and Historical Methodologies", "Race and Ethnicity",
           "Race, Ethnicity and Post-Colonial Studies", "Rehabilitation and Therapy", "Religion",
           "Religious Education", "Religious Thought, Theology and Philosophy of Religion",
           "Renaissance Studies", "Rhetoric and Composition", "Scholarship of Teaching and Learning",
           "Social and Behavioral Sciences", "Social and Cultural Anthropology", "Social History",
           "Social Influence and Political Communication", "Social Justice", "Social Media",
           "Social Psychology", "Social Statistics", "Social Work", "Sociology", "Sociology of Culture",
           "Spanish and Portuguese Language and Literature", "Spanish Linguistics", "Spatial Science",
           "Speech and Hearing Science", "Speech Pathology and Audiology", "Structural Biology",
           "Sustainability", "Syntax", "Systems Biology", "Systems Neuroscience", "Theatre History",
           "Translation Studies", "United States History", "Urban Studies", "Visual Studies",
           "Women's Health", "Women's History", "Women's Studies", "Work, Economy and Organizations",
           "Applied Behavior Analysis", "Cancer Biology", "Catalysis and Reaction Engineering",
           "Cell and Developmental Biology", "Classics", "Computational Linguistics", "School Psychology",
           "Data Storage Systems", "Earth Sciences", "Educational Technology", "Environmental Chemistry",
           "Ethnomusicology", "Labor Economics", "Life Sciences", "Linguistics",  "Philosophy of Mind",
           "Neuroscience and Neurobiology", "Other Education", "Other Life Sciences", "Palliative Nursing",
           "Phonetics and Phonology", "Polymer Chemistry", "Psychoanalysis and Psychotherapy",
           "Psycholinguistics and Neurolinguistics", "Quantitative Psychology", "Real Estate",
           "Semantics and Pragmatics", "Spanish Literature", "Theatre and Performance Studies",
           "Atmospheric Sciences", "Business Analytics", "Business Intelligence", "Jewish Studies",
           "Children's and Young Adult Literature", "Ecology and Evolutionary Biology", "Hydrology",
           "Environmental Monitoring", "Fresh Water Studies", "Geology", "Geophysics and Seismology",
           "Logic and Foundations", "Management Information Systems", "Materials Science and Engineering",
           "Meteorology", "Mineral Physics", "Molecular Genetics", "Nanotechnology", "Neurology",
           "Neurosurgery", "Organic Chemicals", "Other Chemistry", "Other Languages, Societies, and Cultures",
           "Physical Chemistry", "Radiology", "Secondary Education",  "Trauma", "Water Resource Management",
           "South and Southeast Asian Languages and Societies", "Tectonics and Structure", "Asian Studies",
           "Acoustics, Dynamics, and Controls", "Agricultural Science", "Agriculture", "Asian History",
           "Amino Acids, Peptides, and Proteins", "Animal Sciences", "Architecture", "Art and Design",
           "Biological Factors", "Biomechanics", "Biomedical Devices and Instrumentation", "Criminal Law",
           "Biomedical Engineering and Bioengineering", "Biomedical", "Biotechnology", "Ceramic Arts",
           "Business Administration, Management, and Operations", "Business", "Caribbean Languages and Societies",
           "Chemical Engineering", "Chemicals and Drugs", "Civil Engineering", "Community Health", "Courts",
           "Developmental Biology", "Digital Communications and Networking", "Disability and Equity in Education",
           "Educational Administration and Supervision", "Educational Leadership", "Education Policy",
           "Entrepreneurial and Small Business Operations", "Environmental Health and Protection",
           "Environmental Public Health", "Epidemiology", "Family, Life Course, and Society", "Robotics",
           "Fiber, Textile, and Weaving Arts", "First and Second Language Acquisition", "Fluid Dynamics",
           "Forensic Science and Technology", "Genetic Processes", "Harmonic Analysis and Representation",
           "Health Economics", "Health Services Research", "Higher Education Administration", "Rhetoric",
           "Higher Education and Teaching", "History of Philosophy", "Humane Education", "Immune System Diseases",
           "Industrial Organization", "Infectious Disease", "Information Security", "Inorganic Chemistry",
           "Intellectual Property Law", "International Law", "International Public Health", "OS and Networks",
           "Italian Language and Literature", "Law", "Logic and Foundations of Mathematics", "Music",
           "Literature in English, Anglophone outside British Isles and North America", "Neurosciences",
           "Male Urogenital Diseases", "Maternal and Child Health", "Medical Cell Biology", "Medical Genetics",
           "Medical Molecular Biology", "Medicinal-Pharmaceutical Chemistry", "Multicultural Psychology",
           "Nucleic Acids, Nucleotides, and Nucleosides", "Oceanography", "Operational Research",
            "Other Applied Mathematics", "Other Astrophysics and Astronomy", "Plant Sciences", "Probability",
           "Other Electrical and Computer Engineering", "Other Political Science", "Public Administration",
           "Other Social and Behavioral Sciences", "Pharmacy and Pharmaceutical Sciences", "Physical Therapy",
            "Public Health Education and Promotion", "Public Health", "Radiochemistry", "Remote Sensing",
           "Secondary Education and Teaching", "Signal Processing", "Soil Science", "Survival Analysis",
           "Special Education Administration", "Special Education and Teaching", "Strategic Management Policy",
           "Systems and Communications", "Systems Architecture", "Systems Engineering", "Urology",
           "Teacher Education and Professional Development", "Translational Medical Research", "Urban Education",
           "Urban Studies and Planning", "Virus Diseases", "German Language and Literature",
           "Instructional Media Design", "Social Welfare"]
tocurl = 'https://academicworks.cuny.edu/gc_etds'

prerecs = []
date = False
for page in range(pages):
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")
        time.sleep(3)
    except:
        print("retry %s in 180 seconds" % (tocurl))
        time.sleep(180)
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")

    for div in tocpage.body.find_all('div', attrs = {'id' : 'series-home'}):
        for child in div.children:
            try:
                name = child.name
            except:
                continue
            if name == 'h4':
                for span in child.find_all('span'):
                    date = span.text.strip()
            elif name == 'p':
                if int(date) >= ejlmod3.year(backwards=years):
                    if child.has_attr('class') and 'article-listing' in child['class']:
                        rec = {'jnl' : 'BOOK', 'tc' : 'T', 'date' : date, 'note' : [], 'supervisor' : []}
                        for a in child.find_all('a'):
                            rec['tit'] = a.text.strip()
                            rec['artlink'] = a['href']
                            a.replace_with('')
                        if ejlmod3.ckeckinterestingDOI(rec['artlink']):
                            prerecs.append(rec)
    tocurl = 'https://academicworks.cuny.edu/gc_etds/index.%i.html' % (page+2)
    print('  %i recs so far' % (len(prerecs)))

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
        print("retry %s in 180 seconds" % (rec['artlink']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['description', 'keywords', 'bepress_citation_author',
                                        'bepress_citation_pdf_url',
                                        'bepress_citation_doi', 'bepress_citation_online_date'])
    #thesis type
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'bepress_citation_dissertation_name'}):
        thesistype = meta['content']
        if thesistype in boring:
            keepit = False
        else:
            rec['note'].append(meta['content'])
    #categories
    for div in artpage.body.find_all('div', attrs = {'id' : 'bp_categories'}):
        for p in div.find_all('p'):
            for category in re.split(' \| ', p.text.strip()):
                if category in boring:
                    keepit = False
                else:
                    rec['note'].append('CATEGORY=%s' % (category))
    #supervisor
    for div in artpage.body.find_all('div', attrs = {'id' : ['advisor1', 'advisor2']}):
        for p in div.find_all('p'):
            rec['supervisor'].append([ re.sub('^Dr. ', '', p.text.strip())])
    #ORCID
    for div in artpage.body.find_all('div', attrs = {'id' : 'orcid'}):
        for h4 in div.find_all('h4'):
            if re.search('Author ORCID', h4.text):
                for a in div.find_all('a'):
                    rec['autaff'][-1].append(re.sub('.*\/', 'ORCID:', a.text.strip()))
    if keepit:
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
