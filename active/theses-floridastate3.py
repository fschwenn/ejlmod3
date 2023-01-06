# -*- coding: utf-8 -*-
#harvest Florida State University theses
#FS: 2020-04-24


import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import codecs
import time
import ssl
import undetected_chromedriver as uc

publisher = 'Florida State U., Tallahassee (main)'
jnlfilename = 'THESES-FLORIDASTATE-%s' % (ejlmod3.stampoftoday())
pages = 7

topicsdict = {'Applied mathematics' : 'm', 'Astronomy' : 'a', 'Condensed matter' : 'f',
              'Mathematics' : 'm', 'Materials science' : '', 'Nuclear physics' : '',
              'Particles (Nuclear physics)' : '', 'Physics' : '', 'Plasma (Ionized gases)' : '',
              'Science' : '', 'Communication' : '', 'Computer science' : 'c',
              'Artificial intelligence' : 'c', 'Astrophysics' : 'a', 'Astrophysics' : 'a',
              'Electrical engineering' : '', 'Engineering' : '', 'Low temperatures' : '',
              'Mechanical engineering' : '', 'Nanoscience' : '', 'Nanotechnology' : '',
              'Statistics' : 's', 'Information science' : '',
              'Quantum theory' : 'k', 'Optics' : '', 'Information technology' : '',
              'Numerical analysis' : '', 'Computer engineering' : ''}
boringtopics = ['Biophysics', 'Chemistry', 'Educational technology', 'Music', 'Special education',
                'Acoustics', 'Administration', 'Aerospace engineering', 'African Americans', 'Aging',
                'American literature', 'Animal behavior', 'Archaeology', 'Arts', 'Art',
                'Biogeochemistry', 'Bioinformatics', 'Biology', 'Biomedical engineering', 'Botany',
                'British literature', 'Business', 'Caribbean literature', 'Chemical engineering',
                'Chemistry, Analytic', 'Chemistry, Inorganic', 'Chemistry, Physical and theoretical',
                'City planning', 'Civil engineering', 'Civilization, Greco-Roman', 'Classification',
                'Clinical psychology', 'Cognitive psychology', 'Counseling psychology', 'Criminology',
                'Cytology', 'Developmental biology', 'Developmental psychology', 'Diagnostic imaging',
                'Early childhood education', 'Ecology', 'Economics', 'Educational evaluation',
                'Educational leadership', 'Educational psychology', 'Finance', 'Food', 
                'Educational tests and measurements', 'Education and state', 'Education, Higher',
                'Education', 'English literature', 'Environmental engineering',
                'Environmental sciences', 'Ethics', 'Evolution (Biology)', 'Families', 
                'Management', 'Marine biology', 'Marketing', 'Mass media', 'Gender expression',
                'Gender identity', 'Genetics', 'Geochemistry', 'Geodesy', 'Geographic information systems',
                'Geography', 'Geology', 'Health services administration', 'History, Ancient', 'History',
                'Holocaust, Jewish (1939-1945)', 'Human ecology', 'Industrial engineering',
                'International relations', 'Irish literature', 'Judaism', 'Kinesiology',
                'Language and languages', 'Latin American literature', 'Library science', 'Linguistics',
                'Literature', 'Medical sciences', 'Medicine', 'Mental health', 'Metaphysics',
                'Meteorology', 'Molecular biology', 'Molecular dynamics', 'Multicultural education',
                'Multimedia systems', 'Museums', 'Neurosciences', 'Nutrition', 'Oceanography',
                'Operations research', 'Organizational behavior', 'Organizational sociology',
                'Oriental literature', 'Paleoclimatology', 'Paleoecology', 'Paleontology', 'Performing arts',
                'Philosophy', 'Physiology', 'Planning', 'Political science', 'Psychobiology', 'Psychology',
                'Public administration', 'Public health', 'Public policy', 'Radiography, Medical', 'Reading',
                'Religion', 'Research', 'Rhetoric', 'Robotics', 'School management and organization',
                'Social psychology', 'Social service', 'Sociology', 'Sports administration', 
                'Study and teaching', 'System theory', 'Textile research', 'Toxicology', 'Transportation',
                'Virology', 'Vocational education', "Women's studies", 'Biometry', 'Environmental geology',
                'Accounting', 'Communicative disorders', 'Dance', 'Fluid dynamics', 'Force and energy',
                'Geophysics', 'Humanities', 'Hydrology', 'Insurance', 'Interior decoration', 'Jurisprudence',
                'Management information systems', 'Plastics', 'Real property, Exchange of', 'Risk management',
                'Social sciences', 'Theater']

boringdeps = ['College of Music', "College of Criminology and Criminal Justice (degree granting college)",
              "College of Criminology and Criminal Justice (degree granting department)",
              "College of Social Work (degree granting department)",
              "Department of Art History (degree granting department)",
              "Department of Finance (degree granting department)",
              "Department of Urban and Regional Planning (degree granting department)",
              "Reubin O' D. Askew School of Public Administration and Policy (degree granting department)",
              "Department of Classics (degree granting department)",
              "Department of Earth, Ocean, and Atmospheric Science (degree granting department)",
              "Department of Economics (degree granting department)",
              "Department of Geography (degree granting department)",
              "Department of History (degree granting department)",
              "Department of Human Development and Family Science (degree granting department)",
              "Department of Management (degree granting department)",
              "Department of Marketing (degree granting department)",
              "Department of Mechanical Engineering (degree granting department)",
              "Department of Nutrition, Food, and Exercise Science (degree granting department)",
              "Department of Political Science (degree granting department)",
              "Department of Sport Management (degree granting department)",
              "School of Communication (degree granting department)",
              "College of Medicine (degree granting college)",
              "Department of Art Education (degree granting department)",
              "Department of Biomedical Sciences (degree granting department)",
              "Department of Civil and Environmental Engineering (degree granting department)",
              "Department of Industrial and Manufacturing Engineering (degree granting department)",
              "Department of Nutrition and Integrative Physiology (degree granting department)",
              "Program in Materials Science and Engineering (degree granting department)",
              "School of Teacher Education (degree granting department)",
              "College of Fine Arts (degree granting college)",
              "College of Social Work (degree granting college)",
              "Department of Chemical and Biomedical Engineering (degree granting department)",
              "Reubin O’ D. Askew School of Public Administration and Policy (degree granting department)",
              "College of Business (degree granting college)",
              "College of Health and Human Sciences (degree granting college)",
              "Department of Chemistry and Biochemistry (degree granting department)",
              "Department of Modern Languages and Linguistics (degree granting department)",
              "Department of Religion (degree granting department)",
              "Department of Sociology (degree granting department)",
              "College of Communication and Information (degree granting college)",
              "Department of English (degree granting department)",
              "College of Music (degree granting college)",
              "Department of Family and Child Sciences (degree granting department)",
              "Department of Biological Science (degree granting department)",
              "Department of Educational Psychology and Learning Systems (degree granting department)",
              "College of Human Sciences (degree granting college)",
              "Department of Earth, Ocean and Atmospheric Science (degree granting department)",
              "Department of Psychology (degree granting department)",
              "College of Social Sciences and Public Policy (degree granting college)",
              "Department of Educational Leadership and Policy Studies (degree granting department)",
              "College of Education (degree granting college)"]

tocurls = ['https://diginole.lib.fsu.edu/islandora/search/%2A%3A%2A?collection=fsu%3Aresearch_repository&f%5B0%5D=RELS_EXT_hasModel_uri_ms%3A%22info%3Afedora/ir%3AthesisCModel%22&f%5B1%5D=RELS_EXT_isMemberOfCollection_uri_ms%3A%22info%3Afedora/fsu%3Aetds%22&f%5B2%5D=mods_subject_topic_ms%3A%22Mathematics%22&islandora_solr_search_navigation=0&sort=fsu_dates_dt%20desc',
           'https://diginole.lib.fsu.edu/islandora/search/%2A%3A%2A?collection=fsu%3Aresearch_repository&f%5B0%5D=RELS_EXT_hasModel_uri_ms%3A%22info%3Afedora/ir%3AthesisCModel%22&f%5B1%5D=RELS_EXT_isMemberOfCollection_uri_ms%3A%22info%3Afedora/fsu%3Aetds%22&f%5B2%5D=mods_subject_topic_ms%3A%22Physics%22&islandora_solr_search_navigation=0&sort=fsu_dates_dt%20desc']

problematicurls = []#'http://purl.flvc.org/fsu/fd/2019_Spring_SALEHY_fsu_0071E_15151',
                   #'http://purl.flvc.org/fsu/fd/2019_Summer_SorribesRodriguez_fsu_0071E_15274',
                   #'http://purl.flvc.org/fsu/fd/2019_Fall_Can_fsu_0071E_15541']

tocurls = ['https://diginole.lib.fsu.edu/islandora/search?page=' + str(page) + '&type=dismax&islandora_solr_search_navigation=0&f%5B0%5D=ancestors_ms%3A%22fsu%3Aetds%22&sort=fsu_dates_dt%20desc' for page in range(pages)]




#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}


options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/chromium-browser'
options.add_argument('--headless')
driver = uc.Chrome(version_main=103, options=options)

regmaster = re.compile('master thesis')
resupervisor = re.compile('professor .*[Dd]irecting (dissertation|Dissertation|thesis|Thesis)')
redepartment = re.compile('degree granting (department|college)')
prerecs = []
recs = []
for (j, tocurl) in enumerate(tocurls):
    ejlmod3.printprogress('=', [[j+1, len(tocurls)], [tocurl], [len(prerecs)]])
    try:
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(10)
    except:
        print("retry %s in 300 seconds" % (tocurl))
        time.sleep(300)
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")

    for div in tocpage.body.find_all('div', attrs = {'class' : 'solr-field-inner'}):
        keepit = True
        rec = {'jnl' : 'BOOK', 'tc' : 'T', 'supervisor' : [], 'keyw' : [], 'note' : []}
        for div2 in div.find_all('div', attrs = {'class' : 'row'}):
            for label in div2.find_all('div', attrs = {'class' : 'solr-label'}):
                labelt = label.text.strip()
                for value in div2.find_all('div', attrs = {'class' : 'solr-value'}):
                    if labelt == 'Format:':
                        if regmaster.search(value.text):
                            keepit = False
                    elif labelt == 'URLs:':
                        rec['link'] = re.sub('.*?(http.*?), .*', r'\1', value.text)
                        rec['doi'] = '20.2000/FSU/' + re.sub('.*\/', '', rec['link'])
                        if rec['link'] in problematicurls:
                            keepit = False
        if keepit and 'doi' in rec:
            if ejlmod3.checkinterestingDOI(rec['doi']):
                prerecs.append(rec)

for (i, rec) in enumerate(prerecs):
    keepit = True
    ejlmod3.printprogress('-', [[i+1, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        driver.get(rec['link'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(7)
    except:
        print("retry %s in 300 seconds" % (rec['link']))
        time.sleep(300)
        req = urllib.request.Request(rec['link'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_publication_date', 'citation_pdf_url', 'citation_title', 'citation_author'])
    if 'autaff' in rec:
        rec['autaff'][-1].append(publisher)
    else:
        continue
    for div in artpage.body.find_all('div', attrs = {'class' : 'metadata-row'}):
        for th in div.find_all('div', attrs = {'class' : 'field-label'}):
            tht = th.text.strip()
            for td in div.find_all('div', attrs = {'class' : 'field-value'}):
                #supervisor
                if tht == 'Names':
                    for a in td.find_all('a'):
                        at = a.text
                        if resupervisor.search(at):
                            rec['supervisor'].append([re.sub(' \(.*', '', a.text.strip())])
                        elif redepartment.search(at):
                            if at in boringdeps:
                                keepit = False
                            else:
                                rec['note'].append('DEP=' + at)
                #pages
                elif tht == 'Extent':
                    if re.search('\d pages', td.text):
                        rec['pages'] = re.sub('.*?(\d+) pages.*', r'\1', td.text.strip())
                #abstract
                elif re.search('Abstract', tht, re.IGNORECASE):
                    rec['abs'] = td.text.strip()
                #keyword
                elif re.search('Keywords', tht, re.IGNORECASE):
                    rec['keyw'].append(td.text.strip())
                #topics
                elif re.search('Topics', tht, re.IGNORECASE):
                    for a in td.find_all('a'):
                        topic = a.text.strip()
                        if topic in topicsdict:
                            if topicsdict[topic]:
                                rec['fc'] = topicsdict[topic]
                        elif topic in boringtopics:
                            keepit = False
                        else:
                            rec['note'].append('TOPIC=' + topic)
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['doi'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
