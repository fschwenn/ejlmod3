# -*- coding: utf-8 -*-
#harvest theses from University of Southampton
#FS: 2019-09-26
#FS: 2023-01-16

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Southampton U.'
skipalreadyharvested = True
pages = 2
hdr = {'User-Agent' : 'Magic Browser'}
jnlfilename = 'THESES-SOUTHAMPTON-%s' % (ejlmod3.stampoftoday())
prerecs = []

baseurl = 'https://eprints.soton.ac.uk/cgi/search/archive/advanced?order=-date%2Fcontributors_name%2Ftitle&_action_search=Reorder&screen=Search&dataset=archive&exp=0%7C1%7Ccontributors_name%2F-date%2Ftitle%7Carchive%7C-%7Cdivisions%3Adivisions%3AANY%3AEQ%3A7dabceb3-00f4-4066-a715-6d2526f9a63a+a2476d18-5515-484c-b0b5-7be7b4f0cd2f+a8c9dd07-9533-48da-a2e5-0a51a7be7743+de044479-1530-4339-b27e-f79d8fe87772%7Ctype%3Atype%3AANY%3AEQ%3Athesis%7C-%7Ceprint_status%3Aeprint_status%3AANY%3AEQ%3Aarchive%7Cmetadata_visibility%3Ametadata_visibility%3AANY%3AEQ%3Ashow'

dokidir = '/afs/desy.de/user/l/library/dok/ejl/backup'
alreadyharvested = []
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    filenametrunc = re.sub('\d.*', '*doki', jnlfilename)
    alreadyharvested = list(map(tfstrip, os.popen("cat %s/*%s %s/%i/*%s  %s/%i/*%s | grep URLDOC | sed 's/.*=//' | sed 's/;//' " % (dokidir, filenametrunc, dokidir, ejlmod3.year(backwards=1), filenametrunc, dokidir, ejlmod3.year(backwards=2), filenametrunc))))
    print('%i records in backup' % (len(alreadyharvested)))

for page in range(pages):
    tocurl = baseurl + '3&search_offset=' + str(100*page)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for tr in tocpage.body.find_all('tr', attrs = {'class' : 'ep_search_result'}):
        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'autaff' : [], 'supervisor' : [],
               'note' : []}
        for a in tr.find_all('a'):
            rec['link'] = a['href']
            if ejlmod3.checkinterestingDOI(rec['link']):
                prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(5)

recs = []
i = 0
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['eprints.date', 'eprints.title', 'eprints.abstract',
                                        'eprints.document_url', 'eprints.pages',
                                        'eprints.divisions'])
    #UUID
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'eprints.pure_uuid'}):
        rec['uuid'] = meta['content']
        rec['doi'] = '20.2000/southampton/' + meta['content']
    #license
    for div in artpage.body.find_all('div', attrs = {'class' : 'uos-eprints-fileblock-line'}):
        if re.search('under [lL]icense', div.text):
            for a in div.find_all('a'):
                rec['license'] = {'url' : a['href']}
    #contributors section
    for div in artpage.body.find_all('div', attrs = {'class' : 'uos-grid'}):
        for h2 in div.find_all('h2'):
            if h2.text.strip() == 'Contributors':
                #individual contributor
                for div2 in div.find_all('div', attrs = {'class' : 'uos-eprints-dv'}):
                    for span in div2.find_all('span', attrs = {'class' : 'uos-eprints-dv-label'}):
                        ctype = span.text.strip()
                    for span in div2.find_all('span', attrs = {'class' : 'person_name'}):
                        cname = [span.text.strip()]
                    for a in div2.find_all('a'):
                        if re.search('orcid.org', a['href']):
                            cname.append(re.sub('.*orcid.org\/', 'ORCID:', a['href']))
                    cname.append(publisher)
                    if ctype == 'Author:':
                        rec['autaff'].append(cname)
                    elif ctype == 'Thesis advisor:':
                        rec['supervisor'].append(cname)
    #division
    if 'eprints.divisions' in rec:
        for divi in rec['eprints.divisions']:
            if divi in ['de044479-1530-4339-b27e-f79d8fe87772',
                        'ab7d100c-4134-4dc7-bfb9-48eeb1737ca9',
                        '40ea30ae-2b5b-4207-9819-c2a28caadad2',
                        'de044479-1530-4339-b27e-f79d8fe87772']:
                rec['fc'] = 'q'
            elif divi in ['86297b17-76e2-48d4-8996-e3ac47f689bc']:
                rec['fc'] = 'a'
            elif divi in ['f5cf03b2-425c-4643-aa23-b9f481368a67']:
                rec['fc'] = 'a'
            elif divi in ['c149d043-eda9-44dd-939f-5d50f9017fae']:
                rec['fc'] = 'i'
            elif divi in ['7c40f01e-8118-4d48-86f9-13bea77b5c28',
                          '6e316058-25f0-4820-a9cb-83aabf135a08',
                          'fdb225ca-bb83-49d6-9235-aea3dc033988',
                          '7733a6cb-b1d1-4039-8061-c53069029599',
                          '1c5e43b3-b989-41e7-bd1f-079004584d56',
                          '8f5a429e-c670-42a4-955d-9ff7bcbecf3d',
                          '37431378-f01f-4bc6-8971-933d87736a70',
                          '12b56f13-6da6-40e3-9194-51b2aec24dcb',
                          '7dabceb3-00f4-4066-a715-6d2526f9a63a']:
                rec['fc'] = 'c'
            elif divi in ['0c4d7032-e76f-4b15-ac91-258531ebdb14',
                          '7ef7dbe6-e794-49a8-b7e5-f86d66ebd02b']:
                rec['fc'] = 'k'
            elif divi in ['3cf6f76c-0f82-49d3-a152-044a2fb10737',
                          'bd4f9666-cb92-4e93-ab2f-00eeeb1903b6',
                          '0882edda-f7bd-484e-b38c-0df806093cc0',
                          'a2476d18-5515-484c-b0b5-7be7b4f0cd2f']:
                rec['fc'] = 'm'
            elif divi in ['019f89b9-a67d-4818-ae52-9bfc52e0ae25',
                          '5fcb534b-1e7f-43c3-ad8b-501fc417605b',
                          '31a036c3-4dbc-4ced-8663-d061a9c7c91e',
                          '6bcc411c-207c-4dad-8eca-9efa52377ce3',
                          '4ffdceeb-6033-42fa-b414-b95e2951c068',
                          'e18b223d-73f8-4d0b-971e-87475fc2a1e9',
                          '536be819-e4fd-423f-a0e6-f317099a000f',
                          'bb3e50e7-212e-438c-8cea-6c2f5d9b7a0b',
                          'fbc6e442-3f49-48b5-a45a-74aadb6728c7',
                          'c11dee2a-3460-429a-bb0a-3238ba2d5da3',
                          '2308ae23-c3f9-4c93-bf98-ae7e8a07a5cb',
                          'afcd0177-2845-40e1-a82f-23aa03bf8769',
                          'b2797256-bb2a-4e9d-b969-2e7dc8a1a2a4',
                          'b2627edb-8774-4c5d-b529-356f12d56c42',
                          '471d0379-d2c9-4d30-be09-a3871f1c0447',
                          '565bc538-e39b-44ab-9ad2-33a28ebd73c4']:
                keepit = False
            elif not divi in ['7dabceb3-00f4-4066-a715-6d2526f9a63a',
                              '03ec46aa-1e95-45b1-ae8b-34b17f3ac30f',                              
                              'a8c9dd07-9533-48da-a2e5-0a51a7be7743',
                              'a92d0bfc-5afa-426f-b706-1c7204edfe36',
                              'fd81a451-4ec1-4180-abc5-dbbd2428b9aa',
                              '5213723a-4221-4705-af4b-deec7da59e04',
                              '88b0fc07-89f7-4a02-ae06-332e7016be57',                              
                              'fa90bc41-bc3d-41ff-91bc-ab83dbbbbbe6',
                              '738f65c1-e655-4af6-89b2-2a65e085f398',
                              '99d7412d-2eef-458f-ae55-2d3f2cc18d6d']:
                rec['note'].append('DIV=' + divi)
    if rec['doi'] in alreadyharvested:
        print('   already in backup')
    elif keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
