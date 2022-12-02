# -*- coding: utf-8 -*-
#harvest theses from Iceland U.
#FS: 2022-11-21

import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Iceland U.'
jnlfilename = 'THESES-ICELAND-%s' % (ejlmod3.stampoftoday())
rpp = 20
numofpages = 1
years = 2

hdr = {'User-Agent' : 'Magic Browser'}
recs = []
for dep in ['Faculty+of+Physical+Sciences+%28UI%29',
            'Faculty+of+Industrial+Eng.%2C+Mechanical+Eng.+and+Computer+Science+%28UI%29',
            'Faculty+of+Industrial+Eng.%2C+Mechanical+Eng.+and+Computer+Sciences+%28UI%29']:
    for page in range(numofpages):
        tocurl = 'https://opinvisindi.is/handle/20.500.11815/84/browse?type=department&value=' + dep + '&rpp=' + str(rpp) + '&offset=' + str(rpp*page) + '&sort_by=2&type=dateissued&etal=-1&order=DESC'
        ejlmod3.printprogress('=', [[dep], [page+1, numofpages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(5)
        for rec in ejlmod3.getdspacerecs(tocpage, 'https://opinvisindi.is'):
            if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
                continue
            recs.append(rec)
        print('  %4i records so far' % (len(recs)))
            
j = 0
for rec in recs:
    j += 1
    ejlmod3.printprogress('-', [[j, len(recs)], [rec['link']]])
    req = urllib.request.Request(rec['link'] + '?show=full')
    artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(5)
    ejlmod3.metatagcheck(rec, artpage, ['DC.identifier', 'DCTERMS.issued', 'DCTERMS.abstract',
                                        'DC.language', 'DC.rights', 'citation_pdf_url', #'citation_isbn',
                                        'citation_title', 'citation_author', 'DC.subject'])
    rec['autaff'][-1].append(publisher)                        
    for tr in artpage.find_all('tr'):
        tdlabel = ''
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            tdlabel = td.text.strip()
            td.decompose()
            orcid = False
        if tdlabel in ['dc.contributor.advisor', 'dc.contributor.author']:
            for td in tr.find_all('td'):
                for a in td.find_all('a'):
                    if a.has_attr('href') and re.search('orcid.org', a['href']):
                        orcid = re.sub('.*orcid.org\/', 'ORCID:', a['href'])
                        a.decompose()
                #supervisor
                if tdlabel == 'dc.contributor.advisor':
                    if len(td.text) > 6:
                        rec['supervisor'].append([td.text.strip()])
                        if orcid:
                            rec['supervisor'][-1].append(orcid)
                #author
                if tdlabel == 'dc.contributor.author':
                    if len(td.text) > 6:
                        rec['autaff'] = [[td.text.strip()]]
                        if orcid:
                            rec['autaff'][-1].append(orcid)
                        rec['autaff'][-1].append(publisher)
    #clean keywords
    if 'keyw' in rec:
        kws = [kw for kw in rec['keyw'] if kw != 'Doktorsritgerðir']
        rec['keyw'] = kws
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
