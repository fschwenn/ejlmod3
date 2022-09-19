# -*- coding: utf-8 -*-
#harvest theses from Minnesota U.
#FS: 2020-05-05
#FS: 2022-09-10

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

publisher = 'Minnesota U.'

rpp = 100
pages = 2

hdr = {'User-Agent' : 'Magic Browser'}
jnlfilename = 'THESES-MINNESOTA-%s' % (ejlmod3.stampoftoday())

boringmajors = ["Aerospace Engineering and Mechanics", "Animal Sciences", "Anthropology", 
                "Applied Economics", "Applied Plant Sciences", "Biochemistry, Molecular Bio, and Biophysics", 
                "Biological Science", "Biology", "Biomedical Engineering", "Business Administration", 
                "Biomedical Informatics and Computational Biology", "Chemical Engineering", "Chemistry",
                "Bioproducts/Biosystems Science Engineering and Management", "Biostatistics",
                 "Civil Engineering", "Comparative and Molecular Biosciences", "Comparative Literature",
                "Comparative Studies in Discourse and Society", "Conservation Biology",
                "Design, Housing and Apparel", "Earth Sciences", "Ecology, Evolution and Behavior",
                "Economics", "Educational Policy and Administration", "Educational Psychology",
                "Education, Curriculum and Instruction", "English", "Entomology", "Environmental Health",
                "Epidemiology", "Experimental & Clinical Pharmacology", "Family Social Science", "Geography",
                "Germanic Studies", "Health Services Research, Policy and Administration",
                "History of Science, Technology, and Medicine", "Industrial and Systems Engineering",
                "Industrial Engineering", "Integrative Biology and Physiology", "Kinesiology",
                "Land and Atmospheric Science", "Mass Communication", "Mechanical Engineering",
                "Medicinal Chemistry", "Microbiology, Immunology and Cancer Biology",
                "Molecular, Cellular, Developmental Biology and Genetics", "Music Education", "Music",
                "Natural Resources Science and Management", "Neuroscience", "Nutrition",
                "Organizational Leadership, Policy, and Development", "Pharmacology", "Political Science",
                "Psychology", "Rehabilitation Science", "Rhetoric and Scientific and Technical Communication",
                "Scientific Computation", "Social and Administrative Pharmacy", "Sociology",
                "Speech-Language-Hearing Sciences", "Theatre Arts", "Veterinary Medicine", "American Studies",
                "Biophysical Sciences and Medical Physics", "Biosystems and Agricultural Engineering",
                "Chemical Physics", "Child Psychology", "Communication Studies", "Dentistry", "Design",
                "Education, Work/Community/Family Educ", "Food Science", "French",
                "Hispanic and Luso Literatures, Cultures & Linguistics", "History of Science and Technology",
                "History", "Linguistics", "Material Science and Engineering", "Nursing", "Pharmaceutics",
                "Philosophy", "Plant and Microbial Biology", "Plant Biological Sciences", "Plant Pathology",
                "Public Affairs", "Soil Science", "Water Resources Science", "Work and Human Resource Education"]

prerecs = []
for page in range(pages):
    tocurl = 'https://conservancy.umn.edu/handle/11299/45273/discover?sort_by=dc.date.issued_dt&order=desc&rpp=' + str(rpp) + '&page=' + str(page+1)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    prerecs += ejlmod3.getdspacerecs(tocpage, 'https://conservancy.umn.edu')

recs = []
i = 0
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'DC.subject', 'citation_pdf_url', 'DCTERMS.abstract'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'DC.creator':
                author = re.sub(' *\[.*', '', meta['content'])
                rec['autaff'] = [[ author ]]
                rec['autaff'][-1].append(publisher)
    for div in artpage.body.find_all('div', attrs = {'class' : 'simple-item-view-field'}):
        for h5 in div.find_all('h5'):
            if re.search('Description', h5.text):
                h5.decompose()
                divt = re.sub('[\n\t\r]', '', div.text.strip())
                if re.search('\d\d pages', divt):
                    rec['pages'] = re.sub('.*?(\d\d+) pages.*', r'\1', divt)
                if re.search('Advisors:', divt):
                    for sv in re.split(', ', re.sub('.*Advisors: *(.*?)\..*', r'\1', divt)):
                        rec['supervisor'].append([sv])
                if re.search('Major:', divt):
                    major =  re.sub('.*Major: *(.*?)\..*', r'\1', divt)
                    if major == 'Astrophysics':
                        rec['fc'] = 'a'
                    elif major == 'Computer Science':
                        rec['fc'] = 'c'
                    elif major == 'Mathematics':
                        rec['fc'] = 'm'
                    elif major == 'Statistics':
                        rec['fc'] = 's'
                    elif major in boringmajors:
                        keepit = False
                    else:
                        rec['note'].append(major)


    if keepit:            
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])
ejlmod3.writenewXML(recs, publisher, jnlfilename)
