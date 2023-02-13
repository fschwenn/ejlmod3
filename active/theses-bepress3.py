# -*- coding: utf-8 -*-
#harvest theses from bepress-network
#FS: 2022-11-09

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
from inspirelabslib3 import *
import urllib3

urllib3.disable_warnings()

publisher = 'bepress'
jnlfilename = 'THESES-BEPRESS-%s' % (ejlmod3.stampoftoday())
years = 2
rpp = 30
verbatim = True
skipalreadyharvested = True

deps = [('physics/elementary-particles-and-fields-and-string-theory', ''),
        ('physics/plasma-and-beam-physics', 'b'),
        ('physics/quantum-physics', 'k'),
        ('physics/nuclear', ''),
        ('physics/condensed-matter-physics', 'f'),
        ('physics/atomic-molecular-and-optical-physics', 'q'),
        ('physics/engineering-physics', 'q'),
        ('computer-sciences/numerical-analysis-and-scientific-computing', ''),
        ('computer-sciences/other-computer-sciences', 'c'),
        ('physics/other-physics', 'q'),
        ('other-physical-sciences-and-mathematics', ''),
        ('mathematics', 'm'),
        ('applied-mathematics', 'm')]

boring = ['Masters Theses', 'Undergraduate Theses', 'Undergraduate Honors Theses',
          'Student Research Submissions', 'Honors Theses and Capstones',
          'University Honors Program Senior Projects', 'Honors Theses',
          'College of Arts & Sciences Senior Honors Theses', "Senior Projects Fall 2018", "Senior Theses",
          "University Honors Theses", "MSU Graduate Theses", "Electrical Engineering Undergraduate Honors Theses",
          "Senior Projects Spring 2017", "Graduate College Dissertations and Theses", "Honors Undergraduate Theses",
          "All Graduate Plan B and other Reports", "CMC Senior Theses", "Honors College Theses", "Master's Theses",
          "Mechanical Engineering Undergraduate Honors Theses", "Senior Projects Spring 2021",
          "Williams Honors College, Honors Research Projects",
          "The University of Texas MD Anderson Cancer Center UTHealth Graduate School of Biomedical Sciences Dissertations and Theses (Open Access)",
          "All Undergraduate Projects", "Senior Projects Spring 2020", "Scripps Senior Theses",
          "Student Theses 2015-Present", "Honors Thesis", "Senior Projects Spring 2018", "Honors Projects",
          "Selected Student Publications", "Honor Scholar Theses", "HMC Senior Theses", "Senior Projects Spring 2016",
          "Graduate Masters Theses", "Senior Projects Spring 2015", "Physics and Astronomy Honors Papers",
          "Senior Honors Projects, 2010-2019", "Physics Undergraduate Honors Theses", "Undergraduate Theses and Capstone Projects",
          "Senior Honors Projects, 2020-current", "Pomona Senior Theses", "Departmental Honors Projects",
          "Forensic Science Master's Projects", "Honors Program Theses",
          "Computer Science and Computer Engineering Undergraduate Honors Theses", "Senior Projects Spring 2022",
          "Master of Science in Computer Science Theses", "Master's Projects", "Computational and Data Sciences (MS) Theses",
          "Senior Independent Study Theses", "All Master's Theses", "EWU Masters Thesis Collection",
          "Chemical Engineering Undergraduate Honors Theses", "Master's Theses (2009 -)", "Dartmouth College Undergraduate Theses",
          "Senior Projects Fall 2020", "Theses/Capstones/Creative Projects", "Social Work Doctoral Dissertations",
          "Senior Projects Fall 2019", "Senior Projects Spring 2019", "Mathematics and Computer Science Capstones",
          "English (MA) Theses", "Maritime Safety & Environment Management Dissertations (Dalian)",
          "Regis University Student Publications (comprehensive collection)", "All Graduate Projects", "Student Work",
          "Senior Theses and Projects", "Honors Capstone Projects and Theses", "Theses : Honours",
          "Graduate Theses - Physics and Optical Engineering", "Undergraduate Honors Capstone Projects",
          "Mathematical Sciences Undergraduate Honors Theses", "Undergraduate Honors Thesis Collection",
          "All NMU Master's Theses", "Selected Honors Theses", "Masters Essays", "Master of Science in Mathematics",
          "West Chester University Master’s Theses", "Senior Honors Theses and Projects", "Math Theses",
          "Honors Student Research", "St. Mary's University Honors Theses and Projects", "Pitzer Senior Theses",
          "Honors Papers", "Industrial Engineering Undergraduate Honors Theses", "Pence-Boyce STEM Student Scholarship",
          "Honors Senior Capstone Projects", "Graduate Theses and Capstone Projects (excluding DNP)",
          "(HIDDEN) Doctor of Education in Secondary Education Dissertations", "Mathematics Undergraduate Theses",
          "Mathematics Theses", "Capstone Collection", "Senior Honors Theses", "Master's Projects and Capstones",
          "All Student Theses", "All Capstone Projects", "KSU Journey Honors College Capstones and Theses", "Psychology",
          "Doctor of Education (Ed.D)", "Doctor of Education in Teacher Leadership Dissertations", "Doctor of Education (EdD)",
          "Senior Projects Fall 2016", "Mathematics Honors Papers", "Senior Honors Projects", "HIM 1990-2015",
          "Posters, Presentations, and Papers", "Honors Senior Theses/Projects", "Graduate Student Independent Studies",
          "Senior Projects Spring 2013", "WWU Graduate School Collection", "Theses Digitization Project",
          "Mathematics and Statistics Theses", "CUP Ed.D. Dissertations", "Senior Projects Fall 2017",
          "Applied Mathematics Master's Theses", "Biological and Agricultural Engineering Undergraduate Honors Theses",
          "Business and Economics Honors Papers", " Doctoral Dissertations", "Dartmouth College Ph.D Dissertations"]
boring += ['MS Physics', 'Graduate', 'MS', 'Doctor of Education (Ed.D.)', 'Doctor of Education',
           'Masters of Science (Research)', 'M. Eng.', 'M. A.', 'M. S.', 'PHD in Applied Life Sciences']
remaster = re.compile('(Master of Science|MS in |M\.S\.|M\.Sc\.|Master of |Bachelor|BA in|BS in|MA in|M\.A\.)')
redoctor = re.compile('(Doctor of Philosophy|Ph\. D\.|Ph\.D\.|PhD)')
boring += ['Business and Information Systems', 'Chemical and Biomolecular Engineering',
           'Chemistry', 'Human Centered Computing', 'Biochemistry & Molecular Biophysics', 'Biomedical Sciences',
           'Chemical and Materials Engineering', 'Education', 'Education, Teaching-Learning Processes',
           'Environmental Engineering and Earth Science', 'Industrial Engineering & Operations Research',
           'Organismic and Evolutionary Biology', 'Polymer Science and Engineering', 'Biology', 'Biostatistics',
           'Chemical and Biochemical Engineering', 'Chemical and Biomedical Engineering', 'Chemical Engineering',
           'Chemistry and Biochemistry', 'Chemistry, Physical', 'Civil and Environmental Engineering',
           'College of Forest Resources and Environmental Science', 'Geosciences', 'Geoscience', 
           'Department of Geological and Mining Engineering and Sciences','Health Physics and Diagnostic Sciences',
           'Department of Mathematical Sciences: Business Analytics', 'Economics', 'Geology and Geography',
           'Naval Architecture and Marine Engineering', 'Ocean Science and Engineering']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested('THESES')

bibclassifycommand = "/usr/bin/python /afs/desy.de/user/l/library/proc/bibclassify/bibclassify_cli.py  -k /afs/desy.de/user/l/library/akw/HEPont.rdf "
absdir = '/afs/desy.de/group/library/publisherdata/abs'
tmpdir = '/afs/desy.de/user/l/library/tmp'

prerecs = []
baseurls = {}
for i in range(len(deps)):
    for j in range(years):
        dep = deps[i][0]
        fc = deps[i][1]
        year = ejlmod3.year(backwards=j)
        tocurl = 'https://network.bepress.com/explore/physical-sciences-and-mathematics/' + dep + '/?facet=publication_type%3A%22Theses%2FDissertations%22&facet=publication_year%3A%22' + str(year) + '%22'
        ejlmod3.printprogress('=', [[i*years+j+1, len(deps)*years], [tocurl]])
        try:
            tocpages = [BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")]
            time.sleep(6)
        except:
            print("retry %s in 180 seconds" % (tocurl))
            time.sleep(180)
            tocpages = [BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml")]
        for p in tocpages[0].body.find_all('p', attrs = {'class' : 'stats'}):
            numberofrecords = int(re.sub('.* of *(\d+).*', r'\1', p.text.strip()))
            numberofpages = (numberofrecords-1) // rpp + 1
            for k in range(numberofpages-1):
                suburl = '%s&start=%i' % (tocurl, (k+1)*rpp)
                ejlmod3.printprogress('=', [[i*years+j+1, len(deps)*years], [k+2, numberofpages], [suburl]])
                try:
                    tocpages.append(BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(suburl), features="lxml"))
                    time.sleep(3)
                except:
                    print("retry %s in 60 seconds" % (tocurl))
                    time.sleep(60)
                    tocpages.append(BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(suburl), features="lxml"))
        for tocpage in tocpages:
            for div in tocpage.body.find_all('div', attrs = {'class' : 'floatbox'}):
                keepit = True
                rec = {'jnl' : 'BOOK', 'year' : str(year), 'tc' : 'T', 'note' : [dep], 'supervisor' : []}
                if fc:
                    rec['fc'] = fc
                for a in div.find_all('a', attrs = {'target' : '_blank'}):
                    if a.has_attr('href'):
                        for h5 in div.find_all('h5'):
                            disstype = h5.text.strip()
                            if disstype in boring:
                                keepit = False
                                if verbatim: print('    skip %s since %s' % (a['href'], disstype))
                            elif not disstype in ["Physics", "Publicly Accessible Penn Dissertations", "Dissertations", "Open Access Dissertations", 
                                                  "Computational and Data Sciences (PhD) Dissertations", "Mathematics", "All Dissertations",
                                                  "Mechanical Engineering", "Architectural Engineering", "Analytics and Data Science Dissertations",
                                                  "Computer Science and Software Engineering", "Dissertations (1934 -)",  "Computer Science", 
                                                  "College of Computing and Digital Media Dissertations", "Electrical Engineering", "Computer Engineering",
                                                  "World Maritime University Dissertations", "Mathematics and Statistics"]:
                                rec['note'].append(disstype)
                        rec['link'] = a['href']
                        baseurl = ejlmod3.getbaseurl(a['href'])
                        if keepit:
                            dedicated = ejlmod3.dedicatedharvesterexists(baseurl)
                            if dedicated:
                                if verbatim: print('         %s already covered by %s' % (a['href'], dedicated))
                                keepit = False                        
                            elif re.search('honors', rec['link']):
                                if verbatim: print('  honors %s' % (a['href']))
                                keepit = False                                          
                            elif ejlmod3.checkinterestingDOI(rec['link']):
                                if verbatim: print('     ->  %s (%s)' % (a['href'], baseurl))
                                rec['note'].append('BASEURL=%s' % (baseurl))
                                rec['baseurl'] = baseurl
                            else:
                                if verbatim: print('    skip %s' % (a['href']))
                                keepit = False                  
                if keepit:
                    prerecs.append(rec)
                    if baseurl in baseurls:
                        baseurls[baseurl].append(rec['link'])
                    else:
                        baseurls[baseurl] = [rec['link']]
        if verbatim: print('    %i records so far' % (len(prerecs)))

liste = [(len(baseurls[baseurl]), baseurl) for baseurl in baseurls]
liste.sort()
for n, baseurl in liste:
    if verbatim: print('%3i %s' % (n, baseurl))


i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        ejlmod3.metatagcheck(rec, artpage, ['description', 'bepress_citation_author', 'bepress_citation_pdf_url', 'bepress_citation_doi',
                                            'bepress_citation_online_date', 'bepress_citation_author_institution',
                                            'bepress_citation_title', 'keywords'])
        rec['autaff'][-1]
        time.sleep(3)
    except:        
        print("retry %s in 60 seconds" % (rec['link']))
        try:
            time.sleep(60)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
            ejlmod3.metatagcheck(rec, artpage, ['description', 'bepress_citation_author', 'bepress_citation_pdf_url', 'bepress_citation_doi',
                                                'bepress_citation_online_date', 'bepress_citation_author_institution',
                                                'bepress_citation_title', 'keywords'])
            rec['autaff'][-1]
        except:
            continue
    #already in backup?
    if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        print('   already in backup')
        continue
    elif skipalreadyharvested and 'hdl' in rec and rec['hdl'] in alreadyharvested:
        print('   already in backup')
        continue
    #supervisor
    for div in artpage.body.find_all('div', attrs = {'id' : ['advisor1', 'advisor2', 'advisor3', 'advisor4']}):
        for h4 in div.find_all('h4'):
            if re.search('visor', h4.text):
                for p in div.find_all('p'):
                    sv = re.sub('^Dr. ', '', p.text.strip())
                    if re.search(',.*,', sv):
                        rec['supervisor'].append([re.sub(',.*', '', sv)])
                    else:
                        rec['supervisor'].append([sv])
    #language
    for div in artpage.body.find_all('div', attrs = {'id' : 'language'}):
        for p in div.find_all('p'):
            rec['language'] = p.text.strip()
    #keywords
    if not 'keyw' in rec:
        for div in artpage.body.find_all('div', attrs = {'id' : 'keywords'}):
            for p in div.find_all('p'):
                rec['keyw'] = [ p.text.strip() ]
    #pages
    for div in artpage.body.find_all('div', attrs = {'id' : ['pages', 'page_count', 'format_extent']}):
        for p in div.find_all('p'):
            pages = p.text.strip()
            if re.search('\d\d', pages):
                rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', pages)
    #department
    for div in artpage.body.find_all('div', attrs = {'id' : ['department', 'department1', 'department2']}):
        for p in div.find_all('p'):
            department = p.text.strip()
            if department in boring:
                keepit = False
            elif department in ['Computer Science']:
                if not 'fc' in rec:
                    rec['fc'] = 'c'
            elif department in ['Statistics']:
                if not 'fc' in rec:
                    rec['fc'] = 's'
            elif department in ['Mathematical Sciences', 'Mathematics', 'Applied Mathematics']:
                if not 'fc' in rec:
                    rec['fc'] = 'm'
            elif not department in ['Physics and Astronomy', 'Physical Sciences', 'Physics & Astronomy'
                                    'Physics']:
                rec['note'].append('DEPARTMENT='+department)
    #degree
    for div in artpage.body.find_all('div', attrs = {'id' : ['degree_name', 'degree_level']}):
        for p in div.find_all('p'):
            degree = p.text.strip()
            if degree in boring:
                keepit = False
            elif remaster.search(degree):
                keepit = False
            elif not redoctor.search(degree):
                rec['note'].append('DEGREE=' + degree)
    #license
    for div in artpage.body.find_all('div', attrs = {'id' : ['cclicense', 'distribution_license']}):
        aa = div.find_all('a', attrs = {'rel' : 'license'})
        if not aa:
            aa = div.find_all('a')            
        for a in aa:
            if a.has_attr('href') and re.search('creativecommons.org', a['href']):
                rec['license'] = {'url' : a['href']}
            elif re.search('reative', a.text.strip()):
                rec['license'] = {'statement' : a.text.strip()}                
    #INSPIRE check
    if 'doi' in rec and get_recids('doi:%s' % (rec['doi'])):
        keepit = False
        if verbatim: print('   %s ALREADY IN INSPIRE' % (rec['doi']))
    elif get_recids('urls.value:"%s"' % (rec['link'])):
        keepit = False
        if verbatim: print('   %s ALREADY IN INSPIRE' % (rec['link']))
    if not 'doi' in rec:
        rec['doi'] = '30.3000/bepress/' + re.sub('\W', '', rec['link'])    
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)

#now check abstracts with biblassify
restart = re.compile('^Core ')
reend = re.compile('^ *$')
for rec in recs:
    doi1 = re.sub('[\(\)\/]', '_', rec['doi'])
    absfilename = os.path.join(absdir, doi1)
    bibfilename = os.path.join(tmpdir, doi1+'.hep.bib')
    if not os.path.isfile(bibfilename):
        print(' >bibclassify %s' % (doi1))
        try:
            os.system('%s %s > %s' % (bibclassifycommand, absfilename, bibfilename))
        except:
            if verbatim: print('FAILURE: %s %s > %s' % (bibclassifycommand, absfilename, bibfilename))
    kws = []
    if os.path.isfile(bibfilename):
        absbib = open(bibfilename, 'r')
        lines = absbib.readlines()
        active = False
        for line in lines:
            if active:
                if reend.search(line):
                    active = False
                elif line.strip() != '--':
                    kws.append(line.strip())
            elif restart.search(line):
                active = True
        if kws:
            rec['note'].append('KWS[%s]: %i | %s' % (rec['baseurl'], len(kws), '; '.join(kws)))
            if verbatim: print(rec['baseurl'], kws)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
