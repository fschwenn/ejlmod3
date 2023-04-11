# -*- coding: utf-8 -*-
#harvest theses from Paraiba U.
#FS: 2021-01-29
#FS: 2023-04-11

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import unicodedata 
import time
import ssl

publisher = 'Paraiba U.'
jnlfilename = 'THESES-PARAIBA-%s' % (ejlmod3.stampoftoday())

pages = 2
rpp = 100
skipalreadyharvested = False
boringdeps = ['Arquitetura e Urbanismo', 'Administrao', 'Antropologia', 'Artes Cnicas',
              'Biologia Celular e Molecular', 'Biologia Molecular', 'Biotecnologia',
              'Cidadania e Direitos Humanos', 'Cincia das Religies', 'Cincias da Nutrio',
              'Cincias Jurdicas', 'Cincias Veterinrias', 'Educao', 'Enfermagem',
              'Engenharia de Materiais', 'Engenharia de Produo', 'Engenharia Eltrica',
              'Engenharia Mecnica', 'Engenharia Qumica', 'Filosofia', 'Histria',
              'Finanas e Contabilidade', 'Gerenciamento Ambiental', 'Gesto Pblica',
              'Economia do Trabalho e Economia de Empresas', #'Informtica',
              'Jornalismo', 'Letras', 'Lingustica', 'Medicina', 'Msica',
              'Cincia da Informao', 'Engenharia Civil e Ambiental', 'Zoologia',
              'Engenharia de Alimentos', 'Farmacologia', 'Geografia', 'Odontologia', 
              'Psicologia Social', 'Psicologia', 'Servio Social', 'Sociologia',
              'Direitos Humanos', 'Lingustica e ensino', 'cincias Juridicas',
              'Qumica e Bioqumica de Alimentos', 'Tecnologia Agroalimentar',
              'Tecnologia de Alimentos', 'Cincias Fisiolgicas', 'Fisioterapia',
              'Programa Multicntrico de Ps-Graduao em Cincias Fisiolgicas',
              'Economia', 'Engenharias Renovveis', 'Letras Clssicas e Vernculas', 
              'Agricultura', 'Artes Visuais', 'Cincia Animal', 'Cincias Biolgicas',
              'Comunicao', 'Engenharia Cvil e Ambiental', 'Engenharia de Energias Renovveis',
              'Engenharia e Meio Ambiente', 'Fsica', 'Solos e Engenharia Rural', 'Zootecnia',
              'Nutrio', 'Qumica', 'Relaes Internacionais', 'Gesto e Tecnologia Agroindustrial',
              'Educação', 'Educação Física', 'Administração', 'Comunicação', 'Química',
              'Artes Cênicas', 'Ciências da Nutrição', 'Ciências Jurídicas',
              'Engenharia de Energias Renováveis', 'Engenharia Elétrica',
              'Engenharia Mecânica', 'Finanças e Contabilidade', 'Fonoaudiologia',
              'Gestão Pública', 'História', 'Linguística e ensino', 'Música',
              'Relações Internacionais']
              


hdr = {'User-Agent' : 'Magic Browser'}
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for page in range(pages):
    tocurl = 'https://repositorio.ufpb.br/jspui/simple-search?location=&query=&filter_field_1=type&filter_type_1=equals&filter_value_1=Disserta%C3%A7%C3%A3o&rpp=' + str(rpp) + '&sort_by=dc.date.issued_dt&order=DESC&etal=0&submit_search=Update&start=' + str(page*rpp)
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    for td in tocpage.body.find_all('td', attrs = {'headers' : 't2'}):
        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'supervisor' : [], 'note' : [], 'keyw' :[]}
        for a in td.find_all('a'):
            rec['link'] = 'https://repositorio.ufpb.br' + a['href'] #+ '?show=full'
            rec['doi'] = '20.2000/Paraiba/' + re.sub('.*handle\/', '', a['href'])
            if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                if ejlmod3.checkinterestingDOI(rec['doi']):
                    prerecs.append(rec)
    time.sleep(2)
        

i = 0
reprog = re.compile('^(Programa de|Mestrado Profissional|Programa Associado de) ')
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        req = urllib.request.Request(rec['link'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']))
        except:
            print("no access to %s" % (rec['link']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'citation_title', 'DC.language',
                                        'DC.rights', 'DCTERMS.issued', 'citation_keywords',
                                        'DCTERMS.abstract', 'citation_pdf_url'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #supervisor
            if meta['name'] == 'DC.contributor':
                if not meta.has_attr('xml:lang'):
                    rec['supervisor'].append([meta['content']])
            #department
            elif meta['name'] == 'DC.publisher':
                dep = meta['content']
                if not dep in ['Brasil', 'UFPB', 'Universidade Federal da Paraíba']:
                    if not reprog.search(dep):
                        if dep in boringdeps:
                            print('  skip', dep)
                            keepit = False
                        elif dep in ['Matemática']:
                            rec['fc'] = 'm'
                        elif dep in ['Informática']:
                            rec['fc'] = 'c'
                        else:
                            rec['note'].append(dep)
                            print('  ', dep)
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['doi'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
