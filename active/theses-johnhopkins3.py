# -*- coding: utf-8 -*-
#harvest theses from Johns Hopkins U. (main) 
#FS: 2019-12-11
#FS: 2023-01-20

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Johns Hopkins U. (main)'
jnlfilename = 'THESES-JOHN_HOPKINS-%s' % (ejlmod3.stampoftoday())

rpp = 100
pages = 5
skipalreadyharvested = True

rftnogo = ['School+of+Medicine', 'Neuroscience', 'Biomedical+Engineering', 'Mechanical+Engineering', 'Biology',
           'Chemistry', 'Anthropology', 'Clinical+Investigation', 'Environmental+Health+%26+Engineering',
           'Materials+Science+%26+Engineering', 'Materials+Science+and+Engineering', 'Mental+Health',
           'Physiology', 'Population%2C+Family+and+Reproductive+Health', 'Pharmacology+and+Molecular+Sciences',
           'Electrical+Engineering', 'Graduate+Training+Program+in+Clinical+Investigation',
           'Molecular+Microbiology+and+Immunology', 'Sociology', 'Biochemistry', 'Civil+Engineering', 'Economics',
           'Entrepreneurial+Leadership+in+Education', 'History', 'Human+Genetics+and+Molecular+Biology', 'Nursing',
           'Public+Health+Studies', 'Biostatistics', 'Cellular+and+Molecular+Medicine', 'Environmental+Health+and+Engineering',
           'Chemical+%26+Biomolecular+Engineering', 'Chemical+and+Biomolecular+Engineering',
           'Electrical+and+Computer+Engineering', 'Biochemistry%2C+Cellular+and+Molecular+Biology',
           'Cell+Biology', 'Cellular+%26+Molecular+Medicine', 'Health+Policy+and+Management', 'Immunology',
           'Biophysics', 'Education', 'Epidemiology', 'International+Health', 'Chemistry',
           'School+of+Medicine', 'Bloomberg+School+of+Public+Health', 'English',
           'School+of+Advanced+International+Studies', 'China+Studies',
           'Comparative+Literature', 'East+Asian+Studies', 'Egyptian+Art+and+Archaeology',
           'German', 'Global+Security+Studies', 'History+of+Science+%26+Technology',
           'History+of+Science+and+Technology', 'Italian',  'Spanish', 
           'Psychological+and+Brain+Sciences', 'Psychology', 'School+of+Education',
           'Cognitive+Science', 'History+of+Art', 'Humanities', 'Near+Eastern+Studies',
           'Philosophy', 'Political+Science', 'International+Affairs',
           'German+and+Romance+Languages+and+Literatures', 'School+of+Nursing']
rftnogo += ['D.I.A.', 'Ed.D.']

dokidir = '/afs/desy.de/user/l/library/dok/ejl/backup'
alreadyharvested = []
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    filenametrunc = re.sub('\d.*', '*doki', jnlfilename)
    alreadyharvested = list(map(tfstrip, os.popen("cat %s/*%s %s/%i/*%s | grep URLDOC | sed 's/.*=//' | sed 's/;//' " % (dokidir, filenametrunc, dokidir, ejlmod3.year(backwards=1), filenametrunc))))
    print('%i records in backup' % (len(alreadyharvested)))

hdr = {'User-Agent' : 'Magic Browser'}
recs = []
for j in range(pages):
    tocurl = 'https://jscholarship.library.jhu.edu/handle/1774.2/838/browse?rpp=' + str(rpp) + '&sort_by=2&type=dateissued&offset=' + str(j*rpp) + '&etal=-1&order=DESC'
    ejlmod3.printprogress("=", [[j+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), 'lxml')
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://jscholarship.library.jhu.edu', fakehdl=True):
        keepit = True
        rec['doi'] = '20.2000/JohnHopkins/' + re.sub('.*handle\/', '', rec['link'])
        if rec['doi'] in alreadyharvested:
            #print('   %s already in backup' % (rec['doi']))
            pass
        else:
            for dg in rec['degrees']:
                if dg in rftnogo:
                    keepit = False
                    break
                elif dg in ['Applied+Mathematics+and+Statistics', 'Mathematics',
                            'Applied+Mathematics+%26+Statistics']:
                    rec['fc'] = 'm'
                elif dg in ['Astronomy']:
                    rec['fc'] = 'a'
                elif dg in ['Computer+Science']:
                    rec['fc'] = 'c'
            if keepit:
                recs.append(rec)                
    print('  %4i records so far' % (len(recs)))
    time.sleep(30)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), 'lxml')
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), 'lxml')
        except:
            print("no access to %s" % (rec['link']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'DC.subject', 'DCTERMS.abstract', 'citation_pdf_url', ])
    #author
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.creator'}):
        if re.search('\d\d\d\d\-\d\d\d\d',  meta['content']):
            rec['autaff'][-1].append('ORCID:' + meta['content'])
        else:
            author = re.sub(' *\[.*', '', meta['content'])
            rec['autaff'] = [[ author ]]
    rec['autaff'][-1].append(publisher)
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    if 'license' in rec and not 'pdf_url' in rec:
        print('   look for link to PDF in body')
        for div in artpage.find_all('div'):
            for a2 in div.find_all('a'):
                if a2.has_attr('href') and re.search('bistream.*\.pdf', a['href']):
                    divt = div.text.strip()
                    if re.search('Restricted', divt):
                        print(divt)
                    else:
                        rec['FFT'] = 'https://jscholarship.library.jhu.edu' + re.sub('\?.*', '', a['href'])
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
