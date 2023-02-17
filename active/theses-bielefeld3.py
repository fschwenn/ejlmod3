# -*- coding: utf-8 -*-
#harvest theses from Bielefeld U.
#FS: 2019-12-05
#FS: 2023-02-17


import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

publisher = 'U. Bielefeld (main)'

jnlfilename = 'THESES-BIELEFELD-%s' % (ejlmod3.stampoftoday())

numberofrecords = 200
pages = 1+1
skipalreadyharvested = True


if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)


prerecs = {}
for k in range(pages):
    jsonurl = 'https://pub.uni-bielefeld.de/export?cql=type%3Dbi*&cql=type%3Dbi_dissertation&fmt=json&limit=' + str(numberofrecords) + '&sort=year.desc&start=%i' % (k*numberofrecords)

    ejlmod3.printprogress('=', [[k+1, pages], [jsonurl]])
    jfilename = '/tmp/%s.%i.json' % ( jnlfilename, k)
    if not os.path.isfile(jfilename):
        os.system('wget -q -O %s "%s"' % (jfilename, jsonurl))
        time.sleep(2)
    jfile = open(jfilename, mode='r')
    jtext = re.sub('[\n\r\t]', '', ''.join(jfile.readlines()))
    jfile.close()
    theses = json.loads(jtext)


    i = 0
    for thesis in theses:
        i += 1
        #print i, thesis
        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'autaff' : [], 'supervisor' : []}
        #title
        rec['tit'] = thesis['title']
        #DOI, urn
        if 'doi' in list(thesis.keys()):
            rec['doi'] = thesis['doi']
            if skipalreadyharvested and rec['doi'] in alreadyharvested:
                continue
        if 'urn' in list(thesis.keys()):
            rec['urn'] = thesis['urn']
            if skipalreadyharvested and rec['urn'] in alreadyharvested:
                continue
        elif not 'doi' in rec:
            rec['doi'] = '20.2000/bielefeld/' + thesis['_id']
        #license and fulltext
        if 'license' in list(thesis.keys()):
            rec['license'] = {'url' : thesis['license']}
            if 'file' in list(thesis.keys()):
                for datei in thesis['file']:
                    if datei['relation'] == 'main_file':
                        rec['FFT'] = 'https://pub.uni-bielefeld.de/download/%s/%s/%s' % (thesis['_id'], datei['file_id'], datei['file_name'])
        #hidden PDF
        elif 'file' in list(thesis.keys()):
            for datei in thesis['file']:
                if datei['relation'] == 'main_file':
                    rec['hidden'] = 'https://pub.uni-bielefeld.de/download/%s/%s/%s' % (thesis['_id'], datei['file_id'], datei['file_name'])
        #author
        for author in thesis['author']:
            rec['autaff'].append([author['full_name']])
            if 'orcid' in list(author.keys()):
                rec['autaff'][-1].append('ORCID:' + author['orcid'])
            rec['autaff'][-1].append(publisher)
        #supervisor
        if 'supervisor' in list(thesis.keys()):
            for supervisor in thesis['supervisor']:
                rec['supervisor'].append([supervisor['full_name']])
                if 'orcid' in list(supervisor.keys()):
                    rec['supervisor'][-1].append('ORCID:' + supervisor['orcid'])
        #date
        if 'defense_date' in list(thesis.keys()):
            rec['date'] = thesis['defense_date']
        rec['year'] = thesis['year']
        #language
        if thesis['language'][0]['iso'] == 'ger':
            rec['language'] = 'german'
        #DDC
        if 'ddc' in list(thesis.keys()):
            rec['note'] =  [ thesis['ddc'][0] ]
            if thesis['ddc'][0][:2] in ['50', '51', '52', '53']:          
                ejlmod3.printprogress("-", [[k+1, pages], [i, numberofrecords], [', '.join(list(rec.keys()))]])
                prerecs[thesis['_id']] = rec

recs = []
i = 0
for tid in list(prerecs.keys()):
    i += 1
    articlelink = 'https://pub.uni-bielefeld.de/record/' + tid
    ejlmod3.printprogress("--", [[i, len(list(prerecs.keys()))], [articlelink]])
    artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(articlelink), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['DC.description'])
    recs.append(prerecs[tid])
    time.sleep(5)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
