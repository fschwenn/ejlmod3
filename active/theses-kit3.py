# -*- coding: utf-8 -*-
#program to harvest theses from Karlsruhe Insitute of Technolgy
# FS 2020-01-13

import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import time 
import undetected_chromedriver as uc
import os

publisher = 'KIT, Karlsruhe'
jnlfilename = 'THESES-KIT-%s' % (ejlmod3.stampoftoday())
pages = 20#+180
years = 2#+8
skipalreadyharvested = True
boring = ['Fakultät für Geistes- und Sozialwissenschaften (GEISTSOZ)', 'Institut für Kolbenmaschinen (IFKM)',
          'Institut für Technik der Informationsverarbeitung (ITIV)', 'Institut für Nukleare Entsorgung (INE)',
          'Institut für Organische Chemie (IOC)', 'Institut für Telematik (TM)',
          '3D Matter Made to Order (3DMM2O)Institut für Funktionelle Grenzflächen (IFG)',
          'Fakultät für Chemieingenieurwesen und Verfahrenstechnik (CIW)',
          'Fakultät für Chemie und Biowissenschaften (CHEM-BIO)',
          'Fakultät für Wirtschaftswissenschaften (WIWI)', 'Institut für Volkswirtschaftslehre (ECON)',
          'Institut für Angewandte Biowissenschaften (IAB)KIT-Bibliothek (BIB)',
          'Institut für Angewandte Biowissenschaften (IAB)', 'Institut für Anthropomatik und Robotik (IAR)',
          'Institut für Biomedizinische Technik (IBT)', 'Institut für Bio- und Lebensmitteltechnik (BLT)',
          'Institut für Finanzwirtschaft, Banken und Versicherungen (FBV)',
          'Institut für Funktionelle Grenzflächen (IFG)',  'Institut für Produktionstechnik (WBK)',
          'Institut für Industrielle Informationstechnik (IIIT)',
          'Institut für Regelungs- und Steuerungssysteme (IRS)',
          'Institut für Technische Chemie und Polymerchemie (ITCP)',
          'Institut für Technische Thermodynamik und Kältetechnik (TTK)',
          'Institut für Thermische Verfahrenstechnik (TVT)',
          'Fakultät für Bauingenieur-, Geo- und Umweltwissenschaften (BGU)',
          'Fakultät für Elektrotechnik und Informationstechnik (ETIT)', 'Fakultät für Maschinenbau (MACH)',
          'Institut für Angewandte Materialien – Werkstoffkunde (IAM-WK)', 'Institut für Hydromechanik (IFH)']
boring += ['Fakultät für Architektur (ARCH)', 'Geophysikalisches Institut (GPI)', 'Institut Entwerfen und Bautechnik (IEB)',
           'Institut für Anthropomatik und Robotik (IAR)Zentrum für digitale Barrierefreiheit und Assistive Technologien (ACCESS@KIT)',
           'Institut für Entwerfen Kunst und Theorie (EKUT)', 'Institut für Geographie und Geoökologie (IFGG)',
           'Institut für Meteorologie und Klimaforschung – Atmosphärische Spurenstoffe und Fernerkundung (IMK-ASF)Institut für Meteorologie und Klimaforschung Troposphärenforschung (IMKTRO)',
           'Institut für Meteorologie und Klimaforschung – Atmosphärische Spurenstoffe und Fernerkundung (IMK-ASF)',
           'Institut für Meteorologie und Klimaforschung Troposphärenforschung (IMKTRO)Institut für Stochastik (STOCH)',
           'Institut für Meteorologie und Klimaforschung Troposphärenforschung (IMKTRO)',
           'Institut für Wasser und Umwelt (IWU)Scientific Computing Center (SCC)',
           'Troposphärische Messkampagnen und Modellentwicklung (IMKTRO-T)',
           'Institut für Technische Chemie (ITC)', 'Institut für Verkehrswesen (IFV)',
           'Institut Kunst- und Baugeschichte (IKB)',
           'Institut für Angewandte Geowissenschaften (AGW)',
           'Institut für Angewandte Informatik und Formale Beschreibungsverfahren (AIFB)',
           'Institut für Angewandte Materialien – Computational Materials Science (IAM-CMS)',
           'Institut für Angewandte Materialien – Keramische Werkstoffe und Technologien (IAM-KWT1)',
           'Institut für Angewandte Materialien - Werkstoff- und Biomechanik (IAM-WBM)',
           'Fraunhofer-Institut für Optronik, Systemtechnik und Bildauswertung (IOSB)',
           'Zentrum für digitale Barrierefreiheit und Assistive Technologien (ACCESS@KIT)']

options = uc.ChromeOptions()
options.binary_location='/usr/bin/google-chrome'
#options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

host = os.uname()[1]
if host == 'l00schwenn':
    tmpdir = '/home/schwenn/tmp'
else:
    tmpdir = '/afs/desy.de/user/l/library/tmp'
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
prerecs = []
for page in range(pages):
    tocurl = 'https://primo.bibliothek.kit.edu/primo-explore/search?query=any,contains,*&tab=kit&sortby=date&vid=KIT&facet=local8,include,istHochschulschrift&mfacet=local3,include,istFachPhys,1&mfacet=local3,include,istFachMath,1&mode=simple&offset=' + str(10*page) + '&fn=search'
    tocurl = 'https://primo.bibliothek.kit.edu/primo-explore/search?query=any,contains,*&tab=kit&sortby=date&vid=KIT&facet=rtype,include,dissertations&mfacet=local3,include,istFachPhys,1&mfacet=local3,include,istFachMath,1&mode=simple&offset=' + str(10*page) + '&fn=search'
    tocurl = 'https://primo.bibliothek.kit.edu/primo-explore/search?query=any,contains,Hochschulschrift,AND&pfilter=creationdate,exact,2-YEAR,AND&tab=kit_evastar&search_scope=KIT_Evastar&vid=KIT&facet=local8,include,istDissertation&mode=advanced&offset=' + str(10*page) + '&came_from=sort'

    tocurl = 'https://primo.bibliothek.kit.edu/primo-explore/search?query=any,contains,Hochschulschrift,AND&pfilter=creationdate,exact,' + str(years) + '-YEAR,AND&tab=kit_evastar&search_scope=KIT_Evastar&sortby=date&vid=KIT&facet=local8,include,istDissertation&mode=advanced&offset=' + str(10*page) # + '&came_from=pagination_2_4'
    
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    newrecs = []
    try:
        driver.get(tocurl)
        time.sleep(15)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(4)
    except:
        print("retry %s in 300 seconds" % (tocurl))
        time.sleep(300)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    for div in tocpage.find_all('div', attrs = {'class' : 'list-item-wrapper'}):
        for div2 in div.find_all('div', attrs = {'class' : 'list-item-primary-content'}):
            rec = {'jnl' : 'BOOK', 'tc' : 'T', 'note' : [], 'keyw' : [], 'supervisor' : []}
            rec['data-recordid'] = div2['data-recordid']
            rec['artlink'] = 'https://primo.bibliothek.kit.edu/primo-explore/fulldisplay?docid=' + div2['data-recordid']+ '&context=L&vid=KIT&lang=de_DE'
            rec['artlink'] = 'https://primo.bibliothek.kit.edu/permalink/f/dirnb3/' + div2['data-recordid']
            if ejlmod3.checkinterestingDOI(rec['artlink']):
                prerecs.append(rec)
            else:
                print('   %s already known to be uninteresting' % (rec['data-recordid']))
    print('   %i records so far\n' % (len(prerecs)))

i = 0
recs = []
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    isbns = []
    htmlfilename = tmpdir + '/kit' + re.sub('\W', '', rec['artlink'])
    if os.path.isfile(htmlfilename):
        inf = open(htmlfilename, 'r')
        lines = inf.readlines()
        inf.close()
        artpage = BeautifulSoup(''.join(lines), features="lxml")
    else:
        try:
            driver.get(rec['artlink'])
            time.sleep(6)
            artpage = BeautifulSoup(driver.page_source, features="lxml")
            time.sleep(4)
        except:
            print("retry %s in 300 seconds" % (tocurl))
            time.sleep(300)
            driver.get(rec['artlink'])
            time.sleep(4)        
            artpage = BeautifulSoup(driver.page_source, features="lxml")
        ouf = open(htmlfilename, 'w')
        ouf.write(artpage.prettify())
        ouf.close()
    #title
    for div in artpage.body.find_all('div', attrs = {'id' : 'kitopen_primo_titel'}):
        rec['tit'] = div.text.strip()
    #author
    for div in artpage.body.find_all('div', attrs = {'id' : 'KIT_KITopen_allauthors'}):
        for span in div.find_all('span'):
            for sup in span.find_all('sup'):
                sup.decompose()
            if not 'autaff' in rec:
                rec['autaff'] = [[ span.text.strip() ]]
                for a in div.find_all('a'):
                    if a.has_attr('href') and re.search('orcid\.org', a['href']):
                        rec['autaff'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', a['href']))
#            else:
#                rec['autaff'][-1].append([ span.text.strip() ])
#    if len(rec['autaff']) == 1:
        rec['autaff'][-1].append(publisher)

    for div in artpage.body.find_all('div', attrs = {'class' : 'layout-block-xs'}):
        for span in div.find_all('span', attrs = {'class' : 'bold-text'}):
            spant = span.text.strip()
        for div2 in div.find_all('div', attrs = {'class' : 'ng-binding'}):
            #institut
            if spant in ['Zugehörige Institution(en) am KIT', 'Fakultät', 'Institut'] and not 'fc' in rec:
                institut = div2.text.strip()
                if institut in ['Institut für Angewandte und Numerische Mathematik (IANM)',
                                'Institut für Algebra und Geometrie (IAG)',
                                'Institut für Analysis (IANA)',
                                'Fakultät für Mathematik (MATH)']:
                    rec['fc'] = 'm'
                elif institut in ['Institut für Astroteilchenphysik (IAP)']:
                    rec['fc'] = 'a'
                elif institut in ['Institut für Angewandte Physik (APH)']:
                    rec['fc'] = 'q'
                elif institut in ['Institut für Theorie der Kondensierten Materie (TKM)',
                                  'Institut für Theoretische Festkörperphysik (TFP)']:
                    rec['fc'] = 'f'
                elif institut in ['Institut für Quantenmaterialien und -technologien (IQMT)',
                                  'Institut für QuantenMaterialien und Technologien (IQMT)']:
                    rec['fc'] = 'k'
                elif institut in ['Institut für Experimentelle Teilchenphysik (ETP)']:
                    rec['fc'] = 'e'
                elif institut in ['Institut für Informationssicherheit und Verlässlichkeit (KASTEL)',
                                  'Institut für Programmstrukturen und Datenorganisation (IPD)',
                                  'Institut für Theoretische Informatik (ITI)']:
                    rec['fc'] = 'c'
                elif institut in ['Institut für Theoretische Teilchenphysik (TTP)']:
                    rec['fc'] = 'tp'
                elif institut in ['Fakultät für Informatik (INFORMATIK)',
                                  'Institut für Angewandte Informatik und Formale Beschreibungsverfahren (AIFB)',
                                  'Fakultät für Informatik (INFORMATIK)',
                                  'Institut für Technische Informatik (ITEC)',
                                  'Institut für Programmstrukturen und Datenorganisation (IPD)',
                                  'Institut für Automation und angewandte Informatik (IAI)',
                                  'Institut für Theoretische Informatik (ITI)']:
                    rec['fc'] = 'c'
                elif institut in boring:
                    keepit = False
                    print('   skip "%s"' % (institut))
                elif not institut in ['Fakultät für Physik (PHYSIK)', 'Physikalisches Institut (PHI)',
                                      'Institut für Theoretische Physik (ITP)',
                                      'Institut für Angewandte Physik (APH)']:
                    rec['note'].append('INST:::'+institut)
            #language
            if spant in ['Sprache']:
                lang = div2.text.strip()
                if lang == 'Deutsch':
                    rec['language'] = 'German'
                elif lang != 'Englisch':
                    rec['note'].append('LANG:::' + lang)
            #pages
            if spant in ['Umfang']:
                umfang = div2.text.strip()
                if re.search('\d\d', umfang):
                    rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', umfang)
            #date
            if spant in ['Prüfungsdatum']:
                rec['date'] = div2.text.strip()
            elif spant in ['Publikationsdatum']:
                rec['date'] = div2.text.strip()
            elif spant in ['Publikationsjahr']:
                rec['year'] = div2.text.strip()
            #supervisor
            if spant in ['Referent/Betreuer']:
                for br in div2.find_all('br'):
                    br.replace_with('XXX')
                for sv in re.split('XXX', re.sub('[\n\t\r]', '', div2.text.strip())):
                    rec['supervisor'].append([ sv ])
    #PID
    for span in artpage.body.find_all('span', attrs = {'id' : 'hiddenId'}):
        for a in span.find_all('a'):
            if a.has_attr('href') and re.search('doi\.org', a['href']):
                rec['doi'] = re.sub('.*doi.org\/', '', a['href'])
    if not 'doi' in rec:
        for div in artpage.body.find_all('div', attrs = {'class' : 'landingpage-panel-body'}):
            #for div2 in div.find_all('div', attrs = {'class' : 'small_darkgrey_on_lightgrey'}):
            for div2 in div.find_all('div'):
                div2t = re.sub('[\n\t\r]', ' ', div2.text.strip())
                if re.search('DOI.*10\.\d+\/', div2t):
                    rec['doi'] = re.sub(' .*', '', re.sub('.*(10\.\d+\/.*)', r'\1', div2t))
                    


                
    if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        print('   already in backup')
        continue
    if keepit and 'doi' in rec:
        if re.search('^10.5445', rec['doi']):
            print('   checking primo-page')
            try:
                time.sleep(10)
                artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open('https://doi.org/'+rec['doi']), features="lxml")
            except:
                try:
                    print("retry %s in 180 seconds" % ('https://doi.org/'+rec['doi']))
                    time.sleep(180)
                    artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open('https://doi.org/'+rec['doi']), features="lxml")
                except:
                    pass
            for meta in artpage.head.find_all('meta'):
                if meta.has_attr('name'):
                    #abstract
                    if meta['name'] == 'citation_abstract':
                        rec['abs'] = meta['content']
                    #ISBN
                    elif meta['name'] == 'citation_isbn':
                        isbn = re.sub('\-', '', meta['content'])
                        if not isbn in isbns:
                            isbns.append(isbn)
                    #fulltext
                    elif meta['name'] == 'citation_pdf_url':
                        rec['FFT'] = meta['content']
            for table in artpage.body.find_all('table', attrs = {'class' : 'table'}):
                for tr in table.find_all('tr'):
                    tds = tr.find_all('td')
                    if len(tds) == 2:
                        tht = tds[0].text.strip()
                        #Keywords
                        if re.search('Schlagw', tht):
                            for keyw in re.split(', ', tds[1].text.strip()):
                                if not keyw in rec['keyw']:
                                    rec['keyw'].append(keyw)
                        #Language
                        elif tht == 'Sprache':
                            if tds[1].text.strip() != 'Englisch':
                                if tds[1].text.strip() == 'Deutsch':
                                    rec['language'] = 'german'
                                else:
                                    rec['language'] = tds[1].text.strip()
                        #pages
                        elif tht == 'Umfang':
                            if re.search('\d\d\d', tds[1].text.strip()):
                                rec['pages'] = re.sub('.*?(\d\d\d+).*', r'\1', tds[1].text.strip())
                        #supervisor
                        elif re.search('Betreuer', tds[0].text):
                            if not rec['supervisor']:
                                for br in tds[1].find_all('br'):
                                    br.replace_with(';;;')
                                    for sv in re.split(' *;;; *', tds[1].text.strip()):
                                        rec['supervisor'].append([ re.sub('Prof\. ', '', re.sub('Dr\. ', '', sv)) ])
                        #date
                        elif re.search('Pr.fungsdatum', tds[0].text):
                            rec['MARC'] = [ ['500', [('a', 'Presented on ' + re.sub('(\d\d).(\d\d).(\d\d\d\d)', r'\3-\2-\1', tds[1].text.strip()))] ] ]
                        #institue
                        elif tht == 'Institut':
                            if not 'fc' in rec:
                                institut = tds[1].text.strip()
                                if institut in ['Institut für Angewandte und Numerische Mathematik (IANM)',
                                                'Institut für Algebra und Geometrie (IAG)',
                                                'Institut für Analysis (IANA)']:
                                    rec['fc'] = 'm'
                                elif institut in ['Institut für Astroteilchenphysik (IAP)']:
                                    rec['fc'] = 'a'
                                elif institut in ['Institut für Theorie der Kondensierten Materie (TKM)']:
                                    rec['fc'] = 'f'
                                elif institut in ['Institut für Quantenmaterialien und -technologien (IQMT)']:
                                    rec['fc'] = 'k'
                                elif institut in ['Institut für Experimentelle Teilchenphysik (ETP)']:
                                    rec['fc'] = 'e'
                                elif institut in ['Institut für Theoretische Teilchenphysik (TTP)']:
                                    rec['fc'] = 'tp'
                                elif institut in boring:
                                    keepit = False
                                    print('   skip "%s"' % (institut))
                                else:
                                    rec['note'].append('INST:::'+institut)
                                    #urn
                            elif tht == 'Identifikator':
                                for br in tds[1].find_all('br'):
                                    br.replace_with('#')
                                    for tdt in re.split('#',  re.sub('[\n\t\r]', '#', tds[1].text.strip())):
                                        if re.search('urn:nbn', tdt):
                                            rec['urn'] = re.sub('.*?(urn:nbn.*)', r'\1', tdt.strip())
                                            #anmerkung
                                        elif tht == 'Art der Arbeit':
                                            anmerkung = tds[1].text.strip()
                                            if re.search('(Master|Bachelor)', anmerkung):
                                                keepit = False
                                                print('   skip "%s"' % (anmerkung))
                                            elif anmerkung != 'Dissertation':
                                                rec['note'].append(anmerkung)
                                                #license
            for a in artpage.body.find_all('a', attrs = {'class' : 'with-popover'}):
                if a.has_attr('data-content'):
                    adc = a['data-content']
                    if re.search('creativecommons.org', adc):
                        rec['license'] = {'url' : re.sub('.*(http.*?) target.*', r'\1', adc)}
            #english abstract
            for div in artpage.body.find_all('div', attrs = {'id' : 'KIT_KITopen_abstract_eng'}):
                for span in div.find_all('span', attrs = {'class' : 'kit_link_on_white_background'}):
                    span.decompose()
                    rec['abs'] = div.text.strip()
    else:
        rec['doi'] = '20.2000/KIT/'+rec['data-recordid']
        rec['link'] = rec['artlink']
        print('  ! ', rec['doi'])
    if isbns:
        rec['isbns'] = []
        for isbn in isbns:
            rec['isbns'].append([('a', isbn)])            
    if keepit:
        ejlmod3.printrecsummary(rec)
        #ejlmod3.printrec(rec)
        if 'autaff' in rec: recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
driver.quit()
