# -*- coding: utf-8 -*-
#harvest theses from oatd.org (Open Access Theses and Dissertations)
#FS: 2021-02-02
#FS: 2023-03-29

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
from bs4 import Comment
import re
import ejlmod3
import unicodedata
from inspirelabslib3 import *
import time
import json
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import urllib3

urllib3.disable_warnings()

singlewords = ["2HDM", "ABJM", "antibaryon", "antifermion", "antifield",
               "antigravitation", "antihydrogen", "antihyperon", "antineutrino",
               "antinucleon", "antiparticle", "antiquark", "ArgoNeuT", "ASACUSA",
               "axino", "axion", "BaBar", "Bagger-Lambert-Gustavsson", "Baksan",
               "Balitsky-Kovchegov", "baryon", "Becchi-Rouet-Stora", "BFKL",
               "Borexino", "Born-Infeld", "Brans-Dicke", "BTeV", "Callan-Gross",
               "CCFM", "CERN", "Chaplygin", "Chern-Simons", "Chou-Yang",
               "chromoelectric", "chromomagnetic", "CPT", "CRESST", "D-brane",
               "DEAP-3600", "DESY", "DGLAP", "dilaton", "dilepton", "diquark",
               "Dirac-Kaehler", "D-particle", "Drell-Hearn-Gerasimov", "Drell-Yan",
               "Duffin-Kemmer-Petiau", "Dvali-Gabadadze-Porrati", "dyon",
               "Dyson-Schwinger", "Eguchi-Kawai", "Einstein-Yang-Mills", 'Einstein-Yang-Mills-Higgs',
               "electroweak", "Ellis-Jaffe", "EPRL", "eRHIC", "Fermilab",
               "FINUDA", "Froissart", "Gauss-Bonnet", "Gell-Mann-Okubo", "GeV",
               "Georgi-Glashow", "Ginsparg-Wilson", "Glashow-Iliopoulos-Maiani",
               "glasma", "glueball", "GlueX", "gluino", "gluon", "Goldstino",
               "gravitino", "graviton", "Green-Schwarz", "Gross-Neveu", "GZK",
               "hadron", "hadroproduction", "HAPPEX", "HEP", "Higgs", "Higgsino",
               "Higgsless", "Horava-Lifshitz", "Horava-Witten", "hypercharge",
               "hypernucleus", "hyperon", "Hyperon", "hyperonic", "IAXO", "IceCube",
               "Iizuka-Okubo-Zweig", "inflaton", "Isgur-Wise", "JLEIC",
               "Jona-Lasinio-Nambu", "Kaluza-Klein", "KAMIOKANDE", "KamLAND",
               "Kazakov-Migdal", "Klebanov-Witten", "KM3NeT", "Kobayashi-Maskawa",
               "KTeV", "L3", "Landau-Pomeranchuk-Migdal", "leptogenesis", "lepton",
               "leptophilic", "leptophobic", "leptoproduction", "leptoquark", "LHCb",
               "LHeC", "LIGO", "Lippmann-Schwinger", "Majoron", "M-brane", "meson",
               "MicroBooNE", "MiniCLEAN", "MOEDAL", "MSSM", "M-theory", "Mu2e",
               "Mu3e", "muon", "muonium", "N2HDM", "NA48", "NA49", "NA60", "NA61",
               "NA62", "neutrino", "neutrinoless", "neutrinoproduction", "NLSP",
               "NMSSM", "odderon", "Pati-Salam", "Peccei-Quinn", "pentaquark",
               "pomeron", "positronium", "pQCD", "Proca", "QCD", "QFT", "quark",
               "quarkonium", "Randall-Sundrum", "Rarita-Schwinger", "Regge",
               "RHIC", "Salam-Weinberg", "SciBooNE", "S-duality", "Seiberg-Witten ",
               "semileptonic",
               "sfermion", "sine-Gordon", "sinh-Gordon", "Skyrmion", "SLAC", "slepton",
               "sneutrino", "squark", "Supergravity", "SuperKEKB", "superluminal",
               "superstring", "supersymmetry", "SUSY", "T2K", "tachyon", "T-duality",
               "technicolor", "tetraquark", "TeV", "Tevatron", "topcolor", "T-parity",
               "TPC", "TQFT", "Ward-Takahashi", "Wess-Zumino", "Wess-Zumino-Witten",
               "Wheeler-DeWitt", "Wick-Cutkosky", "WIMP", "Wino", "wormhole", "XENON1T",
               "Yang-Mills", "Yang-Mills-Higgs", "Zino"]
singlewords += ['qubit', 'QIS', 'NISQ', 'teleportation', 'qudit', 'qutrit', 'QKD']
multwords = [['AdS', 'CFT'], ['quantum', 'field', 'theory'],
             ['PANDA', 'FAIR'], ['quantum', 'chromodynamics'],
             ['Quantum', 'Cosmology'], ['quantum', 'electrodynamics'],
             ['quantum', 'gravity'], ['string', 'theory'],
             ['wakefield', 'acceleration']]
multwords += [['quantum', 'computing'], ['quantum', 'key', 'distribution'],
              ['quantum', 'information'], ['quantum', 'error', 'correction']]
dedicatedharvester = ['alabama', 'alberta', 'arizona-diss', 'asu', 'barcelona',
                      'baylor', 'bayreuth', 'bielefeld', 'brown', 'caltech', 'cambridge', 'cardiff',
                      'charles-prague', 'colorado', 'columbia-diss', 'cornell', 'dortmund-diss',
                      'durham', 'ethz', 'freiburg-diss', 'gatech', 'glasgow',
                      'goettingen', 'guelph', 'harvard', 'helsinki', 'heid-diss', 'hokkaido',
                      'houston', 'humboldt-diss', 'jhu', 'ksu', 'ku', 'liverpool',
                      'lmu-germany', 'louisville', 'lsu-diss', 'lund', 'manchester', 'mcgill',
                      'melbourne', 'mississippi', 'montana', 'montstate', 'mtu', 'narcis', 'neu',
                      'ncsu', 'odu', 'ohiolink', 'oregon', 'osaka', 'oviedo', 'poli-torino',
                      'potsdam-diss', 'princeton', 'qucosa-diss', 'regensburg-diss', 'regina',
                      'rice', 'rochester', 'rutgers', 'giessen-diss', 'st-andrews', 'syracuse-diss',
                      'tamu', 'temple', 'toronto-diss', 'ttu', 'ubc', 'uconn', 'uky-diss', 'umich',
                      'umn', 'unm', 'unsw', 'upv', 'valencia', 'vandy', 'vcu', 'virginia', 'vt',
                      'washington', 'wayne', 'whiterose', 'wm-mary', 'wurz-diss', 'york',
                      'oklahoma-diss']
dedicatedaffiliations = ['Imperial College London', 'University of Edinburgh',
                         'University College London (University of London)',
                         "King's College London (University of London)", 'University of Manchester']
dedicatedsuboptimalharvester = ['eth', 'fsu', 'karlsruhe-diss', 'stanford', 'texas',
                                'thueringen', 'thueringen-diss', 'florida']
nodedicatedharvester = ['aberdeen', 'ankara', 'arkansas', 'bremen', 'brazil', 'bu',  'clemson',
                        'colo-mines','colostate', 'darmstadt', 'darmstadt2', 'delaware', 'duquesne',
                        'ethos', 'fiu', 'georgia-state', 'groningen','iowa', 'jairo', 'jamescook',
                        'lehigh', 'liberty', 'macquarie-phd', 'maynooth', 'msstate', 'rit', 'siu-diss',
                        'south-carolina', 'star-france', 'stellenbosch',
                        'udel', 'uiuc', 'ulm-diss', 'utk-diss', 'urecht', 'uwm', 'vrije',
                        'wustl', 'wvu']
dontcheckforpdf = ['ethos']
rereportnumbersinlinks = [re.compile('.*rwth\-aachen.de.*?(RWTH\-\d+\-\d+).*'),
                          re.compile('.*www.theses.fr\/(.*)')]

wordsperquery = 10
searches = []
for j in range((len(singlewords)-1)//wordsperquery + 1):
    words = singlewords[j*wordsperquery:(j+1)*wordsperquery]
    if len(words) > 1:
        searches.append('("' + '" OR "'.join(words) + '")')
    else:
        searches.append('"' + words[0]+ '"')
for words in multwords:
    searches.append('(' + ' AND '.join(words) + ')')
startyear = str(ejlmod3.year(backwards=1))
stopyear= str(ejlmod3.year()+1)
startsearch = int(sys.argv[1])
stopsearch = int(sys.argv[2])
rpp = 30
skipalreadyharvested = True
#chunksize = 50
publisher = 'oatd.org'
jnlfilename = 'THESES-OATD_%s__%s-%s' % (ejlmod3.stampoftoday(), startsearch, stopsearch)



host = os.uname()[1]
options = uc.ChromeOptions()
if host == 'l00schwenn':
    options.binary_location='/usr/bin/chromium'
else:
    options.binary_location='/usr/bin/google-chrome'
    options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
driver.get('https://oatd.org/')
time.sleep(20)


comment = Comment('Kommentar')
#check already harvested
ejldirs = ['/afs/desy.de/user/l/library/dok/ejl/backup',
           '/afs/desy.de/user/l/library/dok/ejl/backup/%i' % (ejlmod3.year()),
           '/afs/desy.de/user/l/library/dok/ejl/backup/%i' % (ejlmod3.year(backwards=1))]
redoki = re.compile('THESES.OATD')
renodoi = re.compile('^I\-\-NODOI:(.*)\-\-$')
bereitsin = []
for ejldir in ejldirs:
    print(ejldir)
    for datei in os.listdir(ejldir):
        if redoki.search(datei):
            inf = open(os.path.join(ejldir, datei), 'r')
            for line in inf.readlines():
                if len(line) > 1 and line[0] == 'I':
                    if renodoi.search(line):
                        nodoi = renodoi.sub(r'\1', line.strip())
                        if not nodoi in bereitsin:
                            bereitsin.append(nodoi)
            #print '  %6i %s' % (len(bereitsin), datei)
print('   %i theses already in backup' % (len(bereitsin)))


if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested('THESES')
    skippedrecords = []
i = 0
recs = []
prerecs = []
dois = []
date = 'pub_dt:[' + startyear + '-01-01T00:00:00Z TO ' + stopyear + '-01-01T00:00:00Z]'

driver.implicitly_wait(60)
driver.set_page_load_timeout(30)
for search in searches[startsearch:stopsearch]:
    i += 1
    page = 0
    tocurl = 'https://oatd.org/oatd/search?q=' + search + ' AND ' + date + '&level.facet=doctoral&sort=author&start=' + str(page*rpp+1)
    ejlmod3.printprogress("=", [[i, stopsearch-startsearch], [startsearch+i, len(searches)], [tocurl]])
    time.sleep(70)
    try:
        driver.get(tocurl)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'citeFormatName')))
        tocpages = [BeautifulSoup(driver.page_source, features="lxml")]
    except:
        print('   \ wait 2 minutes /')
        time.sleep(120)
        driver.get(tocurl)
        #WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'citeFormatName')))
        tocpages = [BeautifulSoup(driver.page_source, features="lxml")]
    numofpages = 1
    for link in tocpages[0].find_all('link', attrs = {'rel' : 'last'}):
        time.sleep(45)
        numoftheses = int(re.sub('.*=', '', link['href']))
        numofpages = (numoftheses - 1)//rpp + 1
        for j in range(numofpages-1):
            page = j + 1
            tocurl = 'https://oatd.org/oatd/search?q=(' + search + ') AND ' + date + '&level.facet=doctoral&start=' + str(page*rpp+1)
            print(' =={ %i/%i | %i/%i }==={ %s }===' % (i, stopsearch-startsearch, page+1, numofpages, tocurl))
            try:
                time.sleep(30)
                driver.get(tocurl)
                WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'citeFormatName')))
                tocpages.append(BeautifulSoup(driver.page_source, features="lxml"))
            except:
                print('   \ wait 30s /')
                time.sleep(30)
                try:
                    driver.get(tocurl)
                    tocpages.append(BeautifulSoup(driver.page_source, features="lxml"))
                except:
                    print('   \ wait 120s /')
                    time.sleep(120)
                    driver.get(tocurl)
                    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'citeFormatName')))
                    tocpages.append(BeautifulSoup(driver.page_source, features="lxml"))
    page = 0
    for tocpage in tocpages:
        page += 1
        print('  ={ %i/%i | %i/%i }===' % (i, stopsearch-startsearch, page, numofpages))
        for desce in tocpage.descendants:
            if type(desce) == type(comment) and re.search('Repository', desce.string):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : [search]}
                repo = re.sub('Repository: (.*?) \|.*', r'\1', desce.string).strip()
                rec['repo'] = repo
                tid = re.sub('.*\| ID: (.*?) \|.*', r'\1', desce.string)
                tid = re.sub(':', '\:', tid)
                tid = re.sub('/', '\%2F', tid)
                rec['artlink'] = 'https://oatd.org/oatd/record?record=' + tid
                rec['nodoi'] = '20.2000/OATD/' + re.sub('\W', '', re.sub('.*record=', '', tid))
                if repo in dedicatedharvester:
                    print('   skip', repo)
                else:
                    if re.search('record=handle.:\d+.%2F\d', rec['artlink']):
                        hdl = re.sub('.*handle..(\d+)..2F(\d+)', r'\1/\2', rec['artlink'])
                        if skipalreadyharvested and hdl in alreadyharvested:
                            print('   skip', hdl)
                            continue
                    if repo in nodedicatedharvester:
                        rec['note'].append('(REPO:' + repo + ')')
                    elif repo in dedicatedsuboptimalharvester:
                        rec['note'].append('REPO:' + repo + '!')
                    else:
                        rec['note'].append('REPO:' + repo)
                    if rec['nodoi'] in bereitsin:
                        print('    ((', rec['nodoi'],'))')
                    elif not rec['nodoi'] in dois:
                        print('      ', rec['nodoi'])
                        rec['note'].append('NODOI:'+rec['nodoi'])
                        if ejlmod3.checkinterestingDOI(rec['nodoi']):
                            if not re.search('DSPACE.* .*ufscar.*', rec['artlink']):
                                prerecs.append(rec)
                                dois.append(rec['nodoi'])
                    else:
                        print('     (', rec['nodoi'],')')
        print('    %i records so far' % (len(prerecs)))

i = 0
rehdl = re.compile('.*hdl.handle.net\/')
repothdl = re.compile('.*\/handle\/(\d+\/.*)')
reurn = re.compile('.*resolve.urn=')
redoi = re.compile('.*doi.org\/(10.*)')
reinfodoi = re.compile('^info:doi\/(10.*)')
recc = re.compile('.*(http.*?creativecommons.org.*?)[ ,\.;$].*')
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['repo']], [rec['artlink']], [len(recs)]])
    try:
        time.sleep(30)
        driver.get(rec['artlink'])
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'leftCol')))
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        try:
            print('\\\| wait 45s |///')
            time.sleep(45)
            driver.get(rec['artlink'])
            artpage = BeautifulSoup(driver.page_source, features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    aff = False
    ejlmod3.metatagcheck(rec, artpage, ['citation_author','citation_author_orcid', 'DC.rights',
                                        'dc.date', 'dc.description'])
    #ORCID
    if len(rec['autaff']) == 1:
        for td in artpage.body.find_all('td', attrs = {'itemprop' : 'author'}):
            for a in td.find_all('a'):
                if a.has_attr('href') and re.search('orcid.org\/\d\d\d\d', a['href']):
                    orcid = re.sub('.*orcid.org\/', 'ORCID:', a['href'])
                    print('     ORCID found in body', orcid)
                    rec['autaff'][-1].append(orcid)
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name') and meta.has_attr('content'):
            #title
            if meta['name'] == 'citation_title':
                if 'repo' in rec and rec['repo'] == 'star-france' and re.search(' : ', meta['content']):
                    rec['tit'] = re.sub(' : .*', '', meta['content'])
                    rec['transtit'] = re.sub('.*? : ', '', meta['content'])
                else:
                    rec['tit'] = meta['content']
            #institution
            elif meta['name'] == 'citation_dissertation_institution':
                aff = meta['content']
                if aff in dedicatedaffiliations:
                    keepit = False
                    print('   skip "%s"' % (aff))
            #PIDs
            elif meta['name'] == 'dc.identifier':
                for mc in re.split(' *; *', meta['content']):
                    if rehdl.search(mc):
                        rec['hdl'] = rehdl.sub('', mc)
                    elif reurn.search(mc):
                        rec['urn'] = reurn.sub('', mc)
                    elif redoi.search(mc):
                        rec['doi'] = redoi.sub(r'\1', mc)
                    elif repothdl.search(mc):
                        hdl = repothdl.sub(r'\1', mc)
                        if not re.search('123456789\/', hdl):
                            #verify
                            try:
                                driver.get('http://hdl.handle.net/' + hdl)
                                hdlpage = BeautifulSoup(driver.page_source, features="lxml")
                                for title in hdlpage.find_all('title'):
                                    if title.text.strip() == 'Not Found':
                                        rec['note'].append('%s seems not to be a proper HDL' % (hdl))
                                        rec['link'] = mc
                                    else:
                                        rec['hdl'] = hdl
                                        rec['note'].append('%s seems to be a proper HDL' % (hdl))
                            except:
                                print('could not check handle %s' % (hdl))
                                rec['link'] = mc
                    else:
                        rec['link'] = mc
    if aff: rec['autaff'][0].append(aff)
    for table in artpage.body.find_all('table', attrs = {'class' : 'recordTable'}):
        for tr in table.find_all('tr'):
            for td in tr.find_all('td', attrs = {'class' : 'leftCol'}):
                tdt = td.text.strip()
                td.decompose()
            for td in tr.find_all('td'):
                #keyword
                if tdt == 'Subjects/Keywords':
                    rec['keyw'] = re.split('; ', td.text.strip())
                #language
                elif tdt == 'Language':
                    lang = td.text.strip()
                    rec['language'] = lang
                #other identifiers
                elif tdt == 'Other Identifiers':
                    if reinfodoi.search(td.text) and not 'doi' in rec:
                        rec['doi'] = reinfodoi.sub(r'\1', td.text.strip())
                #license
                elif tdt == 'Rights':
                    if recc.search(td.text):
                        rec['license'] = {'url' : recc.sub(r'\1', td.text.strip())}
    if keepit or i == len(prerecs):
        #try to get pdf
        serverlink = False
        if 'link' in rec and re.search('pdf$', rec['link']):
            rec['FFT'] = rec['link']
        elif 'hdl' in rec:
            serverlink = 'http://hdl.handle.net/' + rec['hdl']
        elif 'doi' in rec:
            serverlink = 'http://dx.doi.org/' + rec['doi']
        elif 'link' in rec:
            serverlink = rec['link']
        if serverlink and not rec['repo'] in dontcheckforpdf:
            rec['note'].append('REPOLINK:'+serverlink)
            print('    ... check for PDF at %s' % (serverlink))
            try:
                time.sleep(2)
                driver.get(serverlink)
                serverpage = BeautifulSoup(driver.page_source, features="lxml")
                for meta in serverpage.find_all('meta', attrs = {'name' : ['citation_pdf_url',
                                                                           'bepress_citation_pdf_url',
                                                                           'eprints.document_url']}):
                    if not 'FFT' in rec:
                        if meta['content']:
                            rec['FFT'] = meta['content']
                            print('          ', meta['content'])
                if not 'doi' in rec:
                    print('    ... check for DOI at %s' % (serverlink))
                    for meta in serverpage.find_all('meta', attrs = {'name' : ['citation_doi',
                                                                               'bepress_citation_doi',
                                                                               'eprints.doi',
                                                                               'eprints.doi_name',
                                                                               'DC.Identifier.doi']}):
                        if re.search('^10\.\d', meta['content']):
                            rec['doi'] = meta['content']
                            rec['note'].append('DOI from reposerver')
                            print('          ', meta['content'])
                    if not 'doi' in rec:
                        for meta in serverpage.find_all('meta', attrs = {'name' : 'DC.identifier'}):
                            if re.search('doi.org', meta['content']):
                                rec['doi'] = re.sub('.*doi.org\/', '', meta['content'])
                                print('          ', rec['doi'])
                                rec['note'].append('DOI from reposerver')
                            elif re.search('handle.net', meta['content']) and not 'hdl' in rec:
                                rec['hdl'] = re.sub('.*handle.net\/', '', meta['content'])
                                print('          ', rec['hdl'])
                                rec['note'].append('HDL from reposerver')
            except:
                print('           failed')
        #ckeck whether DOI/HDL/URN already is in INSPIRE. check whether link contains report number (that is already in INSPIRE).
        if 'doi' in rec and perform_inspire_search_FS('doi:"%s"' % (rec['doi'])):
            print('    %s already in INSPIRE' % (rec['doi']))
            continue
        elif 'hdl' in rec and perform_inspire_search_FS('persistent_identifiers.value:"%s"' % (rec['hdl'])):
            print('    %s already in INSPIRE' % (rec['hdl']))
            continue
        elif 'urn' in rec and perform_inspire_search_FS('persistent_identifiers.value:"%s"' % (rec['urn'])):
            print('    %s already in INSPIRE' % (rec['urn']))
            continue
        elif 'link' in rec:
            time.sleep(3)
            rn = False
            for rernl in rereportnumbersinlinks:
                if not rn and rernl.search(rec['link']):
                    rn = rernl.sub(r'\1', rec['link'])
                    print('    extracted report number "%s" from link "%s"' % (rn, rec['link']))
                    if 'rn' in rec:
                        rec['rn'].append(rn)
                    else:
                        rec['rn'] = [rn]
            if rn and perform_inspire_search_FS('rn:%s' % (rn)):
                print('    %s already in INSPIRE' % (rn))
                continue
        #pseudoDOI?
        if not 'doi' in rec and not 'hdl' in rec:
            if not 'link' in rec:
                rec['link'] = rec['artlink']
            if not 'urn' in rec:
                rec['doi'] = rec['nodoi']
        if 'autaff' in rec:
            if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
                print('   %s already harvested via dedicated crawler' % (rec['doi']))
                skippedrecords.append((rec['doi'], rec['repo']))
                ouf = open('%s/THESES-OATD_%salreadyharvestedviadecicatedcrawler.doki' % (ejldirs[0], ejlmod3.stampoftoday()), 'a')
                ouf.write('I--NODOI:%s--\n' % (rec['nodoi']))
                ouf.close()
            elif skipalreadyharvested and 'hdl' in rec and rec['hdl'] in alreadyharvested:
                print('   %s already harvested via dedicated crawler' % (rec['hdl']))
                skippedrecords.append((rec['hdl'], rec['repo']))
                ouf = open('%s/THESES-OATD_%salreadyharvestedviadecicatedcrawler.doki' % (ejldirs[0], ejlmod3.stampoftoday()), 'a')
                ouf.write('I--NODOI:%s--\n' % (rec['nodoi']))
                ouf.close()
            elif skipalreadyharvested and 'urn' in rec and rec['urn'] in alreadyharvested:
                print('   %s already harvested via dedicated crawler' % (rec['urn']))
                skippedrecords.append((rec['urn'], rec['repo']))
                ouf = open('%s/THESES-OATD_%salreadyharvestedviadecicatedcrawler.doki' % (ejldirs[0], ejlmod3.stampoftoday()), 'a')
                ouf.write('I--NODOI:%s--\n' % (rec['nodoi']))
                ouf.close()
            # elif skipalreadyharvested and pseudodoifromlink(rec['artlink']) in alreadyharvested:
            else:
                recs.append(rec)
                ejlmod3.printrecsummary(rec)
        else:
            print('!')
            ejlmod3.printrec(rec)
            time.sleep(20)
#        if ((i % chunksize) == 0) or (i == len(prerecs)):
#            print(i, len(prerecs), len(recs))
#            if recs:
#                chunknumber = (i-1)//chunksize + 1
#                numofchunks = (len(prerecs) - 1) // chunksize + 1
#                jnlfilename = 'THESES-OATD_%s_%s-%s_%i-%i-%i_%i_%02i-%i' % (ejlmod3.stampoftoday(), startyear, stopyear, startsearch, stopsearch, len(searches), chunksize, chunknumber, numofchunks)
#                crecs = recs[(chunknumber-1)*chunksize:chunknumber*chunksize]
#                ejlmod3.writenewXML(crecs, publisher, jnlfilename)
    else:
        ejlmod3.adduninterestingDOI(rec['nodoi'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
if skipalreadyharvested:
    print('skipped records')
    for (doi, repo) in skippedrecords:
        if not repo in dedicatedsuboptimalharvester+['ethos', 'utrecht', 'groningen']:
            print('%30s %s' % (repo, doi))
