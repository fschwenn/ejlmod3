# -*- coding: utf-8 -*-
#harvest theses from CalTech
#FS: 2020-12-08
#FS: 2023-01-18

import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

pagestocheck = 4
skipalreadyharvested = True

publisher = 'Caltech'
jnlfilename = 'THESES-CALTECH-%s' % (ejlmod3.stampoftoday())

tocurltrunc = 'https://thesis.library.caltech.edu/cgi/search/archive/advanced?screen=Search&dataset=archive&documents_merge=ALL&documents=&title_merge=ALL&title=&creators_name_merge=ALL&creators_name=&creators_id_merge=ALL&creators_id=&creators_orcid_merge=ALL&creators_orcid=&abstract_merge=ALL&abstract=&date=&thesis_type=phd&keywords_merge=ALL&keywords=&option_major=appliedmath&option_major=appmath&option_major=appliedphys&option_major=astronomy&option_major=astrophys&option_major=compscieng&option_major=compsci&option_major=cms&option_major=math&option_major=physics&option_major=plansci&option_major=space&option_major_merge=ANY&option_minor_merge=ANY&divisions_merge=ANY&thesis_advisor_name_merge=ALL&thesis_advisor_name=&thesis_committee_name_merge=ALL&thesis_committee_name=&funders_agency_merge=ALL&funders_agency=&funders_grant_number_merge=ALL&funders_grant_number=&local_group_merge=ALL&local_group=&projects_merge=ALL&projects=&thesis_awards_merge=ALL&thesis_awards=&other_numbering_system_name_merge=ALL&other_numbering_system_name=&other_numbering_system_id_merge=ALL&other_numbering_system_id=&satisfyall=ALL&order=-date%2Fcreators_name%2Ftitle&_action_search=Search'

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
#check content pages
for i in range(pagestocheck):
    tocurl = '%s&search_offset=%i' % (tocurltrunc, 20*i)
    ejlmod3.printprogress("-", [[i+1, pagestocheck], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), 'lxml')
    time.sleep(2)
    for tr in tocpage.body.find_all('tr', attrs = {'class' : 'ep_search_result'}):
        for a in tr.find_all('a'):
            if re.search('thesis.library.caltech.edu\/\d\d', a['href']):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : []}
                rec['artlink'] = a['href']
                if not rec['artlink'] in ['https://thesis.library.caltech.edu/13784/']:
                    prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))

#check individual thesis pages
i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), 'lxml')
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), 'lxml')
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['eprints.creators_name', 'eprints.creators_orcid', 'eprints.title',
                                        'eprints.datestamp', 'eprints.keywords', 'eprints.abstract',
                                        'eprints.thesis_advisor_name', 'eprints.thesis_advisor_email',
                                        'eprints.thesis_advisor_orcid', 'eprints.doi',
                                        'eprints.document_url', 'eprints.creators_email'])
    rec['autaff'][-1].append(publisher)
    #division
    for table in artpage.find_all('table', attrs = {'class' : 'ep_block'}):
        for tr in table.find_all('tr'):
            for th in tr.find_all('th'):
                if re.search('Division:', th.text):
                    for td in tr.find_all('td'):
                        division = td.text.strip()
                        if division in ['Mathematics']:
                            rec['fc'] = 'm'
                        elif division in ['Astrophysics']:
                            rec['fc'] = 'a'
                        elif division in ['Computer Science', 'Computing and Mathematical Sciences']:
                            rec['fc'] = 'c'
                        elif not division in ['Physics, Mathematics and Astronomy']:
                            rec['note'].append(division)
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    if not rec['doi'] in alreadyharvested:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
        print(rec['note'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
