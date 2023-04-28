# -*- coding: utf-8 -*-
#harvest theses from Boston U.
#FS: 2021-04-23
#FS: 2023-04-28

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

jnlfilename = 'THESES-BOSTON-%s' % (ejlmod3.stampoftoday())
publisher = 'Boston U.'

hdr = {'User-Agent' : 'Magic Browser'}

rpp = 50
pages = 15
skipalreadyharvested = True
years = 3
boringdisciplines = ['Mechanical+Engineering', 'Biomedical+Engineering', 'Education',
                     'Systems+Engineering', 'Sargent+College+of+Health+and+Rehabilitation+Sciences',
                     'Microbiology', 'Molecular+and+Translational+Medicine', 'Neuroscience', 'Pharmacology',
                     'Social+Work', 'Anatomy+%26+Neurobiology', 'Chemistry',
                     #'Computer+Science',
                     'Electrical+%26+Computer+Engineering', 'Emerging+Media+Studies', 'Environmental+Health',
                     'Epidemiology', 'Genetics+%26+Genomics', 'Health+Services+Research', 'Management',
                     'Materials+Science+%26+Engineering', 'Pathology', 'Public+Health', 'Social+Work',
                     'American+%26+New+England+Studies', 'Biochemistry', 'Bioinformatics+GRS', 'Biology',
                     'Earth+%26+Environment', 'English', 'French+Language+%26+Literatures', 'Global+Health',
                     'Mass+Communication', 'Orthodontics+and+Dentofacial+Orthopedics', 'Philosophy',
                     'Religious+Studies', 'Theology', 'Emerging+Media+Studies', 'Periodontology', 'Astronomy',
                     'Biostatistics', 'Economics', 'Editorial+Studies', 'Hispanic+Language+%26+Literatures',
                     'History+of+Art+%26+Architecture', 'History', 'Mathematical+Finance', 'Political+Science',
                     'Prosthodontics', 'Sociology+%26+Social+Work', 'Sociology', 'Archaeology',
                     'Molecular+%26+Cell+Biology', 'Molecular+Biology%2C+Cell+Biology+%26+Biochemistry',
                     'Anthropology', 'Behavioral+Neurosciences', 'Physiology', 'Psychological+%26+Brain+Sciences',
                     'Endodontics', 'Nutrition+and+Metabolism', 'Oral+Biology', 'Biophysics',
                     'Medical+Sciences', 'Music+Education', 'Cognitive+%26+Neural+Systems',
                     'Dental+Public+Health', 'Dermatology', 'Molecular+Medicine',
                     'Accounting', 'Art+%26+Architecture%2C+History+of', 'Behavioral+Neuroscience',
                     'Bioinformatics', 'Biomedical+Engineering+and+Pharmacology+and+Experimental+Therapeutics',
                     'Business+Administration', 'Clinical+Psychology',
                     'Electrical+and+Computer+Engineering', 'Electrical+Engineering',
                     'Health+Policy+%26+Management', 'Health+Sciences', 'Materials+Science+and+Engineering',
                     'Medical+Nutritional+Sciences', 'Occupational+Therapy+Doctorate', 'Occupational+Therapy',
                     'Operations+and+Technology+Management', 'Pathology+%26+Laboratory+Medicine',
                     'Pharmacology+%26+Experimental+Therapeutics', 'Physiology+%26+Biophysics', 'Psychology',
                     'Rehabilitation+Sciences', 'Restorative+Sciences+%26+Biomaterials', 'Romance+Studies',
                     'Speech%2C+Language+%26+Hearing+Sciences', 'Speech+Language+and+Hearing+Sciences',
                     'Strategy+and+Innovation','American+and+New+England+Studies', 'American+Studies',
                     'Anatomy+and+Neurobiology', 'Anatomy', 'Applied+Anatomy+and+Physiology', 'Archeology',
                     'Art+History', 'Bimolecular+Pharmacology', 'Biochemistry+and+Cell+and+Molecular+Biology',
                     'Biomedical+engineering', 'Biomolecular+Pharmacology', 'Biophysical+Chemistry',
                     'Brain%2C+Behavior%2C+and+Cognition', 'Cell+%26+Molecular+Biology',
                     'Cell+and+Molecular+Biology', 'Cell+Biology%2C+Molecular+Biology%2C+and+Biochemistry',
                     'Classical+Studies', 'Coastal+Geomorphology', 'Cognitive+and+Neural+Systems',
                     'Comparative+Literature+and+Religious+Studies', 'Counseling+Psychology+and+Religion',
                     'Counseling+Psychology+and+Sports+Psychology', 'Cultural+Anthropology',
                     'Curriculum+and+Teaching', 'Developmental+Studies', 'Earth+Sciences', 'Earth+Science',
                     'Ecology%2C+Evolution%2C+and+Behavior', 'Educational+Policy', 'Engineering',
                     'Engingeering', 'English+Literature', 'Environmental+Studies', 'Experimental+Physics',
                     'Genetics+and+Genomics', 'Geography+and+Environment', 'Geography',
                     'Health+Policy+and+Management+Research', 'Health+Policy+and+Management',
                     'Hispanic+Language+and+Literature', 'Hispanic+Literature', 'Hispanic+Studies',
                     'History+of+Art+and+Architecture', 'Inorganic+Chemistry', 'International+Relations',
                     'Linguistics', 'Literature', 'Marketing', 'Material+Science+and+Engineering',
                     'Medical+Nutrition+Sciences', 'Medicine', 'Microbiology+and+Cell+and+Molecular+Biology',
                     'Molecular%2C+Cell+Biology+%26+Biochemistry', 'Neurology', 'Organic+Chemistry',
                     'Molecular+and+Cellular+Biology+--+Biochemistry', 'Pathology+and+Immunology',
                     'Molecular+Biology%2C+Biochemistry%2C+and+Cell+Biology', 'Philosophy+and+Greek',
                     'Molecular+Biology%2C+Cell+Biology%2C+and+Biochemistry', 'Physiology+and+Biophysics',
                     'Molecular+Biology%2C+Cell+Biology%2C+Biochemistry', 'Rehabilitation+Science',
                     'Pharmacology+and+Experimental+Therapeutics+and+Biomedical+Neuroscience',
                     'Pharmacology+and+Experimental+Therapeutics', 'Pharmacology+and+Neuroscience',
                     'Molecular+Biology%2C+Cell+Biology+and+Biochemistry', 'Religion',
                     'Religious+and+Theological+Studies', 'Spanish', 'Statistical+Mathematics',
                     'Molecular+Medicine%2C+Cell+and+Molecular+Biology', 'Pathology+and+Laboratory+Medicine',
                     'Movement+Rehabilitation+and+Health+Sciences', 'Music', 'Synthetic+Organic+Chemistry',
                     'Near+Eastern+Archaeology+and+Paleoethnobotany', 'Neurobiology', 'Neurolinguistics',
                     'Musicology', 'Computational+Neuroscience', 'Applied+Linguistics', 'Biophysic']
boringdegrees = ['Master+of+Science', 'masters', 'Doctor+of+Education', 'Doctor+of+Musical+Arts',
                 'Master+of+Music', 'Doctor+of+Business+Administration', 'Doctor+of+Occupational+Therapy',
                 'Doctor+of+Ministry', 'Doctor+of+Public+Health', 'Doctor+of+Science+in+Dentistry',
                 'Doctorate+of+Musical+Arts+in+Vocal+Performance']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = alreadyharvested

recs = []
for page in range(pages):
    tocurl = 'https://open.bu.edu/handle/2144/8520/discover?rpp='+str(rpp)+'&etal=0&group_by=none&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://open.bu.edu', alreadyharvested=alreadyharvested, boringdegrees=boringdegrees+boringdisciplines):
        if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
            print('  skip',  rec['year'])
        else:
            recs.append(rec)
    print('  %4i records so far' % (len(recs)))
    time.sleep(2)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        req = urllib.request.Request(rec['link']+ '?show=full', headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            req = urllib.request.Request(rec['link']+ '?show=full', headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_date', 'DCTERMS.abstract',
                                        'citation_pdf_url',  'citation_keywords'])
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.creator'}):
        author = re.sub(' *\[.*', '', meta['content'])
        rec['autaff'] = [[ author ]]
    for tr in artpage.body.find_all('tr'):
        tdt = ''
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            tdt = td.text.strip()
            td.decompose()
        for td in tr.find_all('td'):
            if td.text.strip() == 'en_US':
                continue
            #supervisor
            if tdt in ['dc.contributor.supervisor', 'dc.contributor.advisor']:
                if td.text.strip():
                    rec['supervisor'].append([ re.sub(' \(.*', '', td.text.strip()) ])
            #ORCID
            elif tdt == 'dc.identifier.orcid':
                if re.search('\d\d\d\d\-\d\d\d\d', td.text):
                    rec['autaff'][-1].append('ORCID:' + re.sub('.*orcid.org\/+', '', td.text.strip()))
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    rec['autaff'][-1].append(publisher)

    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
