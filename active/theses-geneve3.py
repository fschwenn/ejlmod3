# -*- coding: utf-8 -*-
#program to harvest theses from U. Geneva
# FS 2023-11-06

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time
import datetime

publisher = 'U. Geneva (main)'
jnlfilename = 'THESES-GENEVE-%s' % (ejlmod3.stampoftoday())

pages = 50
startyear = ejlmod3.year(backwards=1)
daystocheck = 300
skipalreadyharvested = True

boring = ['Section de psychologie', 'Département de langues et littératures romanes',
          'Département de langues et des littératures méditerranéennes, slaves, et orientales',
          'Département de neurosciences fondamentales', 'Institut Ethique Histoire Humanités',
          "Département d'anesthésiologie, pharmacologie, soins intensifs et urgences",
          "Département d'anthropologie et écologie", "Département d'études est-asiatiques",
          "Département d'histoire de l'art et de musicologie",
          "Département d'histoire du droit et des doctrines juridiques et politiques",
          "Département d'histoire, économie et société", "Département d'histoire générale",
          "Département de biochimie", "Département de biologie moléculaire et cellulaire",
          "Département de biologie moléculaire", "Département de chimie organique",
          "Département de chirurgie", "Département de droit civil",
          "Département de droit international public et organisation internationale",
          "Département de droit pénal", "Département de génétique et évolution",
          "Département de langue et de littérature allemandes",
          "Département de langue et de littérature françaises modernes",
          "Département de médecine génétique et développement", "Département de médecine",
          "Département de pédiatrie, gynécologie et obstétrique", "Département de philosophie",
          "Département de physiologie cellulaire et métabolisme",
          "Département de science politique et relations internationales",
          "Département des sciences de l'antiquité", "Département des sciences végétales",
          "Département F.-A. Forel des sciences de l'environnement et de l'eau",
          "Faculté d'économie et de management", "Faculté de médecine",
          "Faculté de psychologie et des sciences de l'éducation",
          "Département de biologie cellulaire", "Département de biologie structurale et bioinformatique",
          "Faculté des sciences de la société", "Geneva Finance Research Institute",
          "Institut d'études de la citoyenneté", "Institut d'histoire économique Paul Bairoch",
          "Institut de démographie et de socioéconomie", "Institut de médecine de premier recours",
          "Institut des sciences de l'environnement", "Institute of Economics and Econometrics",
          "Institute of Management", "Institut universitaire de formation des enseignants",
          "Section des sciences de l'éducation", "Section des sciences pharmaceutiques"]

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
    
records = []

cls = 999
now = datetime.datetime.now()
startdate = now + datetime.timedelta(days=-daystocheck)
stampofstartdate = '%4d-%02d-%02d' % (startdate.year, startdate.month, startdate.day)

tocurl = 'https://archive-ouverte.unige.ch/oai?verb=ListRecords&metadataPrefix=marc21&set=these-ehelvetica&from=%s&until=%s' % (stampofstartdate, ejlmod3.stampoftoday())
rpp = 1
for i in range(pages):
    if rpp*i <= cls:
        tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features='lxml')
        for record in tocpage.find_all('record'):
            records.append(record)
        ejlmod3.printprogress("=", [[i+1, pages], [tocurl], [len(records), cls]])
        cls = 0
        for rt in tocpage.find_all('resumptiontoken'):
            tocurl = 'https://archive-ouverte.unige.ch/oai?verb=ListRecords&resumptionToken=' + rt.text.strip()
            cls = int(rt['completelistsize'])
            if rpp == 1:
                rpp = int(rt['cursor'])
        time.sleep(3)

i = 0
recs = []
for record in records:
    keepit = True
    i += 1 
    ejlmod3.printprogress("-", [[i, len(records)], [len(recs)]])
    rec = {'jnl' : 'BOOK', 'tc' : 'T', 'keyw' : [], 'supervisor' : [], 'note' : []}
    isnew = False
    #DOI/URN
    for df in record.find_all('marc:datafield', attrs = {'tag' : '024'}):
        for sf in df.find_all('marc:subfield', attrs = {'code' : '2'}):
            doityp = sf.text.strip().lower()
        for sf in df.find_all('marc:subfield', attrs = {'code' : 'a'}):
            rec[doityp] = sf.text.strip()
    #title
    for df in record.find_all('marc:datafield', attrs = {'tag' : '245'}):
        for sf in df.find_all('marc:subfield', attrs = {'code' : 'a'}):
            rec['tit'] = sf.text.strip()
    #author
    for df in record.find_all('marc:datafield', attrs = {'tag' : ['100', '700']}):
        for sf in df.find_all('marc:subfield', attrs = {'code' : 'a'}):
            rec['autaff'] = [[ sf.text.strip() ]]
        for sf in df.find_all('marc:subfield', attrs = {'code' : '0'}):
            sft = sf.text.strip()
            if re.search('\(ORCID\)', sft):
                rec['autaff'][-1].append(re.sub('.*\)', 'ORCID:', sft))
        rec['autaff'][-1].append(publisher)
    #supervisor
    for df in record.find_all('marc:datafield', attrs = {'tag' : '508'}):
        for sf in df.find_all('marc:subfield', attrs = {'code' : ['e', '2']}):
            if sf.text == 'Dir.':
                for sf2 in df.find_all('marc:subfield', attrs = {'code' : 'a'}):
                    rec['supervisor'].append([ sf2.text.strip() ])
                    for sf3 in df.find_all('marc:subfield', attrs = {'code' : '0'}):
                        sft = sf3.text.strip()
                        if re.search('\(ORCID\)', sft):
                            rec['supervisor'][-1].append(re.sub('.*\)', 'ORCID:', sft))
                    rec['supervisor'][-1].append(publisher)
    #PDF
    for df2 in record.find_all('marc:datafield', attrs = {'tag' : '856'}):
        for sf2 in df2.find_all('marc:subfield', attrs = {'code' : '3'}):
            if sf2.text == 'Thesis':
                for sf3 in df2.find_all('marc:subfield', attrs = {'code' : 'u'}):
                    rec['pdf_url'] = sf3.text
    #licence and FFT
    for df in record.find_all('marc:datafield', attrs = {'tag' : '506'}):
        for sf in df.find_all('marc:subfield', attrs = {'code' : 'f'}):
            if 'pdf_url' in rec:
                if sf.text == 'Free access':
                    rec['FFT'] = rec['pdf_url']
                elif re.search('o access until [12]\d\d\d\-\d\d\-\d\d', sf.text):
                    embargo = re.sub('.*o access until ([12]\d\d\d\-\d\d\-\d\d).*', r'\1', sf.text)
                    if embargo < ejlmod3.stampoftoday():
                        print('  add FFT (%s)' % (sf.text))
                        rec['FFT'] = rec['pdf_url']
                    else:
                        print("  don't add FFT (%s)" % (sf.text))                                            
                        del rec['pdf_url']
                rec['note'].append(sf.text)    
    #title
    for df in record.find_all('marc:datafield', attrs = {'tag' : '245'}):
        for sf in df.find_all('marc:subfield', attrs = {'code' : 'a'}):
            rec['tit'] =  sf.text.strip()  
    #pages
    for df in record.find_all('marc:datafield', attrs = {'tag' : '082'}):
        for sf in df.find_all('marc:subfield', attrs = {'code' : 'a'}):
            rec['ddc'] =  sf.text.strip()
            if rec['ddc'][0] in ['1', '2', '3', '4', '6', '7', '8', '9']:
                keepit = False
                #print('  skip "%s"' % (rec['ddc']))
    #language
    for df in record.find_all('marc:datafield', attrs = {'tag' : '041'}):
        for sf in df.find_all('marc:subfield', attrs = {'code' : 'a'}):
            if not sf.text.strip() in ['eng', 'English']:
                rec['language'] = sf.text.strip()
    #date
    for df in record.find_all('marc:datafield', attrs = {'tag' : '264'}):
        for sf in df.find_all('marc:subfield', attrs = {'code' : 'c'}):
            rec['date'] = sf.text.strip()
            year = int(re.sub('.*([12]\d\d\d).*', r'\1', rec['date']))
            if year >= startyear:
                isnew = True
    #abstract
    for df in record.find_all('marc:datafield', attrs = {'tag' : '520'}):
        for sf in df.find_all('marc:subfield', attrs = {'code' : 'a'}):
            rec['abs'] = sf.text.strip()
    #keywords
    for df in record.find_all('marc:datafield', attrs = {'tag' : ['650', '653']}):
        for sf in df.find_all('marc:subfield', attrs = {'code' : 'a'}):
            rec['keyw'].append(sf.text.strip())
    #DOI fall back
    if not 'doi' in list(rec.keys()):
        for cf in record.find_all('controlfield', attrs = {'tag' : '001'}):
            recordid = cf.text.strip()
            rec['link'] = 'https://publish.etp.kit.edu/record/' + recordid
            rec['doi'] = '20.2000/Freiburg/' + recordid
    #section
    for df in record.find_all('marc:datafield', attrs = {'tag' : '928'}):
        for sf in df.find_all('marc:subfield', attrs = {'code' : 'a'}):
            section = sf.text.strip()
            if section in boring:
                keepit = False
                #print('  skip "%s"' % (section))
            elif section in ["Centre universitaire d'informatique", "Département d'informatique"]:
                rec['fc'] = 'c'
            elif section in ["Département de physique de la matière quantique"]:
                rec['fc'] = 'k'
            elif section in ["Section de mathématiques"]:
                rec['fc'] = 'm'
            elif section in ["Département d'astronomie"]:
                rec['fc'] = 'a'
            else:
                rec['note'].append('SEC:::' + section)

    if keepit:
        ejlmod3.printrecsummary(rec)
        if isnew:
            if not rec in recs:
                if skipalreadyharvested and rec['doi'] in alreadyharvested:
                    print('   %s already in backup' % (rec['doi']))
                elif skipalreadyharvested and rec['urn'] in alreadyharvested:
                    print('   %s already in backup' % (rec['urn']))
                else:
                    recs.append(rec)
            else:
                print(rec['doi'], 'already in')
        else:
            print('     old thesis (%s)' % (rec['date']))
            
ejlmod3.writenewXML(recs, publisher, jnlfilename)
