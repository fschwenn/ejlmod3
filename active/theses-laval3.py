# -*- coding: utf-8 -*-
#harvest theses from Laval U.
#FS: 2022-05-23
#FS: 2022-10-24

import getopt
import sys
import os
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc


publisher = 'Laval U.'
jnlfilename = 'THESES-LAVAL-%s' % (ejlmod3.stampoftoday())

rpp = 40
pages = 8

boring = ['Faculté de médecine.', 'Faculté des lettres et des sciences humaines.',
          "Faculté des sciences de l'administration.",
          "Faculté des sciences de l'agriculture et de l'alimentation.",
          'Faculté des sciences sociales.', 'Faculté de musique.',
          "Faculté de droit.", "Faculté de foresterie, de géographie et de géomatique.",
          "Faculté des sciences de l'éducation.", 'Faculté de pharmacie.',
          "Faculté de théologie et de sciences religieuses.",
          'Faculté des lettres et des sciences humaines',
          'Faculté de pharmacie.',
          "Faculté des sciences infirmières."]
boring += ['Doctorat en microbiologie-immunologie', 'Doctorat en histoire', 'Doctorat en chimie',
           "Doctorat en actuariat", 'Doctorat en génie chimique', 
           'Doctorat en microbiologie agroalimentaire', 
           "Doctorat en sciences de l'administration - management",
           'Doctorat en service social', 'Doctorat interuniversitaire en océanographie',
           "Doctorat en biologie", 'Doctorat en génie civil',
           "Doctorat en droit", 'Doctorat en biochimie',
           "Doctorat en nutrition", 'Doctorat en architecture',
           "Doctorat en philosophie", 'Doctorat en microbiologie',
           "Doctorat en psychopédagogie", 'Doctorat en théologie',
           "Doctorat en santé communautaire", 'Doctorat en biophotonique',
           "Doctorat en sciences des aliments - microbiologie alimentaire",
           "Doctorat en sciences forestières",
           "Doctorat en technologie éducative",
           "Doctorat sur mesure"]
boring += ['Thèse. Médecine', "Thèse. Administration et politiques de l'éducation",
           "Thèse. Agriculture", "Thèse. Agroéconomie",
           "Thèse. Aménagement du territoire et développement régional",
           "Thèse. Anthropologie", "Thèse. Biochimie", "Thèse. Biologie cellulaire et moléculaire",
           "Thèse. Biologie", "Thèse. Biologie végétale", "Thèse. Chimie",
           "Thèse. Communication publique", "Thèse. Comptabilité", "Thèse. Didactique",
           "Thèse. Droit", "Thèse. Économique", "Thèse. Ethnologie", "Thèse. Génie chimique",
           "Thèse. Génie civil", "Thèse. Génie des mines, de la métallurgie et des matériaux",
           "Thèse. Génie électrique et génie informatique", "Thèse. Génie électrique",
           "Thèse. Génie mécanique", "Thèse. Géographie", "Thèse. Géologie et minéralogie",
           "Thèse. Histoire", "Thèse. Linguistique", "Thèse. Littérature canadienne-française",
           "Thèse. Littérature espagnole", "Thèse. Littérature et arts de la scène et de l'écran",
           "Thèse. Littérature française", "Thèse. Littérature francophone", "Thèse. Management",
           "Thèse. Médecine expérimentale", "Thèse. Microbiologie-immunologie", "Thèse. Musique",
           "Thèse. Nutrition", "Thèse. Pharmacie", "Thèse. Philosophie", "Thèse. Psychologie",
           "Thèse. Psychopédagogie - Adaptation scolaire", "Thèse. Psychopédagogie",
           "Thèse. Relations industrielles", "Thèse. Relations internationales",
           "Thèse. Santé communautaire", "Thèse. Science politique", "Thèse. Sciences animales",
           "Thèse. Sciences cliniques et biomédicales", "Thèse. Sciences de l'administration",
           "Thèse. Sciences de l'éducation", "Thèse. Sciences de l'orientation",
           "Thèse. Sciences des religions", "Thèse. Sciences du bois",
           "Thèse. Sciences et technologie des aliments", "Thèse. Sciences forestières",
           "Thèse. Sciences infirmières", "Thèse. Service social", "Thèse. Sociologie",
           "Thèse. Archéologie", "Thèse. Lettres", "Thèse. Architecture et urbanisme",
           "Thèse. Littérature ancienne", "Mémoire. Génie des mines, de la métallurgie et des matériaux",
           "Thèse. Actuariat", "Thèse. Arts visuels", "Thèse. Éducation physique",
           "Thèse. Histoire de l'art", "Thèse. Littérature anglaise", "Thèse. Sciences de l'éducation.",
           "Thèse. Sols et environnement", "Thèse. Technologie éducative", "Thèse. Théologie"]
boring += ["Doctorat en génie des eaux", "Doctorat en génie des matériaux et de la métallurgie",
           "Doctorat en génie des mines", 
           "Doctorat en psychologie - recherche et intervention (orientation clinique)",
           "Doctorat en psychologie", "Doctorat interuniversitaire en sciences de la Terre",
           "Docteure en psychologie (D. Psy.)", "Faculté des sciences sociales"]

options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/chromium-browser'
options.add_argument('--headless')
driver = uc.Chrome(version_main=103, options=options)

prerecs = []
recs = []
for page in range(pages):
        tocurl = 'https://corpus.ulaval.ca/search?f.resourceTypeName=th%C3%A8se%20de%20doctorat,equals&spc.page=' + str(page+1) + '&spc.sf=dc.date.issued&spc.sd=DESC&spc.rpp=' + str(rpp)
        ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        for li in tocpage.body.find_all('li', attrs = {'class' : 'd-flex'}):
            for a in li.find_all('a', attrs = {'class' : 'item-list-title'}):
                rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : []}
                rec['link'] = 'https://corpus.ulaval.ca' + a['href']  + '/full'
                if ejlmod3.ckeckinterestingDOI(rec['link']):
                    prerecs.append(rec)
        print('                     %3i records so far' % (len(prerecs)))
        time.sleep(6)

i = 0
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        driver.get(rec['link'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            driver.get(rec['link'])
            artpage = BeautifulSoup(driver.page_source, features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_pdf_url'])
    if 'pdf_url' in rec:
        rec['pdf_url'] = re.sub('.*localhost:4000', 'https://corpus.ulaval.ca', rec['pdf_url'])
    (frtitle, frabs) = ('', '')
    for tr in artpage.body.find_all('tr'):
        tds = tr.find_all('td')
        if len(tds) >= 2:
            key = tds[0].text.strip()
            val = tds[1].text.strip()
            if len(tds) >= 3:
                lang = tds[2].text.strip()
            else:
                lang = ''
            #author
            if key == 'dc.contributor.author':
                rec['autaff'] = [[ val, publisher ]]
            #supervisor
            elif key == 'dc.contributor.advisor':
                rec['supervisor'].append([val])
            #title
            elif key == 'dc.title':
                if lang in ['fr', 'fra', 'fr_CA']:
                    frtitle =  val
                else:
                    rec['tit'] = val
            #date
            elif key == 'dc.date.issued':
                rec['date'] = val
            #keywords
            elif key == 'dc.subject.rvm':
                rec['keyw'].append(val)
            #DOI
            elif key == 'dc.identifier.doi':
                if re.search('^10\.\d+\/', val):
                    rec['doi'] = val
            #abstract
            elif key == 'dc.description.abstract':
                if lang in ['eng', 'en']:
                    rec['abs'] = val
                else:
                    frabs = val
            #pages
            elif key == 'dc.format.extent':
                if re.search('\d\d+ pages', val):
                    rec['pages'] = re.sub('.*?(\d\d+) pages.*', r'\1', val)
            #language
            elif key == 'dc.language':
                rec['language'] = val
            #handle
            elif key == 'dc.identifier.uri':
                if re.search('handle.net\/\d', val):
                    rec['hdl'] = re.sub('.*handl.net\/', '', val)
            #references
            elif key == 'dc.identifier.citation':
                rec['refs'].append([('x', val)])
            #degree
            elif key == 'etdms.degree.discipline':
                degree = val
                if degree in boring:
                    keepit = False
                    #print('    skip %s = "%s"' % (key, val))
                elif degree == 'Doctorat en informatique':
                    rec['fc'] = 'c'
                elif degree == 'Doctorat en mathématiques':
                    rec['fc'] = 'm'
                elif degree and degree != 'Doctorat en physique':
                    rec['note'].append('DEGREE_D: %s' % (degree))
            #degree
            elif key == 'etdms.degree.name':
                degree = val
                if degree in boring:
                    keepit = False
                    #print('    skip %s = "%s"' % (key, val))
                elif degree != 'Philosophiæ doctor (Ph. D.)':
                    rec['note'].append('DEGREE_N: %s' % (degree))
            #department
            elif key == 'bul.faculte':
                department = val
                if department in boring:
                    keepit = False
                    #print('    skip %s = "%s"' % (key, val))
                elif department != 'Faculté des sciences et de génie.':
                    rec['note'].append('DEPARTMENT=%s' % (department))
    #take french title if there is no english title
    if not 'tit' in rec:
        if frtitle:
            rec['tit'] = frtitle
    #take french abstract if there is no english abstract
    if not 'abs' in rec:
        if frabs:
            rec['abs'] = frabs
    if keepit:
        if 'autaff' in rec:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
