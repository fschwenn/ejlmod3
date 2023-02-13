# -*- coding: utf-8 -*-
#harvest theses from Witwatersrand U.
#FS: 2020-11-17
#FS: 2023-01-11
import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

publisher = 'Witwatersrand U.'

rpp = 100
pages = 6
skipalreadyharvested = True

boringfacs = ['Faculty of Engineering and the Built Environment',
              'Faculty of Health Sciences', 'Faculty of Commerce',
              'Faculty of Humanities', 'School of Literature',
              'School of Social Sciences', 'Faculty of the Humanities',
              'Faculty of Engineering and the Built Environment',
              'Faculty of Humanities at the University of the Witwatersrand',
              'School of Physiology', 'School of Geography',
              'Faculty of Humanities University of the Witwatersrand',
              'School of Public Health', 'School of Geoscience',
              'School of Construction Economics and Management',
              'School of Chemical and Metallurgical Engineering',
              'School of Economic and Business Sciences',
              'Faculty of health science', 'Faculty of Humanities',
              'Faculty of Health Sciences', 'Faculty of commerce',
              'Faculty of Engineering and the Built Environment',
              'School of Geosciences', 'Faculty of Health Science',
              'School of Architecture and Planning',
              'Faculty of Engineering and Built Environment',
              'Faculty of Humanities at the University of Witwatersrand',
              'School of Chemistry']
boringfacs += ['Faculty of Science School of Geography, Archaeology and Environmental Studies',
               'Graduate School of Business Administration',
               '/ School of Accountancy', '/School of Accountancy',
               'School of Accountancy', 'School of Accounting',
               'School of Anatomical Sciences',
               'School of Animal, Plant and Environmental Sciences',
               'School of Animal, Plant and Environmental Sciences,',
               'School of Business Administration',
               'School of Business and Economic Sciences',
               'School of Business and Governance',
               'School of Business and Management Sciences',
               'School of Business School &a; School of Governance',
               'School of Business Sciences', 'School of Business',
               'School of Chemistry', 'School of Clinical Medicine',
               'School of Developmental Studies', 'School of Digital Business',
               'School of Economic and Business Sciences', 'School of Economic and Finance',
               'School of Economic and Management Sciences', 'School of Economics and Finance',
               'School of Geography, Archaeology &a; Environmental Science',
               'School of Geography, Archaeology &a; Environmental Studies',
               'School of Geography, Archaeology and Environmental Sciences',
               'School of Geography, Archaeology and Environmental studies',
               'School of Geography, Archaeology and Environmental Studies',
               'School of Geography, Archaeology, and Environmental Studies',
               'School of Geography, Archeology and Environmental Studies',
               'School of Governance', 'School of Law',
               'School of Literature, Language and Media',
               'School of Mining Engineering',
               'School of Molecular and Cell Biology',
               'School of Pathology', 'Wits Business School and School of Governance',
               'Wits Business School', 'WITS Graduate School of Governance',
               'Wits School of Governance', 'Witwatersrand Business School']
reboring = [re.compile('[Rr]equirement.* [Dd]egree .*(Master|Bachelor|MSc|M.Sc.|M.Ed.)'),
            re.compile('[Pp]artial [Ff]ull?fill?ment.* [Dd]egree.*(Master|Bachelor|master|bachelor|MSc|M.Sc.|M.Ed.)'),
            re.compile('[sS]ubmitted.* [Ff]ull?fill?ment.*(Master|Bachelor|master|bachelor|MSc|M.Sc.|M.Ed.)'),
            re.compile('[sS]ubmitted.* [dD]egree.*(Master|Bachelor|master|bachelor|MSc|M.Sc.|M.Ed.)'),
            re.compile('partial fulfilment of an? (Master|Bachelor|master|bachelor|MSc|M.Sc.|M.Ed.)')]
hdr = {'User-Agent' : 'Magic Browser'}
jnlfilename = 'THESES-WITWATERSRAND-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

recs = []
allhdls = []
for page in range(pages):
    #http://wiredspace.wits.ac.za/handle/10539/45/
    tocurl = 'https://wiredspace.wits.ac.za/browse/dateissued?scope=1534a1c1-070b-46da-8296-11820af70170&bbm.page=' + str(page+1) +'&bbm.rpp=' + str(rpp) + '&bbm.sd=DESC'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    try:
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    except:
        print("retry in 300 seconds")
        time.sleep(300)
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for rec in ejlmod3.ngrx(tocpage, 'http://wiredspace.wits.ac.za', ['dc.contributor.author', 'dc.date.issued',
                                                                      'dc.description.abstract', 'dc.faculty',
                                                                      'dc.identifier.uri', 'dc.language.iso',
                                                                      'dc.phd.title', 'dc.school', 'dc.title',
                                                                      'dc.type', 'dc.description'], boringfacs):
        rec['autaff'][-1].append(publisher)
        keepit = True
        #check backup
        if rec['hdl'] in alreadyharvested:
            print('   %s already in backup' % (rec['hdl']))
            continue
        elif rec['hdl'] in allhdls:
            print('   %s already in list' % (rec['hdl']))
            continue
        #check PhD
        if 'dc.type' in rec and rec['dc.type'] in ['Article']:
            keepit = False            
        elif 'degree' in rec and (('PHD' in rec['degree']) or ('PhD' in rec['degree'])):
            pass
        elif 'description' in rec:
            for rebo in reboring:
                if keepit and rebo.search(re.sub(',', '', rec['description'])):
                    keepit = False
            if keepit:
                print('   ->', rec['description'])
        #fieldcodr
        for fac in rec['fac']:
            if fac in ['School of Mathematics']:
                rec['fc'] = 'm'
            elif fac in ['School of Statistics and Actuarial Science']:
                rec['fc'] = 's'
        if keepit:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
        else:
            ejlmod3.adduninterestingDOI(rec['hdl'])
    print('  %4i records so far' % (len(recs)))
    time.sleep(3)
    
ejlmod3.writenewXML(recs, publisher, jnlfilename)
