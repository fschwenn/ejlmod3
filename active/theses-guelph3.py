# -*- coding: utf-8 -*-
#harvest theses from Guelph U.
#FS: 2022-04-20
#FS: 2023-03-27

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

jnlfilename = 'THESES-GUELPH-%s' % (ejlmod3.stampoftoday())
publisher = 'Guelph U.'

rpp = 50
pages = 10
skipalreadyharvested = True
years = 2
boringdisciplines = ['Mechanical+Engineering', 'Environmental+Sciences', 'Animal+and+Poultry+Science',
                     'Chemistry', 'Department+of+Animal+Biosciences', 'Department+of+Chemistry',
                     'Department+of+Economics+and+Finance', 'Department+of+Family+Relations+and+Applied+Nutrition',
                     'Department+of+Pathobiology', 'Department+of+Plant+Agriculture', 'Economics', 'Engineering',
                     'Family+Relations+and+Applied+Nutrition', 'Pathobiology', 'Plant+Agriculture', 'Public+Health',
                     'School+of+Engineering', 'Department+of+Population+Medicine', 'Bioinformatics', 'Geography', 
                     'Biomedical+Sciences', 'Clinical+Studies', 'Creative+Writing', 'Department+of+Clinical+Studies', 
                     'Criminology+and+Criminal+Justice+Policy', 'Department+of+Biomedical+Sciences', 'English',
                     'Department+of+Geography%2C+Environment+and+Geomatics', 'Department+of+History', 'History', 
                     'Department+of+Human+Health+and+Nutritional+Sciences', 'Department+of+Integrative+Biology',
                     'Department+of+Marketing+and+Consumer+Studies', 'Department+of+Molecular+and+Cellular+Biology',
                     'Department+of+Psychology', 'Department+of+Sociology+and+Anthropology', 'Doctor+of+Veterinary+Science',
                     'Human+Health+and+Nutritional+Sciences', 'Integrative+Biology', 'Landscape+Architecture', 'Management', 
                     'Latin+American+and+Caribbean+Studies', 'Literary+Studies+%2F+Theatre+Studies+in+English',
                     'Molecular+and+Cellular+Biology', 'Psychology', 'Rural+Planning+and+Development', 'Sociology',
                     'School+of+English+and+Theatre+Studies', 'School+of+Environmental+Design+and+Rural+Development',
                     'School+of+Languages+and+Literatures', 'Theatre+Studies', 'Veterinary+Science', 'Philosophy',
                     'Biophysics', 'Collaborative+International+Development+Studies', 'Department+of+Philosophy', 
                     'Department+of+Food%2C+Agricultural+and+Resource+Economics', 'Department+of+Food+Science',
                     'Department+of+Political+Science', 'Food%2C+Agriculture+and+Resource+Economics', 'Food+Science',
                     'Political+Science', 'School+of+Environmental+Sciences', 'Tourism+and+Hospitality', 'Toxicology',
                     'School+of+Hospitality%2C+Food+and+Tourism+Management', 'Applied+Statistics',
                     'Department+of+Environmental+Biology', 'Department+of+Land+Resource+Science',
                     'Environmental+Biology', 'Faculty+of+Environmental+Sciences', 'Land+Resource+Science',
                     'Population+Medicine']
boringdegrees = ['Master+of+Science', 'masters', 'Doctor+of+Education', 'Doctor+of+Musical+Arts',
                 'Master+of+Music', 'Doctor+of+Business+Administration', 'Doctor+of+Occupational+Therapy',
                 'Doctor+of+Ministry', 'Doctor+of+Public+Health', 'Doctor+of+Science+in+Dentistry',
                 'Master+of+Applied+Science', 'Master+of+Arts', 'Master+of+Fine+Arts', 'Bachelor+of+Science',
                 'Master+of+Business+Administration+%28Hospitality+and+Tourism+Management%29',
                 'Master+of+Landscape+Architecture', 'Master+of+Science+%28Planning%29']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

hdr = {'User-Agent' : 'Magic Browser'}

recs = []
redeg = re.compile('rft.degree=')
for page in range(pages):
    tocurl = 'https://atrium.lib.uoguelph.ca/xmlui/handle/10214/151/browse?order=DESC&rpp='+str(rpp)+'&sort_by=3&etal=-1&offset=' + str((page)*rpp) + '&type=dateissued'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://atrium.lib.uoguelph.ca', alreadyharvested=alreadyharvested):
        if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
            keepit = False            
            #print( '  skip',  rec['year'])
        else:
            keepit = True
            for degree in rec['degrees']:
                if degree in boringdisciplines or degree in boringdegrees:
                    keepit = False
                    #print( '  skip', degree)
        if keepit:
            recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(3)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        req = urllib.request.Request(rec['link'] + '?show=full', headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(4)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            req = urllib.request.Request(rec['link'] + '?show=full', headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'citation_title', 'citation_date',
                                        'DCTERMS.abstract', 'citation_pdf_url',
                                        'citation_keywords', 'DC.rights'])
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
    rec['autaff'][-1].append(publisher)
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
