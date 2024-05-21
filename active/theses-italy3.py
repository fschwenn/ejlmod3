# -*- coding: utf-8 -*-
#harvest theses from different italian universities
#FS: 2020-02-20
#
#repository not very up-to-date

import sys
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import os
import undetected_chromedriver as uc

years = 2
rpp = 20
skipalreadyharvested = True

universities = {'milanbicocca' : ('Milan Bicocca U.', 'https://boa.unimib.it', '/handle/10281/9145', 8),
                'trento' : ('Trento U.', 'https://iris.unitn.it', '/handle/11572/237822', 10),
                'pavia' : ('Pavia U.', 'https://iris.unipv.it', '/handle/11571/1198268', 10),
                'turinpoly' : ('Turin Polytechnic', 'https://iris.polito.it', '/handle/11583/2614423', 10),
                'milan' : ('Milan U.', 'https://air.unimi.it', '/handle/2434/146884', 20),
                'udine' : ('Udine U.', 'https://air.uniud.it', '/handle/11390/1123314', 7),
                'genoa' : ('Genoa U.', 'https://iris.unige.it', '/handle/11567/928192', 15),
                'ferraraeprints' : ('Ferrara U.', 'https://iris.unife.it', '/handle/11392/2380873', 2),
                'ferrara' : ('Ferrara U.', 'https://iris.unife.it', '/handle/11392/2380872', 4),
                'trieste' : ('Trieste U', 'https://arts.units.it', '/handle/11368/2907477', 10),
                'siena' : ('Siena U.', 'https://usiena-air.unisi.it', '/handle/11365/973085', 5),
                'verona' : ('Verona U.', 'https://iris.univr.it', '/handle/11562/924246', 7),
                'cagliari' : ('Cagliari U.', 'https://iris.unica.it', '/handle/11584/207612', 8),
                'sns' : ('Pisa, Scuola Normale Superiore', 'https://ricerca.sns.it', '/handle/11384/78634', 5),
                'sissa' : ('SISSA', 'https://iris.sissa.it', '/handle/20.500.11767/64', 6),
                'cagliarieprints' : ('Cagliari U.', 'https://iris.unica.it', '/handle/11584/265854', 8),
                'parma' : ('Parma U.', 'https://www.repository.unipr.it', '/handle/1889/636', 1),
                'modena' : ('Modena U.', 'https://iris.unimore.it', '/handle/11380/1196085', 7),
                'messina' : ('Messina U.', 'https://iris.unime.it', '/handle/11570/3101346', 5),
                'florence' : ('U. Florence (main)', 'https://flore.unifi.it', '/handle/2158/1001453', 20-15),
                'aquila' : ('U. Aquila (main)', 'https://ricerca.univaq.it', '/handle/11697/143427', 3), #neu 9
                'padua' : ('U. Padua (main)', 'https://www.research.unipd.it', '/handle/11577/3394917', 20)}
boring = ['archeologia medievale', 'beni architettonici e paesaggistici', 'bio',
          'biochemistry and molecular biology bibim 2.0', 'bioingegneria e scienze medico-chirurgiche',
          'biomolecular sciences', 'biotecnologie mediche', 'chemical and pharmaceutical sciences', 'chim',
          'civil, environmental and mechanical engineering', 'cognitive and brain sciences', 'cognitive science',
          'development economics and local systems - delos',
          'dipartimento di studi letterari, filologici e linguistici', 'economia e management', 'economics',
          'economics and management', 'energetica', 'environmental engineering',
          'european cultures. environment, contexts, histories, arts, ideas', u'facolt\xe0 di giurisprudenza',
          'filologia e critica', 'genetica, oncologia e medicina clinica', 'geo', 'gestione, produzione e design',
          'ing-ind', 'ing-inf', 'ingegneria aerospaziale', 'ingegneria chimica', 'ingegneria civile e ambientale',
          'international studies', 'ius', 'l-ant', 'l-art', 'l-fil-let', 'l-lin', 'l-or', 'lettere e filosofia', 'm-dea', 'm-edf', 'm-fil', 'm-ggr',
          'm-ped', 'm-psi', 'm-sto', 'materials, mechatronics and systems engineering', 'med',
          'medicina molecolare', 'metrologia', 'psicologia e scienze cognitive',
          'psychological sciences and education', 'scienza politica - politica comparata ed europea',
          'scienze chimiche e farmaceutiche', 'scienze del testo letterario e musicale',
          "scienze della terra e dell'ambiente", 'scienze della vita', 'scienze della vita-life sciences',
          'scienze giuridiche', 'scienze linguistiche', 'scuola di studi internazionali', 'secs-p',
          'sociologia e ricerca sociale', 'sociology and social research', 'storia',
          'tecnologie per la salute, bioingegneria e bioinformatica', 'urban and regional development']
boring += ['scienze e tecnologie della chimica e dei materiali - drug discovery and nanobiotechnologies',
           'scienze e tecnologie della chimica e dei materiali - nanochemistry',
           'scienze e tecnologie della chimica e dei materiali - scienza e tecnologia dei materiali',
           'bioingegneria e robotica - bioengineering and robotics - bionanotechnology',
           'bioingegneria e robotica - bioengineering and robotics', 'icar', 'agr',
           'biotecnologie in medicina traslazionale - medicina rigenerativa ed ingegneria dei tessuti']
regsec = re.compile('^([a-z]+\-?[a-z]+\-?[a-z]+)\/\d+ .*')
uni = sys.argv[1]
publisher = universities[uni][0]
pages = universities[uni][3]
jnlfilename = 'THESES-%s-%s' % (uni.upper(), ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []


options = uc.ChromeOptions()
#options.binary_location='/usr/bin/chromium'
options.binary_location='/usr/bin/google-chrome'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

    
hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
driver.get(universities[uni][1])
time.sleep(10)
for page in range(pages):
    tocurl = '%s%s?offset=%i&sort_by=-1&order=DESC' % (universities[uni][1], universities[uni][2], (page)*rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    #req = urllib.request.Request(tocurl, headers=hdr)
    #tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    driver.get(tocurl)
    tocpage = BeautifulSoup(driver.page_source, features="lxml")

    recsfound = False
    for tr in tocpage.body.find_all('tr'):
        rec = False
        for td in tr.find_all('td', attrs = {'headers' : 't1'}):
            for a in td.find_all('a'):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : []}
                rec['artlink'] = universities[uni][1] + a['href'] + '?mode=full.716'
                rec['hdl'] = re.sub('.*handle\/', '', a['href'])
        if not rec:
            for td in tr.find_all('td', attrs = {'headers' : 't3'}):
                for a in td.find_all('a'):
                    rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : []}
                    rec['artlink'] = universities[uni][1] + a['href'] + '?mode=full.716'
                    rec['hdl'] = re.sub('.*handle\/', '', a['href'])
        if not rec:
            for td in tr.find_all('td'):
                for a in td.find_all('a'):
                    if a.has_attr('href') and re.search('handle\/\d+', a['href']):
                        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : []}
                        rec['hdl'] = re.sub('.*handle\/(\d+\/\d+).*', r'\1', a['href'])
                        rec['artlink'] = universities[uni][1] +'/handle/' + rec['hdl'] + '?mode=full.716'                    
        if rec:
            recsfound = True
            tds = tr.find_all('td', attrs = {'headers' : 't2'})
            if tds:
                for td in tds:
                    if re.search('[12]\d\d\d', td.text):
                        rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', re.sub('[\n\t\r]', '', td.text.strip()))
                        if int(rec['year']) >= ejlmod3.year(backwards=years):
                            if ejlmod3.checkinterestingDOI(rec['hdl']):
                                if rec['hdl'] in alreadyharvested:
                                    print('    %s already in backup' % (rec['hdl']))
                                else:
                                    prerecs.append(rec)
                        else:
                            print('    %s too old (%s)' % (rec['hdl'], rec['year']))                        
                    elif ejlmod3.checkinterestingDOI(rec['hdl']):
                        print('(YEAR?)', td.text)
                        if rec['hdl'] in alreadyharvested:
                            print('    %s already in backup' % (rec['hdl']))
                        else:
                            prerecs.append(rec)
            elif ejlmod3.checkinterestingDOI(rec['hdl']):
                if rec['hdl'] in alreadyharvested:
                    print('    %s already in backup' % (rec['hdl']))
                else:
                    prerecs.append(rec)
    if not recsfound:
        for a in tocpage.find_all('a', attrs = {'class' : 'list-group-item-action'}):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : []}
            rec['artlink'] = universities[uni][1] + a['href']
            rec['hdl'] = re.sub('.*handle\/', '', a['href'])
            for p in a.find_all('p'):
                if re.search('[12]\d\d\d', p.text):
                    rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', re.sub('[\n\t\r]', '', p.text.strip()))
                    if int(rec['year']) >= ejlmod3.year(backwards=years):
                        if ejlmod3.checkinterestingDOI(rec['hdl']):
                            if rec['hdl'] in alreadyharvested:
                                print('    %s already in backup' % (rec['hdl']))
                            else:
                                prerecs.append(rec)
                    else:
                        print('    %s too old (%s)' % (rec['hdl'], rec['year']))
                else:
                    print('(YEAR?)', p.text)
    print('     %3i records so far' % (len(prerecs)))
    time.sleep(5)

i = 0
recs = []
for rec in prerecs:
    interesting = True
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    if not ejlmod3.checkinterestingDOI(rec['hdl']):
        continue
    try:
        #artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink'] + '?mode=complete'), features="lxml")
        driver.get(rec['artlink'] + '?mode=complete')
        artpage = BeautifulSoup(driver.page_source, features="lxml")
        time.sleep(7)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_author_email', 'citation_author_orcid', 'citation_pdf_url', 'citation_doi',
                                        'citation_title', 'citation_publication_date', 'citation_language', 'DC.subject', 'citation_keywords',
                                        'citation_date', 'DC.identifier', 'DC.description'])
    for meta in artpage.find_all('meta'):
        if meta.has_attr('name') and meta.has_attr('content'):
            #pages
            if meta['name'] == 'citation_lastpage':
                if re.search('^\d+$', meta['content']):
                    rec['pages'] = meta['content']
            #abstract
            elif meta['name'] == 'DCTERMS.abstract':
                if re.search(' (the|of|and) ', meta['content']):
                    rec['abs'] = meta['content']
            #thesis type
            #elif meta['name'] == 'DC.type':
            #    if len(meta['content']) > 5:
            #        rec['note'].append(meta['content'])
            #department
            elif meta['name'] in ['DC.subject', 'citation_keywords']:
                section = re.sub('Settore ', '', meta['content'])
                if re.search('^[A-Z]+\-?[A-Z]+\-?[A-Z]+\/\d+', section):
                    interesting = False
                    if section[:3] in ['FIS', 'INF', 'ING', 'MAT']:
                        if section[:3] == 'INF':
                            rec['fc'] = 'c'
                        elif section[:3] == 'MAT':
                            rec['fc'] = 'm'
                        rec['note'].append(section)
                        interesting = True
                    else:
                        print('  skip', section)
    if not 'autaff' in rec:
        for meta in artpage.find_all('meta', attrs = {'name' : 'DC.creator'}):
            rec['autaff'] = [[ meta['content'] ]]
    # :( meta-tags now hidden in JavaScript
    #print(artpage.text)

    for table in artpage.body.find_all('table', attrs = {'class' : 'itemTagFields'}):
        for tr in table.find_all('tr'):
            for td in tr.find_all('td', attrs = {'class' : 'metadataFieldLabel'}):
                tdlabel = td.text.strip()
            for td in tr.find_all('td', attrs = {'class' : 'metadataFieldValue'}):
                #author
                if re.search('^Autori', tdlabel):
                    if not 'autaff' in rec:
                        rec['autaff'] = [[td.text.strip()]]
                #supervisor
                elif re.search('^Tutore', tdlabel):
                    if not 'supervisor' in rec:
                        rec['supervisor'] = [[td.text.strip()]]
                #title
                elif re.search('^Titolo', tdlabel):
                    if not 'tit' in rec:
                        rec['tit'] = td.text.strip()
                #date
                elif re.search('^Data di', tdlabel):
                    if not 'date' in rec:
                        rec['date'] = re.sub('.*(\d\d\d\d).*', r'\1', td.text.strip())
                #abstract
                elif re.search('^Abstract', tdlabel):
                    if not 'abs' in rec:
                        if re.search(' the ', td.text):
                            rec['abs'] = td.text.strip()
                #language
                elif re.search('^Lingua', tdlabel):
                    if not 'language' in rec:
                        if re.search('Ital', td.text.strip()):
                            rec['language'] = 'italian'
                #keywords
                elif re.search('^Parole.*Inglese', tdlabel):
                    if not 'keyw' in rec:
                        rec['keyw'] = re.split('; ', td.text.strip())
                #section
                elif re.search('^Settore', tdlabel):
                    section = re.sub('Settore ', '', td.text.strip())
                    if re.search('^[A-Z][A-Z][A-Z]', section):
                        interesting = False
                        if section[:3] in ['FIS', 'INF', 'ING', 'MAT']:
                            if section[:3] == 'INF':
                                rec['fc'] = 'c'
                            elif section[:3] == 'MAT':
                                rec['fc'] = 'm'
                            elif section[:6] == 'FIS/05':
                                rec['fc'] = 'a'
                            rec['note'].append(td.text.strip())
                            interesting = True
                        else:
                            print('  skip', section)
                    elif section in ['med/01', 'med/04', 'med/07', 'med/08', 'med/09', 'med/11', 'med/12', 'med/13', 'med/15',
                                     'med/16', 'med/26', 'med/27', 'med/28', 'med/30', 'med/31', 'med/33', 'med/36', 'med/38',
                                     'med/41', 'med/42', 'med/45', 'l-ant/01', 'l-ant/02', 'l-ant/03', 'l-ant/05', 'l-ant/06',
                                     'l-ant/07', 'l-ant/08', 'l-art/01', 'l-art/02', 'l-art/03', 'l-art/04', 'l-art/05',
                                     'l-art/06', 'l-art/07', 'geo/01', 'geo/02', 'geo/03', 'geo/04', 'geo/05', 'agr/01',
                                     'agr/02', 'agr/03', 'agr/05', 'agr/06', 'agr/07', 'agr/08', 'agr/09', 'agr/10', 'agr/11',
                                     'agr/12', 'agr/13', 'agr/14', 'agr/15', 'agr/16', 'agr/19', 'agr/20', 'bio/03', 'bio/05',
                                     'bio/07', 'bio/08', 'bio/09', 'bio/10', 'bio/11', 'bio/12', 'bio/13', 'bio/14', 'bio/16',
                                     'bio/17', 'bio/18', 'bio/19', 'chim/01', 'chim/02', 'chim/03', 'chim/04', 'chim/06',
                                     'chim/08', 'chim/09', 'chim/12', 'geo/06', 'geo/07', 'geo/08', 'geo/09', 'geo/10',
                                     'l-art/08', 'l-fil-let/01', 'l-fil-let/02', 'ius/01', 'ius/02', 'ius/04', 'ius/07',
                                     'ius/08', 'ius/09', 'ius/10', 'ius/11', 'ius/13', 'ius/16', 'ius/17', 'ius/18', 'ius/19',
                                     'ius/20', 'l-fil-let/04', 'l-fil-let/05', 'l-fil-let/08', 'l-fil-let/10', 'l-fil-let/11',
                                     'l-fil-let/12', 'l-fil-let/13', 'l-fil-let/14', 'l-lin/01', 'l-lin/03', 'l-lin/05',
                                     'l-lin/07', 'l-lin/12', 'l-lin/13', 'l-lin/21', 'l-or/02', 'l-or/04', 'l-or/07',
                                     'l-or/08', 'l-or/21']:
                        interesting = False    
                        print('  skip', section)                
        #FFT
        if not 'FFT' in rec:
            for div in artpage.body.find_all('div', attrs = {'class' : 'itemTagBitstreams'}):
                for span in div.find_all('span', attrs = {'class' : 'label'}):
                    if re.search('Open', span.text):
                        for a in div.find_all('a'):
                            if re.search('pdf$', a['href']):
                                rec['FFT'] = universities[uni][1] + a['href']
    #faculty
    for div in artpage.body.find_all('div', attrs = {'id' : ['dc.authority.orgunit_content', 'dc.description.phdCourse_content',
                                                             'dc.authority.academicField2000_content', 'dc.ugov.classaux4_content',
                                                             'dc.ugov.classaux1_content', 'dc.subject.miur_content']}):
        for em in div.find_all('em'):
            fac = em.text.strip().lower()
            fac = re.sub(' \(.*', '', fac)
            fac = re.sub('^\d+ cicli?o \- ', '', fac)
            fac = re.sub('^[xiv]+ cicli?o \- ', '', fac)
            fac = re.sub('^settore ', '', fac)
            fac = regsec.sub(r'\1', fac)
            if fac in boring:
                interesting = False
                print('  skip', fac)
            elif re.search('mat\/\d+ ', fac):
                rec['fc'] = 'm'
            elif re.search('inf\/\d+ ', fac):
                rec['fc'] = 'c'
            else:
                rec['note'].append(fac)
    #pages
    for div in artpage.body.find_all('div', attrs = {'id' : 'dc.relation.numberofpages_content'}):
        for em in div.find_all('em'):
            if re.search('^\d+$', em.text):
                rec['pages'] = em.text
    if 'autaff' in rec:
        rec['autaff'][-1].append(publisher)
        #year might be the year of deposition
        if 'date' in rec and not 'year' in rec:
            rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])
        if 'year' in rec and not 'date' in rec:
            rec['date'] = rec['year']
        #license
        ejlmod3.globallicensesearch(rec, artpage)
        #abstract
        if not 'abs' in rec or not rec['abs'] or len(rec['abs']) < 20:
            for p in artpage.body.find_all('p', attrs = {'class' : 'abstractEng'}):
                rec['abs'] = p.text.strip()
        #abstract
        if not 'abs' in rec or not rec['abs'] or len(rec['abs']) < 20:
            for p in artpage.find_all('p', attrs = {'class' : 'abstractIta'}):
                rec['abs'] = p.text.strip()
        #link
        if not 'doi' in rec and not 'hdl' in rec:
            rec['link'] = rec['artlink']
        if interesting:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
        else:
            ejlmod3.adduninterestingDOI(rec['hdl'])
    else:
        print('---[ NO AUTHOR! ]---  ')

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
