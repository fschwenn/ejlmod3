# -*- coding: utf-8 -*-
#harvest theses from Ulm
#JH: 2023-04-01
#FS: 2023-08-15

from bs4 import BeautifulSoup
from requests import Session
from time import sleep
import ejlmod3


rpp = 50
pages = 10
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

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

with Session() as session:
    for page in range(pages):
        tocurl = 'https://oparu.uni-ulm.de/xmlui/browse?rpp=' + str(rpp) + '&offset=' + str(rpp*page) + '&etal=-1&sort_by=2&type=resourcetype&value=Dissertation&order=DESC'
        ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
        page_resp = session.get(tocurl)

        if page_resp.status_code != 200:
            print("# Error: Can't reach site:", tocurl)
            continue

        prerecs += ejlmod3.getdspacerecs(BeautifulSoup(page_resp.content.decode('utf-8'), 'lxml'), 'https://oparu.uni-ulm.de', fakehdl=True)
        sleep(10)
        print('  %4i records so far' % (len(prerecs)))
        
for (i, rec) in enumerate(prerecs):
    keepit = True
    ejlmod3.printprogress('-', [[i+1, len(prerecs)], [rec['link']], [len(recs)]])
    if not ejlmod3.checkinterestingDOI(rec['link']):
        continue
    try:
        article_resp = session.get(rec['link'] + '?show=full')
        if article_resp.status_code != 200:
            print("# Error: Can't reach site:", rec.get('link'))
            continue
        article_soup = BeautifulSoup(article_resp.content.decode('utf-8'), 'lxml')
    except:
        sleep(30)
        article_resp = session.get(rec['link'] + '?show=full')
        if article_resp.status_code != 200:
            print("# Error: Can't reach site:", rec.get('link'))
            continue
        article_soup = BeautifulSoup(article_resp.content.decode('utf-8'), 'lxml')
        
    sleep(6)
    # Get the faculty
    faculty = article_soup.find_all('b', string='Fakultät')
    if len(faculty) == 1:
        row = faculty[0].parent.parent.parent
        cols = row.find_all('td')
        rec['note'] = ["Faculty: " + cols[1].text]
    # Get the institution
    for tr in article_soup.find_all('tr'):
        tds = tr.find_all('td')
        if tds:
            tdt = tds[0].text.strip()
            if tdt in ['Fakultät', 'Faculty']:
                fac = tds[1].text.strip()
                if fac in boring:
                    keepit = False
                elif not fac in ['Fakultät für Mathematik und Wirtschaftswissenschaften',
                                 'Fakultät für Naturwissenschaften']:
                    rec['note'].append('FAC:::' + fac)
            elif tdt == 'Institution':
                ins = tds[1].text.strip()
                if ins in boring:
                    keepit = False
                elif ins in ['Institut für Algebra und Zahlentheorie',
                             'Institut für Angewandte Analysis',
                             'Institut für Numerische Mathematik',
                             'Institut für Analysis', 'Institut für Statistik',
                             'Institut für Stochastik',
                             'Institut für Reine Mathematik',
                             'Institut für Zahlentheorie und Wahrscheinlichkeitstheorie']:
                    rec['fc'] = 'm'
                elif ins in ['Institut für Festkörperphysik']:
                    rec['fc'] = 'f'
                elif ins in ['Institut für Quantenphysik']:
                    rec['fc'] = 'k'
                elif ins in ['Institut für Softwaretechnik und Programmiersprachen',
                             'Institut für Theoretische Informatik',
                             'THU.IFI Institut für Informatik']:
                    rec['fc'] = 'c'
                elif not ins in ['Institut für Experimentelle Physik',
                                 'Institut für Komplexe Quantensysteme',
                                 'Institut für Theoretische Physik',
                                 'Institut für Verteilte Systeme',
                                 'Institut für Mikrowellentechnik', 'Sonstige',
                                 'Institut für Quantenoptik', 'Institut für Quantenmaterie',
                                 'Universität Ulm', 'Institut für Künstliche Intelligenz']:
                    rec['note'].append('INS:::' + ins)
    if keepit:
        ejlmod3.metatagcheck(rec, article_soup, ["DC.creator", "DCTERMS.issued", "DCTERMS.abstract",
                                                 "DC.language", "DC.rights", "DC.subject", "DC.title",
                                                 "citation_doi", "citation_pdf_url"])
        if not skipalreadyharvested or not 'doi' in rec or not rec['doi'] in alreadyharvested:
            rec['autaff'][-1].append(publisher)
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
