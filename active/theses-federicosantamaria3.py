# -*- coding: utf-8 -*-
#harvest theses from Santa Maria U., Valparaiso
#FS: 2020-03-24
#FS: 2023-03-15

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import mechanize
import unicodedata

publisher = 'Santa Maria U., Valparaiso'
jnlfilename = 'THESES-SANTAMARIA-%s' % (ejlmod3.stampoftoday())

numberofpages = 1
recordsperpage = 50
skipalreadyharvested = True
wrongdepartments = ['Universidad Técnica Federico Santa María. Departamento de Arquitectura',
                    'Universidad Técnica Federico Santa María. Departamento de Electrónica',
                    'Universidad Técnica Federico Santa María. Departamento de Industrias',
                    'Universidad Técnica Federico Santa María. Departamento de Ingeniería Comercial',
                    'Universidad Técnica Federico Santa María. Departamento de Ingeniería Química y Ambiental',
                    'Universidad Técnica Federico Santa María. Departamento de Química']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []

prerecs = []
recs = []
for pn in range(numberofpages):
    tocurl = 'https://repositorio.usm.cl/handle/11673/21680/browse?rpp=' + str(recordsperpage) + '&sort_by=2&type=dateissued&offset=' + str(pn * recordsperpage) + '&etal=-1&order=DESC'
    ejlmod3.printprogress("=", [[pn+1, numberofpages], [tocurl]])
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features='lxml')
    prerecs += ejlmod3. getdspacerecs(tocpage, 'https://repositorio.usm.cl', alreadyharvested=alreadyharvested)
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(10)

i = 0
for rec in prerecs:
    wrongdegree = False
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DC.title', 'DCTERMS.issued', 'DCTERMS.extent',
                                        'DC.subject', 'DC.language', 'citation_pdf_url', 'DC.rights',
                                        'DCTERMS.abstract'])
    rec['autaff'][-1].append(publisher)
    for meta in artpage.find_all('meta'):
        if meta.has_attr('name') and meta.has_attr('content'):
            #supervisor
            if meta['name'] == 'DC.contributor':
                if meta.has_attr('xml:lang'):
                    rec['division'] = meta['content']
                    rec['note'].append(rec['division'])
                    if meta['content'] == 'Universidad Técnica Federico Santa María. Departamento de Informática':
                        rec['fc'] = 'c'
                    elif meta['content'] == 'Universidad Técnica Federico Santa María. Departamento de Matemática':
                        rec['fc'] = 'm'
                    elif meta['content'] in wrongdepartments:
                        #print('   ignore "%s"' % (meta['content']))
                        wrongdegree = True
                elif not rec['supervisor']:
                    rec['supervisor'].append([re.sub('([a-z])\.$', r'\1', meta['content'])])
            #thesis type
            elif meta['name'] == 'DC.description':
                rec['note'].append(meta['content'])
                if re.search('(Mag.ster|Licenciado|Licenciatura) en', meta['content'], re.IGNORECASE):
                    #print('   skip "%s"' % (meta['content']))
                    wrongdegree = True
    if  wrongdegree:
        ejlmod3.adduninterestingDOI(rec['hdl'])
    else:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
