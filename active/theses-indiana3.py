# -*- coding: utf-8 -*-
#harvest theses Indiana U., Bloomington (main)
#FS: 2020-05-13
#FS: 2023-04-28

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Indiana U., Bloomington (main)'
jnlfilename = 'THESES-INDIANABLOOMINGTON-%s' % (ejlmod3.stampoftoday())

skipalreadyharvested = True
rpp = 50
pages = 2
boringdepartments = ['Anthropology/University Graduate School', 'Department of Anthropology',
                     'Department of Biology School of Informatics Computing Engineering/University Graduate School',
                     'Department of Communication Culture', 'Department of Earth Atmospheric Sciences',
                     'Department of English/University Graduate School', 'Department of Folklore Ethnomusicology',
                     'Department of History', 'Department of Linguistics',
                     'Department of Linguistics the Department of Second Language Studies',
                     'Department of Psychological Brain Sciences',
                     'Department of Psychological Brain Sciences/College of Arts Sciences',
                     'Department of Psychological Brain Sciences Program in Neuroscience',
                     'Department of Psychological Brain Sciences the Cognitive Science Program',
                     'Department of Psychological Brain Sciences the Program in Neural Science',
                     'Department of Psychological Brain Sciences the Program in Neuroscience',
                     'Department of Psychological Brain Sciences/University Graduate School',
                     'Department of Spanish Portuguese', 'Department of Speech Hearing Sciences',
                     'History Philosophy of Science Medicine/University Graduate School',
                     'Jacobs School of Music', 'Kelley School of Business',
                     'Linguistics/University Graduate School', 'Department of Biology',
                     'Media School/University Graduate School',
                     'Musicology/Jacobs School of Music', 'School of Education',
                     'School of Education/University Graduate School',
                     'School of Optometry', 'School of Public Environmental Affairs',
                     'School of Public Health', 'School of Public Health/University Graduate School',
                     'Anthropology', 'Biochemistry', 'Biochemistry Molecular Biology',
                     'Biology', 'Business', 'Cellular Integrative Physiology',
                     'Central Eurasian Studies', 'Chemistry', 'Classical Studies',
                     'Cognitive Science', 'Cognitive Science Program',
                     'Cognitive Science/Psychological Brain Sciences',
                     'Communication Culture', 'Comparative Literature', 'Criminal Justice',
                     'Department of Biochemistry Molecular Biology',
                     'Department of Biology School of Informatics Computing Engineering/University Graduate School',
                     'Department of Central Eurasian Studies', 'Department of English',
                     'Department of Folklore Ethnomusicology', 'Department of French Italian',
                     'Department of Psychological Brain Sciences',
                     'Department of Psychological Brain Sciences Program in Neuroscience',
                     'Department of Psychological Brain Sciences the Department of Biology',
                     'Department of Psychological Brain Sciences the Program in Neuroscience',
                     'Department of Sociology', 'East Asian Languages Cultures',
                     'East Asian Languages Cultures (EALC', 'Ecology Evolutionary Biology',
                     'Economics', 'Education', 'Educational Leadership',
                     'Educational Leadership Policy Studies', 'English', 'Environmental Science',
                     'Fine Arts', 'Folklore Ethnomusicology', 'French',
                     'Geography', 'Geological Sciences', 'Germanic Studies',
                     'Health Rehabilitation Sciences', 'History', 'History/American Studies',
                     'History of Art', 'History Philosophy of Science', 'Italian',
                     'Journalism', 'Linguistics', 'Linguistics Central Eurasian Studies',
                     'Linguistics/Second Language Studies', 'Mass Communications/Telecommunications',
                     'Microbiology', 'Microbiology Immunology', 'Molecular Cellular Developmental Biology',
                     'Music', 'Near Eastern Languages Cultures', 'Neuroscience',
                     'Nursing Science', 'Optometry', 'Pharmacology Toxicology',
                     'Philanthropic Studies', 'Philosophy', 'Political Science',
                     'Psychological Brain Sciences',
                     'sychological Brain Sciences/Cognitive Science',
                     'Psychological Brain Sciences/Cognitive Sciences',
                     'Psychological Brain Sciences the Cognitive Science Program',
                     'Psychology', 'Public Affairs', 'Public Health', 'Public Policy',
                     'School of Health Physical Education Recreation',
                     'Sociology', 'Spanish', 'Spanish Portuguese', 'Speech Hearing']


if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for page in range(pages):
    tocurl = 'https://scholarworks.iu.edu/dspace/handle/2022/3086/browse?rpp=' + str(rpp) + '&sort_by=2&type=dateissued&offset=' + str(page*rpp) + '&etal=-1&order=DESC'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    divs = tocpage.body.find_all('div', attrs = {'class' : 'item-metadata'})
    for div in divs:
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'note' : [], 'supervisor' : []}
        for a in div.find_all('a'):
            rec['artlink'] = 'https://scholarworks.iu.edu' + a['href'] #+ '?show=full'
            rec['hdl'] = re.sub('.*handle\/', '', a['href'])
            if not skipalreadyharvested or not rec['hdl'] in alreadyharvested:
                if ejlmod3.checkinterestingDOI(rec['hdl']):
                    prerecs.append(rec)
    time.sleep(10)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("   retry %s in 5 seconds" % (rec['artlink']))
            time.sleep(5)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("   no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.contributor', 'DC.title',
                                        'DC.subject', 'DCTERMS.abstract', 'citation_pdf_url',
                                        'DC.identifier'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #date
            if meta['name'] == 'DCTERMS.issued':
                rec['date'] = meta['content'][:10]
            #department
            elif meta['name'] == 'DC.description':
                dep = re.sub('.*Indiana University, *(.*), [12].*', r'\1', meta['content'])
                dep = re.sub('(,| and|\&) ', ' ', dep)
                rec['department'] = dep
                rec['note'].append(meta['content'])
            #thesis type
            elif meta['name'] == 'DC.type':
                if meta['content'] != 'Doctoral Dissertation':
                    rec['note'].append(meta['content'])
    rec['autaff'][-1].append(publisher)
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    if 'department' in rec and rec['department'] in boringdepartments:
        print('  skip "%s"' % (rec['department']))
        ejlmod3.adduninterestingDOI(rec['hdl'])
    else:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
