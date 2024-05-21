# -*- coding: utf-8 -*-
#harvest theses from Barcelona, Autonoma U.
#FS: 2019-09-15
#FS: 2023-01-28

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Barcelona, Autonoma U.'
jnlfilename = 'THESES-TDX-%s' % (ejlmod3.stampoftoday())

sections = [('396268', ''), ('65', ''), ('668603', ''),
            ('178', 'c'), ('123', 'm'), ('668614', 'm')]
sections.append(('95809', ''))
sections.append(('31843', 'm'))
sections.append(('84', 'm'))
sections.append(('386309', 'mc'))

rpp = 10
pages = 2
years = 3 
skipalreadyharvested = True

alreadyharvested = []
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename) + ejlmod3.getalreadyharvested('THESES-BarcelonaAutonomaU')

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for (section, fc) in sections:
    for page in range(pages):
        tocurl = 'https://www.tdx.cat/handle/10803/' + section + '/discover?rpp=' + str(rpp) + '&etal=0&scope=&group_by=none&page=' + str(page+1) + '&sort_by=dc.date.issued_dt&order=desc&filtertype_0=dateIssued&filter_relational_operator_0=equals&filter_0='    
        ejlmod3.printprogress('=', [[section], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        for rec in ejlmod3.getdspacerecs(tocpage, 'https://www.tdx.cat', divclass='media-body'):
            if fc: rec['fc'] = fc
            if not rec['hdl'] in alreadyharvested:
                prerecs.append(rec)
                alreadyharvested.append(rec['hdl'])
        print('  %4i records so far' % (len(prerecs)))
        time.sleep(3)
        
recs = []
for (i, rec) in enumerate(prerecs):
    ejlmod3.printprogress("-", [[i+1, len(prerecs)], [rec['link']], [len(recs)]])
    keepit = True
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(13)
        ejlmod3.metatagcheck(rec, artpage, ['DCTERMS.issued'])
        rec['date']
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'DC.subject', 'DCTERMS.extent',
                                        'DC.rights', 'DC.language', 'citation_pdf_url', 'DC.identifier'])
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.creator'}):
        author = re.sub(' *\[.*', '', meta['content'])
        rec['autaff'] = [[ author ]]
        if re.search('\[UNESP\]', meta['content']):
            rec['autaff'][-1].append('Universidade Estadual Paulista (UNESP), Instituto de Fisica Teorica (IFT), 01140-070, Sao Paulo, Brazil')
    if len(rec['autaff'][0]) == 1:
        rec['autaff'][-1].append(publisher)
#    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DC.contributor'}):
#        rec['note'].append('INST:::' + meta['content'])
    if not 'fc' in rec:
        for div in artpage.body.find_all('div', attrs = {'class' : 'element'}):
            for h4 in div.find_all('h4'):
                h4t = h4.text.strip()
                if h4t == 'Subjects':
                    for p in div.find_all('p'):
                        subject = p.text.strip()
                        if subject == '004 - Computer science and technology. Computing. Data processing':
                            rec['fc'] = 'c'
                        elif subject in ['512 - Algebra', '515.1 - Topology',
                                         '517 - Analysis', '519.1 - Combinatorial analysis. Graph theory']:
                            rec['fc'] = 'm'
                        elif subject in ['538.9 - Condensed matter physics. Solid state physics']:
                            rec['fc'] = 'f'
                        elif subject in ['52 - Astronomy. Astrophysics. Space research. Geodesy']:
                            rec['fc'] = 'a'
                        elif subject in ['573 - General and theoretical biology',
                                         '577 - Material bases of life. Biochemistry. Molecular biology. Biophysics',
                                         '616 - Pathology. Clinical medicine',
                                         '93 - History. Auxiliary sciences of history. Local History']:
                            keepit = False
                        else:
                            rec['note'].append('SUBJECT:::' + p.text.strip())
                elif h4t == 'Note':
                    for p in div.find_all('p'):
                        rec['note'].append('NOTE:::' + p.text.strip())
    if keepit:
        if 'years' in rec and int(rec['years']) <= ejlmod3.year(backwards=years):
            print('  too old')
        else:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])
	
ejlmod3.writenewXML(recs, publisher, jnlfilename)
