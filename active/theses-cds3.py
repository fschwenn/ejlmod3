# -*- coding: utf-8 -*-
#harvest theses from CDS
#FS: 2022-09-27

import urllib.request, urllib.error, urllib.parse
import urllib.parse
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
targetnumberoftheses = 20
jnlfilename = 'THESES-CDS-%s' % (ejlmod3.stampoftoday())

hdr = {'User-Agent' : 'Magic Browser'}
recs = []
listofunknownsexps = []
for page in range(pages):
    tocurl = 'https://cds.cern.ch/search?jrec=' + str(page*rpp+1) + '&ln=en&p=037__a%3ACERN-THESIS-*+502__a%3Aphd+not+035__9%3Ainspire&action_search=Search&op1=a&m1=a&p1=&f1=&c=CERN+Document+Server&sf=year&so=d&rm=&rg=' + str(rpp) + '&sc=1&of=xm'
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
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
                elif exp in ['CMS', 'CMS---CERN LHC']:
                    rec['exp'] = 'CERN-LHC-CMS'
                elif exp == 'ATLAS':
                    rec['exp'] = 'CERN-LHC-ATLAS'
                elif exp == 'LHCb':
                    rec['exp'] = 'CERN-LHC-LHCb'
                elif exp == 'ALPHA AD-5':
                    rec['exp'] = 'CERN-ALPHA'
                elif exp == 'SHip':
                    rec['exp'] = 'CERN-SPS-SHIP'
                elif exp == 'COMPASS NA58':
                    rec['exp'] = 'CERN-NA-058'
                elif exp == 'TOTEM':
                    rec['exp'] = 'CERN-LHC-TOTEM'
                elif exp == 'ALICE':
                    rec['exp'] = 'CERN-LHC-ALICE'
                elif exp == 'SHINE NA61':
                    rec['exp'] = 'CERN-NA-061'
                elif exp == 'NA62':
                    rec['exp'] = 'CERN-NA-062'
                elif exp == 'nTOF':
                    rec['exp'] = 'CERN-nTOF'
                elif exp == 'ISOLTRAP':
                    rec['exp'] = 'CERN-ISOLTRAP'
                elif exp == 'RD50':
                    rec['exp'] = 'CERN-RD-050'
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
