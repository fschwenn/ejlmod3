# -*- coding: utf-8 -*-
#harvest theses from Sussex U.
#FS: 2020-03-23
#FS: 2022-12-21

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Sussex U.'
hdr = {'User-Agent' : 'Magic Browser'}

skipalreadyharvested = True
boring = ['Media and Film', 'Management', 'Media and Cultural Studies', 'Accounting and finance',
          'Accounting and Finance', 'American studies', 'Anthropology', 'Art History',
          'Biochemistry', 'Biology', 'Chemistry', 'Development Studies', 'Economics', 'Education',
          'Engineering', 'English', 'Genome stability', 'Geography', 'History',
          'Institute of Development Studies', 'International Development', 'International Relations',
          'Law', 'Life Sciences', 'Media and film', 'Music', 'Neuroscience', 'Philosophy',
          'Politics', 'Psychology', 'Science policy research unit', 'Social work', 'Social Work',
          'Sociology', '|SPRU - Science Policy Research Unit', 'SPRU - Science Policy Research Unit']
prerecs = []
jnlfilename = 'THESES-SUSSEX-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

for year in [ejlmod3.year(), ejlmod3.year(backwards=1)]:
#    for (fc, dep) in [('', 'd234'), ('m', 'd235')]:
#        tocurl = 'http://sro.sussex.ac.uk/view/divisions/%s/%i.html' % (dep, year)
    tocurl = 'http://sro.sussex.ac.uk/view/type/thesis/%i.html' % (year)
    print(tocurl)
    try:
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(2)
    except:
        continue
    for p in tocpage.find_all('p'):
        if re.search('PhD', p.text):
            for a in p.find_all('a'):
                if a.has_attr('href'):
                    rec = {'tc' : 'T', 'jnl' : 'BOOK', 'link' : a['href'], 'note' : []}
                    rec['tit'] = a.text.strip()
                    rec['doi'] = '20.2000/UCLodon/' + re.sub('\D', '', a['href'])
                    if ejlmod3.checkinterestingDOI(rec['doi']):
                        if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                            prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))

recs = []
i = 0
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(10)
    except:
        try:
            print('retry %s in 180 seconds' % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print('no access to %s' % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['eprints.creators_name', 'eprints.creators_orcid',
                                        'eprints.keywords', 'eprints.abstract',
                                        'eprints.date', 'eprints.doi', 'eprints.pages'])                                  
    rec['autaff'][-1].append(publisher)
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #PDF
            if meta['name'] == 'DC.identifier':
                if re.search('pdf$', meta['content']):
                    rec['hidden'] = meta['content']
            #PDF
            elif meta['name'] == 'eprints.thesis_award':
                rec['note'].append(meta['content'])
            #department
            elif meta['name'] == 'eprints.department':
                dep = meta['content']
                if dep in boring:
                    keepit = False
                elif dep == 'Astronomy':
                    rec['fc'] = 'a'
                elif dep == 'Mathematics':                    
                    rec['fc'] = 'm'
                elif dep == 'Informatics':                    
                    rec['fc'] = 'c'
                elif not dep in ['Physics']:
                    rec['note'].append('DEP=' + dep)
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['doi'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
