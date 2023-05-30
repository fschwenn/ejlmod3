# -*- coding: utf-8 -*-
#harvest theses from CDS
#FS: 2022-09-27

import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
from inspirelabslib3 import *
import urllib3

urllib3.disable_warnings()

publisher = 'CERN'
rpp = 20
pages = 100
maxtries = 4
targetnumberoftheses = 20
skipalreadyharvested = True
jnlfilename = 'THESES-CDS-%s' % (ejlmod3.stampoftoday())

expdict = {'CMS' : 'CERN-LHC-CMS', 'CMS---CERN LHC' : 'CERN-LHC-CMS',
           'ATLAS' : 'CERN-LHC-ATLAS',
           'LHCb' : 'CERN-LHC-LHCb',
           'ALPHA AD-5' : 'CERN-ALPHA',
           'SHip' : 'CERN-SPS-SHIP',
           'COMPASS NA58' : 'CERN-NA-058',
           'TOTEM' : 'CERN-LHC-TOTEM',
           'ALICE' : 'CERN-LHC-ALICE',
           'SHINE NA61' : 'CERN-NA-061',
           'NA62' : 'CERN-NA-062',
           'nTOF' : 'CERN-nTOF',
           'ISOLTRAP' : 'CERN-ISOLTRAP',
           'RD39' : 'CERN-RD-039',
           'RD42' : 'CERN-RD-042',
           'RD44' : 'CERN-RD-044',
           'RD45' : 'CERN-RD-045',
           'RD46' : 'CERN-RD-046',
           'RD48' : 'CERN-RD-048',
           'RD49' : 'CERN-RD-049',
           'RD50' : 'CERN-RD-050',
           'RD51' : 'CERN-RD-051',
           'RD52' : 'CERN-RD-052',
           'RD53' : 'CERN-RD-053'}


if skipalreadyharvested:    
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}
recs = []
listofunknownsexps = []
for page in range(pages):
    tocurl = 'https://cds.cern.ch/search?jrec=' + str(page*rpp+1) + '&ln=en&p=037__a%3ACERN-THESIS-*+502__a%3Aphd+not+035__9%3Ainspire&action_search=Search&op1=a&m1=a&p1=&f1=&c=CERN+Document+Server&sf=year&so=d&rm=&rg=' + str(rpp) + '&sc=1&of=xm'
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    tocpage = False
    for j in range(maxtries):
        if not tocpage:
            try:
                req = urllib.request.Request(tocurl, headers=hdr)
                tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
            except:
                print(' try again (%i/%i)' % (j+2, maxtries))
                time.sleep(10)
    i = 0
    for record in tocpage.find_all('record'):
        i += 1
        keepit = True
        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : [], 'autaff' : [], 'rn' : [],
               'supervisor' : [], 'keyw' : []}
        #recID
        for cf in record.find_all('controlfield', attrs = {'tag' : '001'}):
            rec['recid'] = cf.text.strip()
            rec['link'] = 'https://cds.cern.ch/record/' + rec['recid']
            rec['doi'] = '30.3000/CDS/' + rec['recid']
            ejlmod3.printprogress('-', [[i, rpp], [i+page*rpp, pages*rpp], [rec['link']], [len(recs), targetnumberoftheses]])
        #DOI 
        for df in record.find_all('datafield', attrs = {'tag' : '024', 'ind1' : '7'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
                rec['doi'] = sf.text.strip()
                if skipalreadyharvested and rec['doi'] in alreadyharvested:
                    keepit = False
        #reportnumber
        for df in record.find_all('datafield', attrs = {'tag' : ['037', '088']}):
            for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
                rn = sf.text.strip()
                if re.search('^ISBN:', rn):
                    rec['isbn'] = rn
                elif re.search('^(urn|URN):', rn):
                    rec['urn'] = rn
                elif re.search('^CERN\-THES', rn):
                    inspire = perform_inspire_search_FS('report_numbers.value:'+rn)
                    if inspire:
                        keepit = False
                        print('    %s in INSPIRE' % (rn))
                    else:
                        rec['rn'].append(rn)
                        print('    %s' % (rn))
                else:
                    rec['rn'].append(rn)
        #author
        for df in record.find_all('datafield', attrs = {'tag' : '100'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
                rec['autaff'].append([sf.text.strip()])
            for sf in df.find_all('subfield', attrs = {'code' : 'm'}):
                rec['autaff'][-1].append('EMAIL:' + sf.text.strip())
            for sf in df.find_all('subfield', attrs = {'code' : 'u'}):
                rec['autaff'][-1].append(sf.text.strip())
        #supervisor
        for df in record.find_all('datafield', attrs = {'tag' : '701'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
                rec['supervisor'].append([sf.text.strip()])
            for sf in df.find_all('subfield', attrs = {'code' : 'u'}):
                rec['supervisor'][-1].append(sf.text.strip())
        #title
        for df in record.find_all('datafield', attrs = {'tag' : '245'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
                rec['tit'] = sf.text.strip()
        for df in record.find_all('datafield', attrs = {'tag' : '246'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
                rec['transtit'] = sf.text.strip()
        #date
        for df in record.find_all('datafield', attrs = {'tag' : '260'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'c'}):
                rec['date'] = sf.text.strip()
        #pages
        for df in record.find_all('datafield', attrs = {'tag' : '300'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
                rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', sf.text.strip())
        #pubnote
        for df in record.find_all('datafield', attrs = {'tag' : '502'}):
            marc = []
            for sf in df.find_all('subfield'):
                marc.append((sf['code'], sf.text.strip()))
                if sf['code'] == 'c' and not 'date' in rec:
                    rec['date'] = sf.text.strip()
            rec['MARC'] = [('502', marc)]
        #abstract
        for df in record.find_all('datafield', attrs = {'tag' : '520'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
                rec['abs'] = sf.text.strip()
        #experiment
        for df in record.find_all('datafield', attrs = {'tag' : '693'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'e'}):
                exp = sf.text.strip()
                if exp in ['CMS', 'ATLAS', 'LHCb', 'ALPHA AD-5', 'SHip', 'COMPASS NA58', 'CMS---CERN LHC', 'TOTEM']:
                    rec['fc'] = 'e'
                elif exp in ['ALICE', 'SHINE NA61', 'NA62']:
                    rec['fc'] = 'xe'
                elif exp in ['nTOF', 'ISOLTRAP', 'ISOL']:
                    rec['fc'] = 'x'
                if exp in expdict:
                    rec['exp'] = expdict[exp]
                else:
                    if not exp in listofunknownsexps:
                        listofunknownsexps.append(exp)
                    if keepit:
                        print('    unknown experiment "%s"' % (exp))                                            
        #fulltext
        for df in record.find_all('datafield', attrs = {'tag' : '856', 'ind1' : '4'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'u'}):
                if re.search('\.pdf$', sf.text):
                    rec['FFT'] = sf.text
        #keywords
        for df in record.find_all('datafield', attrs = {'tag' : '653', 'ind1' : '1'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
                rec['keyw'].append(sf.text.strip())
        #language
        for df in record.find_all('datafield', attrs = {'tag' : '041'}):
            for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
                rec['language'] = sf.text.strip()
        #
        #for df in record.find_all('datafield', attrs = {'tag' : '', 'ind1' : ''}):
        #    for sf in df.find_all('subfield', attrs = {'code' : 'a'}):
        #        rec[''] = sf.text.strip()
        if keepit:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    if len(recs) >= targetnumberoftheses:
        break
    time.sleep(5)

ejlmod3.writenewXML(recs, publisher, jnlfilename, retfilename='retfiles_special')

for exp in listofunknownsexps:
    if exp != 'Not applicable':
        print('%-20s https://inspirehep.net/experiments?sort=mostrecent&size=25&page=1&q=%s' % (exp, exp))
