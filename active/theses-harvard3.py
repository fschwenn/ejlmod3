# -*- coding: utf-8 -*-
#harvest theses from Harvard
#FS: 2020-01-14
#FS: 2023-03-14

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import undetected_chromedriver as uc

publisher = 'Harvard U. (main)'
jnlfilename = 'THESES-HARVARD-%s' % (ejlmod3.stampoftoday())

rpp = 40
years = 2
skipalreadyharvested = True
departments = [('m', 'Mathematics', 1), ('', 'Physics', 1),
               ('a', 'Astronomy', 1), ('c', 'Computer+Science', 1),
               ('', '_ALL_', 10)]
bunchsize = 10


boring = ['Social+Policy', 'Chemistry+and+Chemical+Biology', 'Medical+Sciences',
          'Population+Health+Sciences', 'Anthropology', 'History+of+Art+and+Architecture',
          'Economics', 'Biology%2C+Molecular+and+Cellular', 'Government',
          'English', 'German', 'French', 'Spanish', 'Public+Policy', 
          'East+Asian+Languages+and+Civilizations', 'Music', 'American+Studies',
          'History', 'Slavic+Languages+and+Literatures', 'Education', 'Chemical+Biology',
          'Architecture%2C+Landscape+Architecture+and+Urban+Planning',
          'Organizational+Behavior', 'Middle+Eastern+Studies+Committee',
          'Systems+Biology', 'Sociology', 'Linguistics', 'Business+Administration',
          'Religion%2C+Committee+on+the+Study+of', 'Comparative+Literature',
          'Psychology', 'Biology%2C+Organismic+and+Evolutionary', 'Biostatistics',
          'African+and+African+American+Studies', 'Romance+Languages+and+Literatures',
          'Classics', 'Health+Policy', 'Political+Economy+and+Government',
          'South+Asian+Studies', 'Near+Eastern+Languages+and+Civilizations',
          'Germanic+Languages+and+Literatures', 'Business+Economics',
          'Biological+Sciences+in+Public+Health', 'Film+and+Visual+Studies',
          'Human+Evolutionary+Biology', 'Biological+Sciences+in+Dental+Medicine',
          'Inner+Asian+and+Altaic+Studies', 'Biophysics', 'Celtic+Languages+and+Literatures']


options = uc.ChromeOptions()
options.binary_location='/opt/google/chrome/google-chrome'
#options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)
#driver = uc.Chrome( options=options)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []
hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
fakedois = ['30.3000/' + re.sub('\W', '',  'https://dash.harvard.edu') + '/1/37370210']
for (fc, dep, numofpages) in departments:
    for i in range(numofpages):
        if dep == '_ALL_':
            tocurl = 'https://dash.harvard.edu/handle/1/4927603/browse?rpp=%i&sort_by=2&type=dateissued&offset=%i&etal=-1&order=DESC' % (rpp, i*rpp)
        else:
            tocurl = 'https://dash.harvard.edu/handle/1/4927603/browse?type=department&value=%s&rpp=%i&sort_by=2&type=dateissued&offset=%i&etal=-1&order=DESC' % (dep, rpp, i*rpp)
        ejlmod3.printprogress("-", [[dep], [i+1, numofpages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(10)
        for rec in ejlmod3.getdspacerecs(tocpage, 'https://dash.harvard.edu', fakehdl=True, alreadyharvested=alreadyharvested, boringdegrees=boring):
            if fc: rec['fc'] = fc
            if not rec['doi'] in fakedois:
                #department
                if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
                    print('    skip "%s"' % (rec['year']))
                else:
                    prerecs.append(rec)
                    fakedois.append(rec['doi'])
        print('  %4i records so far' % (len(prerecs)))
            
j = 0
recs = []
for rec in prerecs:
    j += 1
    keepit = True

    ejlmod3.printprogress("-", [[j, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        driver.get(rec['link'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        print('wait a minute')
        driver.get(rec['link'])
        artpage = BeautifulSoup(driver.page_source, features="lxml")
    time.sleep(5)
    #author
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'DC.date', 'DCTERMS.abstract',
                                        'citation_pdf_url', 'citation_keywords'])
    for info in rec['infos']:
        if re.search('rft.author=.*%40', info):
            rec['autaff'][-1].append(re.sub('.*=(.*)%40(.*)', r'EMAIL:\1@\2', info))
        elif re.search('rft_id=\d\d\d\d\-\d\d\d\d\-', info):
            rec['autaff'][-1].append(re.sub('.*=', 'ORCID:', info))
    rec['autaff'][-1].append(publisher)
    
    #URN
    for meta in artpage.find_all('meta', attrs = {'name' : 'DC.identifier'}):
        if meta.has_attr('scheme'):
            if re.search('URI', meta['scheme']):
                rec['urn'] = re.sub('.*harvard.edu\/', '', meta['content'])
                if skipalreadyharvested and rec['urn'] in alreadyharvested:
                    keepit = False
                    print('  %s already in backup' % (rec['urn']))
                else:
                    rec['link'] = meta['content']
            else:
                rec['note'].append(meta['content'])
    if not 'urn' in list(rec.keys()):
        rec['doi'] = '20.2000/Harvard' + re.sub('.*\/', '', rec['link'])
        if skipalreadyharvested and rec['doi'] in alreadyharvested:
            keepit = False
            print('  %s already in backup' % (rec['doi']))
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    if len(recs) % bunchsize == 0:
        ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize))


if len(recs) % bunchsize != 0:
    ejlmod3.writenewXML(recs[((len(recs)-1) // bunchsize)*bunchsize:], publisher, jnlfilename + '--%04i' % (1 + (len(recs)-1) // bunchsize))



#ejlmod3.writenewXML(recs, publisher, jnlfilename)
