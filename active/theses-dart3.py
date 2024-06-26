# -*- coding: utf-8 -*-
#harvest theses from dart-europe.org (DART-Europe E-theses Portal)
#FS: 2021-02-03
#FS: 2022-10-04

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import unicodedata 
import codecs
import datetime
import time
import json
import requests
import mimetypes
import urllib3
import ssl
from inspirelabslib3 import *

wordsperquery = 10
chunksize = 50
years = [ejlmod3.year(), ejlmod3.year(backwards=1)]
#years = [2012, 2011, 2010, 2009]
#whether to check ALL sources or only those where we do not have a dedicated harvester
checkall = False 
verbose = False

# do not work: "M-theory", "M-brane", "D-brane", "D-particle", "T-duality", "T-parity", "S-duality",
# do not give results: "DEAP-3600", 'Einstein-Yang-Mills-Higgs', "Glashow-Iliopoulos-Maiani", "Isgur-Wise", "Kazakov-Migdal",
singlewords = ["ABJM", "antibaryon", "antifermion", "antifield", "antihydrogen", "antihyperon", "antineutrino",
               "antinucleon", "antiparticle", "ArgoNeuT", "ASACUSA", "axion", "BaBar",
               "Baksan", "baryon", "Becchi-Rouet-Stora",
               "Borexino", "Brans-Dicke", "BTeV", "CERN", "Chaplygin", "Chern-Simons",
               "chromoelectric", "chromomagnetic", "CPT", "CRESST", "DESY", "dilaton",
               "dilepton", "Drell-Yan",
               "Dvali-Gabadadze-Porrati", "dyon", "Dyson-Schwinger", "Eguchi-Kawai", "Einstein-Yang-Mills",
               "electroweak", "EPRL", "eRHIC", "Fermilab", "FINUDA", "Froissart", "GeV", 
               "GlueX", "graviton", "antigravitation", "Horava-Lifshitz",
               "Gauss-Bonnet", "LIGO", "Born-Infeld", "Green-Schwarz", "Gross-Neveu", "GZK", "HAPPEX", "HEP",
               "Higgs", "N2HDM", "2HDM", "Higgsless", "Jona-Lasinio-Nambu", "Horava-Witten", "hypercharge",
               "hypernucleus", "hyperon", "Hyperon", "hyperonic", "IAXO", "IceCube", "Iizuka-Okubo-Zweig",
               "inflaton", "JLEIC", "Kaluza-Klein", "KAMIOKANDE", "KamLAND", 
               "Klebanov-Witten", "KM3NeT", "Kobayashi-Maskawa", "KTeV", "L3", "Landau-Pomeranchuk-Migdal",
               "leptogenesis", "lepton", "leptophilic", "leptophobic", "leptoproduction", "leptoquark", "LHCb",
               "LHeC", "Lippmann-Schwinger", "Majoron", "MicroBooNE", "MiniCLEAN", "MOEDAL", "MSSM", "Mu2e",
               "Mu3e", "muon", "muonium", "NA48", "NA49", "NA60", "NA61", "NA62", "neutrino", "neutrinoless",
               "neutrinoproduction", "NLSP", "NMSSM", "Higgsino", "slepton", "sneutrino", "squark", "sfermion",
               "Goldstino", "gravitino", "gluino", "axino", "Pati-Salam", "Peccei-Quinn", "positronium",
               "Proca", "QCD", "pQCD", "pentaquark", "tetraquark", "meson", "hadron", "gluon",
               "hadroproduction", "antiquark", "BFKL", "CCFM", "DGLAP", "glasma", "glueball", "diquark",
               "quark", "quarkonium", "QFT", "Randall-Sundrum", "Rarita-Schwinger", "Regge",
               "Reggeon", "odderon", "pomeron", "RHIC", "Salam-Weinberg", "SciBooNE", 
               "Seiberg-Witten", "semileptonic", "sine-Gordon", "sinh-Gordon", "Skyrmion", "SLAC",
               "Supergravity", "SuperKEKB", "superluminal", "superstring", "supersymmetry", "SUSY", "T2K",
               "tachyon", "technicolor", "TeV", "Tevatron", "topcolor", "TPC", "TQFT", "Ward-Takahashi",
               "Wess-Zumino", "Wheeler-DeWitt", "WIMP", "Wino", "wormhole", "XENON1T",
               "Yang-Mills", "Yang-Mills-Higgs", "Zino"]
singlewords += ['qubit', 'QIS', 'NISQ', 'IBMQ', 'Qiskit', 'qudit', 'qutrit']
multwords = [['AdS', 'CFT'], ['quantum', 'field', 'theory'], ['PANDA', 'FAIR'], ['quantum', 'chromodynamics'],
             ['Quantum', 'Cosmology'], ['quantum', 'electrodynamics'], ['gravitational', 'radiation'],
             ['gravitational', 'waves'], ['quantum', 'gravity'], ['string', 'theory'],
             ['wakefield', 'acceleration']]
multwords += [['quantum', 'computing'], ['quantum', 'sensing'], ['quantum', 'algorithm']]

#hyphens do not work as expected
realsinglewords = []
for word in singlewords:
    if re.search('\-', word):
        multwords.append(re.split('\-', word))
    else:
        realsinglewords.append(word)
        
searches = []
for j in range((len(realsinglewords)-1)//wordsperquery + 1):
    words = []
    for word in realsinglewords[j*wordsperquery:(j+1)*wordsperquery]:
        words.append(word)
    searches.append('+OR+'.join(words))
for words in multwords:
    searches.append('+'.join(words))

#statistics
statistics = {}

publisher = 'dart-europe.org'

#collections with dedicated harvester
dedicated = ['TEL', 'Manchester Research Explorer', 'Durham e-Theses',
             'University of Helsinki', 'NORA', 'TDX', 'Archive ouverte UNIGE',
             'DIAL.pr@UCL', 'ETH Zurich Research Collection', 'University of Birmingham',
             'White Rose', 'Glasgow University Theses', 'Lancaster EPrints',
             'NARCIS', 'DiVA', 'ePrints Soton', 'Spiral', 'ERA', 'LUP']
dedicated += ['Université Paris-Saclay', 'Université Grenoble Alpes',
              'University of Padova', 'Universität Heidelberg',
              'SISSA Scuola Internazionale Superiore di Studi Avanzati',
              'UCL (University College London)', 'Universidad Autónoma de Madrid',
              'Rheinisch-Westfälischen Technischen Hochschule (RWTH) Aachen',
              'Université Pierre et Marie Curie - Paris VI',
              'Università degli Studi di Milano', 'Technische Universität München',
              'Imperial College London', 'Université Sorbonne Paris Cité',
              'Université de Lyon', 'Aix Marseille Université', 'Universität Zürich',
              'University of Warwick', 'Università degli Studi di Milano-Bicocca',
              'Technischen Universität Dortmund', 'Johannes Gutenberg-Universität Mainz',
              'University of Basel', 'Universiteit Gent',
              'Albert-Ludwigs-Universität Freiburg',
              'Ludwig-Maximilians-Universität München', 'Karlsruher Institut für Technologie',
              'Université de Montpellier', 'Université Paul Sabatier - Toulouse III',
              'Université de Nantes', 'University of Surrey', 'Normandie Université',
              'Lund University', 'HEDI']
dedicated += ['Ruhr-Universität Bochum', 'Justus-Liebig-Universität Gießen', 'STAR',
              'RCAAP', 'Universidad de Granada', 'Unimore Iris', 'PLEIADI', 'ethz',
              'UCrea Universidad de Cantabria', 'Leicester Research Archive']
dedicated += [u'Humboldt-Universität zu Berlin', u'Technische Universität Dresden',
              u'Universität zu Köln', u'Bergische Universität Wuppertal',
              u'Eberhard Karls Universität Tübingen', u'Freie Universität Berlin',
              u'Friedrich-Alexander-Universität Erlangen-Nürnberg',
              u'Georg-August-Universität Göttingen', u'Goethe Universität Frankfurt am Main',
              u'Gottfried Wilhelm Leibniz Universität Hannover',
              u'Universität Hamburg',
              u'Rheinische Friedrich-Wilhelms-Universität Bonn',
              u'Julius-Maximilians-Universität Würzburg', u'Technischen Universität Darmstadt',
              u'Trinity College Dublin', u'Universidad Complutense de Madrid',
              u'Universidade do Porto', u'Universität Bielefeld', u'Universität Potsdam',
              u'Universität Regensburg', u'Universität Siegen', u'University of Cyprus',
              u'University of Ljubljana', u'University of Zagreb']

#regular expressins for identifiers
rehdl = re.compile('.*hdl.handle.net\/')
repothdl = re.compile('.*\/handle\/(\d+\/\d+).*')
reurn1 = re.compile('.*resolve.urn=')
reurn2 = re.compile('^urn:[a-z]+:[a-z]+')
reurn2b = re.compile('^URN:[A-Z]+:[A-Za-z]+')
reurn3 = re.compile('^http.*resolv.*(urn:[a-z]+:[a-z]+.*)')
reurn4 = re.compile('^http.*\/(urn:[a-z]+:[a-z]+.*)')
redoi1 = re.compile('.*doi.org\/(10.*)')
redoi2 = re.compile('^(10.\d+\/.*)')
redoi3 = re.compile('^(info:doi\/|doi:|elte:)(10.\d+\/.*)')
reisbn1 = re.compile('.*(urn:isbn|URN:ISBN):(978[\-\d]+)')
reisbn2 = re.compile('^978[\-\d]+$')
rehtml = re.compile('^http')
recc = re.compile('.*(http.*?creativecommons.org.*?)[ ,\.;$].*')
reportnumber = re.compile('^tel\-\d+$')



#check already harvested
ejldirs = ['/afs/desy.de/user/l/library/dok/ejl/backup',           
           '/afs/desy.de/user/l/library/dok/ejl/backup/%i' % (ejlmod3.year()),
           '/afs/desy.de/user/l/library/dok/ejl/backup/%i' % (ejlmod3.year(backwards=1))]
redoki = re.compile('THESES.DART.*doki$')
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
            print('  %6i %s' % (len(bereitsin), datei))

#corrupt records
bereitsin.append('20.2000/DART-EUROPE/2081327')
bereitsin.append('20.2000/DART-EUROPE/2082645')

#check weblinks for persistant identifiers
def checkweblinks(rec):    
    for weblink in rec['weblinks']:        
        if 'doi' in list(rec.keys()) and 'hdl' in list(rec.keys()) and 'urn' in list(rec.keys()):
            if verbose: print('   PIDs complete')
        elif 'doi' in list(rec.keys()) and 'hdl' in list(rec.keys()):
            if verbose: print('   DOI and HDL are enough, do not look for URN')
        elif re.search('www.theses.fr', weblink) or re.search('d\-nb.info\/\d', weblink):
            continue
        elif weblink in ['https://d-nb.info/120141492X/34', 'https://plus.si.cobiss.net/opac7/bib/3384164 ?lang=sl']:
            continue            
        else:
            pids = []
            for pid in ['doi', 'hdl', 'urn']:
                if pid in list(rec.keys()):
                    pids.append(pid)
            print('   look for PIDs in addition to (%s) in %s' % (', '.join(pids), weblink))
            try:
                response = requests.get(weblink)
                content_type = response.headers['content-type']
                if verbose: print('       content_type = %s' % (content_type))
            except:
                content_type = ''
            if re.search('pdf', content_type):
                if verbose: print('   skip PDF')
            else:
                try:
                    req = urllib.request.Request(weblink, headers=hdr)
                    webpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
                except:
                    continue
                for meta in webpage.find_all('meta'):
                    if meta.has_attr('name') and meta.has_attr('content'):
                        #DOI
                        if not 'doi' in list(rec.keys()):
                            if meta['name'] in ['citation_doi', 'DC.identifier', 'DC.identifier', 'DC.Identifier.doi', 'eprints.doi', 'eprints.doi_name', 'eprints.id_number', "eprints.own_doi"]:
                                doi = meta['content']
                                if redoi2.search(doi):
                                    rec['doi'] = doi
                                    if verbose: print('   (* found DOI=%s in %s *)' % (doi, weblink))
                                    rec['note'].append('   (* found DOI=%s in %s *)' % (doi, weblink))
                                elif redoi1.search(doi):
                                    rec['doi'] = redoi1.sub(r'\1', doi)
                                    if verbose: print('   (* found DOI=%s in %s *)' % (rec['doi'], weblink))
                                    rec['note'].append('   (* found DOI=%s in %s *)' % (rec['doi'], weblink))
                        #URN
                        if not 'urn' in list(rec.keys()):
                            if meta['name'] in ['citation_urn', 'DC.identifier', 'DC.identifier', 'DC.Identifier.urn', 'eprints.urn', 'eprints.urn_name', 'eprints.own_urn', 'eprints.id_number']:
                                urn = meta['content']
                                if reurn2.search(urn) or reurn2b.search(urn):
                                    rec['urn'] = urn
                                    if verbose: print('   (* found URN=%s in %s *)' % (urn, weblink))
                                    rec['note'].append('   (* found URN=%s in %s *)' % (urn, weblink))
                                elif reurn3.search(urn):
                                    rec['urn'] = reurn3.sub(r'\1', urn)
                                    if verbose: print('   (* found URN=%s in %s *)' % (rec['urn'], weblink))
                                    rec['note'].append('   (* found URN=%s in %s *)' % (rec['urn'], weblink))
                                elif reurn4.search(urn):
                                    rec['urn'] = reurn4.sub(r'\1', urn)
                                    if verbose: print('   (* found URN=%s in %s *)' % (rec['urn'], weblink))
                                    rec['note'].append('   (* found URN=%s in %s *)' % (rec['urn'], weblink))
                        #HDL
                        if not 'hdl' in list(rec.keys()):
                            if meta['name'] in ['citation_hdl', 'DC.identifier', 'DC.identifier', 'DC.Identifier.hdl', 'eprints.hdl', 'eprints.hdl_name', 'eprints.id_number', "eprints.own_hdl"]:
                                hdl = meta['content']
                                if re.search('^\d+\/\d+$', hdl):
                                    rec['hdl'] = hdl                                
                                    if verbose: print('   (* found HDL=%s in %s *)' % (hdl, weblink))
                                    rec['note'].append('   (* found HDL=%s in %s *)' % (hdl, weblink))
                                elif re.search('http.*handle.net\/\d+\/', hdl):
                                    rec['hdl'] = re.sub('.*handle.net\/', '', hdl)                          
                                    if verbose: print('   (* found HDL=%s in %s *)' % (hdl, weblink))
                                    rec['note'].append('   (* found HDL=%s in %s *)' % (hdl, weblink))
                #special cases
                if not 'doi' in list(rec.keys()):
                    #Munich
                    if re.search('edoc.ub.uni\-muenchen.de', weblink):
                        for div in webpage.find_all('div', attrs = {'class' : 'ep_block_doi'}):
                            for a in div.find_all('a'):
                                if redoi1.search(a['href']):
                                    rec['doi'] = redoi1.sub(r'\1', a['href'])
                                    if verbose: print('   (* found DOI=%s in %s *)' % (rec['doi'], weblink))
                                    rec['note'].append('   (* found DOI=%s in %s *)' % (rec['doi'], weblink))
    return

                                        

i = 0
prerecs = []
dois = []
hdr = {'User-Agent' : 'Magic Browser'}
urllib3.disable_warnings()
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
for search in searches:
    statistics[search] = {'total' : 0, 'bereitsin' : 0, 'dedicated' : 0, 'harvested' : 0}
    i += 1
    for year in years:
        page = 1
        tocurl = 'https://www.dart-europe.org/basic-results.php?kw[]=' + search + '&f=y&fy=' + str(year) + '&page=' + str(page)
        ejlmod3.printprogress('=', [[i, len(searches)], [year], [search], [tocurl]])
        try:
            time.sleep(10)
            req = urllib.request.Request(tocurl, headers=hdr)
            tocpages = [BeautifulSoup(urllib.request.urlopen(req), features="lxml")]
        except:
            print('\\\| wait 3 minutes |///')
            time.sleep(180)
            req = urllib.request.Request(tocurl, headers=hdr)
            tocpages = [BeautifulSoup(urllib.request.urlopen(req), features="lxml")]
        numofpages = 1        
        for p in tocpages[0].find_all('p'):
            if re.search('Displaying records', p.text):
                strongs = p.find_all('strong')
                if len(strongs) == 5:
                    numofpages = int(strongs[4].text.strip())
                    numoftheses = int(strongs[2].text.strip())
        for j in range(numofpages-1):
            page = j + 2      
            tocurl = 'https://www.dart-europe.org/basic-results.php?kw[]=' + search + '+&f=y&fy=' + str(year) + '&page=' + str(page)
            print(' =={ %i / %i | %i/%i }==={ %i }==={ %s }===' % (i, len(searches), page, numofpages, year, search))
            try:
                time.sleep(5)
                req = urllib.request.Request(tocurl, headers=hdr)
                tocpages.append(BeautifulSoup(urllib.request.urlopen(req), features="lxml"))
            except:
                print('\\\| wait 30s |///')
                time.sleep(30)
                req = urllib.request.Request(tocurl, headers=hdr)
                tocpages.append(BeautifulSoup(urllib.request.urlopen(req), features="lxml"))
        page = 0
        for tocpage in tocpages:
            page += 1
            print('  ={ %i / %i | %i/%i }==={ %i }==={ %s }===' % (i, len(searches), page, numofpages, year, search))
            for table in tocpage.find_all('table', attrs = {'id' : 'search-results'}):
                for tr in table.find_all('tr'):
                    rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : [search], 'supervisor' : [],
                           'year' : str(year), 'date' : str(year), 'rn' : [], 'isbns' : [],
                           'weblinks' : []}
                    tds = tr.find_all('td')
                    if len(tds) == 6:
                        #affiliation
                        rec['university'] = tds[4].text.strip()
                        rec['note'].append('university:'+tds[4].text.strip())
                        #collection
                        rec['collection'] = tds[5].text.strip()
                        rec['note'].append('collection:'+tds[5].text.strip())
                    for input in tr.find_all('input', attrs = {'type' : 'checkbox'}):
                        rec['artlink'] = 'https://www.dart-europe.org/full.php?id=' + input['value']
                        rec['nodoi'] = '20.2000/DART-EUROPE/' + input['value']
                        if rec['nodoi'] in bereitsin:
                            if verbose: print('    ((', rec['nodoi'],'))')
                            statistics[search]['bereitsin'] += 1
                            statistics[search]['total'] += 1
                        elif (rec['collection'] in dedicated) or (rec['university'] in dedicated):
                            if checkall:
                                if verbose: print('      ', rec['nodoi'])
                                rec['note'].append('NODOI:'+rec['nodoi'])
                                prerecs.append(rec)
                                dois.append(rec['nodoi'])
                                statistics[search]['harvested'] += 1
                            else:
                                if verbose: print('     [ %s ] %s | %s ' % (rec['nodoi'], rec['collection'], rec['university']))
                                statistics[search]['dedicated'] += 1
                            statistics[search]['total'] += 1
                        elif not rec['nodoi'] in dois:
                            if verbose: print('      ', rec['nodoi'])
                            rec['note'].append('NODOI:'+rec['nodoi'])
                            prerecs.append(rec)
                            dois.append(rec['nodoi'])
                            statistics[search]['harvested'] += 1
                            statistics[search]['total'] += 1
                        else:
                            if verbose: print('     (', rec['nodoi'],')')
                            statistics[search]['total'] += 1
            print('    %i records so far' % (len(prerecs)))
        #if not prerecs:
        #    print '[]', re.sub('\n *\n', '\n', re.sub('  +', '', tocpage.text))


#statistics
totals = [(statistics[search]['total'], search) for search in list(statistics.keys())]
totals.sort()
if verbose: print('   tot hrv ded bin')
for (tot, search) in totals:
    if verbose: print(' - %3i %3i %3i %3i %s' % (tot, statistics[search]['harvested'], statistics[search]['dedicated'], statistics[search]['bereitsin'], search))
        
i = 0
recs = []
for rec in prerecs:
    i += 1
    english = False
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']]])
    try:
        time.sleep(10)
        req = urllib.request.Request(rec['artlink'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    except:
        try:
            print('\\\| wait 40s |///')
            time.sleep(40)           
            req = urllib.request.Request(rec['artlink'], headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    aff = False
    for table in artpage.find_all('table', attrs = {'id' : 'full'}):
        for tr in table.find_all('tr'):
            for th in tr.find_all('th'):
                tht = th.text.strip()
            for td  in tr.find_all('td'):
                tdt = td.text.strip()
                #title
                if tht == 'Title':
                    if re.search(' \/ ', tdt):                        
                        rec['tit'] = re.sub(' \/ .*', '', tdt)
                        rec['note'].append(re.sub('.* \/ ', '', tdt))
                    else:
                        rec['tit'] = tdt
                #author
                elif tht == 'Author':
                    tdt = re.sub(' \[Verfasser\]$', '', tdt)
                    rec['autaff'] = [[ tdt ]]
                elif tht == 'Authors':
                    rec['autaff'] = [[ re.sub(' \[.*', '', tdt) ]]
                #supervisor
                #elif tht == 'Contributor':
                #    rec['supervisor'].append([tdt])
                #keywords
                elif tht == 'Subject(s)':
                    rec['keyw'] = re.split('; ', tdt)
                #PID
                elif tht == 'Identifier':
                    if rehtml.search(tdt):
                        rec['weblinks'].append(tdt)
                    #URN
                    if reurn1.search(tdt):
                        rec['urn'] = reurn1.sub('', tdt)
                    if reurn2.search(tdt) or reurn2b.search(tdt):
                        rec['urn'] = tdt
                    if reurn3.search(tdt):
                        rec['urn'] = reurn3.sub(r'\1', tdt)
                    if reurn4.search(tdt):
                        rec['urn'] = reurn4.sub(r'\1', tdt)
                    #DOI
                    elif redoi1.search(tdt):
                        rec['doi'] = redoi1.sub(r'\1', tdt)
                    elif redoi2.search(tdt):
                        rec['doi'] = tdt
                    elif redoi3.search(tdt):
                        rec['doi'] = redoi3.sub(r'\2', tdt)
                    #ISBN
                    elif reisbn1.search(tdt):
                        rec['isbns'].append([('a', re.sub('\-', '', reisbn1.sub(r'\2', tdt)))])
                    elif reisbn2.search(tdt):
                        rec['isbns'].append([('a', re.sub('\-', '', tdt))])
                    #HDL
                    elif rehdl.search(tdt):
                        rec['hdl'] = rehdl.sub('', tdt)
                    elif repothdl.search(tdt):
                        if not 'hdl' in list(rec.keys()):
                            hdl = repothdl.sub(r'\1', tdt)
                            if not re.search('123456789\/', hdl):
                                #verify
                                try:
                                    req = urllib.request.Request('http://hdl.handle.net/' + hdl, headers=hdr)
                                    hdlpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
                                    for title in hdlpage.find_all('title'):
                                        if title.text.strip() == 'Not Found':
                                            rec['note'].append('%s seems not to be a proper HDL' % (hdl))
                                            rec['link'] = tdt
                                        else:
                                            rec['hdl'] = hdl
                                            rec['note'].append('%s seems to be a proper HDL' % (hdl))
                                except:
                                    rec['note'].append('could n ot check whether %s is a proper HDL' % (hdl))
                                    rec['link'] = tdt
                                    
                    #weblink
                    elif rehtml.search(tdt):
                        rec['link'] = tdt
                    #report number
                    elif reportnumber.search(tdt):
                        rec['rn'].append(tdt)
                    else:
                        rec['note'].append(tdt)
                #PID2
                elif tht == 'Relation':
                    for a in td.find_all('a'):
                        if a.has_attr('href'):
                            #DOI
                            if redoi1.search(a['href']):
                                rec['doi'] = redoi1.sub(r'\1', a['href'])
                            #HDL
                            elif rehdl.search(a['href']):
                                rec['hdl'] = rehdl.sub('', a['href'])
                            #URN
                            elif reurn3.search(a['href']):
                                rec['urn'] = reurn3.sub(r'\1', a['href'])
                #pages
                elif tht == 'Format':
                    if re.search('^\d+ p', tdt):
                        rec['pages'] = re.sub(' .*', '', tdt)
                #Abstract
                elif tht == 'Abstract':
                    rec['abs'] = tdt
                #language
                elif tht == 'Language':
                    rec['language'] = tdt
                #license
                elif tht == 'Rights':
                    if recc.search(tdt):
                        rec['license'] = {'url' : recc.sub(r'\1', tdt)}
    #author's affiliation
    if 'university' in list(rec.keys()):        
        if 'autaff' in list(rec.keys()):
            rec['autaff'][0].append(rec['university'])
        else:
            rec['autaff'] = [[ 'Mustermann, Max', rec['university'] ]]
    #discard 'additional' language
    if english and 'language' in list(rec.keys()):
        del rec['language']
    #do we need article link and/or pseudo-DOI
    checkweblinks(rec)
    if 'doi' in rec and get_recids('doi:%s' % (rec['doi'])):
        print('   skip "%s" since already in INSPIRE' % (rec['doi']))
    elif 'hdl' in rec and get_recids('persistent_identifiers.value:"%s"' % (rec['hdl'])):
        print('   skip "%s" since already in INSPIRE' % (rec['hdl']))
    else:
        recs.append(rec)
    if not 'doi' in rec and not 'hdl' in rec:
        if not 'link' in rec:
            rec['link'] = rec['artlink']
        if not 'urn' in list(rec.keys()):
            rec['doi'] = rec['nodoi']
    ejlmod3.printrecsummary(rec)
    if not 'autaff' in list(rec.keys()):
        sys.exit(0)
    if ((i % chunksize) == 0) or (i == len(prerecs)):
        chunknumber = (i-1)//chunksize + 1
        numofchunks = (len(recs) - 1) // chunksize + 1
        jnlfilename = 'THESES-DART_%s_%i-%i_%i_%03i-%03i' % (ejlmod3.stampoftoday(), years[0], years[-1], chunksize, chunknumber, numofchunks)
        crecs = recs[(chunknumber-1)*chunksize:chunknumber*chunksize]
        #closing of files and printing
        ejlmod3.writenewXML(crecs, publisher, jnlfilename)#, retfilename='retfiles_special')

#statistics
print('   tot hrv ded bin')
for (tot, search) in totals:
    print(' - %3i %3i %3i %3i  %s' % (tot, statistics[search]['harvested'], statistics[search]['dedicated'], statistics[search]['bereitsin'], search))
