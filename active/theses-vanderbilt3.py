# -*- coding: utf-8 -*-
#harvest theses from Vanderbilt U.
#JH: 2021-11-21
#FS: 2023-02-21

import getopt
import sys
import os
#from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import ejlmod3
import re
import cloudscraper

publisher = 'Vanderbilt U.'
jnlfilename = 'THESES-VANDERBILT-%s' % (ejlmod3.stampoftoday())
pages = 15
skipalreadyharvested = True
boringdepartments = ['Anthropology', 'Art History', 'Biochemistry', 'Biological Sciences',
                     'Biomedical Engineering', 'Biomedical Informatics', 'Biomedical Sciences',
                     'Biostatistics', 'Cancer Biology', 'Cell & Developmental Biology',
                     'Cell and Development Biology', 'Cell and Developmental Biology',
                     'Chemical & Physical Biology', 'Chemical Engineering',
                     'Chemical and Physical Biology', 'Chemistry', 'Civil Engineering',
                     'Civil and Enviromental Engineering', 'Community Research & Action',
                     'Community Research and Action', 'Comparative Literature',
                     'Creative Writing', 'Earth & Environmental Sciences',
                     'Earth and Environmental Sciences', 'Economic Development', 'Economics',
                     'Education & Human Development', 'Electrical Engineering', 'English',
                     'English and Comparative Media Analysis and Practice',
                     'Environmental Engineering', 'Epidemiology', 'French',
                     'French and Comparative Media Analysis', 'Geology', 'German',
                     'Hearing & Speech Sciences', 'Hearing and Speech Sciences', 'History',
                     'History of Art', 'Human & Organizational Development', 'Human Genetics',
                     'Human and Organizational Development', 'Interdisciplinary',
                     'Interdisciplinary Materials Science', 'Interdisciplinary Studies: <Major>',
                     'Interdisciplinary Studies: Analytical Pharmacology',
                     'Interdisciplinary Studies: Applied Statistics',
                     'Interdisciplinary Studies: Biological and Applied Chemistry',
                     'Interdisciplinary Studies: Cancer Pharmacology',
                     'Interdisciplinary Studies: Cardiovascular Pharmacology',
                     'Interdisciplinary Studies: Communication Disorders and Neurodevelopmental Disabilities',
                     'Interdisciplinary Studies: Developmental Neuropharmacology',
                     'Interdisciplinary Studies: Engineering Management',
                     'Interdisciplinary Studies: Environmental Management',
                     'Interdisciplinary Studies: Environmental Management and Policy',
                     'Interdisciplinary Studies: Focus on Clinical and Cellular Biology',
                     'Interdisciplinary Studies: Health Services Research and Policy',
                     'Interdisciplinary Studies: Human Computer Interaction',
                     'Interdisciplinary Studies: Human Genetics',
                     'Interdisciplinary Studies: Information Technology',
                     'Interdisciplinary Studies: Integrated Computational Decision Science',
                     'Interdisciplinary Studies: Interdisciplinary Pharmacology',
                     'Interdisciplinary Studies: Language and Literacy',
                     'Interdisciplinary Studies: Magnetic Resonance Imaging and Spectroscopic Methodology',
                     'Interdisciplinary Studies: Management of Technology',
                     'Interdisciplinary Studies: Membrane Transporter Biology',
                     'Interdisciplinary Studies: Metabolic Pharmacology',
                     'Interdisciplinary Studies: Molecular Neuropharmacology',
                     'Interdisciplinary Studies: Molecular Pharmacology',
                     'Interdisciplinary Studies: Neurogenetics',
                     'Interdisciplinary Studies: Prosody, Language and Music',
                     'Interdisciplinary Studies: Structural Composite Materials',
                     'Interdisciplinary Studies: Systems Engineering',
                     'Interdisciplinary Studies: Systems Engineering and Operations Research',
                     'Interdisciplinary Studies: Systems Neuroscience', 'Latin American Studies',
                     'Law & Economics', 'Law and Economics', 'Leadership & Policy Studies',
                     'Leadership and Policy Studies', 'Learning, Teaching & Diversity',
                     'Learning, Teaching and Diversity', 'Learning, Teaching, and Diversity',
                     'Liberal Arts and Science', 'Management', 'Management of Technology',
                     'Materials Science and Engineering', 'Mechanical Engineering',
                     'Medicine, Health & Society', 'Medicine, Health, and Society',
                     'Microbe-Host Interactions', 'Microbiology and Immunology', 'Molecular Biology',
                     'Molecular Pathology & Immunology', 'Molecular Physiology & Biophysics',
                     'Molecular Physiology and Biophysics', 'Neuroscience', 'Nursing Science',
                     'Pathology', 'Pathology, Microbiology and Immunology', 'Pharmacology',
                     'Philosophy', 'Political Science', 'Psychology', 'Religion',
                     'Social and Political Thought', 'Sociology', 'Spanish',
                     'Spanish & Portuguese', 'Spanish and Portuguese', 'Special Education',
                     'Teaching and Learning', 'Teaching, Learning, and Diversity',
                     'cell and developmental biology', 'ell & Developmental Biology']
                     
# Initilize Webdriver
#driver = webdriver.PhantomJS()
scraper = cloudscraper.create_scraper()

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

recs = []

def get_sub_side(url, department):
        hdl = re.sub('.*handle\/', '', url)
        if skipalreadyharvested and hdl in alreadyharvested:
                return

        rec = {'link' : url, 'tc' : 'T', 'jnl' : 'BOOK'}

        if department:
                if department == 'Astrophysics':
                        rec['fc'] = 'a'
                elif department == 'Computer Science':
                        rec['fc'] = 'c'
                elif department == 'Mathematics':
                        rec['fc'] = 'm'
                elif not department in ['Physics', 'Other']:
                        rec['note'] = [ department ]

        print("[" + url + "] --> Harversting Data")

        soup = BeautifulSoup(scraper.get(url).text, 'lxml')
        sleep(10)

        # Get the title
        title_section = soup.find_all('h2')
        for i in title_section:
                if i.get('class') == None:
                        rec['tit'] = i.text

        # Get Author
        author_section = soup.find_all('div', attrs={'class': 'author-entry'})
        rec['autaff'] = [[author_section[0].text]]
        if len(author_section) > 1 and re.search('\d\d\d\d\-\d\d\d\d', author_section[1].text):
                rec['autaff'][-1].append(author_section[1].text)
        rec['autaff'][-1].append(publisher)

        # Get Handle Link
        for meta in soup.find_all('meta', attrs = {'name' : 'DC.identifier'}):
                if re.search('handle.net\/', meta['content']):
                        rec['hdl'] = re.sub('.*handle.net\/', '', meta['content'])

        # Get publish date
        date_section = soup.find_all('div', attrs={'class': 'simple-item-view-date'})
        if len(date_section) == 1:
                rec['date'] = date_section[0].text.split('\n')[-1].replace(' ', '')

        # Get the abstract
        abstract_section = soup.find_all('div', attrs={'class': 'item-abstract'})
        if len(abstract_section) == 1:
                rec['abs'] = abstract_section[0].text

        # Get the hidden pdf file link
        pdf_link_section = soup.find_all('div', attrs={'class': 'file-link'})
        if len(pdf_link_section) == 1:
                pdf_link = pdf_link_section[0].find_all('a')
                if len(pdf_link) == 1:
                        pdf = pdf_link[0].get('href')
                        rec['hidden'] = "https://ir.vanderbilt.edu" + pdf

        #pseudoDOI
        if not 'hdl' in list(rec.keys()):
                rec['doi'] = '20.2000/Vanderbilt/' + re.sub('\W', '', url[20:])

        if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
                print('   already in backup')
        elif skipalreadyharvested and 'hdl' in rec and rec['hdl'] in alreadyharvested:
                print('   already in backup')
        else:
                ejlmod3.printrecsummary(rec)
                print('   ', list(rec.keys()))
                recs.append(rec)

# Open Initial Page
for page in range(pages):
        tocpage = "https://ir.vanderbilt.edu/handle/1803/9598/recent-submissions?offset=" + str(20*page)
        print("--- Open Page " + str(page+1) + "/" + str(pages) + " --- " + tocpage)

        for artifact in BeautifulSoup(scraper.get(tocpage).text, 'lxml').find_all('div', attrs={'class': 'artifact-description'}):
                (department, interesting) = ('', True)
                for div in artifact.find_all('div', attrs = {'class' : 'publisher'}):
                        department = re.sub('Department: *', '', div.text.strip())
                        department = re.sub('&amp;', '&', department)
                        if department in boringdepartments:
                                interesting = False
                                print('  skip "%s"' % (department))
                if interesting:
                        sub_side_link = artifact.find_all('a')
                        get_sub_side("https://ir.vanderbilt.edu" + sub_side_link[0].get('href'), department)
        sleep(5)


ejlmod3.writenewXML(recs, publisher, jnlfilename)
