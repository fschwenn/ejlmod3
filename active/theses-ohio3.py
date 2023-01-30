# -*- coding: UTF-8 -*-
# Program to harvest Ohio Department of Higher Education
# JH 2023-01-01

from requests import Session
from time import sleep
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import ejlmod3
import re
import os

recs: list = []

publisher = 'OhioLink'
jnlfilename = 'THESES-OHIO-%s' % (ejlmod3.stampoftoday())
rpp = 100
skipalreadyharvested = True
boring = ['Education', 'Educational Leadership', 'Higher Education', 'Fine Arts',
          'Biology', 'Biomedical Engineering', 'Biomedical Research',
          'Chemical Engineering', 'Chemistry', 'Clinical Psychology',
          'Educational Psychology', 'Engineering', 'Geology', 'Molecular Biology',
          'Nursing', 'Paleontology', 'Social Psychology', 'Adult Education',
          'Behavioral Psychology', 'Behavioral Sciences', 'Biology',
          'Biomedical Engineering', 'Biomedical Research', 'Chemical Engineering',
          'Chemistry', 'Clinical Psychology', 'Cognitive Psychology',
          'Counseling Education', 'Counseling Psychology', 'Developmental Psychology',
          'Educational Psychology', 'Education History', 'Education Policy',
          'Education', 'Engineering', 'Gender Studies', 'Gender', 'Geology',
          'Higher Education', 'Kinesiology', 'Molecular Biology', 'Nursing',
          'Paleontology', 'Psychological Tests', 'Psychology', 'Psychotherapy',
          'Public Policy', 'Social Psychology', 'Sports Medicine',
          'Aerospace Materials', 'African Americans', 'African American Studies',
          'African Studies', 'Analytical Chemistry', 'Black History',
          'Environmental Engineering', 'Environmental Health', 'Environmental Justice',
          'Environmental Science', 'Environmental Studies', 'Health Care',
          'Immunology', 'Law', 'Materials Science', 'Mechanical Engineering',
          'Medicine', 'Neurosciences', 'Occupational Health', 'Occupational Safety',
          'Political Science', 'Public Health Education', 'Public Health',
          'Biochemistry', 'Biomechanics', 'Civil Engineering',
          'Community College Education', 'Community Colleges', 'Curricula',
          'Curriculum Development', 'Elementary Education',
          'English As A Second Language', 'Environmental Education',
          'Literature', 'Medical Imaging', 'Special Education', 'Theology',
          'Academic Guidance Counseling', 'Accounting', 'Aerospace Engineering',
          'Aesthetics', 'Agricultural Economics', 'Agriculture', 'Anatomy and Physiology',
          'Animal Sciences', 'Archaeology', 'Architectural', 'Art History',
          'Bilingual Education', 'Biostatistics', 'Business Administration',
          'Cellular Biology', 'Classical Studies', 'Climate Change', 'Communication',
          'Conservation', 'Criminology', 'Cultural Anthropology', 'Design',
          'Developmental Biology', 'Ecology', 'Educational Evaluation',
          'Educational Software', 'Educational Technology', 'Entomology',
          'Environmental Economics', 'Environmental Management', 'Epidemiology',
          'European History', 'Families and Family Life', 'Finance', 'Food Science',
          'Freshwater Ecology', 'Genetics', 'Health Education', 'Health Sciences',
          'High Temperature Physics', 'History', 'Holocaust Studies', 'Horticulture',
          'Industrial Engineering', 'Information Systems', 'Instructional Design',
          'Language', 'Latin American Literature', 'Linguistics', 'Management',
          'Marketing', 'Mass Media', 'Mental Health', 'Microbiology',
          'Multimedia Communications', 'Music', 'Neurology', 'Nutrition', 'Oncology',
          'Organic Chemistry', 'Organizational Behavior', 'Pharmaceuticals',
          'Pharmacology', 'Pharmacy Sciences', 'Philosophy', 'Physiological Psychology',
          'Physiology', 'Plant Biology', 'Plant Pathology', 'Plant Sciences',
          'Polymers', 'Rhetoric', 'Science Education', 'Social Work', 'Sociology',
          'Speech Therapy', 'Sports Management', 'Sustainability', 'Teaching',
          'Therapy', 'Transportation Planning', 'Urban Planning', 'Veterinary Services',
          'Virology', 'Welfare', 'Wildlife Conservation', 'Zoology', 'Acoustics',
          'Aging', 'Agricultural Education', 'Agricultural Engineering',
          'American History', 'American Literature', 'American Studies', 'Animals',
          'Art Education', 'Audiology', 'Bioinformatics', 'Biophysics',
          'Business Costs', 'Cartography', 'Clergy', 'Composition', 'Dentistry',
          'Early Childhood Education', 'Earth', 'East European Studies', 'Economics',
          'Educational Sociology', 'Educational Theory', 'Education Philosophy',
          'Entrepreneurship', 'European Studies', 'Experimental Psychology',
          'Film Studies', 'Folklore', 'Foreign Language', 'Geochemistry',
          'Geographic Information Science', 'Geography', 'Germanic Literature',
          'Gerontology', 'Health Care Management', 'Higher Education Administration',
          'Hydrology', 'Individual and Family Studies', 'International Relations',
          'Language Arts', 'Latin American Studies', 'Literacy', 'Mathematics Education',
          'Meteorology', 'Minority and Ethnic Groups', 'Molecular Chemistry',
          'Molecular Physics', 'Multicultural Education', 'Multilingual Education',
          'Music Education', 'Operations Research', 'Ophthalmology', 'Organismal Biology',
          'Organization Theory', 'Paleoecology', 'Pastoral Counseling', 'Pedagogy',
          'Physical Anthropology', 'Physical Chemistry', 'Physical Geography',
          'Preschool Education', 'Psychobiology', 'Public Administration',
          'Reading Instruction', 'Rehabilitation', 'Religion', 'Robotics',
          'Science History', 'Spirituality', 'Surgery', 'Systems Design',
          'Teacher Education', 'Theater', 'British and Irish Literature', 'Health',
          'Pathology', 'Polymer Chemistry', 'Alternative Medicine', 'Ancient History',
          'Atmospheric Sciences', 'Cognitive Therapy', 'Dance',
          'Educational Tests and Measurements', 'Education Finance', 'English literature',
          'Evolution and Development', 'Fluid Dynamics', 'Geological', 'Geophysics',
          'Land Use Planning', 'Library Science', 'Low Temperature Physics', 'Mechanics',
          'Medieval History', 'Medieval Literature', 'Middle School Education',
          'Native Americans', 'Neurobiology', 'Occupational Psychology', 'Oceanography',
          'Performing Arts', 'Physical Education', 'School Administration',
          'Social Research', 'Social Studies Education', 'Theater Studies',
          'Womens Studies', 'African Literature', 'Animal Diseases', 'Aquaculture',
          'Asian Literature', 'Automotive Materials', 'Botany', 'Business Education',
          'Condensation', 'Continuing Education', 'German literature', 'Judaic Studies',
          'Labor Economics', 'Military History', 'Mineralogy', 'Motion Pictures',
          'Personality', 'Religious Education', 'Robots', 'Romance Literature',
          'Sanitation', 'School Counseling', 'Secondary Education', 'Slavic Literature',
          'Soil Sciences', 'Textile Research', 'Transportation', 'Alternative Energy',
          'Area Planning and Development', 'Automotive Engineering', 'Biogeochemistry',
          'Endocrinology', 'Geomorphology', 'Inorganic Chemistry', 'Mass Communications',
          'Occupational Therapy', 'Quantitative Psychology', 'Regional Studies',
          'Russian History', 'Slavic Studies', 'Sociolinguistics', 'Toxicology',
          'African History', 'Architecture', 'Arts Management', 'Banking',
          'Biological Oceanography', 'Caribbean Literature', 'Comparative Literature',
          'Economic Theory', 'Fish Production', 'Geotechnology', 'Home Economics',
          'Journalism', 'Metallurgy', 'Morphology', 'Packaging', 'Petroleum Engineering',
          'Petroleum Production', 'Radiology', 'Religious History', 'Aquatic Sciences',
          'Biology, Zoology', 'Canadian Studies', 'Information Technology',
          'Native Studies', 'Natural Resource Management', 'Philosophy of Science',
          'Plastics', 'Theater History', 'Ancient Civilizations', 'Biblical Studies',
          'Comparative', 'Cultural Resources Management', 'Gifted Education',
          'Middle Eastern History', 'Modern Language', 'Near Eastern Studies',
          'Personal Relationships', 'Recreation', 'Social Structure',
          'Water Resource Management', 'Art Criticism', 'Behaviorial Sciences',
          'Glbt Studies', 'Military Studies', 'Modern Literature', 'Middle Ages',
          'Physical Therapy', 'Systems Science', "Women's Studies",
          'Paleoclimate Science', 'Agronomy', 'Medical Ethics', 'Peace Studies'
          'Atmosphere', 'Business Community', 'Geobiology', 'Legal Studies',
          'Middle Eastern Studies', 'Modern History', 'Scientific Imaging',
          'Atmospheric Chemistry', 'Environmental Geology']
reboring = re.compile('(Master of|Bachelor of|MS|BS|MA|BA|Psy\. D\.)', re.MULTILINE)

dokidir = '/afs/desy.de/user/l/library/dok/ejl/backup'
alreadyharvested = []
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    filenametrunc = re.sub('\d.*', '*doki', jnlfilename)
    alreadyharvested = list(map(tfstrip, os.popen("cat %s/*%s %s/%i/*%s | grep URLDOC | sed 's/.*=//' | sed 's/;//' " % (dokidir, filenametrunc, dokidir, ejlmod3.year(backwards=1), filenametrunc))))
    print('%i records in backup' % (len(alreadyharvested)))

def get_sub_site(url, sess):
    #print("[%s] --> Harvesting data" % url)
    pseudodoi = '20.2000/LINK/' + re.sub('\W', '', url[4:])
    if url in alreadyharvested:
        print('   already in backup')
        return
    rec: dict = {
        'tc': 'T',
        'jnl': 'BOOK',
        'note' : []
    }

    resp = sess.get(url)

    if resp.status_code != 200:
        print("[%s] --> Can't reach this site! Skipping..." % url)
        return

    soup = BeautifulSoup(resp.content.decode('utf-8'), 'lxml')
    ejlmod3.metatagcheck(rec, soup, ['citation_date', 'citation_pdf_url',
                                     'citation_author', 'citation_author_institution', 'citation_author_orcid'])
    # Get the title
    title_section = soup.find_all('h1', attrs={'class': 'red-text'})
    if len(title_section) == 1:
        rec['tit'] = title_section[0].text

    # Get the author
    #author_section = soup.find_all('span', attrs={'class': 'abstract-author'})
    #if len(author_section) == 1:
    #    rec['autaff'] = [[author_section[0].text, publisher]]

    # Get the permanent link
    link_section = soup.find_all('a', attrs={'title': 'permanent link to this ETD'})
    if len(link_section) == 1:
        rec['link'] = link_section[0].get('href')

    # Get the pdf-link
    pdf_section = soup.find_all('a', attrs={'class': 'doc-link'})
    if len(pdf_section) == 1:
        rec['hidden'] = pdf_section[0].get('href')

    # Get the abstract
    abs_section = soup.find_all('span', attrs={'id': 'P10_ABSTRACT'})
    if len(abs_section) == 1:
        rec['abs'] = abs_section[0].text

    # Get subjects
    for span in soup.find_all('span', attrs={'id': 'P10_SUBJECTS'}):
        for a in span.find_all('a'):
            subject = a.text.strip()
            if subject in ['Computer Engineering',
                           'Computer Science']:
                rec['fc'] = 'c'
            elif subject in ['Theoretical Mathematics', 'Mathematics',
                             'Applied Mathematics']:
                rec['fc'] = 'm'
            elif subject in ['Statistics']:
                rec['fc'] = 's'
            elif subject in ['Quantum Physics']:
                rec['fc'] = 'k'
            elif subject in ['Plasma Physics']:
                rec['fc'] = 'b'
            elif subject in ['Astronomy', 'Astrophysics']:
                rec['fc'] = 'a'
            elif subject in ['Solid State Physics',
                             'Condensed Matter Physics']:
                rec['fc'] = 'f'
            elif not subject in ['Physics', 'Experiments',
                                 'Remote Sensing', 'Technology',
                                 'Electrical Engineering', 'Nuclear Physics',
                                 'Nanotechnology', 'Optics',
                                 'Atoms and Subatomic Particles', 'Radiation',
                                 'Nanoscience', 'Energy', 'Logic',
                                 'Artificial Intelligence',
                                 'Theoretical Physics', 'Particle Physics',
                                 'Information Science', 'Nuclear Engineering',
                                 'Electromagnetics', 'Electromagnetism']:
                rec['note'].append('subject:::'+subject)

    # Get the supervisors
    supervisor_section = soup.find_all('span', attrs={'id': 'P10_ADVISORS'})
    if len(supervisor_section) == 1:
        rec['supervisor'] = []
        for supervisor in re.split('\)', supervisor_section[0].text):
            if re.search('Advisor', supervisor):
                sv = re.sub(' \(.*', '', supervisor)
                sv = re.sub('Dr\. ', '', sv)
                rec['supervisor'].append([sv])

    # Get the pages
    page_section = soup.find_all('span', attrs={'id': 'P10_NUM_OF_PAGES'})
    if len(page_section) == 1:
        rec['pages'] = page_section[0].text.split(' ')[0]

    # Get the keywords
    keyword_section = soup.find_all('span', attrs={'id': 'P10_KEYWORDS'})
    if len(keyword_section) == 1:
        rec['keyw'] = keyword_section[0].text.split(', ')

    # Get the orcid
    orcid_section = soup.find_all('span', attrs={'id': 'P10_AUTHOR_ORCID'})
    if len(orcid_section) == 1:
      rec['orcid'] = orcid_section[0].text

    recs.append(rec)
    ejlmod3.printrecsummary(rec)

    return

options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/chromium-browser'
chromeversion = int(re.sub('Chro.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
#chromeversion = 108
driver = uc.Chrome(version_main=chromeversion, options=options)


tocurl = 'https://etd.ohiolink.edu/apexprod/rws_olink/r/1501/search-results?token=2077610qRWPtPjxpDLkdlCyHutFjuMH&clear=1001,RP&p1001_page_rows=' + str(rpp)
#2023: tocurl = 'https://etd.ohiolink.edu/apexprod/rws_olink/r/1501/search-results?token=2233876QZsBdCpQQZnygMSuIvKaDvWd&clear=1001,RP&p1001_page_rows=' + str(rpp)

ejlmod3.printprogress('=', [[1], [tocurl]])
driver.get(tocurl)
tocpage = BeautifulSoup(driver.page_source, 'lxml')
for inp in tocpage.find_all('input', attrs = {'name' : ['P1001_TOTAL_COUNT', 'p1001_total_count']}):
    numtheses = int(inp['value'])
    pages = (numtheses-1) // rpp + 1

i = 0
with Session() as session:
    for page in range(1, pages+1):
        tocpage = BeautifulSoup(driver.page_source, 'lxml')
        for li in tocpage.find_all('li', attrs = {'class' : 't-SearchResults-item'}):
            i += 1
            keepit = True
            for span in li.find_all('span'):
                for b in span.find_all('b'):
                    if re.search('Subjects', b.text):
                        b.decompose()
                        for subject in re.split('; ', span.text.strip()):
                            #print('      ', subject)
                            if subject in boring:
                                keepit = False
                                break
            if keepit:
                for p in li.find_all('p', attrs = {'class' : 't-SearchResults-degree'}):
                    #print('         ', p.text.strip())
                    if reboring.search(p.text):
                        keepit = False
#                    else:
#                        print(p.text.strip())
            if keepit:
                for article in li.find_all('h3', attrs={'class': 't-SearchResults-title'}):
                    #print(article.text.strip())
                    article_link: str = article.find_all('a')[0].get('href')
                    ejlmod3.printprogress('-', [[i, numtheses], [article_link]])
                    get_sub_site('https://etd.ohiolink.edu%s' % article_link, session)
                    sleep(5)
            else:
                ejlmod3.printprogress('-', [[i, numtheses]])
        #ejlmod3.writenewXML(recs, publisher, jnlfilename+'TMP', retfilename='retfiles_special')
        print('  %4i records so far (checked %i of %i)' % (len(recs), rpp*page, numtheses))
        if rpp*page < numtheses:
            if (page+1) % 10  ==  1:
                print('\n --> click for Next Set\n')
                ejlmod3.printprogress('==', [[page+1, pages]])
                #driver.find_element(By.CLASS_NAME, 't-Report-paginationLink--next').click()
                driver.find_element(By.PARTIAL_LINK_TEXT, 'Next Set').click()
                #tocpage = BeautifulSoup(driver.page_source, 'lxml')
                #print(tocpage.text)
                sleep(5)
            else:
                print('\n  -> click for page %i\n' % (page+1))
                ejlmod3.printprogress('==', [[page+1, pages]])
                driver.find_element(By.LINK_TEXT, str(page + 1)).click()
                sleep(5)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
