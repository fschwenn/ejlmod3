# -*- coding: utf-8 -*-
#harvest theses from Ulm
#JH: 2023-04-01
#FS: 2023-08-15
#FS: 2024-02-14

from bs4 import BeautifulSoup
from requests import Session
import time
import ejlmod3
import undetected_chromedriver as uc
import re
import os

rpp = 40
pages = 30
skipalreadyharvested = True

recs = []
prerecs = []
publisher = 'Ulm U.'
jnlfilename = 'THESES-ULM-%s' % (ejlmod3.stampoftoday())
boring = ['Institut für Theoretische Chemie', 'Institut für Analytische und Bioanalytische Chemie',
          'Institut für Anorganische Chemie II (Synthese und Charakterisierung anorganischer Materialien)',
          'Institut für Biochemie und Molekulare Biologie', 'Institut für Elektrochemie',
          'Institut für Medizinische Systembiologie', 'Institut für Mess-, Regel- und Mikrotechnik',
          'Institut für Nachrichtentechnik', 'Medizinische Fakultät', 'Bundeswehrkrankenhaus Ulm (BWK)',
          'International Graduate School in Molecular Medicine Ulm (IGradU)',
          'Institut für Organische Chemie III (Makromolekulare Chemie und Organische Materialien)',
          'Institut für Physiologische Chemie', 'Institut für Psychologie und Pädagogik',          
          'Zentrum für Sonnenenergie- und Wasserstoff-Forschung Baden-Württemberg (ZSW)',
          'Institut für Anatomie und Zellbiologie', 'Helmholtz-Institut Ulm',
          'Institut für Anorganische Chemie I (Materialien und Katalyse)', 'Institut für Biophysik',
          'Institut für Business Analytics', 'Institut für Controlling',
          'Institut für Energiewandlung und -speicherung',
          'Institut für Evolutionsökologie und Naturschutzgenomik', 'Institut für Finanzmathematik',
          'Institut für Funktionelle Nanosysteme', 'Institut für Medieninformatik',
          'Institut für Mikrobiologie und Biotechnologie', 'Institut für Chemieingenieurwesen',
          'Institut für Molekulare Genetik und Zellbiologie',
          'Institut für Nachhaltige Unternehmensführung', 'Institut für Neurobiologie',
          'Institut für Optimierung und Operations Research',
          'Institut für Organische Chemie II und Neue Materialien', 'Institut für Organische Chemie I',
          'Institut für Versicherungswissenschaften', 'Institut für Proteinbiochemie', 
          'UKU. Institut für Naturheilkunde und Klinische Pharmakologie',
          'UKU. Institut für Pharmakologie und Toxikologie',
          'UKU. Klinik für diagnostische und interventionelle Radiologie', 'UKU. Klinik für Neurochirurgie',
          'ZE Elektronenmikroskopie', 'Institut für Datenbanken und Informationssysteme',
          'Institut für Elektronische Bauelemente und Schaltungen',
          'Institut für Geschichte, Theorie und Ethik der Medizin', 'Institut für Molekulare Botanik',
          'Institut für Molekulare Endokrinologie der Tiere', 'Institut für Neuroinformatik',
          'Institut für Rechnungswesen und Wirtschaftsprüfung', 'Institut für Wirtschaftswissenschaften',
          'UKU. Abteilung für Gentherapie', 'UKU. Institut für Molekulare Virologie',
          'UKU. Institut für Virologie', 'UKU. Klinik für Frauenheilkunde und Geburtshilfe',
          'UKU. Klinik für Innere Medizin II', 'UKU. Klinik für Kinder- und Jugendmedizin',
          'UKU. Klinik für Innere Medizin I', 'Institut für Mikroelektronik',
          'Internationale Graduiertenschule für Molekulare Medizin',
          'Institut für Lasertechnologien in der Medizin und Meßtechnik an der Universität Ulm (ILM)',
          'Institut für Oberflächenchemie und Katalyse',
          'Institut für Organisation und Management von Informationssystemen',
          'Institut für Systematische Botanik und Ökologie',
          'UKU. Institut für Unfallchirurgische Forschung und Biomechanik',
          'UKU. Klinik für Kinder- und Jugendpsychiatrie/Psychotherapie',
          'UKU. Klinik für Orthopädie',
          'UKU. Klinik für Psychosomatische Medizin und Psychotherapie',
          'Institut für Pharmazeutische Biotechnologie',
          'Institut für Anorganische Chemie II', 'Institut für Eingebettete Systeme/Echtzeitsysteme',
          'Institut für Finanzwirtschaft', 'Institut für Mikro- und Nanomaterialien',
          'Institut für Optoelektronik', 'Institut für Strategische Unternehmensführung und Finanzierung',
          'Institut für Technologie- und Prozessmanagement', 'Institut für Wirtschaftspolitik',
          'Kompetenzzentrum "Ulm Peptide Pharmaceuticals (U-PEP)"',
          'Stabsstelle Zentrum für Lehrentwicklung (ZLE)', 'THU.IAF Institut für Angewandte Forschung',
          'Werkstoffe der Mikrotechnik']
boring += ['Institute of Molecular Biology and Biotechnology of Prokaryotes.',
           'Institut für Volkswirtschaftslehre', 'Medizinische Fakultät',
           'Medizinische Faultät']
boring += ['Abschlussarbeit (Master; Diplom)', 'Beitrag zu einer Konferenz',
           'Erratum', 'Wissenschaftlicher Artikel',
           'Abschlussarbeit (Bachelor)', 'Bewegte Bilder',
           'Forschungsdaten', 'Konferenzband',
           'Wissenschaftlicher Beitrag',
           'Zeitschriftenheft', 'Buch', 'Rezension']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)


baseurl = 'https://oparu.uni-ulm.de'
collection = 'fb3824de-4a02-44c0-a144-112baa4efa9e'



for page in range(pages):
    tocurl = baseurl + '/collections/' + collection + '?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
    tocurl = baseurl + '/search?query=&spc.page=' + str(page+1) + '&spc.sf=dc.date.issued&spc.sd=DESC&spc.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        time.sleep(10)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        time.sleep(10)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.author', 'dc.subject',
                                               'dc.subject.ddc', 'dc.subject.gnd',
                                               'dc.subject.lcsh', 'dc.title',
                                               'dc.type', 'dc.identifier.urn',
                                               'dc.date.issued', 'dc.identifier.doi',
                                               'dc.description.abstract', 'dc.language.iso',
                                               'uulm.affiliationGeneral',
                                               'uulm.affiliationSpecific',
                                               'dc.subject.mesh',
                                               'uulm.dissISBN'], boring=boring, alreadyharvested=alreadyharvested):
        if 'autaff' in rec and rec['autaff']:
            rec['autaff'][-1].append(publisher)
        else:
            rec['autaff'] = [[ 'Dee, John' ]] 
        ejlmod3.printrecsummary(rec)
        #print(rec['thesis.metadata.keys'])
        recs.append(rec)
    print('  %i records so far' % (len(recs)))
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)





