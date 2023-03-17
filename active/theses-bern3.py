# -*- coding: utf-8 -*-
#harvest theses from University of Bern
#FS: 2019-09-27
#FS: 2023-03-17

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Bern U.'
jnlfilename = 'THESES-BERN-%s' % (ejlmod3.stampoftoday())

skipalreadyharvested = True
pages = 1
rpp = 50

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}
tocurl = 'https://boris.unibe.ch/cgi/search/advanced?screen=Search&_action_search=Search&eprintid=&date=&title_merge=ALL&title=&contributors_name_merge=ALL&contributors_name=&contributors_orcid=&editors_name_merge=ALL&editors_name=&publication_merge=ALL&publication=&abbrev_publication_merge=ALL&abbrev_publication=&publisher_merge=ALL&publisher=&event_title_merge=ALL&event_title=&event_location_merge=ALL&event_location=&issn=&isbn=&book_title_merge=ALL&book_title=&abstract_merge=ALL&abstract=&keywords_merge=ALL&keywords=&note_merge=ALL&note=&divisions=DCD5A442C024E17DE0405C82790C4DE2&divisions=DCD5A442C44AE17DE0405C82790C4DE2&divisions=DCD5A442BE78E17DE0405C82790C4DE2&divisions=DCD5A442C6C6E17DE0405C82790C4DE2&divisions_merge=ANY&grad_school_merge=ANY&type=thesis&refereed=EITHER&doc_content_merge=ANY&doc_license_merge=ANY&doc_format_merge=ANY&doi_name=&id_fs=&doi=&pubmed_id=&wos_id=&satisfyall=ALL&order=-date%2Fcreators_name%2Ftitle'
tocurl = 'https://boris.unibe.ch/cgi/search/archive/advanced?screen=Search&_action_search=Search&eprintid=&date=&title_merge=ALL&title=&contributors_name_merge=ALL&contributors_name=&contributors_orcid=&contributors_type_merge=ANY&editors_name_merge=ALL&editors_name=&publication_merge=ALL&publication=&abbrev_publication_merge=ALL&abbrev_publication=&publisher_merge=ALL&publisher=&event_title_merge=ALL&event_title=&event_location_merge=ALL&event_location=&issn=&isbn=&book_title_merge=ALL&book_title=&abstract_merge=ALL&abstract=&keywords_merge=ALL&keywords=&note_merge=ALL&note=&divisions_merge=ANY&divisions=DCD5A442C024E17DE0405C82790C4DE2&divisions=DCD5A442C025E17DE0405C82790C4DE2&divisions=DCD5A442C148E17DE0405C82790C4DE2&divisions=DCD5A442BED5E17DE0405C82790C4DE2&divisions=DCD5A442BE96E17DE0405C82790C4DE2&divisions=DCD5A442C2AFE17DE0405C82790C4DE2&divisions=DCD5A442BE75E17DE0405C82790C4DE2&divisions=DCD5A442C44AE17DE0405C82790C4DE2&divisions=DCD5A442BE78E17DE0405C82790C4DE2&divisions=39347D2A205B46358F9F9AAD63FC05AC&divisions=DCD5A442C6C6E17DE0405C82790C4DE2&grad_school_merge=ANY&org_units_id_merge=ANY&org_units_id_match=IN&type=thesis&refereed=EITHER&doc_content_merge=ANY&doc_license_merge=ANY&doc_format_merge=ANY&doi_name=&id_fs=&doi=&pubmed_id=&wos_id=&satisfyall=ALL&order=-date%2Fcreators_name%2Ftitle'
prerecs = []
for page in range(pages):
    tocurl = 'https://boris.unibe.ch/cgi/search/archive/advanced?exp=0%7C1%7C-date%2Fcreators_name%2Ftitle%7Carchive%7C-%7Cdivisions%3Adivisions%3AANY%3AEQ%3ADCD5A442C024E17DE0405C82790C4DE2+DCD5A442C025E17DE0405C82790C4DE2+DCD5A442C148E17DE0405C82790C4DE2+DCD5A442BED5E17DE0405C82790C4DE2+DCD5A442BE96E17DE0405C82790C4DE2+DCD5A442C2AFE17DE0405C82790C4DE2+DCD5A442BE75E17DE0405C82790C4DE2+DCD5A442C44AE17DE0405C82790C4DE2+DCD5A442BE78E17DE0405C82790C4DE2+39347D2A205B46358F9F9AAD63FC05AC+DCD5A442C6C6E17DE0405C82790C4DE2%7Ctype%3Atype%3AANY%3AEQ%3Athesis%7C-%7Ceprint_status%3Aeprint_status%3AANY%3AEQ%3Aarchive%7Cmetadata_visibility%3Ametadata_visibility%3AANY%3AEQ%3Ashow&_action_search=1&order=-date%2Fcreators_name%2Ftitle&screen=Search&cache=5579956&search_offset=' + str(rpp*page)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
    for div in tocpage.body.find_all('div', attrs = {'class' : 'ep_search_results'}):
        for a in div.find_all('a'):
            if re.search('^http', a['href']):
                rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'fc' : '', 'note' : []}
                rec['artlink'] = a['href']
                prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))
    
recs = []
for (i, rec) in enumerate(prerecs):
    ejlmod3.printprogress("-", [[i+1, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features='lxml')
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features='lxml')
        except:
            print("no access to %s" % (rec['artlink']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.title', 'DC.date', 'eprints.doi_name',
                                        'eprints.abstract', 'eprints.pages', 'eprints.document_url',
                                        'DC.contributor', 'eprints.urn', "eprints.language"])
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.subject'}):
        ddc = meta['content']
        if ddc in ['520 Astronomy']:
            rec['fc'] += 'a'
        elif ddc in ['510 Mathematics']:
            rec['fc'] += 'm'
        elif ddc in ['000 Computer science, knowledge & systems']:
            rec['fc'] += 'c'
        elif ddc in ['580 Plants (Botany)', '660 Chemical engineering', '070 News media, journalism & publishing']:
            rec['fc'] += 'o'
        elif not ddc in ['530 Physics', '620 Engineering', '600 Technology', '500 Science']:
            rec['note'].append(ddc)
    rec['autaff'][-1].append('Bern U.')
    #license 
    for a in artpage.body.find_all('a'):
        if a.has_attr('href') and re.search('creativecommons.org', a['href']):
            atext = a.text.strip()
            if re.search('\(CC.[A-Z][A-Z]', atext):
                rec['license'] = {'statement' : re.sub('.*\((CC.*?)\).*', r'\1', atext)}
    if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        print('   already in backup')
    else:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
