# -*- coding: utf-8 -*-
#harvest theses from Alberta U.
#FS: 2020-05-13
#FS: 2022-12-21

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Alberta U.'
pages = 100

boringdegrees = ['Master of Science', 'Master of Arts/Master of Library and Information Studies',
                 'Master of Arts', 'Master of Education', 'Master of Nursing', 'Master of Laws',
                 'Master of Library and Information Studies', 'Masters of Science']
boringdepartments = ['Department of Civil and Environmental Engineering',
                     'Comparative Literature', 'Neuroscience', 'Department of Anthropology',
                     'Department of Biological Sciences', 'Department of Educational Psychology',
                     'Department of East Asian Studies', 'Department of Art and Design',
                     'Department of Linguistics', 'Department of Music', 'Department of Sociology',
                     'Department of Surgery', 'Digital Humanities', 'Department of English and Film Studies',
                     'Faculty of Pharmacy and Pharmaceutical Sciences', 'Faculty of Rehabilitation Medicine',
                     'Department of Physiology', 'Department of Agricultural, Food, and Nutritional Science',
                     'Department of Biochemistry', 'Department of Cell Biology',
                     'Department of Chemical and Materials Engineering', 'Department of Chemistry',
                     'Department of Earth and Atmospheric Sciences', 'Department of Economics',
                     'Department of Educational Policy Studies', 'Department of Mechanical Engineering',
                     'Department of Electrical and Computer Engineering', 'Department of Elementary Education',
                     'Department of History and Classics', 'Department of Laboratory Medicine and Pathology',
                     'Department of Medical Microbiology and Immunology', 'Department of Medicine',
                     'Department of Modern Languages and Cultural Studies', 'Department of Pharmacology',
                     'Department of Political Science', 'Department of Psychology',
                     'Department of Public Health Sciences', 'Department of Renewable Resources',
                     'Department of Resource Economics and Environmental Sociology',
                     'Department of Secondary Education', 'Department of Secondary Education',
                     'Faculty of Business', 'Faculty of Kinesiology, Sport, and Recreation',
                     'Faculty of Nursing', 'Medical Sciences-Laboratory Medicine and Pathology',
                     'Department of Biological Sciences Department of Chemical and Materials Engineering',
                     'Department of Chemical and Materials Engineering Department of Laboratory Medicine and Pathology',
                     'Department of Oncology', 'Department of Philosophy', 'Faculty of Law',
                     'School of Public Health', 'Medical Sciences-Paediatrics',
                     'Department of Biomedical Engineering', 'Centre for Neuroscience',
                     'Department of Chemical and Materials Engineering Department of Biomedical Engineering Department of Biomedical Engineering',
                     'Department of Chemical and Materials Engineering Department of Biomedical Engineering',
                     'Department of Chemical and Materials Engineering Department of Human Ecology',
                     'Department of Earth and Atmospheric Sciences Medical Sciences-Paediatrics',
                     'Department of Educational Studies', 'Department of Human Ecology',
                     'Department of Secondary Education Faculty of Extension',
                     'Faculty of Kinesiology, Sport, Recreation', 'Religious Studies',
                     'Faculty of Physical Education and Recreation Department of Drama',
                     'Faculty of Physical Education and Recreation', 'Kinesiology, Sport and Recreation',
                     'Laboratory Medicine and Pathology', 'Medical Sciences-Dentistry',
                     'Medical Sciences-Medical Genetics', 'Physical Education and Recreation',
                     'Department of Elementary Education School of Library and Information Studies',
                     'Department of Modern Languages and Cultural Studies Department of Anthropology',
                     'Department of Psychiatry', 'Department of Sociology Department of Art and Design',
                     'Medical Sciences-Orthodontics', 'Medical Sciences-Shantou in Laboratory Medicine and Pathology',
                     'School of Library and Information Studies', 'Medical Sciences-Oral Biology',
                     'Department of Agricultural, Food, and Nutritional Science Department of Public Health Sciences',
                     'Department of History and Classics Department of Modern Languages and Cultural Studies',
                     'Medical Sciences- Laboratory Medicine and Pathology',
                     'Centre for Neuroscience Physical Education and Recreation',
                     'Faculty of Nursing Department of Public Health Sciences',
                     'School Public Health Sciences', 'Drama Department', 'Medical Sciences-Periodontology',
                     'Medical Sciences-Biomedical Engineering', 'School of Public Health Sciences',
                     'Rehabilitation Medicine', 'Medicine', 'Rural Economy', 'School of Business', 
                     'Department of Mathematical and Statistical Sciences', 'Department of Drama',
                     'Department of Agricultural, Food and Nutritional Science',
                     'Faculty of Rehabilitation Medicine Department of Communication Sciences and Disorders',
                     'Department of Agricultural, Food, and Nutritional Science Department of Biological Sciences',
                     'Department of Chemical and Materials Engineering Department of Biological Sciences',
                     'Department of Educational Policy Studies School of Library and Information Studies',
                     'Department of Physiology Medical Sciences-Obstetrics and Gynecology',
                     'Medical Science - Shantou Biomedical Engineering',
                     'Medical Sciences-Radiology and Diagnostic Imaging']

jnlfilename = 'THESES-ALBERTA-%s' % (ejlmod3.stampoftoday())
hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
recs = []
for page in range(pages):
    tocurl = 'https://era.library.ualberta.ca/search?direction=desc&facets[member_of_paths_dpsim][]=db9a4e71-f809-4385-a274-048f28eb6814%2Ff42f3da6-00c3-4581-b785-63725c33c7ce&search=&sort=sort_year&page=' + str(page+1)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for div in tocpage.body.find_all('div', attrs = {'class' : 'media-body'}):
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'note' : [], 'supervisor' : []}
        for h3 in div.find_all('h3'):
            for a in h3.find_all('a'):
                rec['artlink'] = 'https://era.library.ualberta.ca' + a['href']
                if ejlmod3.checkinterestingDOI(rec['artlink']):
                    prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(5)

i = 0
dois = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_title', 'citation_doi',
                                        'citation_publication_date', 'citation_pdf_url'])
    rec['autaff'][-1].append(publisher)
    #abstract
    for li in artpage.body.find_all('li', attrs = {'class' : 'list-unstyled'}):
        for p in li.find_all('p', attrs = {'title' : 'Description / Abstract'}):
            rec['abs'] = li.text.strip()
    for dl in artpage.body.find_all('dl'):
        for dt in dl.find_all('dt'):
            dtt = dt.text.strip()
            for dd in dl.find_all('dd'):
                #keywords
                if dtt == 'Subjects / Keywords':
                    for li in dd.find_all('li'):
                        rec['keyw'].append(li.text.strip())
                #degree
                elif dtt == 'Degree':
                    rec['degree'] = dd.text.strip()
                    rec['note'].append(dd.text.strip())
                #license
                elif dtt == 'License':
                    for a in dd.find_all('a'):
                        if re.search('creativecommons.org', a['href']):
                            rec['license'] = {'url' :  a['href']}
                #department
                elif dtt == 'Department':
                    rec['department'] = re.sub('  +', ' ', re.sub('[\n\t\r]', ' ', dd.text.strip()))
                    if rec['department'] == 'Department of Computing Science':
                        rec['fc'] = 'c'
                    else:
                        rec['note'].append(rec['department'])
                #supervisor
                elif dtt == 'Supervisor / co-supervisor and their department(s)':
                    for a in dd.find_all('a'):
                        sv = re.sub(' \(.*', '', a.text.strip())
                        if re.search(',.*,', sv):
                            sv = re.sub(' *,.*', '', sv)
                        rec['supervisor'].append([sv])
    #cherry picking
    if 'department' in list(rec.keys()) and rec['department'] in boringdepartments:
        print('  skip "%s"' % (rec['department']))
        ejlmod3.adduninterestingDOI(rec['artlink'])
    else:
        if 'degree' in list(rec.keys()) and rec['degree'] in boringdegrees:
            print('  skip "%s"' % (rec['degree']))
            ejlmod3.adduninterestingDOI(rec['artlink'])
        else:
            if not 'doi' in rec:
                rec['doi'] = '20.2000/Alberta/' + re.sub('.*items\/', '', rec['artlink'])
                rec['link'] = rec['artlink']
            if not rec['doi'] in dois:
                dois.append(rec['doi'])
                ejlmod3.printrecsummary(rec)
                recs.append(rec)
                
ejlmod3.writenewXML(recs, publisher, jnlfilename)
