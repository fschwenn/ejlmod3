# -*- coding: utf-8 -*-
#harvest theses from bdtd.ibict.br
#FS: 2020-01-06

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

startyear = ejlmod3.year(backwards=1)
stopyear =  ejlmod3.year()

subject = sys.argv[1]
skipalreadyharvested = True

filters = {'physics' : (2, 'dc.subject.por.fl_str_mv%3A%22F%C3%ADsica%22', ''),
           'comp' : (2, 'dc.publisher.program.fl_str_mv%3A%22Ci%C3%AAncias%2Bda%2BComputa%C3%A7%C3%A3o%2Be%2BMatem%C3%A1tica%2BComputacional%22', 'c'),
           'math' : (2, 'dc.publisher.program.fl_str_mv%3A%22Matem%C3%A1tica%22', 'm'),
           'nucl' : (2, 'dc.subject.por.fl_str_mv%3A%22F%C3%ADsica+nuclear%22', ''),
           'physpost' : (3, 'dc.publisher.program.fl_str_mv%3A%22Programa+de+P%C3%B3s-Gradua%C3%A7%C3%A3o+em+F%C3%ADsica%22', ''),
           'physics2' : (2, 'dc.publisher.program.fl_str_mv%3A%22F%C3%ADsica%22', ''),
           'cnpq' : (2, 'dc.subject.cnpq.fl_str_mv%3A%22CNPQ%3A%3ACIENCIAS+EXATAS+E+DA+TERRA%3A%3AFISICA%22', '')}



  

hdr = {'User-Agent' : 'Magic Browser'}
publisher = 'publisher'
jnlfilename = 'THESES-IBICT-%s_%s' % (subject, ejlmod3.stampoftoday())

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested('THESES')

numberofpages = filters[subject][0]
prerecs = []
for i in range(numberofpages):
    tocurl = 'http://bdtd.ibict.br/vufind/Search/Results?filter%5B%5D=format%3A%22doctoralThesis%22&filter%5B%5D=' + filters[subject][1] + '&filter%5B%5D=publishDate%3A%22%5B' + str(startyear) + '+TO+' + str(stopyear) + '%5D%22&lookfor=%2A%3A%2A&type=AllFields&page=' + str(i+1)
    ejlmod3.printprogress('=', [[i+1, numberofpages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    time.sleep(10)
    for div in tocpage.body.find_all('div', attrs = {'class' : 'result'}):
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'notes' : []}
        for a in div.find_all('a', attrs = {'class' : 'title'}):
            rec['tit'] = a.text.strip()
            rec['artlink'] = 'http://bdtd.ibict.br' + a['href']
            rec['doi'] = '20.2000/IBICT/' + re.sub('\W', '', a['href'][15:])
            if filters[subject][2]:
                rec['fc'] = filters[subject][2]
        if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
            prerecs.append(rec)
        

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        req = urllib.request.Request(rec['artlink'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    for table in artpage.body.find_all('table'):
        for tr in table.find_all('tr'):
            for th in tr.find_all('th'):
                tht = th.text.strip()
            for td in tr.find_all('td'):
                #date
                if tht == 'Data de Defesa:':
                    rec['date'] = td.text.strip()
                #author
                elif tht == 'Autor/a:':
                    rec['auts'] = [ td.text.strip() ]
                #language
                elif tht == 'Idioma:':
                    rec['language'] = td.text.strip()
                #link
                elif tht in ['Download Texto Completo:', 'Online Access:']:
                    for a in tr.find_all('a'):
                        if re.search('orcid.org', a['href']):
                            continue
                        elif re.search('handle.net\/', a['href']):
                            rec['hdl'] = re.sub('.*handle.net\/', '', a['href'])
                            del(rec['doi'])
                        rec['link'] = a['href']
                        if re.search('teses\.usp\.br', a['href']):
                            rec['notes'].append('should also be harvested by theses-saopaulo.py')
                        elif re.search('repositorio\.unesp\.br', a['href']):
                            rec['notes'].append('should also be harvested by theses-unsep.py')
                #aff
                elif re.search('Institui', tht):
                    rec['aff'] = [ td.text.strip() + ', Brasil' ]
                #keywords
                elif re.search('Assuntos em Ingl', tht):
                    for a in tr.find_all('a'):
                        rec['keyw'].append(a.text.strip())
                #abstract
                elif re.search('Resumo ingl', tht):
                    rec['abs'] = td.text.strip()
    #abstract
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'DCTERMS.abstract', 'xml:lang' : 'en'}):
        rec['abs'] = meta['content']
    if not 'abs' in rec:
        for meta in artpage.head.find_all('meta', attrs = {'name' : 'DCTERMS.abstract', 'xml:lang' : 'pt-br'}):
            rec['abs'] = meta['content']
    #try direct link
    if 'link' in rec:
        try:
            artpage2 = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
            time.sleep(3)
        except:
            try:
                print("retry %s in 180 seconds" % (rec['link']))
                time.sleep(180)
                artpage2 = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
            except:
                print("no access to %s" % (rec['link']))
                continue
        ejlmod3.metatagcheck(rec, artpage2, ['citation_pdf_url', 'citation_doi', 'DCTERMS.abstract',
                                             'citation_keywords', 'citation_date', 'DC.identifier'])
    else:
        rec['link'] = rec['artlink']        
    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
