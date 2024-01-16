# -*- coding: utf-8 -*-
#harvest theses from Universität Erlangen-Nürnberg
#FS: 2019-11-04
#FS: 2022-09-22
#FS: 2024-01-12

import getopt
import sys
import os
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json

skipalreadyharvested = True
pages = 15
rpp = 60
bunchsize = 10
years = 3


publisher = 'Erlangen - Nuremberg U.'

boring = ['Abteilung für Nephropathologie, Pathologisches Institut', 'Chair of Medicinal Chemistry',
          'Department Chemie und Pharmazie, Lehrstuhl für Organische Chemie II, Nikolaus-Fiebiger-Str. 10, 91058 Erlangen',
          'Department Chemie und Pharmazie, Lehrstuhl für Physikalische Chemie II',
          'Department Chemistry &a; Pharmacy', 'Department für Chemie und Pharmazie',
          'GeoZentrum Nordbayern, Department of Geography and Geosciences, Friedrich-Alexander University Erlangen-Nürnberg, Erlangen, Germany',
          'Medizinische Fakultät / Frauenklinik', 'Medizinische Fakultät / Hautklinik',
          'Medizinische Fakultät / Mikrobiologisches Institut - Klinische Mikrobiologie, Immunologie und Hygiene',
          'Medizinische Fakultät', 'Naturwissenschaftliche Fakultät / Department Biologie',
          'Naturwissenschaftliche Fakultät / Department Chemie und Pharmazie',
          'Universitätsklinikum Erlangen / Institut für Klinische und Molekulare Virologie',
          'Friedrich-Alexander-Universität Erlangen-Nürnberg (FAU) / Naturwissenschaftliche Fakultät / Department Chemie und Pharmazie Lehrstuhl für Physikalische Chemie I',
          'Medizinische Fakultät / Humangenetisches Institut',
          'Medizinische Fakultät / Institut für Biochemie',
          'Medizinische Fakultät / Medizinische Fakultät -ohne weitere Spezifikation-',
          'Medizinische Fakultät / Medizinische Klinik 5 - Hämatologie und Internistische Onkologie',
          'Medizinische Fakultät / Neurologische Klinik',
          'Medizinische Fakultät / Plastisch- und Handchirurgische Klinik',
          'Medizinische Fakultät / Radiologisches Institut',
          'Naturwissenschaftliche Fakultät / Department Geographie und Geowissenschaften']

recs = []
prerecs = []
jnlfilename = 'THESES-ERLANGEN-%s' % (ejlmod3.stampoftoday())

baseurl = 'https://open.fau.de'
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []


options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
options.headless=True
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)



recs = []
for page in range(pages):
    tocurl = 'https://open.fau.de/collections/ba3206ae-7d66-437a-91c5-dca309c94211?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    try:
        driver.get(tocurl)
        time.sleep(5)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
        divs = tocpage.find_all('div', attrs = {'class' : 'pagination-info'})
        1 / len(divs)
    except:
        print('  ... wait 60s')
        time.sleep(60)
        driver.get(tocurl)
        time.sleep(2)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    for div in tocpage.find_all('div', attrs = {'class' : 'pagination-info'}):
        for span in div.find_all('span'):
            spant = span.text.strip()
            if re.search('\d of \d', spant):
                total = int(re.sub('.*\d of (\d+).*', r'\1', spant))
                allpages = (total-1) // rpp + 1
                if allpages < pages:
                    pages = allpages
    for rec in ejlmod3.ngrx(tocpage, baseurl, ['dc.contributor.advisor', 'dc.contributor.author',
                                               'dc.date.issued', 'dc.rights.uri',
                                               'dc.contributor.department', 'dc.rights',
                                               'dc.description.abstract', 'dc.identifier.uri',
                                               'dc.subject', 'dc.title',  'thesis.degree.discipline',
                                               'thesis.degree.name', 'dc.language.iso', 'dc.provenance',
                                               'dc.type', 'local.subject.fakultaet'],
                            boring=boring, alreadyharvested=alreadyharvested, fakehdl=True):
        if 'DC.TYPE=article' in rec['note'] or 'DC.TYPE=preprint' in rec['note'] or 'DC.TYPE=review' in rec['note']:
            print('    skip non-thesis')
        else:
            if 'date' in rec:
                rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])
                if int(rec['year']) <= ejlmod3.year(backwards=years):
                    print('    skip %s' % (rec['year']))
                    continue
            #correct PDF-link and ORCIDs
            if 'link' in rec and 'pdf_url' in rec:
                driver.get(rec['link'])
                artpage = BeautifulSoup(driver.page_source, features="lxml")
                for ds in artpage.find_all('ds-file-download-link'):
                    for a in ds.find_all('a'):
                        if a.has_attr('href') and re.search('download', a['href']):
                            rec['pdf_url'] = baseurl + a['href']
                orcids = {}
                for a in artpage.find_all('a'):
                    if a.has_attr('href') and re.search('orcid.org\/\d{4}', a['href']):
                        orcid = re.sub('.*orcid.org\/', 'ORCID:', a['href'])
                        name = a.text.strip()
                        if name == rec['autaff'][0][0]:
                            rec['autaff'] = [[ name, orcid ]]
                        else:
                            orcids[name] = orcid
                if 'supervisor' in rec and orcids:
                    newsv = []
                    for sv in rec['supervisor']:
                        if sv[0] in orcids:
                            newsv.append([sv[0], orcids[sv[0]]])
                        else:
                            newsv.append(sv)
                    rec['supervisor'] = newsv
            rec['autaff'][-1].append(publisher)
            ejlmod3.printrecsummary(rec)
            #ejlmod3.printrec(rec)
            #print(rec['thesis.metadata.keys'])
            recs.append(rec)
    #ejlmod3.writenewXML(recs, publisher, jnlfilename + '.%03i_of_%i' % (page+1, pages), retfilename='retfiles_special')
    print('  %i records so far' % (len(recs)))
    if page >= pages:
        break
    time.sleep(20)
ejlmod3.writenewXML(recs, publisher, jnlfilename)



