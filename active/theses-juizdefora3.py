# -*- coding: utf-8 -*-
#harvest theses from Juiz de Fora U.
#FS: 2023-08-21

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Juiz de Fora U.'
jnlfilename = 'THESES-JuizDeFora-%s' % (ejlmod3.stampoftoday())

rpp = 50
pages = 1
skipalreadyharvested = True
departments = ['29', '23']
hdr = {'User-Agent' : 'Magic Browser'}
boring = ['CNPQ::CIENCIAS EXATAS E DA TERRA::QUIMICA',
          'CNPQ::ENGENHARIAS::ENGENHARIA CIVIL',
          'CNPQ::CIENCIAS EXATAS E DA TERRA::QUIMICA::QUIMICA ANALITICA',
          'CNPQ::CIENCIAS EXATAS E DA TERRA::QUIMICA::QUIMICA INORGANICA',
          'CNPQ::CIENCIAS EXATAS E DA TERRA::QUIMICA::QUIMICA ORGANICA',
          'CNPQ::CIENCIAS HUMANAS::EDUCACAO',
          'CNPQ::CIENCIAS HUMANAS',
          'CNPQ::CIENCIAS SOCIAIS APLICADAS::ARQUITETURA E URBANISMO']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

j = 0
prerecs = []
recs = []
for dep in departments:
    j += 1
    for page in range(pages):
        tocurl = 'https://repositorio.ufjf.br/jspui/handle/ufjf/' + dep + '/simple-search?query=&filter_field_1=type&filter_type_1=equals&filter_value_1=Disserta%C3%A7%C3%A3o&sort_by=dc.date.issued_dt&order=desc&rpp=' + str(rpp) + '&etal=0&start=' + str(rpp*page)
        ejlmod3.printprogress("=", [[dep], [page+1 + (j-1)*pages, pages*len(departments)], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(6)
        for tr in tocpage.find_all('tr'):
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : []}
            for td in tr.find_all('td', attrs = {'headers' : 't1'}):
                rec['date'] = td.text.strip()
            for td in tr.find_all('td', attrs = {'headers' : 't2'}):
                for a in td.find_all('a'):
                    if a.has_attr('href') and re.search('handle\/', a['href']):
                        rec['link'] = 'https://repositorio.ufjf.br' + a['href']  + '?mode=full&locale=en'
                        if ejlmod3.checkinterestingDOI(rec['link']):
                            prerecs.append(rec)
        print('\n  %4i records so far\n' % (len(prerecs)))

i = 0
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(5)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']))
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_language', 
                                        'citation_date', 'citation_author',
                                        'citation_keywords', 'citation_pdf_url',
                                        'DC.rights',
                                        'DCTERMS.abstract', 'DC.identifier'])
    rec['autaff'][-1].append(publisher)
    #more metadata
    for table in artpage.body.find_all('table', attrs = {'class' : 'panel-body'}):
        for tr in table.find_all('tr'):
            for td in tr.find_all('td', attrs = {'class' : 'metadataFieldLabel'}):
                label = td.text.strip()
            for td in tr.find_all('td', attrs = {'class' : 'metadataFieldValue', 'headers' : 's2'}):
                #supervisor
                if label in ['dc.contributor.advisor', 'dc.contributor.advisor1', 'dc.contributor.advisor2']:
                    if td.text.strip():
                        rec['supervisor'].append([re.sub('.*\((.*)\)', r'\1', td.text.strip())])
                #subject
                elif label == 'dc.subject.cnpq':
                    cnpq = td.text.strip()
                    if cnpq in ['CNPQ::CIENCIAS EXATAS E DA TERRA::CIENCIA DA COMPUTACAO',
                                'CNPQ::CIENCIAS EXATAS E DA TERRA::CIENCIA DA COMPUTACAO::SISTEMAS DE COMPUTACAO']:
                        rec['fc'] = 'c'
                    elif cnpq == 'CNPQ::CIENCIAS EXATAS E DA TERRA::FISICA::FISICA DA MATERIA CONDENSADA':
                        rec['fc'] = 'f'
                    elif cnpq in ['CNPQ::CIENCIAS EXATAS E DA TERRA::MATEMATICA',
                                  'CNPQ::CIENCIAS EXATAS E DA TERRA::MATEMATICA::ALGEBRA',
                                  'CNPQ::CIENCIAS EXATAS E DA TERRA::MATEMATICA::GEOMETRIA E TOPOLOGIA',
                                  'CNPQ::CIENCIAS EXATAS E DA TERRA::MATEMATICA::MATEMATICA APLICADA',
                                  'CNPQ::CIENCIAS EXATAS E DA TERRA::PROBABILIDADE E ESTATISTICA']:
                        rec['fc'] = 'm'
                    elif cnpq in boring:
                        keepit = False
                    elif not cnpq in ['CNPQ::CIENCIAS EXATAS E DA TERRA::FISICA',
                                      'CNPQ::CIENCIAS EXATAS E DA TERRA', 'CNPQ::ENGENHARIAS']:
                        rec['note'].append(cnpq)
    if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
        print('   %s already in backup' % (rec['doi']))
    elif keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
