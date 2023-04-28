# -*- coding: utf-8 -*-
#harvest theses Northern Illinois U.
#FS: 2020-12-23
#FS: 2023-04-28

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json
import ssl

publisher = 'NIU, DeKalb'
jnlfilename = 'THESES-NorthernIllinois-%s' % (ejlmod3.stampoftoday())

skipalreadyharvested = True

rpp = 50
pages = 2
boring = ['M.S. (Master of Science)', 'M.S. Ed. (Master of Education)',
          'M.A. (Master of Arts)', 'Ed.D. (Doctor of Education)']
boring += ['Department of Geographic and Atmospheric Sciences',
           'Department of Kinesiology and Physical Education',
           'Department of Leadership, Educational Psychology and Foundations',
           'Department of Educational Technology, Research and Assessment',
           'Department of Art and Design', 'Department of Health and Human Sciences',
           'Counseling, Adult and Higher Education', 'Department of Art and Design',
           'Department of Biological Sciences', 'Department of Chemistry and Biochemistry',
           'Department of Curriculum and Instruction', 'Department of Economics',
           'Department of Educational Technology, Research and Assessment',
           'Department of English',  'Department of Health and Human Sciences',
           'Department of History', 'Department of Geographic and Atmospheric Sciences',
           'Department of Leadership, Educational Psychology and Foundations',           
           'Department of Geology and Environmental Geosciences',
           'Department of Political Science', 'Department of Psychology',
           'Department of Geography']

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

tocurl = 'https://huskiecommons.lib.niu.edu/allgraduate-thesesdissertations/'
for page in range(pages):
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    for p in tocpage.body.find_all('p', attrs = {'class' : 'article-listing'}):
        for a in p.find_all('a'):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : [], 'supervisor' : []}
            rec['link'] = a['href']
            rec['doi'] = '20.2000/NorthernIllinois/' + re.sub('\D', '', a['href'])
            if ejlmod3.checkinterestingDOI(rec['link']):
                if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                    prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(10)
    tocurl = 'https://huskiecommons.lib.niu.edu/allgraduate-thesesdissertations/index.%i.html' % (page+2)

i = 0
recs = []
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        req = urllib.request.Request(rec['link'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(3)
    except:
        try:
            print("   retry %s in 15 seconds" % (rec['link']))
            time.sleep(15)
            req = urllib.request.Request(rec['link'], headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        except:
            print("   no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['bepress_citation_author', 'description',
                                        'bepress_citation_date', 'bepress_citation_title',
                                        'bepress_citation_pdf_url'])
    rec['autaff'][-1].append(publisher)
    #type
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'bepress_citation_dissertation_name'}):
        if meta['content'] in boring:
            keepit = False
        else:
            rec['note'].append('TYP:::' + meta['content'])
    #pages
    for div in artpage.body.find_all('div', attrs = {'id' : 'extent'}):
        for p in div.find_all('p'):
            if re.search('\d\d', p.text):
                rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', p.text.strip())
    #advisor
    for div in artpage.body.find_all('div', attrs = {'id' : ['advisor1', 'advisor2']}):
        rec['supervisor'].append([p.text.strip()])
    #department
    for div in artpage.body.find_all('div', attrs = {'id' : 'department'}):
        for p in div.find_all('p'):
            dep = p.text.strip()
            if dep in boring:
                keepit = False
            elif dep in ['Department of Mathematical Science',
                         'Department of Mathematical Sciences']:
                rec['fc'] = 'm'
            elif dep == 'Department of Statistics':
                rec['fc'] = 's'
            elif dep != 'Department of Physics':
                rec['note'].append('DEP:::'+dep)
    #group    
    for div in artpage.body.find_all('div', attrs = {'id' : 'lcsh'}):
        for p in div.find_all('p'):
            lcsh = p.text.strip()
            if lcsh in ['Condensed matter; Physics',
                        'Nanostructures; Superconductivity',
                        'Physics; Condensed matter']:
                rec['fc'] = 'f'                
            else:
                rec['note'].append('LCSH:::'+lcsh)                
    if keepit:
        ejlmod3.globallicensesearch(rec, artpage)
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])
        


ejlmod3.writenewXML(recs, publisher, jnlfilename)
