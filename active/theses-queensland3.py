# -*- coding: utf-8 -*-
#harvest theses from Queensland U.
#
#FS: 2020-04-03
#FS: 2023-02-24

#
# All hidden behinde JavaSCript :-(
# 

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

publisher = 'Queensland U.'
rpp = 100
pages = 15 
startyear = ejlmod3.year(backwards=1)
stopyear = ejlmod3.year()
skipalreadyharvested = True

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
jnlfilename = 'THESES-QUEENSLAND-%sB' % (ejlmod3.stampoftoday())

#driver
options = uc.ChromeOptions()
#options.add_argument('--headless')
#options.binary_location='/usr/bin/chromium-browser'
options.binary_location='/usr/bin/google-chrome'
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
    
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

boringunits = ['School of Music,', 'Institute for Molecular Bioscience,',
               'School of Chemical Engineering,', 'School of Mechanical and Mining Engineering,',
               'School of Agriculture and Food Sciences,', 'School of Medicine,',
               'Australian Institute for Bioengineering and Nanotechnology,',
               'Faculty of Medicine,', 'Medicine Faculty,', 'Queensland Brain Institute,',
               'School of Biological Sciences,', 'School of Veterinary Science,',
               'School of Earth and Environmental Sciences,',
               'School of Economics,', 'School of Health & Rehabilitation Sciences,',
               'School of Health and Rehabilitation Sciences,',
               'School of Historical and Philosophical Inquiry,',
               'School of Information Technology & Electrical Engineering,',
               'School of Information Technology and Electrical Engineering,',
               'University of Queensland Business School,', 'UQ Business School,'
               'Advanced Water Management Centre,',
               'Australian Institute for Bioengineering & Nanotechnology,',
               'Australian Institute for Bioengineering and Nanotechnology ,',
               'Business School,', 'Faculty of Medicine ,',
               'Institute for Social Science Research,',
               'Julius Kruttschnitt Mineral Research Centre,',
               'Queensland Alliance for Agriculture and Food Innovation,',
               'School of Agriculture & Food Sciences,',
               'School of Architecture,', 'School of Biological Science,',
               'School of Biomedical Sciences,', 'School of Business,',
               'School of Chemistry & Molecular Biosciences,',
               'School of Chemistry and Molecular Biosciences,',
               'School of Civil Engineering,', 'School of Communication and Arts,',
               'School of Earth and Environmental Science,', 'School of Education,',
               'School of Engineering, Civil Engineering,',
               'School of Health & Rehabilitation Sciences,',
               'School of Human Movement and Nutrition Sciences,',
               'School of Information Technology & Electrical Engineering,',
               'School of Languages and Cultures,',  'School of Law,',
               'School of Nursing, Midwifery and Social Work,', 'School of Pharmacy,',
               'School of Political Science and International Studies,',
               'School of Psychology,', 'School of Public Health,',
               'Sustainable Minerals Institute, Minerals Industry Safety and Health Centre,',
               'Sustainable Minerals Institute,',
               'Sustainable Minerals Institute, The Julius Kruttschnitt Mineral Research Centre,',
               'TC Beirne School of Law,',
               'The School of Chemistry and Molecular Biosciences,',
               'The School of Historical and Philosophical Inquiry,',
               'The School of Psychology,',
               'UQ Diamantina Institute,', 'UQ School of Business,',
               'School of Social Science,', 'UQ Business School,',
               'Advanced Water Management Centre,',
               'Australian Institute for Bioengineering and Nanotechnology (AIBN),',
               'Australian Institute of Bioengineering and Nanotechnology (AIBN),',
               'Centre for Coal Seam Gas,',
               'Centre for Crop Science, Queensland Alliance for Agriculture and Food Innovation,',
               'Information Technology & Electrical Engineering,',
               'Institute of Molecular Bioscience,',
               'Queensland Alliance for Agriculture and Food Innovation (QAAFI),',
               'Queensland Brain Institute and The Centre for Advanced Imaging,',
               'School of Biomedical Sciences and Faculty of Medicine,',
               'School of Chemistry and Molecular Bioscience,',
               'School of Communications and Arts,',
               'School of Dentistry,', 'School of Economics and Finance,',
               'School of Historical and Philosophical Enquiry,',
               'School of Language and Comparative Cultural Studies,',
               'School of Mechanical & Mining Engineering,',
               'School of Mechanical and Mining Engineering and School of Clinical Medicine,',
               'School of Political Science and International Studies and School of Social Science,',
               'School of Population Health,', 'School of Languages and Cultures.,',
               'School of Social Science, Faculty of Social and Behavioural Sciences,',
               'School of Social Sciences,', 'School of Veterinary Science ,',
               'Science and Engineering Faculty,', 'School of Nursing,',
               'Sustainable Minerals Institute and Julius Kruttschnitt Mineral Research Centre,',
               'T.C. Beirne School of Law,', 'The School of Veterinary Science,',
               'The University of Queensland Diamantina Institute,',
               'Aust Institute for Bioengineering & Nanotechnology,',
               'Australian Institute for Bioengineering and Nanotechnology and the Centre for Advanced Imaging,',
               'Australian Institute For Bioengineering and Nanotechnology,',
               'Australian Institute of Bioengineering and Nanotechnology,',
               'Australian Inst of Bioengineering & Nanotechnology,',
               'Biological Sciences,', 'BRC/SMI,',
               'Cancer Prevention Research Centre, School of Population Health,',
               'Centre for Accident Research & Road Safety - Qld (CARRS-Q),',
               'Centre for Hypersonics,',
               'Centre for Learning Innovation, Faculty of Education,',
               'Centre for Learning Innovation,',
               'Centre for Marine Studies/ School of Biological Sciences,',
               'Centre for Marine Studies,',
               'Centre for Marine Study, School of Biological Sciences,',
               'Centre For Mined Land Rehabilitation, Sustainable Minerals Institute,',
               'Centre for Nutrition and Food Sciences,',
               'Centre for Social Responsibility in Mining,',
               'Centre of Excellence for Environmental Decisions, School of Biological Sciences,',
               'Charles Darwin University,',
               'Chemistry and Molecular Biosciences,',
               'College of Engineering,',
               'Department of Architecture,',
               'Department of Engineering,',
               'Department of Engineering, University of Cambridge,',
               'Department of Environmental Science and Technology, La Trobe University,',
               'Department of Geology,',
               'Department of Linguistics,',
               'Department of Management and Engineering,',
               'Department of Political and Social Change,',
               'Department of Theoretical and Applied Linguistics,',
               'Desautels Faculty of Management,',
               'Diamantina Institute for Cancer, Immunology and Metabolic Medicine,',
               'Diamantina Institute,',
               'Discipline of General Practice, School of Medicine,',
               'Earth Systems Science Computational Centre,',
               'Ecology,', 'Economics,', 'Education,', 'EMSAH,',
               'English Media Studies and Art History,', 'Facultad de Filosofía y Letras,',
               'Faculty of Architecture, Design and Planning,',
               'Faculty of Arts and Business - The University of the Sunshine Coast,',
               'Faculty of Biology and Medicine, Department of Ecology and Evolution,',
               #'Faculty of Electrical Engineering, Mathematics & Computer Science,',
               'Faculty of Health and Behavioural Sciences,',
               'Faculty of Law, Business & Arts,', 'Faculty of Veterinary Science,',
               'Geography, Planning and Environmental Management,',
               'History, Philosophy, Religion and Classics (HPRC),',
               'History, Philosophy, Religion and Classics,',
               'Human Movement and Nutrition Sciences,',
               'Information Technology & Electrical Engineering,',
               'Information Technology and Electrical Engineering,',
               'Institute of Social & Cultural Anthropology,',
               'Institute of Social and Economic Research,',
               'Institut für Anglistik und Amerikanistik,', 'Laboratoire de Génie Chimique,',
               'Laboratoire Mat&apos;eriaux et Ph&apos;enom`enes Quantics,',
               'Laney Graduate School, French,',
               'Mechanical and Mining Engineering,',
               'Mechanical Engineering,',
               'Medicine - Greenslopes Private Hospital,', 'Music,',
               'Political Science and International Studies,',
               'Population Health,', 'Psychology,',
               'Qld Alliance for Agriculture and Food Innovation,',
               'Queensland Alliance for Agricultural and Food Innovation,',
               'Queensland Brain Institute and School of Mathematics and Physics,',
               'Queensland Brain Institute, Centre for Advanced Imaging,',
               'Queensland University of Technology,',
               'QUT School of Nursing and Institute of Health & Biomedical Innovation,',
               'Schoof of Nursing and Midwifery,',
               'School Biomedical Sciences,',
               'School of Agriculture and Food Sciences; School of Economics,',
               'School of Animal Studies,',
               'School of Architecture and Design, RMIT University,',
               'School of Biomedical Sciences and Queensland Brain Institute,',
               'School of Biomedical Science,',
               'School of Chemical and Molecular Biosciences,',
               'School of Chemical Engineering / Advanced Water Management Centre,',
               'School of Chemical Engineering, Advanced Water Management Centre,',
               'School of Chemical Engineering/Advanced Water Management Centre,',
               'School of Chemical Engineering/Australian Institue of Bioengineering and Nanotechnology,',
               'School of Chemical Engineering, National Research Centre for Environmental Toxciology,',
               'School of Chemistry & Molecular Bioscience,',
               'School of Chemistry and Molecular Biology,',
               'School of Chemistry and Molecular Biosciences (SCMB),',
               'School of Chemistry Molecular Biosciences,',
               'School of Communication and the Arts,',
               #'School of Computer Science, University of Adelaide,',
               #'School of Computing Science,',
               'School of Criminal Justice,',
               'School of Earth Sciences,', 'School of Education, Flinders Universiy,',
               'School of Engineering,',
               'School of English, Media Studies and Art history,',
               'School of English Media Studies and Art History,',
               'School of English, Media Studies and Art History,',
               'School of English, Media Studies, and Art History,',
               'School of Geography, Planning & Environmental Management,',
               'School of Geography, Planning & Env Management,',
               'School of Geography Planning and Environmental Management,',
               'School of Geography, Planning and Environmental Management,',
               'School of Geography, Planning and Environment Management,',
               'School of Government and International Relations,',
               'School of Historical and Philosophical Inquiry - Ecole Doctorale de Sciences Po,',
               'School of History, Philosophy, and Classics,',
               'School of History, Philosophy, Religion amd Classics,',
               'School of History, Philosophy, Religion & Classics,',
               'School of History, Philosophy, Religion and Classics,',
               'School of History, Philosophy, Religion, and Classics,',
               'School of History, Philosophy, Religion Classics,',
               'School of History, Religion, Philosophy, and Classics,',
               'School of Human Movement and Nutrition Sciences and Mater Research Institute - UQ,',
               'School of Human Movement Studies,',
               'School of Integrative Systems,',
               'School of Journalism and Communication,',
               'School of Justice,',
               'School of Land, Crop and Food Sciences, Centre for Native Floriculture,',
               'School of Land, Crop and Food Sciences,',
               'School of Language & Comparative Cultural Studies,',
               'School of Languages & Comparative Cultural Studies,',
               'School of languages and comparative cultural studies,',
               'School of Languages and Comparative Cultural Studies,',
               'School of Languages and Comp Cultural Studies,',
               'School of Mechancial and Mining Engineering,',
               'School of Mechanical & Mining Engineering,',
               'School of Mechanical and Mining Engineering, Centre for Hypersonics,',
               'School of Mechanical Engineering,',
               'School of Medicine and QIMR Berghofer Medical Research Institute,',
               'SCHOOL OF MEDICINE CENTRAL CLINICAL DIVISION,',
               'School of Medicine, Southern Clinical Division,',
               'School of Medicine (South),', 'School Of Medicine,',
               'School of Molecular and Chemical Biosciences,',
               'School of Nursing and Midwifery,',
               'School of Pharmacy and Queensland Children&apos;s Medical Research Institute,',
               'School of Political Science & Internat&apos;l Studies & the Institute for Social Science Research,',
               'School of Political Science & Internat&apos;l Studies,',
               'School of Political Science & International Studies,',
               'School of Political Science and International Studies/ Institute for Social Science Research (ISSR),',
               'School of Population Heallth,',
               'School of Psychology and Center for Youth Substance Abuse Research,',
               'School of Rehabilitation Health Sciences,',
               'School of Social Work and Human Services,',
               'School of Tourism,',
               'Schools of Civil Engineering and Chemical Engineering,',
               'Schoool of Economics,',
               'Schoool of Medicine,',
               'Social Work and Human Services,',
               'Sustainable Mineral Institute, Julius Kruttschnitt Mineral Research Centre,',
               'Sustainable Minerals Institute, Julius Kruttschnitt Mineral Research Centre,',
               'The Australian Institute for Bioengineering and Nanotechnology,',
               'The Global Change Institute / The School of Biological Sciences,',
               'The Institute for Molecular Bioscience,',
               'The Queensland Brain Institute,',
               'The School of Education,', 'The University of Queensland Business School,',
               'The School of Health and Rehabilitation Sciences,',
               'The School of Information Technology and Electrical Engineering,',
               'The School of Languages and Comparative Cultural Studies,',
               'The School of Medicine,', 'Queensland Alliance for Environmental Health Sciences,',
               'The School of Pharmacy,', 'School of Biology & Environmental Science,',
               'The School of Social Science,',
               'The Sustainable Minerals Institute,',
               'UQ Diamantina Insitute,', 'Translational Medicine',
               'Veterinary Science and Animal Production,', 'Management',
               'Microbiology and Immunology', 'Pharmacology and Toxicology', 'Physiology', 
               'School of Architecture, Design and Planning,', 
               'School of Communication and Arts ,', 'School of Design,',
               'School of Psychology & Counselling,', 'The School of Music,',
               'UQ Centre for Clinical Research,', 'Centre for Horticultural Science,']
boringunits += ['Advanced Water Management Centre, School of Chemical Engineering,',
                'Art, Design and Architecture,', 'Australian Centre for Water and Environmental Biotechnology,',
                'Centre for Advanced Imaging (CAI) Research Groups,',
                'Centre for Hypersonics, School of Mechanical and Mining Engineering,',
                'Centre for Mined Land Rehabilitation,', 'Centre for Public Awareness of Science,',
                'College of Law,', 'College of Nursing, Medicine and Health Sciences,', 'CSRH,',
                'Department of Accounting, Finance & Economics,', 'Department of Anthropology,',
                'Department of Metallurgical and Materials Engineering,', 'Faculty of Business and Law,',
                'Faculty of Health,', 'Faculty of Law,', 'Faculty of Medicine, School of Public Health,',
                'Graduate School of Education,', 'Institute for Molecular Biosciences,',
                'Macquarie Business School,', 'Queensland Alliance for Agriculture and Food Innovation ,',
                'Queensland Alliance of Agriculture and Food Innovation,', 'Queensland Conservatorium,',
                'QUT School of Advertising, Marketing & Public Relations,',
                'School Mechanical and Mining Engineering,',
                'School of Agriculture and Food Sciences, School of Veterinary Science,',
                'School of Agriculture and Food Science,',
                'School of Agricutural, Environmental and Veterinary Sciences,',
                'School of Architecture and Built Environment,', 'School of Art, Design and Architecture,',
                'School of Biological Sciences ,', 'School of Biology,',
                'School of Biomedical Sciences, Faculty of Health, Queensland University of Technology,',
                'School of Business ,', 'School of Chemistry and Molecular Biosciences ,',
                'School of Civil & Environmental Engineering,', 'School of Clinical Sciences,',
                'School of Design ,', 'School of Earth and Atmospheric Sciences,',
                'School of Earth, Atmosphere and Environment,', 'School of Education ,',
                'School of Engineering, Advanced Water Management Centre,',
                'School of Historical and Philosophical Inquiry, TC Beirne School of Law,',
                'School of History and Philosophical Inquiry,',
                'School of Law and Society, Sustainability Research Centre,', 'School of Law ,',
                'School of Management,', 'Schoolof Mechanical and Mining Engineering ,',
                'School of Political Science and International Studies School,',
                'School of Psychology and Counselling,', 'The School of Chemical Engineering,']


prerecs = []
page = 0
dois = []
tocurl = 'https://espace.library.uq.edu.au/records/search?page=' + str(page+1) + '&pageSize=' + str(rpp) + '&sortBy=published_date&sortDirection=Desc&activeFacets%5Branges%5D%5BYear+published%5D%5Bfrom%5D=' + str(startyear) + '&activeFacets%5Branges%5D%5BYear+published%5D%5Bto%5D=' + str(stopyear) + '&advancedSearchFields%5B%5D=Scopus+document+type&advancedSearchFields%5B%5D=Genre&advancedSearchFields%5B%5D=Year+published&advancedSearchFields%5B%5D=Published+year+range&advancedSearchFields%5B%5D=Genre&searchQueryParams%5Brek_genre_type%5D%5Bvalue%5D%5B%5D=PhD+Thesis&searchQueryParams%5Brek_genre_type%5D%5Blabel%5D%5B%5D=PhD+Thesis&searchQueryParams%5Brek_display_type%5D%5B%5D=187&searchMode=advanced'
driver.get(tocurl)
WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'citationContent')))
for page in range(pages):
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    tocpage = BeautifulSoup(driver.page_source, features="lxml")
    #print( tocpage.body)
    time.sleep(1)
    divs = tocpage.body.find_all('div', attrs = {'class' : 'publicationCitation'})
    for div in divs:
        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : [], 'supervisor' : [], 'keyw' : []}
        for span in div.find_all('span', attrs = {'class' : 'citationOrgUnit'}):
            rec['unit'] = span.text.strip()
            rec['note'].append(span.text.strip())
        for span in div.find_all('span', attrs = {'class' : 'citationThesisType'}):
            rec['type'] = span.text.strip()
            #rec['note'].append('TYPE:::' + rec['type'])
        for span in div.find_all('span', attrs = {'class' : 'citationTitle'}):
            rec['tit'] = span.text.strip()
        for span in div.find_all('span', attrs = {'class' : 'citationAuthors'}):
            rec['autaff'] = [[ span.text.strip(), publisher ]]
        for span in div.find_all('span', attrs = {'class' : 'citationDate'}):
            rec['date'] = re.sub('\D', '', span.text.strip()) 
        for a in div.find_all('a'):
            if re.search('\/view\/', a['href']):
                rec['artlink'] = 'https://espace.library.uq.edu.au' + a['href']
                rec['doi'] = '20.2000/Queensland/' + re.sub('\W', '', a['href'])
        if 'unit' in list(rec.keys()) and rec['unit'] in boringunits:
            print('  skip "%s"' % (rec['unit']))
        else:
            if not rec['unit'] in ['Faculty of Science,', 'School of Mathematics and Physics,']:
                rec['note'].append('UNIT:::' + rec['unit'])
            if skipalreadyharvested and rec['doi'] in alreadyharvested:
                print('  %s already in backup' % (rec['doi']))
            elif not rec['doi'] in dois:
                prerecs.append(rec)
                dois.append(rec['doi'])
                #print(rec['doi'])
    print('  %4i records so far' % (len(prerecs)))
    if page+1 < pages:
        print('\n  --> click for page %i/%i <--\n' % (page+2, pages))
        input("\n  --> then press Enter to continue <---\n\n")





j = 0
reunkw = re.compile('^UQ Theses')
recs = []
for rec in prerecs:
    j += 1
    ejlmod3.printprogress("-", [[j, len(prerecs)], [rec['artlink']], [len(recs)]])
#    try:
    driver.get(rec['artlink'])
    time.sleep(2)
    #WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'social-icon')))
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'MuiGrid2-container')))
    artpage = BeautifulSoup(driver.page_source, features="lxml")
    time.sleep(5)
#    except:
#        print('  try again in 30s')
#        driver.get(rec['artlink'])
#        #WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'social-icon')))
#        artpage = BeautifulSoup(driver.page_source, features="lxml")
#        time.sleep(30)
#    print(artpage)
#    print(artpage.text)
    ejlmod3.metatagcheck(rec, artpage, ['citation_abstract', 'citation_date', 'citation_title',
                                        'citation_keywords', 'citation_authors', 'citation_doi'])
    #rec['autaff'][-1].append(publisher)
    spans = {}
    for div in artpage.body.find_all('div', attrs = {'class' : 'MuiGrid2-container'}):
        subdivs = div.find_all('div', attrs = {'class' : 'MuiGrid2-container'})
        if len(subdivs):
            continue
        spans = {}
        for span in div.find_all('span'):            
            if span.has_attr('data-testid'):
                spans[span['data-testid']] = span.text.strip()
        if 'rek-keywords-label' in spans:
            for li in div.find_all('li'):
                if not reunkw.search(li.text):
                    rec['keyw'].append(li.text.strip())
        elif 'rek-supervisor-label' in spans:
            for li in div.find_all('li'):
                rec['supervisor'].append([li.text.strip()])
        if 'rek-description' in spans:
            rec['abs'] = spans['rek-description']
        elif 'rek-total-pages' in spans:
            rec['pages'] = spans['rek-total-pages']
        elif 'rek-oa-status-type' in spans:
            rec['oastatus'] = spans['rek-oa-status-type']        
        elif 'rek-doi' in spans:
            rec['doi'] = spans['rek-doi']
        elif 'rek-date' in spans:
            rec['date'] = spans['rek-date']     
        #print(spans.keys())
    for a in artpage.body.find_all('a', attrs = {'data-analyticsid' : 'file-name-0-download-link'}):
        rec['fulltext'] = re.sub('pdf\?.*', 'pdf', a['href'])
                
    #public or hidden PDF
    if 'fulltext' in rec:
        if 'oastatus' in list(rec.keys()) and rec['oastatus'] in  ['Gold', 'DOI']:
            rec['FFT'] = rec['fulltext']            
        else:
            rec['hidden'] = rec['fulltext']
    if skipalreadyharvested and rec['doi'] in alreadyharvested:
        print('    %s already in backup' % (rec['doi']))
    else:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
driver.quit()
