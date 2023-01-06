# -*- coding: utf-8 -*-
#harvest theses from Rome U. La Sapienza
#FS: 2022-28-18

import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Rome U.'
rpp = 100
numofpages = 3
jnlfilename = 'THESES-ROME-%s' % (ejlmod3.stampoftoday())

boring = ['DIPARTIMENTO DI SCIENZE GIURIDICHE', 'DIPARTIMENTO DI SCIENZE ODONTOSTOMATOLOGICHE E MAXILLO-FACCIALI',
          'DIPARTIMENTO DI FILOSOFIA', "DIPARTIMENTO DI PIANIFICAZIONE, DESIGN, TECNOLOGIA DELL'ARCHITETTURA",
          'DIPARTIMENTO DI PSICOLOGIA', 'DIPARTIMENTO DI SCIENZE POLITICHE',
          'DIPARTIMENTO MATERNO INFANTILE E SCIENZE UROLOGICHE',
          'DIPARTIMENTO DI CHIMICA', "DIPARTIMENTO DI ECONOMIA E DIRITTO",
          "DIPARTIMENTO DI INGEGNERIA STRUTTURALE E GEOTECNICA", "DIPARTIMENTO DI MEDICINA MOLECOLARE",
          "DIPARTIMENTO DI PSICOLOGIA DINAMICA, CLINICA E SALUTE",
          "DIPARTIMENTO DI SANITA' PUBBLICA E MALATTIE INFETTIVE", "DIPARTIMENTO DI SCIENZE DELL'ANTICHITA'",
          "DIPARTIMENTO DI SCIENZE DI BASE ED APPLICATE PER L'INGEGNERIA",
          "DIPARTIMENTO DI STORIA ANTROPOLOGIA RELIGIONI ARTE SPETTACOLO",
          "DIPARTIMENTO DI STORIA, DISEGNO E RESTAURO DELL'ARCHITETTURA", 
          "DIPARTIMENTO DI STUDI EUROPEI, AMERICANI E INTERCULTURALI", "DIPARTIMENTO DI NEUROSCIENZE UMANE",
          "FACOLTA' DI FARMACIA E MEDICINA", "IPARTIMENTO DI ARCHITETTURA E PROGETTO",
          "DIPARTIMENTO DI BIOLOGIA AMBIENTALE", 'DIPARTIMENTO DI BIOLOGIA E BIOTECNOLOGIE "CHARLES DARWIN"',
          "DIPARTIMENTO DI CHIMICA E TECNOLOGIE DEL FARMACO", "DIPARTIMENTO DI COMUNICAZIONE E RICERCA SOCIALE",
          'DIPARTIMENTO DI FISIOLOGIA E FARMACOLOGIA "VITTORIO ERSPAMER"',
          "DIPARTIMENTO DI INGEGNERIA CHIMICA, MATERIALI, AMBIENTE",
          "DIPARTIMENTO DI INGEGNERIA CIVILE, EDILE E AMBIENTALE", "DIPARTIMENTO DI SCIENZE DELLA TERRA", 
          "DIPARTIMENTO DI INGEGNERIA INFORMATICA, AUTOMATICA E GESTIONALE -ANTONIO RUBERTI-",
          "DIPARTIMENTO DI INGEGNERIA MECCANICA E AEROSPAZIALE", "DIPARTIMENTO DI LETTERE E CULTURE MODERNE",
          "DIPARTIMENTO DI MANAGEMENT", "DIPARTIMENTO DI MEDICINA CLINICA E MOLECOLARE",
          "DIPARTIMENTO DI METODI E MODELLI PER L'ECONOMIA, IL TERRITORIO E LA FINANZA",          
          "DIPARTIMENTO DI PSICOLOGIA DEI PROCESSI DI SVILUPPO E SOCIALIZZAZIONE",
          "DIPARTIMENTO DI SCIENZE E BIOTECNOLOGIE MEDICO-CHIRURGICHE", "DIPARTIMENTO DI ORGANI DI SENSO",
          "DIPARTIMENTO DI SCIENZE SOCIALI ED ECONOMICHE", "DIPARTIMENTO DI STUDI GIURIDICI ED ECONOMICI",
          'DIPARTIMENTO "ISTITUTO ITALIANO DI STUDI ORIENTALI - ISO"', "FACOLTA' DI MEDICINA E PSICOLOGIA",
          "FACOLTA' DI ECONOMIA", "FACOLTA' DI LETTERE E FILOSOFIA", "FACOLTA' DI MEDICINA E ODONTOIATRIA",
          "DIPARTIMENTO DI ARCHITETTURA E PROGETTO", "DIPARTIMENTO DI DIRITTO ED ECONOMIA DELLE ATTIVITA' PRODUTTIVE",
          "DIPARTIMENTO DI MEDICINA SPERIMENTALE", "DIPARTIMENTO DI MEDICINA TRASLAZIONALE E DI PRECISIONE",          
          "DIPARTIMENTO DI SCIENZE ANATOMICHE, ISTOLOGICHE, MEDICO LEGALI E DELL'APPARATO LOCOMOTORE",
          "DIPARTIMENTO DI SCIENZE CHIRURGICHE", "DIPARTIMENTO DI SCIENZE MEDICO-CHIRURGICHE E DI MEDICINA TRASLAZIONALE"] 
boring += ['ICAR', 'SPS', 'MED', 'BIO', 'IUS', 'M-PED', 'M-GIL', 'M-PSI', 'M-FIL',
           'L-ANT', 'L-FIL-LET', 'L-LIN', 'SECS-P', 'GEO', 'L-ART', 'L-OR', 'CHIM']

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for page in range(numofpages):
        tocurl = 'https://iris.uniroma1.it/simple-search?query=&filter_field=typeFull&filter_type=equals&filter_value=07+Tesi+di+Dottorato&filter_value_display=07+Tesi+di+Dottorato&sort_by=dc.date.issued_dt&order=desc&rpp=' + str(rpp) + '&etal=0&start=' + str(rpp*page)
        ejlmod3.printprogress('=', [[page+1, numofpages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(2)
        for a in tocpage.body.find_all('a', attrs = {'class' : 'list-group-item'}):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : [], 'autaff' : [], 'keyw' : [], 'supervisor' : []}
            rec['link'] = 'https://iris.uniroma1.it' + a['href']
            rec['hdl'] = re.sub('\/handle\/', '', a['href'])
            rec['tit'] = a.text.strip()
            if ejlmod3.checkinterestingDOI(rec['hdl']):
                prerecs.append(rec)
            
j = 0
recs = []
for rec in prerecs:
    j += 1
    keepit = True
    ejlmod3.printprogress('-', [[j, len(prerecs)], [rec['link']], [len(recs)]])
    req = urllib.request.Request(rec['link'] + '?mode=complete')
    artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(5)
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_author', 'citation_author_email',
                                        'citation_author_orcid', 'citation_date', 'citation_pdf_url',
                                        'citation_language'])
    if 'date' in rec and rec['date'] == '9999':
        keepit = False
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    #abstract
    for p in artpage.body.find_all('p', attrs = {'class' : 'abstractEng'}):
        rec['abs'] = p.text.strip()
    if not 'abs' in rec:
        for p in artpage.find_all('p', attrs = {'class' : 'abstractIta'}):
            rec['abs'] = p.text.strip()
    #keywords
    for meta in artpage.find_all('meta', attrs = {'name' : 'DC.subject', 'xml:lang' : '*'}):
        rec['keyw'].append(meta['content'])
    #section
    for meta in artpage.find_all('meta', attrs = {'name' : 'DC.contributor'}):
        if not meta['content'] in ['ITA', 'ITALIA', 'IRN', 'IRAN', 'RUS', 'ESP', 'GEORGIA',
                                   'INDIA', 'BRA', 'ALB', 'ALBANIA', 'BRASILE', 'MESSICO',
                                   'REPUBBLICA POPOLARE CINESE', 'TUR']:
            contributor = meta['content']
            if contributor == 'DIPARTIMENTO DI INFORMATICA':
                rec['fc'] = 'i'
            elif contributor == 'DIPARTIMENTO DI MATEMATICA':
                rec['fc'] = 'm'
            elif contributor in boring:
                keepit = False
            else:
                rec['note'].append(contributor)
    #section
    for meta in artpage.find_all('meta', attrs = {'name' : 'citation_keywords'}):
        for section in re.split(' *;? *\-? *Settore ', meta['content']):
            sectionfac = re.sub('\/\d.*', '', section)
            if sectionfac in ['MAT']:
                rec['fc'] = 'm'
            elif section == 'FIS/05 - Astronomia e Astrofisica':
                rec['fc'] = 'a'
            elif sectionfac in ['SECS-S']:
                rec['fc'] = 's'
            elif sectionfac in boring:
                keepit = False
            else:
                rec['note'].append(section)
    #supervisor
    for div in artpage.body.find_all('div', attrs = {'id' : 'dc.authority.advisor_content'}):
        for br in div.find_all('br'):
            br.replace_with(';;;')
            for sv in re.split(';;;', div.text):
                rec['supervisor'].append([sv])
    if keepit:
        rec['autaff'][-1].append(publisher)    
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
