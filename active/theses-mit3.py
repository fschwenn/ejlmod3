# -*- coding: utf-8 -*-
#harvest theses from MIT
#FS: 2019-09-13
#FS: 2022-12-20

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'MIT'

jnlfilename = 'THESES-MIT-%s' % (ejlmod3.stampoftoday())

rpp = 100
pages = 8+17
skipalreadyharvested = True
bunchsize = 10
#these keywords are in fact the departments/institute/PhD prorgams
boringkeywords = ['Joint Program in Biological Oceanography.',
                  'Joint Program in Marine Geology and Geophysics.',
                  'Joint Program in Physical Oceanography.',
                  "Woods Hole Oceanographic Institution",
                  "Massachusetts Institute of Technology. Department of Earth, Atmospheric, and Planetary Sciences",
                  'Sloan School of Management. Master of Finance Program.',
                  'Civil and Environmental Engineering.', 'Economics.',
                  'Harvard--MIT Program in Health Sciences and Technology.',
                  'Operations Research Center.', 'Biological Engineering.',
                  'Joint Program in Oceanography/Applied Ocean Science and Engineering.',
                  'Sloan School of Management.', 'Chemical Engineering.',
                  'Institute for Data, Systems, and Society.',
                  'Materials Science and Engineering.', 'Technology and Policy Program.',
                  'Center for Real Estate. Program in Real Estate Development.',
                  'Chemistry.', 'Program in Media Arts and Sciences',
                  'Aeronautics and Astronautics.', 'Biology.', 'Mechanical Engineering.',
                  'Earth, Atmospheric, and Planetary Sciences.',
                  'Woods Hole Oceanographic Institution.',
                  'Joint Program in Applied Ocean Science and Engineering',
                  'Joint Program in Oceanography/Applied Ocean Science and Engineering',
                  'Massachusetts Institute of Technology. Computational and Systems Biology Program',
                  'Massachusetts Institute of Technology. Department of Economics',
                  'Massachusetts Institute of Technology. Department of Political Science',
                  'Massachusetts Institute of Technology. Microbiology Graduate Program',
                  'Massachusetts Institute of Technology. Operations Research Center',
                  'Massachusetts Institute of Technology. Program in Science, Technology and Society',
                  'Massachusetts Institute of Technology. Department of Brain and Cognitive Sciences',
                  'Massachusetts Institute of Technology. Department of Linguistics and Philosophy',
                  'Massachusetts Institute of Technology. Department of Civil and Environmental Engineering',
                  'Massachusetts Institute of Technology. Graduate Program in Science Writing',
                  'Massachusetts Institute of Technology. Department of Biological Engineering',
                  'Massachusetts Institute of Technology. Department of Architecture',
                  'Massachusetts Institute of Technology. Department of Chemical Engineering',
                  'Massachusetts Institute of Technology. Department of Urban Studies and Planning',
                  'Massachusetts Institute of Technology. Department of Aeronautics and Astronautics',
                  'System Design and Management Program.', 'Sloan School of Management',
                  'Massachusetts Institute of Technology. Department of Materials Science and Engineering',
                  'Massachusetts Institute of Technology. Department of Biology',
                  'Massachusetts Institute of Technology. Department of Chemistry',
                  'Massachusetts Institute of Technology. Program in Comparative Media Studies/Writing',
                  'Program in Media Arts and Sciences (Massachusetts Institute of Technology)',
                  'Harvard-MIT Program in Health Sciences and Technology',
                  'Massachusetts Institute of Technology. Supply Chain Management Program',
                  'Massachusetts Institute of Technology. Center for Real Estate. Program in Real Estate Development.']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for page in range(pages):
    tocurl = 'https://dspace.mit.edu/handle/1721.1/7582/discover?sort_by=dc.date.issued_dt&order=desc&rpp=' + str(rpp) + '&page=' + str(page+1)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(5)
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://dspace.mit.edu'):
        if not rec['hdl'] in alreadyharvested:
            keepit = True
            if 'degrees' in rec:
                for deg in rec['degrees']:
                    if deg[:10] == 'Master+of+':
                        keepit = False
            if keepit:
                prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))

recs = []
i = 0
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+ '?show=full'), features="lxml")
        time.sleep(10)
    except:
        try:
            print("retry %s in 300 seconds" % (rec['link']))
            time.sleep(300)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']+ '?show=full'), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue      
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'DC.language', 'DCTERMS.extent',
                                        'citation_pdf_url', 'DCTERMS.abstract', 'DC.rights'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'DC.creator':
                author = re.sub(' *\[.*', '', meta['content'])
                rec['autaff'] = [[ author ]]
                rec['autaff'][-1].append('MIT')
            #keywords
            elif meta['name'] == 'DC.subject':
                for keyw in re.split(' *; *', meta['content']):
                    rec['keyw'].append(keyw)
                    if keyw in boringkeywords:
                        keepit = False
            #department
            elif meta['name'] == 'DC.contributor':
                dep = meta['content']
                if dep in boringkeywords:
                    keepit = False
                elif dep in ['Massachusetts Institute of Technology. Department of Mathematics']:
                    rec['fc'] = 'm'
                else:
                    rec['note'].append(dep)
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'ds-table-row'}):
        (label, word) = ('', '')
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            label = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'word-break'}):
            word = td.text.strip()
        #supervisor
        if re.search('dc.contributor.advisor', label):
            rec['supervisor'].append([ word ])
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
        ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize))#, retfilename='retfiles_special')
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])



#ejlmod3.writenewXML(recs, publisher, jnlfilename)

