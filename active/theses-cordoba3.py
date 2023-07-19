# -*- coding: utf-8 -*-
#harvest theses Cordoba U.
#FS: 2023-07-17

import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Cordoba U..'
jnlfilename = 'THESES-CORDOBA-%s' % (ejlmod3.stampoftoday())
rpp = 10
numofpages = 1
years = 2*10
skipalreadyharvested = True

boring = ['bachelorThesis', 'masterThesis']


if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested =  []

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for (dep, fc) in  [('16537', 'a'), ('16541', 'c'), ('16536', ''), ('16535', 'm')]:
    for page in range(numofpages):
        tocurl = 'https://rdu.unc.edu.ar/handle/11086/' + dep + '/browse?rpp=' + str(rpp) + '&sort_by=2&type=dateissued&offset=' + str(rpp * page) + '&etal=-1&order=DESC'
        ejlmod3.printprogress('=', [[dep], [page+1, numofpages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(5)
        for rec in ejlmod3.getdspacerecs(tocpage, 'https://rdu.unc.edu.ar', alreadyharvested=alreadyharvested):
            if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
                continue
            if fc:
                rec['fc'] = fc
            prerecs.append(rec)
        print('  %4i records so far' % (len(prerecs)))
            
j = 0
recs = []
for rec in prerecs:
    j += 1
    keepit = True
    ejlmod3.printprogress('-', [[j, len(prerecs)], [rec['link']], [len(recs)]])
    req = urllib.request.Request(rec['link'] + '?show=full')
    artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(5)
    ejlmod3.metatagcheck(rec, artpage, ['DC.identifier', 'DCTERMS.issued', 'DCTERMS.abstract',
                                        'DC.language', 'DC.rights', 'citation_pdf_url', #'citation_isbn',
                                        'citation_title', 'DC.creator', 'DC.subject'])
    rec['autaff'][-1].append(publisher)                        
    for tr in artpage.find_all('tr'):
        tdlabel = ''
        for td in tr.find_all('td', attrs = {'class' : 'label-cell'}):
            tdlabel = td.text.strip()
            td.decompose()
            #supervisor
            if tdlabel == 'dc.contributor.advisor':
                for td2 in tr.find_all('td'):
                    if len(td2.text) > 6:
                        rec['supervisor'].append([td2.text.strip()])
            #degree
            elif tdlabel == 'dc.type':
                for td2 in tr.find_all('td'):
                    deg = td2.text.strip()
                    if deg in boring:
                        keepit = False
                    elif not deg in ['es', 'en', 'doctoralThesis']:
                        rec['note'].append('DEG:::' + deg)
    if keepit:    
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
