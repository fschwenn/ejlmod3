# -*- coding: utf-8 -*-
#harvest theses from Heidelberg
#FS: 2019-09-15
#FS: 2022-09-20

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import datetime

publisher = 'U. Heidelberg (main)'
jnlfilename = 'THESES-HEIDELBERG-%s' % (ejlmod3.stampoftoday())

boring = ['Zentrum für Biomedizin und Medizintechnik (CBTM)', 'European Molecular Biology Laboratory (EMBL)',
          "Alfred-Weber-Institut for Economics", "Anglistisches Seminar",
          "Centre for Organismal Studies Heidelberg (COS)", "Chirurgische Klinik",
          u"Chirurgische Universitätsklinik", u"Dean's Office of The Faculty of Behavioural and Cultural Studies",
          u"Dean's Office of the Faculty of Bio Sciences", u"Dekanat der Fakultät für Chemie und Geowissenschaften",
          u"Dekanat der Medizinischen Fakultät Heidelberg", u"Dekanat Medizin Mannheim",
          u"Dekanat Neuphilologische Fakultät", u"Department for Infectiology",
          u'Department „History, Philosophy, and Ethics in Medicine"',
          u"Department of Neonatology, University Medicine Mannheim",
          u"Exzellenzcluster Asia and Europe in a Global Context", u"Fakultät für Chemie und Geowissenschaften",
          u"Frauenklinik", u"German Cancer Research Center (DKFZ)",
          u"Graduiertenschulen", u"Hautklinik",
          u"Heidelberg Center for American Studies (HCA)", u"Historisches Seminar",
          u"Institute of Environmental Physics", u"Institute of Geography",
          u"Institute of Inorganic Chemistry", u"Institute of Organic Chemistry",
          u"Institute of Pharmacy and Molecular Biotechnology", u"Institute of Political Science",
          u"Institute of Psychology", u"Institut für Anästhesiologie und operative Intensivmedizin",
          u"Institut für Bildungswissenschaft", u"Institut für Computerlinguistik",
          u"Institut für Deutsch als Fremdsprachenphilologie", u"Institut für Geowissenschaften",
          u"Institut für Hygiene und Medizinische Mikrobiologie", u"Institut für Klassische Archäologie",
          u"Institut für Klinische Pharmakologie", u"Institut für Klinische Radiologie",
          u"Institut für Kunstgeschichte Ostasiens", u"Institut für Medizinische Biometrie und Informatik",
          u"Institut für Papyrologie und antike Paläographie", u"Institut für Public Health (IPH)",
          u"Institut für Sinologie", u"Institut für Sport und Sportwissenschaft",
          u"Kinderklinik", u"Klinik für Strahlentherapie und Radioonkologie",
          u"Kunsthistorisches Institut", u"Max-Planck-Institute allgemein",
          u"Medizinische Fakultät Heidelberg", u"Medizinische Fakultät Mannheim",
          u"Medizinische Klinik - Lehrstuhl für Innere Medizin III",
          u"Medizinische Klinik - Lehrstuhl für Innere Medizin II",
          u"Medizinische Klinik - Lehrstuhl für Innere Medizin I",
          u"Medizinische Universitäts-Klinik und Poliklinik",
          u"MPI for Medical Research", u"Neuphilologische Fakultät",
          u"Neurochirurgische Klinik", u"Neurologische Klinik",
          u"Neurologische Universitätsklinik", u"Orthopädische Klinik",
          u"Pathologisches Institut MA", u"Pathologisches Institut",
          u"Pharmakologisches Institut", u"Philosophische Fakultät",
          u"Philosophisches Seminar", u"Psychiatrische Universitätsklinik",
          u"Psychosomatische Universitätsklinik", u"Seminar für klassische Philologie",
          u"Seminar für Sprachen und Kulturen des Vorderen Orients", u"Service facilities",
          u"South Asia Institute (SAI)", u"The Faculty of Behavioural and Cultural Studies",
          u"The Faculty of Bio Sciences", u"The Faculty of Economics and Social Studies",
          u"Universitätskinderklinik", u"Urologische Klinik",
          u"Zentralinstitut für Seelische Gesundheit",
          u"Zentrum für Medizinische Forschung"]
now = datetime.datetime.now()
if now.month <= 8:
    years = [str(now.year - 1), str(now.year)]
else:
    years = [str(now.year)]

tocurl = 'http://archiv.ub.uni-heidelberg.de/volltextserver/view/type/doctoralThesis.html'
print(tocurl)
hdr = {'User-Agent' : 'Magic Browser'}
req = urllib.request.Request(tocurl, headers=hdr)
tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
prerecs = []
ps = tocpage.body.find_all('p')
i = 0 
for p in ps:
    i += 1
    for span in p.find_all('span', attrs = {'class' : 'person_name'}):
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'pacs' : [], 'supervisor' : [], 'note' : []}
        for a in p.find_all('a'):
            rec['artlink'] = a['href']
            rec['tit'] = a.text.strip()
            a.replace_with('')
        pt = re.sub('[\n\t\r]', ' ', p.text.strip())
        if re.search('\(\d\d\d\d\)', pt):
            rec['date'] = re.sub('.*\((\d\d\d\d)\).*', r'\1', pt)
            if rec['date'] in years:
                if ejlmod3.ckeckinterestingDOI(rec['artlink']):
                    prerecs.append(rec)

i = 0
recs = []
repacs = re.compile('(\d\d\.\d\d.\d[a-z]).*')
for rec in prerecs:
    keepit = True
    i += 1
    time.sleep(3)
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    req = urllib.request.Request(rec['artlink'], headers=hdr)
    artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['eprints.creators_name', 'eprints.keywords', 'DC.language',
                                        'DC.identifier', 'DC.description', 'DC.description'])
    rec['autaff'][-1].append('U. Heidelberg (main)')
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #PACS
            if meta['name'] == 'eprints.class_labels':
                if repacs.search(meta['content']):
                    rec['pacs'].append(repacs.sub(r'\1', meta['content']))
            #DDC
            elif meta['name'] == 'eprints.subjects':
                if not 'ddc' in list(rec.keys()):
                    rec['ddc'] = meta['content']
                elif meta['content'] < rec['ddc']:
                    rec['ddc'] = meta['content']
            #FFT
            elif meta['name'] == 'eprints.document_url':
                if re.search('http', meta['content']):
                    rec['FFT'] = meta['content']
                else:
                    rec['FFT'] = 'https://archiv.ub.uni-heidelberg.de' + meta['content']
    if 'ddc' in list(rec.keys()):
        if rec['ddc'][0] == '5':
            if rec['ddc'] in ['540', '570']:
                keepit = False
            else:
                rec['note'].append(' DDC: %s ' % (rec['ddc']))
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'eprint-field-advisor'}):
        for span in tr.find_all('span', attrs = {'class' : 'person_name'}):
            sv = re.sub('Prof\. *', '', span.text.strip())
            sv = re.sub('Dr\. *', '', sv)
            sv = re.sub('h\.c\. *', '', sv)
            rec['supervisor'].append([sv])
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'eprint-field-divisions'}):
        for a in tr.find_all('a'):
            division = a.text.strip()
            if division in boring:
                keepit = False
            else:
                rec['note'].append(division)
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
	
