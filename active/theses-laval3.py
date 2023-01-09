# -*- coding: utf-8 -*-
#harvest theses from Laval U.
#FS: 2022-05-23
#FS: 2023-01-06

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc
import json

publisher = 'Laval U.'
jnlfilename = 'THESES-LAVAL-%s' % (ejlmod3.stampoftoday())

rpp = 50
years = [ejlmod3.year(), ejlmod3.year(backwards=1)]

hdr = {'User-Agent' : 'Magic Browser'}
options = uc.ChromeOptions()
options.headless=True
options.binary_location='/usr/bin/chromium-browser'
driver = uc.Chrome(version_main=103, options=options)


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
boring += ['Doctorat en sciences de l&s;administration - finance et assurance',
           'Maîtrise en nutrition',
           'Maîtrise en psychopédagogie - adaptation scolaire',
           'Maîtrise en sciences des aliments',
           'Faculté des sciences de l&s;administration.',
           'Faculté des sciences de l&s;agriculture et de l&s;alimentation.',
           'Faculté des sciences de l&s;éducation.']
boring += ['Doctorat en biologie végétale', 'Doctorat en génie des eaux',
           'Doctorat en génie électrique', 'Doctorat en génie mécanique',
           'Doctorat en sciences animales',
           'Doctorat en sciences de l&s;administration - finance et assurance',
           'Doctorat en sciences des aliments', 'Maîtrise en arts visuels',
           'Maîtrise en biologie', 'Maîtrise en biologie végétale',
           'Maîtrise en chimie', 'Maîtrise en génie chimique',
           'Maîtrise en génie civil', 'Maîtrise en génie des eaux',
           'Maîtrise en génie des matériaux et de la métallurgie',
           'Maîtrise en génie électrique', 'Maîtrise en génie mécanique',
           'Maîtrise en microbiologie', 'Maîtrise en philosophie',
           'Maîtrise en physique', 'Maîtrise en psychopédagogie',
           'Maîtrise en sciences de la consommation',
           'Maîtrise en sciences des aliments - microbiologie alimentaire',
           'Faculté d&s;aménagement, d&s;architecture, d&s;art et de design.',
           'Faculté de philosophie.',
           'Faculté des sciences de l&s;administration.',
           'Faculté des sciences de l&s;agriculture et de l&s;alimentation.',
           'Faculté des sciences de l&s;éducation.',
           'Doctorat en génie des matériaux et de la métallurgie',
           'Maîtrise en biochimie',
           'Maîtrise en biophotonique',
           'Maîtrise en biostatistique',
           'Maîtrise en études internationales - relations internationales',
           'Maîtrise en études internationales',
           'Maîtrise en informatique',
           'Maîtrise en mathématiques',
           'Maîtrise en sciences dentaires - endodontie',
           'Maîtrise en sciences dentaires - parodontie',
           'Maîtrise en statistique',
           'Maîtrise interuniversitaire en sciences de la Terre',
           'Maîtrise sur mesure',
           'École supérieure d&amp;s;études internationales.',
           'Faculté de médecine dentaire.']
boring += ['Doctorat en génie des mines',
           'Doctorat en psychologie - recherche et intervention (orientation clinique)',
           'Doctorat en psychologie',
           'Maîtrise en actuariat',
           'Maîtrise en chimie - avec mémoire (M. Sc.)',
           'Maîtrise en génie civil - avec mémoire (M. Sc.)',
           'Maîtrise en génie des mines',
           'Maîtrise en physique - physique médicale',
           'Faculté des sciences sociales']

prerecs = []
recs = []
i = 0
for year in years:
    i += 1
    pages = 0
    starturl = 'https://corpus.ulaval.ca/browse/dateissued?scope=32fa194e-af6e-41d8-bde3-fae02aed6899&bbm.page=1&startsWith=' + str(year) + '&bbm.sd=DESC&bbm.rpp=' + str(rpp)
    ejlmod3.printprogress("=", [[i, len(years)], [year], [starturl]])
    driver.get(starturl)
    tocpages = [BeautifulSoup(driver.page_source, features="lxml")]
    for div in tocpages[0].find_all('div', attrs = {'class' : 'pagination-info'}):
        for span in div.find_all('span'):
            spant = span.text.strip()
            if re.search('1.* (of|sur) \d+', spant):
                numoftheses = int(re.sub('.* (of|sur) (\d+).*', r'\2', spant))
                pages = (numoftheses-1) // rpp + 1
    for page in range(pages-1):
        time.sleep(5)
        tocurl = 'https://corpus.ulaval.ca/browse/dateissued?scope=32fa194e-af6e-41d8-bde3-fae02aed6899&bbm.page=' + str(page+2) + '&startsWith=' + str(year) + '&bbm.sd=DESC&bbm.rpp=' + str(rpp)
        ejlmod3.printprogress("=", [[i, len(years)], [year], [page+2, pages]])
        driver.get(tocurl)
        req = urllib.request.Request(starturl, headers=hdr)
        tocpages.append(BeautifulSoup(driver.page_source, features="lxml"))
    for tocpage in tocpages:
        for script in tocpage.find_all('script'):
            if script.contents:
                scriptt = re.sub('&q;', '"', re.sub('[\n\t]', '', script.contents[0].strip()))
            else:
                scriptt = False
        if scriptt:
            scripttjson = json.loads(scriptt)
            metadata = scripttjson['NGRX_STATE']['core']['cache/object']
            links = metadata.keys()
            for (i, link) in enumerate(links):
                ejlmod3.printprogress('-', [[i+1, len(links)], [link]])
                if 'data' in metadata[link]:
                    keepit = True
                    thesis = metadata[link]['data']
                    if 'isWithdrawn' in thesis and thesis['isWithdrawn']:
                        continue
                    if 'handle' in thesis:
                        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : []}
                        rec['hdl'] = thesis['handle']
                    else:
                        continue
                    if not 'metadata' in thesis:
                        print(thesis.keys())
                        continue
                    #fulltext
                    rec['pdf_url'] = 'https://corpus.ulaval.ca/bitstreams/%s/download' % (thesis['uuid'])
                    rec['link'] = 'https://corpus.ulaval.ca/entities/publication/%s' % (thesis['uuid'])
                    #faculty
                    if 'bul.faculte' in thesis['metadata']:
                        for fac in thesis['metadata']['bul.faculte']:
                            if fac['value'] in boring:
                                print('    skip %s' % (fac['value']))
                                keepit = False
                            else:
                                rec['note'].append('FAC=' + fac['value'])
                    #supervisor
                    if "dc.contributor.advisor" in thesis['metadata']:
                        for sv in thesis['metadata']['dc.contributor.advisor']:
                            rec['supervisor'].append([sv['value']])
                    #author
                    for au in thesis['metadata']['dc.contributor.author']:
                        rec['autaff'] = [[au['value'], publisher]]
                    #date
                    if 'dc.date.available' in thesis['metadata']:
                        for date in thesis['metadata']['dc.date.available']:
                            rec['date'] = date['value']
                    #abstract
                    if 'dc.description.abstract' in thesis['metadata']:
                        for abstract in thesis['metadata']['dc.description.abstract']:
                            if 'language' in abstract:
                                if abstract['language'] == 'en':
                                    rec['abs'] = abstract['value']
                                else:
                                    rec['absfr'] = abstract['value']
                        if not 'abs' in rec and 'absfr' in rec:
                            rec['abs'] = rec['absfr']
                    #pages
                    if 'dc.format.extent' in thesis['metadata']:
                        for extent in thesis['metadata']['dc.format.extent']:
                            if re.search('\d\d p', extent['value']):
                                rec['pages'] = re.sub('.*?(\d\d+) p.*', r'\1', extent['value'])
                            else:
                                rec['note'].append('EXTENT='+extent['value'])
                    #language
                    if 'dc.language' in thesis['metadata']:
                        for lang in thesis['metadata']['dc.language']:
                            rec['language'] = lang['value']
                    #license
                    if 'dc.rights' in thesis['metadata']:
                        for rights in thesis['metadata']['dc.rights']:
                            if re.search('creativecom', rights['value']):
                                rec['license'] = {'url' : rights['value']}
                    #title
                    if 'dc.title' in thesis['metadata']:
                        for tit in thesis['metadata']['dc.title']:
                            rec['tit'] = tit['value']
                    #degree
                    if 'etdms.degree.discipline' in thesis['metadata']:
                        for degree in thesis['metadata']['etdms.degree.discipline']:
                            if degree['value'] in boring:
                                keepit = False
                            elif degree['value'] in ['Doctorat en mathématiques']:
                                rec['fc'] = 'm'
                            elif degree['value'] in ['Doctorat en informatique']:
                                rec['fc'] = 'c'
                            elif degree['value'] in ['Doctorat en statistique']:
                                rec['fc'] = 's'
                            elif not degree['value'] in ['Doctorat en physique']:
                                rec['note'].append('DEG=' + degree['value'])
                    #keywords
                    if 'dc.subject.rvm' in thesis['metadata']:
                        for keyw in thesis['metadata']['dc.subject.rvm']:
                            rec['keyw'].append(keyw['value'])
                    if keepit:
                        recs.append(rec)
                        ejlmod3.printrecsummary(rec)
        print('  %4i records so far' % (len(recs)))

ejlmod3.writenewXML(recs, publisher, jnlfilename)



