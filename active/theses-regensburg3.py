# -*- coding: utf-8 -*-
#harvest theses from Regensburg U.
#FS: 2019-10-25
#FS: 2023-03-24

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

pagestocheck = 2
skipalreadyharvested = True

publisher = 'Regensburg U.'
jnlfilename = 'THESES-REGENSBURG-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

tocurltrunc = 'https://epub.uni-regensburg.de/cgi/search/archive/advanced?screen=Search&dataset=archive&documents_merge=ALL&documents=&title_merge=ALL&title=&creators_name_merge=ALL&creators_name=&creators_id_merge=ALL&creators_id=&creators_orcid=&editors_name_merge=ALL&editors_name=&editors_id_merge=ALL&editors_id=&editors_orcid=&date=&id_number_name_merge=ALL&id_number_name=&abstract_merge=ALL&abstract=&keywords_merge=ALL&keywords=&publication_merge=ALL&publication=&publisher_merge=ALL&publisher=&book_title_merge=ALL&book_title=&series_rgbg_merge=ALL&series_rgbg=&series_merge=ALL&series=&teaching_series_merge=ALL&teaching_series=&subjects_merge=ANY&institutions=fak09&institutions=fak10_01&institutions=fak10_02&institutions=fak10&institutions=zen02&institutions=fak13_02&institutions=fak13_03&institutions=fak13_04&institutions_merge=ANY&projects_merge=ALL&projects=&network_merge=ANY&research_group_merge=ANY&type=thesis_rgbg&type=thesis&department_merge=ALL&department=&referee_merge=ALL&referee=&isbn_merge=ALL&isbn=&classification_name_merge=ALL&classification_name=&own_doi_merge=ALL&own_doi=&ranking_merge=ANY&own_properties_merge=ALL&own_properties=&satisfyall=ALL&order=-date%2Fcreators_name%2Ftitle&_action_search=Search'
hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
#check content pages
for i in range(pagestocheck):
    tocurl = '%s&search_offset=%i' % (tocurltrunc, 20*i)
    ejlmod3.printprogress("-", [[i+1, pagestocheck], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
    time.sleep(2)
    for tr in tocpage.body.find_all('tr', attrs = {'class' : 'ep_search_result'}):
        for a in tr.find_all('a'):
            if re.search('epub.uni-regensburg.de\/\d\d', a['href']):
                rec = {'tc' : 'T', 'jnl' : 'BOOK'}
                rec['link'] = a['href']
                prerecs.append(rec)

#check individual thesis pages
i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
        except:
            print("no access to %s" % (rec['link']))
            continue
    #first get author
    ejlmod3.metatagcheck(rec, artpage, ['eprints.creators_name'])
    #get abstract or translated abstract
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'eprints.abstract_lang'}):
        #abstract is English
        if meta['content'] == 'eng':
            for meta2 in artpage.head.find_all('meta', attrs = {'name' : 'eprints.abstract'}):
                rec['abs'] = meta2['content']
        #abstract is not English
        else:
            #look for translated abstract
            for meta2 in artpage.head.find_all('meta', attrs = {'name' : 'eprints.abstract_translated'}):
                rec['abs'] = meta2['content']
            #fall back to non-English abstract
            if not 'abs' in list(rec.keys()):
                for meta2 in artpage.head.find_all('meta', attrs = {'name' : 'eprints.abstract'}):
                    rec['abs'] = meta2['content']
    #other metadata
    ejlmod3.metatagcheck(rec, artpage, ['eprints.contact_email', 'eprints.creators_orcid',
                                        'eprints.title',  'eprints.datestamp', 'eprints.keywords',
                                        'eprints.abstract', 'eprints.referee_one_name',
                                        'eprints.own_urn', 'eprints.referee', 'eprints.document_url',
                                        'eprints.own_doi'])
    #language
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'eprints.title_lang'}):
        if meta['content'] == 'ger':
            rec['language'] = 'german'
            for meta2 in artpage.head.find_all('meta', attrs = {'name' : 'eprints.title_translated'}):
                rec['transtit'] = meta2['content']
    rec['autaff'][-1].append('Regensburg U.')
    #license
    if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        print('   already in backup')
    elif skipalreadyharvested and 'urn' in rec and rec['urn'] in alreadyharvested:
        print('   already in backup')
    else:
        ejlmod3.globallicensesearch(rec, artpage)
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
