# -*- coding: utf-8 -*-
#harvest theses from Cornell
#FS: 2019-12-09
#FS: 2022-11-07


import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

publisher = 'Cornell U.'
jnlfilename = 'THESES-CORNELL-%s' % (ejlmod3.stampoftoday())

rpp = 10
yearstocover = 2
pages = 30

hdr = {'User-Agent' : 'Magic Browser'}
allhdls = []
recs = []
boring = ['Biomedical+and+Biological+Sciences', 'Global+Development', 'Art',
          'Anthropology', 'Computational+Biology', 'History', 'Medicine', 'Law',
          'Linguistics', 'Mechanical+Engineering', 'Animal+Science', 'Statistics',
          'Chemistry+and+Chemical+Biology', 'Computer+Science', 'Microbiology',
          'Natural+Resources', 'Science+and+Technology+Studies', 'J.S.D.%2C+Law',
          'Ecology+and+Evolutionary+Biology', 'Food+Science+and+Technology',
          'Genetics%2C+Genomics+and+Development', 
          'Comparative+Literature', 'Geological+Sciences', 'Government', 'Biophysics',
          'Plant+Biology', 'Plant+Breeding', 'Psychology', 'Theoretical+and+Applied+Mechanics',
          'Aerospace+Engineering', 'Applied+Economics+and+Management', 'Nutrition', 
          'Biochemistry%2C+Molecular+and+Cell+Biology', 'Biomedical+Engineering',
          'Chemical+Engineering', 'Civil+and+Environmental+Engineering', 'Communication',
          'D.M.A.%2C+Music', 'Economics', 'English+Language+and+Literature',
          'Germanic+Studies', 'Hotel+Administration', 'Industrial+and+Labor+Relations',
          'Music', 'Operations+Research+and+Information+Engineering', 'Sociology',
          'Biological+and+Environmental+Engineering', 'City+and+Regional+Planning',
          'Design+and+Environmental+Analysis', 'Development+Sociology', 'Horticulture',
          'Plant+Pathology+and+Plant-Microbe+Biology', 'Policy+Analysis+and+Management', 
          'History+of+Art%2C+Archaeology%2C+and+Visual+Studies', 'Management',
          'Asian+Literature%2C+Religion+and+Culture', 'Human+Development',
          'Philosophy', 'Romance+Studies', 'Soil+and+Crop+Sciences', 'Medieval+Studies',
          'Africana+Studies', 'Architecture', 'Atmospheric+Science', 'Classics', 'Entomology',
          'Fiber+Science+and+Apparel+Design', 'Near+Eastern+Studies', 'Theatre+Arts',
          'Neurobiology+and+Behavior', 'Regional+Science', 'Systems+Engineering', 
          'Materials+Science+and+Engineering', 'Asian+Literature%2C+Religion%2C+and+Culture',
          'Comparative+Biomedical+Sciences', 'Education', 'Environmental+Toxicology',
          'Genetics%2C+Genomics+and++Development', 'Genetics+and+Development', 'Zoology',
          'History+of+Art%2C+Archaeology+and+Visual+Studies', 'Horticultural+Biology',
          'Immunology+and+Infectious+Disease', 'Molecular+and+Integrative+Physiology',
          'Operations+Research', 'Pharmacology', 'Agricultural+and+Biological+Engineering',
          'Agricultural+Economics', 'Apparel+Design', 'Behavioral+Biology', 'Biochemistry',
          'Biometry', 'Developmental+Psychology', 'East+Asian+Literature', 'Ecology',
          'Electrical+Engineering', 'Evolutionary+Biology', 'Fiber+Science', 'Genetics',
          'History+of+Architecture+and+Urban+Development', 'History+of+Art+and+Archaeology',
          'Hospitality+Management', 'Human+Behavior+and+Design', 'Musicology', 'Neurobiology',
          'Physiology', 'Plant+Pathology', 'Resource+Economics', 'Veterinary+Medicine', 
          'Human+Development+and+Family+Studies', 'Immunology', 'Molecular+and+Cell+Biology']


for page in range(pages):
    tocurl = 'https://ecommons.cornell.edu/handle/1813/47/recent-submissions?rpp=' + str(rpp) + '&offset=' + str((page)*rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://ecommons.cornell.edu'):
        keepit = True
        if 'degrees' in rec:
            for degree in rec['degrees']:
                if degree in boring:
                    #print(' skip "%s"' % (degree))
                    keepit = False
                elif degree in ['Applied+Mathematics', 'Mathematics']:
                    rec['fc'] = 'm'
                elif degree in ['Astronomy', 'Astronomy+and+Space+Sciences']:
                    rec['fc'] = 'a'
                elif not degree in ['Doctor+of+Philosophy', 'Cornell+University', 'Physics', 'Applied+Physics'] and not re.search('^Ph..D', degree):
                    rec['note'].append(degree)
            if rec['hdl'] in allhdls:
                print('skip double appearance of', rec['hdl'])
            elif keepit:
                recs.append(rec)
                allhdls.append(rec['hdl'])
    print('               %i records so far ' % (len(recs)))
    time.sleep(10)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']))
        except:
            print("no access to %s" % (rec['link']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['DC.identifier', 'DC.title', 'DCTERMS.issued',
                                        'DC.subject', 'DCTERMS.abstract', 'citation_pdf_url'])
    if not 'pdf_url' in rec:
        for div in artpage.find_all('div'):
            for a in div.find_all('a'):
                if a.has_attr('href') and re.search('bistream.*\.pdf', a['href']):
                    divt = div.text.strip()
                    if re.search('Restricted', divt):
                        print(divt)
                    else:
                        rec['pdf_url'] = 'https://ecommons.cornell.edu' + re.sub('\?.*', '', a['href'])
    ejlmod3.globallicensesearch(rec, artpage)
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'DC.creator':
                author = re.sub(' *\[.*', '', meta['content'])
                rec['autaff'] = [[ author ]]
                rec['autaff'][-1].append(publisher)
            #pages
            elif meta['name'] == 'DC.description':
                if re.search('\d\d+ pages', meta['content']):
                    rec['pages'] = re.sub('.*?(\d\d+) pages.*', r'\1', meta['content'])
    ejlmod3.printrecsummary(rec)
                                    
ejlmod3.writenewXML(recs, publisher, jnlfilename)
