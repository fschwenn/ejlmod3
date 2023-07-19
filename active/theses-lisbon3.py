# -*- coding: utf-8 -*-
#harvest theses from U. Lisbon (main)
#FS: 2021-02-09
#FS: 2023-03-25

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import unicodedata

publisher = 'U. Lisbon (main)'
jnlfilename = 'THESES-LISBON-%s' % (ejlmod3.stampoftoday())
skipalreadyharvested = True

rpp = 50
pages = 2

standard = ['Universidade de Lisboa', 'Tese de doutoramento', 'Faculdade de Ciencias',
            'Tese de Doutoramento']
boring = ['Energia e Ambiente (Energia e Desenvolvimento Sustentavel)',
          'Alteracoes Climaticas e Politicas de Desenvolvimento Sustentavel (Ciencias do Ambiente)',
          'Biologia (Biologia de Sistemas)', 'Biologia (Biotecnologia)',
          'Biologia e Ecologia das Alteracoes Globais (Biologia e Ecologia Tropical)',
          'Ciencias do Mar', 'Engenharia Biomedica e Biofisica', 'Quimica (Quimica)',
          'Arte e Sociedade (Filosofia da Tecnologia)', 'Biodiversidade (Genetica e Evolucao)',
          'Biodiversidade', 'Biologia (Biodiversidade)', 'Biologia (Biologia do Desenvolvimento)',
          'Biologia (Biologia Marinha e Aquacultura)', 'Biologia (Microbiologia)',
          'Bioquimica (Bioquimica Estrutural)', 'Ciencias Geofisicas e da Geoinformacao (Geofisica)',
          'Ciencias Geofisicas e da Geoinformacao (Meteorologia)', 'Doutoramento em Bioquimica',
          'Doutoramento em Biologia e Ecologia das Alteracoes Globais', 'Doutoramento em Biologia',
          'Doutoramento em Ciencias do Mar', 'Doutoramento em Ciencias Geofisicas e da Geoinformacao',
          'Doutoramento em Informatica', 'Doutoramento em Quimica', 'Geologia (Geodinamica Interna)',
          'Doutoramento em Sistemas Sustentaveis de Energia', 'Genetica e Evolucao',
          'Geologia (Geoquimica)', 'Historia e Filosofia das Ciencias', 'logica e fundamentos)',
          'Logica e Fundamentos)', 'Quimica (Quimica Analitica)', 'Quimica (Quimica Inorganica)',
          'Doutoramento em Alteracoes Climaticas e Politicas de Desenvolvimento Sustentavel',
          'Doutoramento em Biodiversidade Genetica e Evolucao', 'Doutoramento em Ciencias do Ambiente',
          'Doutoramento em Biologia (Antropologia Biologica)', 'Doutoramento em Ciencias Geofisicas',
          'Doutoramento em Educacao', 'Doutoramento em Energia e Ambiente',
          'Doutoramento em Engenharia Biomedica e Biofisica', 'Doutoramento em Engenharia Fisica',
          'Doutoramento em e-Planeamento', 'Doutoramento em Geologia',
          'Doutoramento em Historia e Filosofia das Ciencias', 'Doutoramento em Historia',
          'Tese doutoramento em Biologia (Biologia Molecular) Universidade de Lisboa',
          'Tese doutoramento em Ciencias do Mar. Universidade de Lisboa',
          'Tese doutoramento em Quimica (Quimica Analitica) Universidade de Lisboa',
          'Quimica (Quimica Organica)', 'Tecnologia', 'Sistemas Sustentaveis de Energia',
          'Biologia e Ecologia das Alteracoes Globais (Biologia Ambiental e Saude)',
          'Biologia e Ecologia das Alteracoes Globais (Biologia do Genoma e Evolucao)',
          'Biologia e Ecologia das Alteracoes Globais (Biologia e Ecologia Marinha)',
          'Biologia e Ecologia das Alteracoes Globais (Ecologia e Biodiversidade Funcional)',
          'Biologia (Etologia)', 'Bioquimica (Genetica Molecular)', 'Bioquimica (Regulacao Bioquimica)',
          'Ciencias Geofisicas e da Geoinformacao (Engenharia Geografica)',
          'Ciencias Geofisicas e da Geoinformacao (Oceanografia)',
          'Ciencias Geofisicas e da Geoinformacao',
          'Estatistica e Investigacao Operacional (Bioestatistica e Bioinformatica)',
          'Geologia (Geodinamica Externa)', 'Geologia (Geotecnia)', 'Geologia (Metalogenia)',
          'Geologia (Paleontologia e Estratigrafia)', 'Geologia (Sedimentologia)']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

#get ORCID from author search page
def getorcid(a):
    #print '{', 'https://repositorio.ul.pt' + a['href'], '}'
    authorpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open('https://repositorio.ul.pt' + a['href']), features='lxml')
    for span in authorpage.find_all('span'):
        spant = span.text.strip()
        #print spant
        if re.search('\d\d\d\d\-\d\d\d\d\-\d\d\d', spant):
            return 'ORCID:' + spant
    return False

###remove accents from a string
def akzenteabstreifen(string):
    if not type(string) == type('unicode'):
        string = str(string,'utf-8', errors='ignore')
        if not type(string) == type('unicode'):
            return string
        else:
            return str(unicodedata.normalize('NFKD',re.sub('ß', 'ss', string)).encode('ascii','ignore'),'utf-8')
    else:
        return str(unicodedata.normalize('NFKD',re.sub('ß', 'ss', string)).encode('ascii','ignore'),'utf-8')



refac = re.compile('(Life|Health|Medicine|Social|Information|Music|Arts|Chemistry)')
hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for j in range(pages):
    tocurl = 'https://repositorio.ul.pt/handle/10451/27/browse?rpp=' + str(rpp) + '&sort_by=2&type=dateissued&offset=' + str(j*rpp) + '&etal=-1&order=DESC'
    ejlmod3.printprogress("=", [[j+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for td in tocpage.body.find_all('td', attrs = {'headers' : 't2'}):
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'autaff' : [], 'note' : [], 'supervisor' : []}
        for a in td.find_all('a'):
            rec['artlink'] = 'https://repositorio.ul.pt' + a['href'] + '?locale=en'
            rec['hdl'] = re.sub('.*handle\/', '', a['href'])
            if ejlmod3.checkinterestingDOI(rec['hdl']):
                if not skipalreadyharvested or not rec['hdl'] in alreadyharvested:
                    prerecs.append(rec)
    time.sleep(10)

i = 0
recs = []
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features='lxml')
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'DCTERMS.issued', 'citation_language',
                                        'citation_pdf_url'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #keywords
            if meta['name'] == 'DC.subject':
                for keyw in re.split(' *; *', meta['content']):
                    if not re.search('\:\:', keyw) and not re.search('Teses de doutoramento', keyw):
                        rec['keyw'].append(keyw)
            #abstract
            elif meta['name'] == 'DCTERMS.abstract':
                if re.search(' the ',  meta['content']):
                    rec['abs'] = meta['content']
                else:
                    rec['abspt'] = meta['content']
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    #abstract
    if not 'abs' in list(rec.keys()) and 'abspt' in list(rec.keys()):
        rec['abs'] = rec['abspt']
    for tr in artpage.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldLabel'}):
            tht = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'metadataFieldValue'}):
            #author
            if re.search('Author:', tht):
                for a in td.find_all('a'):
                    rec['autaff'] = [[ re.sub(', \d.*', '', a.text.strip()) ]]
                    orcid = getorcid(a)
                    if orcid:
                        rec['autaff'][-1].append(orcid)
                    rec['autaff'][-1].append(publisher)
            #supervisor
            elif re.search('Advisor:', tht):
                for a in td.find_all('a'):
                    rec['supervisor'].append([ re.sub(', \d.*', '', a.text.strip()) ])
                    orcid = getorcid(a)
                    if orcid:
                        rec['supervisor'][-1].append(orcid)
            #department
            elif re.search('Designation:', tht):
                desig = akzenteabstreifen(td.text.strip())
                for part in re.split(', ', desig):
                    if len(part) > 4 and not part in standard:
                        if part in boring:
                            print('  skip', part)
                            keepit = False
                        else:
                            rec['note'].append(part)
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['hdl'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
