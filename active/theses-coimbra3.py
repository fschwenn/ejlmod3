# -*- coding: utf-8 -*-
#harvest theses from Coimbra U.
#FS: 2020-08-25
#FS: 2023-03-13

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Coimbra U.'
jnlfilename = 'THESES-COIMBRA-%s' % (ejlmod3.stampoftoday())

numberofpages = 1
rpp = 100
skipalreadyharvested = True

boringdepartments = ['00502UniversidadedeCoimbraFaculdadedeDireito',
                     '00505UniversidadedeCoimbraFaculdadedeLetras',
                     '00503UniversidadedeCoimbraFaculdadedeEconomia',
                     '00506UniversidadedeCoimbraFaculdadedeMedicina',
                     '00507UniversidadedeCoimbraFaculdadedePsicologiaedeCinciasdaEducao',
                     '00507UniversidadedeCoimbraFaculdadedePsicologiaedeCiênciasdaEducação',
                     '00508UniversidadedeCoimbraFaculdadedeCinciasdoDesportoeEducaoFsica',
                     '00508UniversidadedeCoimbraFaculdadedeCiênciasdoDesportoeEducaçãoFísica',
                     '00509UniversidadedeCoimbraColgiodasArtes',                     
                     '00509UniversidadedeCoimbraColégiodasArtes',
                     '0505UniversidadedeCoimbraFaculdadedeLetras']

prerecs = []
recs = []
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
for pn in range(numberofpages):
    tocurl = 'https://estudogeral.sib.uc.pt/handle/10316/15519/browse?type=dateissued&sort_by=2&order=DESC&rpp=' + str(rpp) + '&etal=0&submit_browse=Update&offset='+ str(pn * rpp)
    ejlmod3.printprogress("=", [[pn+1, numberofpages], [tocurl]])
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features="lxml") 
    for tr in tocpage.body.find_all('tr'):
        year = ejlmod3.year()
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : [],
               'oa' : False, 'department' : []}
        #Open Access
        for td in tr.find_all('td', attrs = {'headers' : 't5'}):            
            if re.search('openAccess', td.text):
                rec['oa'] = True
        #year
        for td in tr.find_all('td', attrs = {'headers' : 't1'}):
            if re.search('\d', td.text):
                year = int(re.sub('.*([12]\d\d\d).*', r'\1', td.text.strip()))
        if year > ejlmod3.year(backwards=2):
            for td in tr.find_all('td', attrs = {'headers' : 't2'}):
                for a in td.find_all('a'):
                    if re.search('handle\/\d', a['href']):
                        rec['artlink'] = 'https://estudogeral.sib.uc.pt' + a['href'] + '?mode=full'
                        rec['hdl'] = re.sub('.*handle\/(.*\d).*', r'\1', a['href'])
                        if skipalreadyharvested and rec['hdl'] in alreadyharvested:
                            pass
                        elif ejlmod3.checkinterestingDOI(rec['hdl']):
                            prerecs.append(rec)
    time.sleep(5)



i = 0
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue        
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'citation_title', 'DCTERMS.issued',
                                        'DCTERMS.issued', 'DC.subject', 'DC.language',
                                        'citation_pdf_url', 'DC.rights'])
    for meta in artpage.find_all('meta'):
        if meta.has_attr('name') and meta.has_attr('content'):
            #supervisor
            if meta['name'] == 'DC.contributor':
                if meta.has_attr('xml:lang'):
                    rec['division'] = meta['content']
                    rec['note'].append(rec['division'])
                else:
                    rec['supervisor'].append([meta['content']])
            #abstract
            elif meta['name'] == 'DCTERMS.abstract':
                if re.search(' the ', meta['content']): 
                    rec['abs'] = meta['content']
                else:
                    rec['abspt'] = meta['content']
    if not 'abs' in list(rec.keys()):
        if 'abspt' in list(rec.keys()):
            rec['abs'] = rec['abspt']
    for tr in artpage.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldLabel'}):
            tdt = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldValue'}):
            #ORCID of supervisors (dont know to whom of the advisors it belong)
            if tdt == 'crisitem.advisor.orcid':
                pass
            #ORCID of author
            elif tdt == 'crisitem.author.orcid':
                rec['autaff'][-1].append('ORCID:' + td.text.strip())
            #department
            elif tdt == 'thesis.degree.grantorUnit':
                dep = re.sub('\W', '', td.text.strip())
                if dep:
                    rec['department'].append(dep)
                    rec['note'].append(dep)

    rec['autaff'][-1].append(publisher)

    keepit = True
    for dep in rec['department']:
        if dep in boringdepartments:
            print('  skip "%s"' % (dep))
            keepit = False
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
