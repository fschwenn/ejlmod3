# -*- coding: utf-8 -*-
#harvest theses from TU Munich
#FS: 2019-09-24
#FS: 2022-11-24


import sys
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Munich, Tech. U.'
jnlfilename = 'THESES-TUM-%s' % (ejlmod3.stampoftoday())
rpp = 100
boring = ['Fakultät für Sport- und Gesundheitswissenschaften']
boring += ['CHE Chemie', 'BAU 550', 'BAU 650', 'BAU 650', 'UMW 300', 'BAU 651', 'BAU 900', 'BAU 950',
           'BAU Bauingenieurwesen, Vermessungswesen', 'GEO Geowissenschaften',
           'BAU Bauingenieurwesen, Vermessungswesen', 'BIO 110','BIO 250', 'BIO Biowissenschaften',
           'BRA 200', 'BRA Brauwesen', 'ERG Energietechnik, Energiewirtschaft', 'FER 000',
           'FER Fertigungstechnik', 'FOR 110', 'FOR Forstwissenschaften', 'IND 020',
           'LEB Lebensmitteltechnologie', 'MED 040', 'MED 535', 'MED 320', 'MED 410', 'MED 430',
           'MED 320', 'MED 430', 'MED 450', 'MED Medizin', 'VER 630', 'MAS 590',
           'VER Technik der Verkehrsmittel', 'WIR 531', 'WIR 700', 'WIR 800', 'WIR 895',
           'WIR Wirtschaftswissenschaften']
boring += ['ARC 045', 'ARC 165', 'ARC 279', 'ARC 370', 'ARC Architektur', 'BAU 005', 'BAU 050',
           'BAU 150', 'BAU 450', 'BAU 967', 'BIO 120', 'BIO 140', 'BIO 300', 'BIO 780', 'BIO 950',
           'CHE 140', 'CHE 167', 'CHE 513', 'CHE 800', 'CHE 880', 'CIT 001', 'CIT 200', 'CIT 280',
           'CIT 325', 'CIT 335', 'CIT 680', 'CIT 900', 'CIT 960',
           'CIT Chemie-Ingenieurwesen, Technische Chemie, Biotechnologie', 'EDU 640',
           'EDU Erziehungswissenschaften', 'GES Geschichte', 'IND Sonstige Industrien',
           'INF Informationswesen, Bibliotheks-, Dokumentations-, Archiv-, Museumswesen',
           'Ingenieurfakultät Bau Geo Umwelt', 'KUN 850', 'KUN Kunst', 'LAN 120', 'LAN 332',
           'LAN 490', 'LAN 610', 'LAN 640', 'LAN Landbauwissenschaft', 'LEB 020', 'LEB 050',
           'LEB 054', 'MAS 000', 'MAS 520', 'MAS 700', 'MAS Maschinenbau', 'MED 230', 'MED 280',
           'MED 370', 'MED 385', 'MED 403', 'MED 580', 'MED 600', 'MED 670', 'MTA 000', 'MTA 009',
           'MTA 300', 'MTA 309', 'MTA 600', 'MTA 900',
           'MTA Technische Mechanik, Technische Thermodynamik, Technische Akustik', 'OEK 100',
           'OEK 160', 'OEK Ökotrophologie, Ernährungswissenschaft', 'POL 650', 'POL Politologie',
           'PSY Psychologie', 'RPL 000', 'RPL 734', 'RPL 900', 'RPL Raumplanung, Raumordnung',
           'SOZ 700', 'SPO 570', 'SPO 600', 'SPO 610', 'SPO 617', 'SPO 630', 'SPO 650', 'SPO 680',
           'SPO 695', 'SPO 720', 'SPO Sport', 'UMW 028', 'UMW 200', 'UMW 350',
           'UMW Umweltschutz und Gesundheitsingenieurwesen', 'VER 020', 'VER 500', 'VER 505',
           'VER 600', 'VER 700', 'VER 800', 'WEH Wehrtechnik', 'WER 000', 'WER 440', 'WER 490',
           'WER 740', 'WER Werkstoffwissenschaften', 'WIR 006', 'WIR 523', 'WIR 527', 'WIR 780',
           'WIS 600', 'WIS Wissenschaftskunde']
hdr = {'User-Agent' : 'Magic Browser'}

prerecs = []
links = []
reboring = re.compile('(Bachelorarbeit|Masterarbeit)')
for (fc, dep, pages) in [('', '603847', 1), ('m', '603845', 1), ('c', '603842', 1), ('o', '603787', 10)]:
    tocurl = 'https://mediatum.ub.tum.de/' + dep + '?id=' + dep + '&sortfield0=-year&sortfield1=&nodes_per_page=' + str(rpp)
    for page in range(pages):
        ejlmod3.printprogress('=', [[dep], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        for div in tocpage.body.find_all('div', attrs = {'class' : 'preview_list'}): 
            for a in div.find_all('a'):
                keepit = True
                rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'note' : [], 'supervisor' : []}
                rec['link'] = re.sub('.*=', 'https://mediatum.ub.tum.de/?id=', a['href'])
            for child in div.find_all('div', attrs = {'class' : 'mediatum-stylelist-div'}):
                if not reboring.search(child.text) and ejlmod3.ckeckinterestingDOI(rec['link']):
                    if not rec['link'] in links:
                        prerecs.append(rec)
                        links.append(rec['link'])
        print('  %4i records so far' % (len(prerecs)))
        time.sleep(5)
        nextpage = tocpage.body.find_all('a', attrs = {'class' : 'page-nav-next'})
        if nextpage:
            tocurl = 'https://mediatum.ub.tum.de' + nextpage[0]['href']
        else:
            break
            
recs = []
for (i, rec) in enumerate(prerecs):
    i += 1
    keepit = True
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
    req = urllib.request.Request(rec['link'], headers=hdr)
    artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'DC.subject', 'citation_publication_date',
                                        'citation_pdf_url'])
    #first get Language
    for div in artpage.body.find_all('div', attrs = {'class' : ['field-language', 'field-lang']}):
        for div2 in div.find_all('div', attrs = {'class' : 'mask_value'}):
            rec['language'] = div2.text.strip()
    #Metadata
    for div in artpage.body.find_all('div', attrs = {'class' : 'mask_row'}):
        row = ''
        for cl in div['class']:
            if cl != 'mask-row':
                row = cl
        for div2 in div.find_all('div', attrs = {'class' : 'mask_value'}):
            #Document type
            if row == 'field-type':
                rec['documenttype'] = div2.text.strip()
                rec['note'].append(rec['documenttype'])
            #Author
            elif row == 'field-studentauthor':
                rec['autaff'] = [[div2.text.strip()]]
            #Title
            elif row in ['field-title', 'field-booktitle']:
                rec['tit'] = div2.text.strip()
            elif row == 'field-title-translated':
                rec['transtit'] = div2.text.strip()
            #Abstract
            elif row in ['field-abstract', 'field-description'] and rec['language'] == 'en':
                rec['abs'] = div2.text.strip()
            elif row in ['field-abstract-translated', 'field-description-translated'] and rec['language'] == 'de':
                rec['abs'] = div2.text.strip()
            #classification
            elif row in ['field-subject', 'field-subject2']:
                for subject in re.split(' *; *', div2.text.strip()):
                    if subject in boring:
                        keepit = False
                        #print('   skip "%s"' % (subject))
                    elif subject in ['DAT Datenverarbeitung, Informatik']:
                        rec['fc'] = 'c'
                    elif subject in ['MAT Mathematik']:
                        rec['fc'] = 'm'
                    elif subject in ['PHY 600']:
                        rec['fc'] = 'f'
                    elif subject in ['PHY 900']:
                        rec['fc'] = 'a'
                    elif subject in ['PHY 410']:
                        rec['fc'] = 'p'
                    elif subject in ['PHY 023', 'PHY 025', 'PHY 035', 'PHY 037']:
                        rec['fc'] = 't'
                    elif subject in ['PHY 040', 'PHY 041', 'PHY 042', 'PHY 043']:
                        rec['fc'] = 'g'
                    elif subject in ['PHY 402', 'PHY 403', 'PHY 404']:
                        rec['fc'] = 'b'
                    else:
                        rec['note'].append(subject)
            #field-ddc
            elif row == 'field-ddc':
                rec['ddc'] = []
                for part in re.split('[,;]',  div2.text.strip()):
                    ddc = re.sub('\D', '', part)
                    if len(ddc) == 3:
                        rec['ddc'].append(ddc)
                        if ddc[:2] == '00':
                            rec['fc'] = 'c'
                        elif ddc[:2] == '51':
                            rec['fc'] = 'm'
                        elif ddc[:2] == '52':
                            rec['fc'] = 'a'
                        elif not rec['ddc'][:2] in ['50', '53', '60', '62']:
                            keepit = False
                            #print('   skip "%s"' % (div2.text.strip()))
            #Supervisor
            elif row in ['field-studentadvisor', 'field-advisor']:
                rec['supervisor'].append([re.sub(' \(.*', '', div2.text.strip())])
            #Faculty
            elif row == 'field-faculty':
                department = div2.text.strip()
                if department in boring:
                    keepit = False
                    #print('   skip "%s"' % (department))
                elif department == 'Fakultät für Informatik':
                    rec['fc'] = 'm'
                elif department == 'Fakultät für Informatik':
                    rec['fc'] = 'c'
                else:                    
                    rec['note'].append(department)
            #pages
            elif row in ['field-pages', 'field-pdf_pages']:
                if re.search('\d\d', div2.text):
                    rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', div2.text.strip())
            #URN
            elif row == 'field-urn_link':
                rec['urn'] = re.sub('.*\?', '', div2.text.strip())
    #abstract
    if not 'abs' in rec:
        if 'language' in rec and rec['language'] == 'de':
            for div in artpage.body.find_all('div', attrs = {'id' : 'description-translated_full'}):
                rec['abs'] = div.text.strip()
        else:
            for div in artpage.body.find_all('div', attrs = {'id' : 'description_full'}):
                rec['abs'] = div.text.strip()
    #Habilitation
    if 'documenttype' in rec and rec['documenttype'] == 'Habilitation':
        year = re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])
        rec['MARC'] = [('502', [('b', 'habilitation'), ('c', publisher), ('d', year)])]
    #PDF       
    for div in artpage.body.find_all('div', attrs = {'class' : 'document_download'}):
        for a in div.find_all('a'):
            rec['hidden'] = 'https://mediatum.ub.tum.de' + a['href']
    if keepit:
        rec['autaff'][-1].append(publisher)
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])
    time.sleep(5)
        
ejlmod3.writenewXML(recs, publisher, jnlfilename)
