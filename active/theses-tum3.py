# -*- coding: utf-8 -*-
#harvest theses from TU Munich
#FS: 2019-09-24
#FS: 2022-11-24


import sys
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import os
import ejlmod3
import time

publisher = 'Munich, Tech. U.'
jnlfilename = 'THESES-TUM-%s' % (ejlmod3.stampoftoday())
rpp = 100
years = 2
skipalreadyharvested = True

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

alreadyharvested = []
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
links = []
reboring = re.compile('(Bachelorarbeit|Masterarbeit)')
#for (fc, dep, pages) in [('', '603847', 1), ('m', '603845', 1), ('c', '603842', 1), ('o', '603787', 10)]:
for (fc, dep, pages) in [('c', '1691132', 1), ('m', '1691133', 1), ('', '1688930', 5)]:
#                         ('m', '603815', 2), ('', '603821', '')]:
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
                if not reboring.search(child.text) and ejlmod3.checkinterestingDOI(rec['link']):
                    if not rec['link'] in links:
                        for br in child.find_all('br'):
                            br.replace_with('XXXXXX')
                        for part in re.split(' *XXXXXX *', child.text):
                            if re.search('^[12]\d\d\d$', part):
                                rec['year'] = part
                                if int(part) <= ejlmod3.year(backwards=years):
                                    keepit = False
                        if keepit:
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
    req = urllib.request.Request(rec['link'] + '&change_language=de', headers=hdr)
    artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_publication_date',
                                        'citation_pdf_url'])
    #Metadata
    for dl in artpage.body.find_all('dl', attrs = {'class' : 'object_meta'}):
        for child in dl.children:
            try:
                childclass = child['class'][0]
            except:
                continue
            if childclass == 'mask_label':
                label = child.text.strip()
            elif childclass == 'mask_value':
                #Document type
                if label == 'Dokumenttyp:':
                    rec['documenttype'] = child.text.strip()
                    rec['note'].append(rec['documenttype'])
                #Author
                elif label == 'Autor:':
                    rec['autaff'] = [[ child.text.strip() ]]
                    for a in child.find_all('a'):
                        if a.has_attr('href') and a['href'][:6] == 'mailto':
                            rec['autaff'][-1].append(re.sub('mailto:', 'EMAIL:', a['href']))
                #title:
                elif label == 'Originaltitel:':
                    rec['tit'] = child.text.strip()
                elif label == 'Übersetzter Titel:':
                    rec['transtit'] = child.text.strip()
                #Abstract
                elif label == 'Kurzfassung:':
                    rec['origabs'] = child.text.strip()
                elif label == 'Übersetzte Kurzfassung:':
                    rec['transabs'] = child.text.strip()
                #classification
                elif label in ['Fachgebiet:', 'TU-Systematik:']:
                    for subject in re.split(' *; *', child.text.strip()):
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
                #DDC
                elif label == 'DDC:':
                    rec['ddc'] = []
                    for part in re.split('[,;]',  child.text.strip()):
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
                elif label == 'Betreuer:':
                    rec['supervisor'].append([re.sub(' \(.*', '', child.text.strip())])
                #Faculty
                elif label in ['Institution:', 'Fakultät:']:
                    department = child.text.strip()
                    if department in boring:
                        keepit = False
                        #print('   skip "%s"' % (department))
                    elif department == 'Fakultät für Informatik':
                        rec['fc'] = 'm'
                    elif department == 'Fakultät für Informatik':
                        rec['fc'] = 'c'
                    else:                    
                        rec['note'].append(department)
                #Pages
                elif label == 'Seiten:':
                    if re.search('\d\d', child.text):
                        rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', child.text.strip())
                #URN
                elif label in ['URN:', 'Urn (Zitierfähige URL):']:
                    rec['urn'] = re.sub('.*\?', '', child.text.strip())
                #Keywords
                elif label in ['Stichworte:', 'Übersetzte Stichworte:']:
                    rec['keyw'] += re.split(', ', child.text.strip())
                #language
                elif label == 'Sprache:':
                    rec['language'] = child.text.strip()
                #ISBN
                elif label == 'ISBN:':
                    rec['isbn'] = child.text.strip()
                #Hinweis
                elif label == 'Hinweis:':
                    rec['note'].append(child.text.strip())
                #
                #elif label == '':
                #    rec[''] = child.text.strip()
                elif not label in ['Jahr:', 'Gutachter:', 'Dateigröße:', 'WWW:', 'Eingereicht am:',
                                   'Mündliche Prüfung:', 'Letzte Änderung:',
                                   'Originaluntertitel:', 'Übersetzter Untertitel:']:
                    print('\n  - ', label, ':', child.text.strip() + '\n')
    #abstract
    if 'language' in rec and rec['language'] == 'de' and 'transabs' in rec:
        rec['abs'] = rec['transabs']
    elif 'origabs' in rec:
        rec['abs'] = rec['origabs']
    #title
    if 'language' in rec and rec['language'] == 'en' and 'transtit' in rec:
        del(rec['transtit'])
    #Habilitation
    if 'documenttype' in rec and rec['documenttype'] == 'Habilitation':
        year = re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])
        rec['MARC'] = [('502', [('b', 'habilitation'), ('c', publisher), ('d', year)])]
    #PDF       
    for div in artpage.body.find_all('div', attrs = {'class' : 'document_download'}):
        for a in div.find_all('a'):
            rec['hidden'] = 'https://mediatum.ub.tum.de' + a['href']
    if keepit:
        if 'urn' in rec and rec['urn'] in alreadyharvested:
            print('  already in backup')
        else:
            rec['autaff'][-1].append(publisher)
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])
    time.sleep(5)
        
ejlmod3.writenewXML(recs, publisher, jnlfilename)
