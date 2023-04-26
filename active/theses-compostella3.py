# -*- coding: utf-8 -*-
#harvest theses from U. Santiago de Compostela (main)
#FS: 2020-10-08
#FS: 2023-04-26
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

jnlfilename = 'THESES-SantiagoDeCompostella-%s' % (ejlmod3.stampoftoday())
publisher = 'U. Santiago de Compostela (main)'

hdr = {'User-Agent' : 'Magic Browser'}
rpp = 50
skipalreadyharvested = True
pages = 1
years = 2
boringdisciplines = ['UniversidadedeSantiagodeCompostelaProgramadeDoutoramentoenAvancesenBioloxaMicrobianaeParasitaria',
                     'UniversidadedeSantiagodeCompostelaProgramadeDoutoramentoenBiodiversidadeeConservacindoMedioNatural',
                     'UniversidadedeSantiagodeCompostelaProgramadeDoutoramentoenCienciaeTecnoloxaQumica',
                     'UniversidadedeSantiagodeCompostelaProgramadeDoutoramentoenEnerxasRenovableseSustentabilidadeEnerxtica<',
                     'UniversidadedeSantiagodeCompostelaProgramadeDoutoramentoenEstatsticaeInvestigacinOperativa',
                     'UniversidadedeSantiagodeCompostelaProgramadeDoutoramentoenInnovacinenSeguridadeeTecnoloxaAlimentarias',
                     'UniversidadedeSantiagodeCompostelaProgramadeDoutoramentoenInvestigacineDesenvolvementodeMedicamentos',
                     'UniversidadedeSantiagodeCompostelaProgramadeDoutoramentoenNeurocienciaePsicoloxaClnica',
                     'CentroSingulardeInvestigacinenQumicaBiolxicaeMateriaisMolecularesCiQUS',
                     'FacultadedeQumica',
                     'UniversidadedeSantiagodeCompostelaProgramadeDoutoramentoenCienciadeMateriais',
                     'UniversidadedeSantiagodeCompostelaProgramadeDoutoramentoenCienciasAgrcolaseMedioambientais',
                     'UniversidadedeSantiagodeCompostelaProgramadeDoutoramentoenEnerxasRenovableseSustentabilidadeEnerxtica',
                     'UniversidadedeSantiagodeCompostelaProgramadeDoutoramentoenMedicinaMolecular',
                     'UniversidadedeSantiagodeCompostelaProgramadeDoutoramentoenMedioAmbienteeRecursosNaturais',
                     'UniversidadedeSantiagodeCompostelaProgramadeDoutoramentoenBiodiversidadeeConservacióndoMedioNatural',
                     'UniversidadedeSantiagodeCompostelaProgramadeDoutoramentoenCienciaeTecnoloxíaQuímica',
                     'UniversidadedeSantiagodeCompostelaProgramadeDoutoramentoenCienciasMariñasTecnoloxíaeXestión']
                                         
boringdegrees = []

if skipalreadyharvested:    
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

prerecs = []
for page in range(pages):
    tocurl = 'https://minerva.usc.es/xmlui/handle/10347/2291/discover?rpp=' + str(rpp) + '&etal=0&group_by=none&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for rec in ejlmod3.getdspacerecs(tocpage, 'https://minerva.usc.es', alreadyharvested=alreadyharvested):
        if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
            print('  skip',  rec['year'])
        else:
            prerecs.append(rec)
    time.sleep(2)

i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link'] + '?show=full'), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'citation_title', 'DCTERMS.issued',
                                        'DCTERMS.abstract', 'citation_pdf_url'])
    rec['autaff'][-1].append(publisher)
    #keywords
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_keywords'}):
        for keyw in re.split('[,;] ', meta['content']):
            if not re.search('^info.eu.repo', keyw):
                rec['keyw'].append(keyw)
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'ds-table-row'}):
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            tdt = td.text.strip()
            td.decompose()
        for td in tr.find_all('td'):
            if td.text.strip() == 'en_US':
                continue
            #supervisor
            if tdt == 'dc.contributor.advisor':
                rec['supervisor'] = [[ re.sub(' \(.*', '', td.text.strip()) ]]
            #discipline
            elif tdt == 'dc.contributor.affiliation':
                discipline = re.sub('\W', '', td.text.strip())
                if discipline in boringdisciplines:
                    print('  skip "%s"' % (discipline))
                    keepit = False
                else:
                    rec['note'].append(discipline)
            #degree
            elif tdt == 'dc.type':
                degree = td.text.strip()
                if degree in boringdegrees:
                    print('  skip "%s"' % (degree))
                    keepit = False
                else:
                    rec['note'].append(degree)
            #language
            elif tdt == 'dc.language.iso':
                if td.text.strip() == 'spa':
                    rec['language'] = 'spanish'
            #license
            elif tdt == 'dc.rights.uri':
                if re.search('creativecommons.org', td.text):
                    rec['license'] = {'url' : td.text.strip()}
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
