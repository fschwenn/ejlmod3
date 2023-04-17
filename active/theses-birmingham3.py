# -*- coding: utf-8 -*-
#harvest theses from Birmingham U.
#FS: 2020-11-26
#FS: 2023-04-17

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

publisher = 'Birmingham U.'
jnlfilename = 'THESES-BIRMINGHAM-%s' % (ejlmod3.stampoftoday())

rpp = 20
skipalreadyharvested = True
subjects = [('QC', 'phys', ''), ('QB', 'astro', 'a'), ('QA', 'math', 'm'),
            ('Q', 'general', ''), ('QA75', 'comp', 'c'), ('QA76', 'comp', 'c')]
levels = [('d_ph', 1), ('higher', 1)]
hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alldois = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alldois = []

recs = []
for (sj, subject, fc) in subjects:
    for (level, pages) in levels:
        for page in range(pages):
            tocurl = 'https://etheses.bham.ac.uk/cgi/search/archive/advanced?screen=Search&dataset=archive&tit_abs_ft_merge=ALL&tit_abs_ft=&fulltext_merge=ALL&fulltext=&anyname_merge=ALL&anyname=&title_merge=ALL&title=&abstract_merge=ALL&abstract=&keywords_merge=ALL&keywords=&subjects=' + sj + '&subjects_merge=ANY&divisions=10col_ephy&department_merge=ALL&department=&funders_merge=ANY&projects_merge=ALL&projects=&supervisors_name_merge=ALL&supervisors_name=&thesis_type=' + level + '&date=&satisfyall=ALL&order=-date%2Fcreators_name%2Ftitle&_action_search=Search&search_offset=' + str(page*rpp)
            ejlmod3.printprogress("=", [[subject], [level], [page+1, pages], [tocurl]])
            try:
                time.sleep(3)
                req = urllib.request.Request(tocurl, headers=hdr)
                tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
            except:
                print("retry in 300 seconds")
                time.sleep(300)
                req = urllib.request.Request(tocurl, headers=hdr)
            for tr in tocpage.body.find_all('tr', attrs = {'class' : 'ep_search_result'}):
                rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'note' : [], 'autaff' : [], 'supervisor' : []}
                for a in tr.find_all('a'):
                    if a.has_attr('href') and re.search('eprint', a['href']):
                        rec['link'] = a['href']
                        rec['doi'] = '20.2000/Birmingham/' + re.sub('\D', '', a['href'])
                        if fc:
                            rec['fc'] = fc
                        if level == 'higher':
                            rec['note'].append('higher level degree')
                        if not rec['doi'] in alldois:
                            recs.append(rec)
                            alldois.append(rec['doi'])
            print('  %i recs so far' % (len(recs)))
i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']))
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.globallicensesearch(rec, artpage)
    ejlmod3.metatagcheck(rec, artpage, ['eprints.creators_name', 'eprints.creators_orcid', 'eprints.title',
                                        'eprints.date', 'eprints.keywords', 'eprints.document_url',
                                        'eprints.abstract', 'eprints.supervisors_name',
                                        'eprints.supervisors_orcid'])
    rec['autaff'][-1].append(publisher)
    ejlmod3.printrecsummary(rec)
   
ejlmod3.writenewXML(recs, publisher, jnlfilename)
