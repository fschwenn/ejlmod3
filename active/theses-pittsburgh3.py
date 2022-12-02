# -*- coding: utf-8 -*-
#harvest Pittsburgh Theses
#FS: 2020-02-04
#FS: 2022-09-24


import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time


publisher = 'U. Pittsburgh (main)'
hdr = {'User-Agent' : 'Magic Browser'}



recs = []
jnlfilename = 'THESES-PITTSBURGH-%s' % (ejlmod3.stampoftoday())
for year in [ejlmod3.year(backwards=1), ejlmod3.year()]:
    tocurl = 'https://d-scholarship.pitt.edu/cgi/search/archive/advanced?screen=Search&dataset=archive&_action_search=Search&documents_merge=ALL&documents=&title_merge=ALL&title=&creators_name_merge=ALL&creators_name=&creators_id_merge=ALL&creators_id=&creators_orcid=&contributors_name_merge=ALL&contributors_name=&contributors_type_merge=ANY&etdcommittee_name_merge=ALL&etdcommittee_name=&corp_creators_merge=ALL&corp_creators=&abstract_merge=ALL&abstract=&date='+ str(year) + '&datestamp=&lastmod=&degree=PhD&keywords_merge=ALL&keywords=&divisions=sch_as_appliedmathematics&divisions=sch_as_appliedstatistics&divisions=sch_as_astronomy&divisions=sch_as_compsci&divisions=sch_as_math&divisions=sch_as_philosophy&divisions=sch_as_physics&divisions=sch_fas_mathematics&divisions=sch_fas_philosophy&divisions=sch_fas_physics&divisions=sch_compinfo&divisions_merge=ANY&centers_merge=ANY&event_title_merge=ALL&event_title=&department_merge=ALL&department=&editors_name_merge=ALL&editors_name=&refereed=EITHER&publication_merge=ALL&publication=&issn_merge=ALL&issn=&funders_merge=ALL&funders=&projects_merge=ALL&projects=&note_merge=ALL&note=&other_id_merge=ALL&other_id=&pmcid_merge=ALL&pmcid=&pmid_merge=ALL&pmid=&mesh_headings_merge=ALL&mesh_headings=&chemical_names_merge=ALL&chemical_names=&grants_grantid_merge=ALL&grants_grantid=&grants_agency_merge=ALL&grants_agency=&grants_country_merge=ALL&grants_country=&etdurn_merge=ALL&etdurn=&etd_approval_date=&etd_release_date=&etd_submission_date=&etd_defense_date=&etd_patent_pending=EITHER&userid=&satisfyall=ALL&order='
    yearcomplete = False
    while not yearcomplete:
        ejlmod3.printprogress('=', [[year], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        for tr in tocpage.body.find_all('tr', attrs = {'class' : 'ep_search_result'}):
            for a in tr.find_all('a'):
                if a.has_attr('href') and re.search('d.scholarship.pitt.edu\/\d', a['href']):
                    rec = {'tc' : 'T', 'jnl' : 'BOOK', 'link' : a['href'], 'year' : str(year), 'note' : []}
                    rec['tit'] = re.sub('\.$', '', a.text.strip())
                    rec['link'] = a['href']
                    rec['doi'] = '20.2000/Pittsburgh/' + re.sub('\D', '', a['href'])
                    recs.append(rec)
        for span in tocpage.body.find_all('span', attrs = {'class' : 'ep_search_control'}):
            yearcomplete = True
            for a in span.find_all('a'):
                if a.has_attr('href') and a.text.strip() == 'Next':
                    tocurl = 'https://d-scholarship.pitt.edu' + a['href']
                    yearcomplete = False
        print('   %4i records so far' % (len(recs)))
        
i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        try:
            print('retry %s in 180 seconds' % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print('no access to %s' % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['eprints.creators_name', 'eprints.creators_email',
                                        'eprints.creators_orcid', 'eprints.keywords',
                                        'eprints.abstract', 'DC.date', 'eprints.doi',
                                        'eprints.pages', 'eprints.document_url'])
    #department
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'eprints.divisions'}):
        rec['department'] = meta['content']
        rec['note'].append(rec['department'])
    rec['autaff'][-1].append(publisher)
    ejlmod3.printrecsummary(rec)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
