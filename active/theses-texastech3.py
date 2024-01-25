# -*- coding: utf-8 -*-
#harvest theses from Texas Tech.
#FS: 2021-04-14
#FS: 2023-02-24

import sys
import os
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Texas Tech.'
jnlfilename = 'THESES-TexasTech-%s' % (ejlmod3.stampoftoday())
rpp = 60
pages = 20
skipalreadyharvested = True
years = 2

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

boring = ['One Health', 'pesticides', 'teacher education', 'African American',
          'breathability', 'Chlorella sorokiniana', 'Climate Change',
          'Community College', 'cotton', 'Family and Consumer Sciences',
          'health', 'Law', 'lipids', 'liver abscess', 'mental health',
          'Mexican American', 'nutrition', 'Obesity', 'poetry',
          'Retirement Planning', 'Rural', 'Salmonella', 'SARS-CoV-2',
          'social media', 'sonochemistry', 'Sorghum', 'toxicology', 'Wolbachia',
          'writing studies', 'Cotton', 'gender', 'Prymnesium parvum',
          'Zebrafish', 'Air Quality', 'beef quality', 'Children',
          'community college', 'Disability Studies', 'fifth-grade',
          'financial literacy', 'Gender', 'Latent Class Analysis', 'Middle East',
          'middle school', 'narrative inquiry', 'online learning', 'Pedagogy',
          'Queer', 'Religion', 'Rural Education', 'STEM Education',
          'United States', 'beef', 'China', 'Drought', 'higher education',
          'Photosynthesis', 'Additive Manufacturing', 'Attitudes', 'Authenticity',
          'autism', 'Autism', 'autoethnography', 'Biometric Authentication (BA)',
          'Biophilia', 'Burnout', 'Cancer', 'Cannabis', 'eating disorders',
          'Education', 'Emotions', 'English Learners', 'Existentialism',
          'Explosive detection', 'Explosive odor profile', 'Fiction',
          'Financial Knowledge', 'Financial Satisfaction', 'Fiscal Policy',
          'Food Security', 'Gender Studies', 'Geopolitical Risk', 'Glycomics',
          'Glycoproteomics', 'Health', 'Higher Education', 'Homemade Explosive',
          'identity', 'Latin America', 'Letters', 'Literacy', 'Loneliness',
          'Mental Health', 'Mental Illness', 'Mexican Literature', 'Mixed Logit',
          'mobility', 'Mobility', 'Music', 'Narrative Inquiry',
          'Natural Disasters', 'New Mexico', 'Nostalgia', 'Odor delivery',
          'Older Adults', 'pedagogical content knowledge',
          'Photoplethysmography (PPG)', 'Policy', 'Pseudomonas aeruginosa',
          'resilience', 'rhetoric', 'Rhetoric', 'Risk', 'School Psychologist',
          'Secondary Traumatic Stress', 'Short Stories', 'Smokeless powder',
          'Social Work', 'Staphylococcus aureus', 'Stigma', 'storytelling',
          'Sub-Saharan Africa', 'Sucrose', 'Suicide', 'Teachers',
          'Tornadogenesis', 'Unobserved heterogeneity',
          'User Authentication (UA)', 'User Experience', 'Video Games',
          'Vietnam War', 'vigilance', 'Volatile Organic Compound (VOC)',
          'Wellbeing', 'women', 'Autoethnography', 'Consumer Behavior',
          'leadership', 'Military', 'monetary policy', 'Saudi Arabia',
          'special education', 'Special Education', 'Technical Communication',
          'Borderlands', 'COVID-19', 'Aggression Towards Teachers',
          'Breast Cancer', 'depression', 'Diabetes', 'Invasive Species',
          'language', 'muscle activation', 'Pharmaceuticals', 'Poetry',
          'Psychological Distress']
boring += ['Agricultural Communications and Education', 'Agricultural Education and Communications',
           'Agricultural Education', 'Agricultural Leadership, Education, and Communications',
           'Agricultural Sciences &a; Natural Resources', 'Analytical Chemistry',
           'Animal and Food Sciences', 'Animal and Food Science', 'Animal Science', 'Architecture',
           'Atmospheric Sciences', 'Biochemistry', 'Biological Sciences', 'Biology',
           'Business Administration', 'Chemical Engineering', 'Chemistry &a; Biochemistry',
           'Chemistry and Biochemistry', 'Chemistry', 'Classical Modern Languages and Literature',
           'Clinical Psychology', 'Cognition and Cognitive Neuroscience', 'Communication Studies',
           'Community, Family, and Addiction Sciences', 'Counseling Psychology',
           'Counselor Education and Supervision', 'Counselor Education',
           'Couple, Marriage, and Family Therapy', 'Creative Writing', 'Curriculum &a; Instruction',
           'Curriculum and Instruction', 'Economics', 'Educational Leadership',
           'Educational Psychology and Leadership', 'Educational Psychology', 'English', 
           'Educational Psychology, Leadership and Counseling', 'Educational Psychology Leadership', 
           'English with concentration in linguistic', 'Environmental Geosciences',
           'Environmental Toxicology', 'Experimental Psychology', 'Family and Consumer Sciences Education',
           'Fine Arts: Critical Studies and Artistic Practices',
           'Fine Arts - Music', 'Geology and Geophysics', 'Geology', 'Geosciences',
           'Industrial and Systems Engineering Management', 'Industrial Engineering',
           'Industrial, Manufacturing, and Systems Engineering',
           'Land-Use Planning, Management, and Design', 'Land-Use Planning, Management. And Design',
           'Literature', 'Management Information Systems', 'Marketing', 'Mechanical Engineering',
           'Media and Communication', 'Natural Resources Management', 'Nutritional Sciences',
           'Political Science', 'Psychologial Sciences', 'Psychological Sciences', 'Psychology',
           'Rehabilitation Science', 'School of Music', 'School Psychology',
           'Technical Communication &a; Rhetoric', 'Technical Communication and Rhetoric',
           'Visual and Performing Arts', 'Wildlife, Aquatic and Wildlife Science and Management',
           'Accounting', 'Addictive Disorders and Recovery Studies',
           'Agricultural and Applied Economics', 'Agricultural Applied Economics', 'Art',
           'Civil and Environmental Engineering', 'Civil Engineering',
           'Civil, Environmental, &a; Construction Engineering',
           'Community, Family, and Addiction Services', 'Crop Science', 'Design',
           'Educational Psychology, Leadership, &a; Counseling',
           'Education Psychology &a; Leadership: Higher Education Research',
           'Environmental Engineering', 'Exercise Physiology', 'Financial Planning',
           'Fine Arts', 'History', 'Horticulture', 'Hospitality Administration',
           'Hospitality and Retail Management', 'Hospitality, Tourism and Retail Management',
           'Human Development and Family Studies', 'Industrial and Systems Engineering',
           'Interior and Environmental Design', 'Kinesiology &a; Sports Management',
           'Kinesiology and Sport Management', 'Marriage and Family Therapy',
           'Mass Communications', 'National Wind Institute', 'Nutrition, Hospitality and Retailing',
           'Personal Financial Planning', 'Petroleum Engineering', 'Plant and Soil Science',
           'Systems and Engineering Management', 'Wind Science and Engineering']

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

baseurl = 'https://ttu-ir.tdl.org'

recs = []
for page in range(pages):
    tocurl = baseurl + '/collections/b1585d49-384a-4757-b89c-0f13aa770030?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        time.sleep(5)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")

    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.creator',
                                               'dc.date.issued', 'dc.subject',
                                               'dc.description.faculty',
                                               'dc.rights', 'dc.language.iso',
                                               'dc.description.abstract', 'dc.identifier.uri',
                                               'dc.title', 'thesis.degree.department'],
                            boring=boring, alreadyharvested=alreadyharvested):
        if 'autaff' in rec and rec['autaff']:
            rec['autaff'][-1].append(publisher)
        else:
            rec['autaff'] = [['Doe, John', 'Unlisted']]
        #print(rec['thesis.metadata.keys'])
        if 'date' in rec and re.search('[12]\d\d\d', rec['date']) and int(re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])) <= ejlmod3.year(backwards=years):
            print('    too old:', rec['date'])
        else:
            keepit = True
            if 'keyw' in rec:
                for keyw in rec['keyw']:
                    if keyw in boring:
                        keepit = False
                        print('    skip "%s"' % (keyw))
                        break
            if keepit:
                ejlmod3.printrecsummary(rec)
                recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
