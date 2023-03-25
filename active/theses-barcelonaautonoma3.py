# -*- coding: utf-8 -*-
#harvest Barcelona, Autonoma U.
#FS: 2021-01-08
#FS: 2022-08-23

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

rpp = 50
pages = 10
skipalreadyharvested = True

publisher = 'Barcelona, Autonoma U.'
hdr = {'User-Agent' : 'Magic Browser'}

departmentstoskip = ['e%20Biologia%20Cel%C2%B7lular%2C%20de%20Fisiologia%20i%20d%27Immunologia',
                     'e%20Did%C3%A0ctica%20de%20la%20Llengua%20i%20la%20Literatura%20i%20de%20les%20Ci%C3%A8ncies%20Socials',
                     'e%20Filologia%20Espanyola', 'e%20Psicologia%20Social',
                     'e%20Traducci%C3%B3%20i%20d%27Interpretaci%C3%B3%20i%20d%27Estudis%20de%20l%27%C3%80sia%20Oriental',
                     'e%20Telecomunicaci%C3%B3%20i%20Enginyeria%20de%20Sistemes',
                     '%27Hist%C3%B2ria%20Moderna%20i%20Contempor%C3%A0nia',
                     '%27Antropologia%20Social%20i%20Cultural',
                     'e%20Medicina', 'e%20Prehist%C3%B2ria',
                     'e%20Pediatria%2C%20d%27Obstetr%C3%ADcia%20i%20Ginecologia%20i%20de%20Medicina%20Preventiva',
                     'e%20Psiquiatria%20i%20de%20Medicina%20Legal',
                     'e%20Ci%C3%A8ncies%20de%20l%27Antiguitat%20i%20de%20l%27Edat%20Mitjana',
                     'e%20Filologia%20Anglesa%20i%20de%20German%C3%ADstica', 'e%20Filosofia',
                     'e%20Geografia', 'e%20Pedagogia%20Sistem%C3%A0tica%20i%20Social',
                     'e%20Psicologia%20B%C3%A0sica%2C%20Evolutiva%20i%20de%20l%27Educaci%C3%B3',
                     'e%20Psicologia%20Cl%C3%ADnica%20i%20de%20la%20Salut',
                     '%27Economia%20Aplicada', 'e%20Cirurgia', '%27Empresa',
                     '%27Antropologia%20Social%20i%20Prehist%C3%B2ria',
                     'e%20Biologia%20Cel%C2%B7lular%20i%20de%20Fisiologia',
                     'e%20Bioqu%C3%ADmica%20i%20Biologia%20Molecuar',
                     'e%20Ci%C3%A8ncia%20i%20Tecnologia%20Ambientals',
                     #'e%20Ci%C3%A8ncies%20de%20la%20Computaci%C3%B3',
                     'e%20Comunicaci%C3%B3%20Audiovisual%20i%20de%20Publicitat',
                     'e%20Did%C3%A0ctica%20de%20l%27Expressi%C3%B3%20de%20la%20M%C3%BAsica%2C%20Arts%20Pl%C3%A0stiques%20i%20l%27Educaci%C3%B3%20Corporal',
                     'e%20Did%C3%A0ctica%20i%20Organitzaci%C3%B3%20Educativa',
                     'e%20Patologia%20i%20de%20Producci%C3%B3%20Animals',
                     'e%20Psicologia%20de%20l%27Educaci%C3%B3',
                     'e%20Psicologia%20de%20la%20Salut%20i%20de%20Psicologia%20Social',
                     'e%20Publicitat%2C%20Relacions%20P%C3%BAbliques%20i%20Comunicaci%C3%B3%20Audiovisual',
                     'e%20Traducci%C3%B3%20i%20d%27Interpretaci%C3%B3',
                     'e%20Traducci%C3%B3%20i%20Filologia', '%27Infermeria',
                     '%27Economia%20de%20l%27Empresa', 'e%20Dret%20Privat',
                     '%27Enginyeria%20Qu%C3%ADmica%2C%20Biol%C3%B2gica%20i%20Ambiental',
                     'e%20Biologia%20Animal%2C%20de%20Biologia%20Vegetal%20i%20d%27Ecologia',
                     'e%20Bioqu%C3%ADmica%20i%20de%20Biologia%20Molecular',
                     'e%20Ci%C3%A8ncia%20Animal%20i%20dels%20Aliments',
                     'e%20Ci%C3%A8ncia%20Pol%C3%ADtica%20i%20de%20Dret%20P%C3%BAblic',
                     '%27Arquitectura%20de%20Computadors%20i%20Sistemes%20Operatius',
                     '%27Economia%20i%20d%27Hist%C3%B2ria%20Econ%C3%B2mica',
                     '%27Enginyeria%20de%20la%20Informaci%C3%B3%20i%20de%20les%20Comunicacions',
                     '%27Enginyeria%20Electr%C3%B2nica', '%27Art',
                     '%27Enginyeria%20Qu%C3%ADmica', 'e%20Geologia',
                     'e%20Ci%C3%A8ncies%20Morfol%C3%B2giques',
                     'e%20Comunicaci%C3%B3%20Audiovisual%20i%20Publicitat',
                     'e%20Did%C3%A0ctica%20de%20l%27Expressi%C3%B3%20Musical%2C%20Pl%C3%A0stica%20i%20Corporal',
                     'e%20Farmacologia%2C%20de%20Terap%C3%A8utica%20i%20de%20Toxicologia',
                     'e%20Microelectr%C3%B2nica%20i%20Sistemes%20Electr%C3%B2nics',
                     'e%20Pedagogia%20Aplicada', 'e%20Sociologia',
                     'e%20Psicobiologia%20i%20de%20Metodologia%20de%20les%20Ci%C3%A8ncies%20de%20la%20Salut',
                     'e%20Construccions%20Arquitect%C3%B2niques%20I',
                     'e%20Dret%20P%C3%BAblic%20i%20de%20Ci%C3%A8ncies%20Historicojur%C3%ADdiques',
                     'e%20Gen%C3%A8tica%20i%20de%20Microbiologia',
                     'e%20Medicina%20i%20Cirurgia%20Animals',
                     'e%20Mitjans%2C%20Comunicaci%C3%B3%20i%20Cultura',
                     'e%20Periodisme%20i%20de%20Ci%C3%A8ncies%20de%20la%20Comunicaci%C3%B3',
                     'e%20Sanitat%20i%20d%27Anatomia%20Animals',
                     '%27Art%20i%20de%20Musicologia', 'e%20Filologia%20Catalana',
                     'e%20Filologia%20Francesa%20i%20Rom%C3%A0nica', 'e%20Qu%C3%ADmica']
departmentstoskip += ['e%20Doctorat%20en%20Antropologia%20Social%20i%20Cultural',
                      'e%20Doctorat%20en%20Bioinform%C3%A0tica',
                      'e%20Doctorat%20en%20Biologia%20Cel%C2%B7lular',
                      'e%20Doctorat%20en%20Biologia%20i%20Biotecnologia%20Vegetal',
                      'e%20Doctorat%20en%20Bioqu%C3%ADmica%2C%20Biologia%20Molecular%20i%20Biomedicina',
                      'e%20Doctorat%20en%20Ci%C3%A8ncia%20Cognitiva%20i%20Llenguatge',
                      'e%20Doctorat%20en%20Ci%C3%A8ncia%20i%20Tecnologia%20Ambientals',
                      'e%20Doctorat%20en%20Cirurgia%20i%20Ci%C3%A8ncies%20Morfol%C3%B2giques',
                      'e%20Doctorat%20en%20Comunicaci%C3%B3%20Estrat%C3%A8gica%2C%20Publicitat%20i%20Relacions%20P%C3%BAbliques',
                      'e%20Doctorat%20en%20Comunicaci%C3%B3%20i%20Periodisme',
                      'e%20Doctorat%20en%20Creaci%C3%B3%20i%20Gesti%C3%B3%20d%27Empreses',
                      'e%20Doctorat%20en%20Cultures%20en%20Contacte%20a%20la%20Mediterr%C3%A0nia',
                      'e%20Doctorat%20en%20Educaci%C3%B3',
                      'e%20Doctorat%20en%20Estudis%20de%20G%C3%A8nere%20Cultura%2C%20Societats%20i%20Pol%C3%ADtiques',
                      'e%20Doctorat%20en%20Filologia%20Anglesa', 'e%20Doctorat%20en%20Filologia%20Espanyola',
                      'e%20Doctorat%20en%20Filosofia', 'e%20Doctorat%20en%20Gen%C3%A8tica',
                      'e%20Doctorat%20en%20Geologia', 'e%20Doctorat%20en%20Neuroci%C3%A8ncies',
                      'e%20Doctorat%20en%20Hist%C3%B2ria%20Comparada%2C%20Pol%C3%ADtica%20i%20Social',
                      'e%20Doctorat%20en%20Llengua%20i%20Literatura%20Catalanes%20i%20Estudis%20Teatrals',
                      'e%20Doctorat%20en%20Medicina', 'e%20Doctorat%20en%20Microbiologia',
                      'e%20Doctorat%20en%20Medicina%20i%20Sanitat%20Animals',
                      'e%20Doctorat%20en%20Metodologia%20de%20la%20Recerca%20Biom%C3%A8dica%20i%20Salut%20P%C3%BAblica',
                      'e%20Doctorat%20en%20Persona%20i%20Societat%20en%20el%20M%C3%B3n%20Contemporani',
                      'e%20Doctorat%20en%20Producci%C3%B3%20Animal',
                      'e%20Doctorat%20en%20Psicologia%20de%20la%20Salut%20i%20de%20l%27Esport',
                      'e%20Doctorat%20en%20Psiquiatria', 'e%20Doctorat%20en%20Qu%C3%ADmica',
                      'e%20Doctorat%20en%20An%C3%A0lisi%20Econ%C3%B2mica',
                      'e%20Doctorat%20en%20Aq%C3%BCicultura',
                      'e%20Doctorat%20en%20Arqueologia%20Prehist%C3%B2rica', 'e%20Doctorat%20en%20Biodiversitat',
                      'e%20Doctorat%20en%20Ci%C3%A8ncia%20dels%20Aliments',
                      'e%20Doctorat%20en%20Comunicaci%C3%B3%20Audiovisual%20i%20Publicitat',
                      'e%20Doctorat%20en%20Dret', 'e%20Doctorat%20en%20Ecologia%20Terrestre',
                      'e%20Doctorat%20en%20Economia%20Aplicada', 'e%20Doctorat%20en%20Farmacologia',
                      'e%20Doctorat%20en%20Hist%C3%B2ria%20de%20l%27Art%20i%20Musicologia',
                      'e%20Doctorat%20en%20Mitjans%2C%20Comunicaci%C3%B3%20i%20Cultura',
                      'e%20Doctorat%20en%20Pediatria%2C%20Obstetr%C3%ADcia%20i%20Ginecologia',
                      'e%20Doctorat%20en%20Seguretat%20Humana%20i%20Dret%20Global',
                      'e%20Doctorat%20en%20Sociologia', 'e%20Doctorat%20en%20Demografia',
                      'e%20Doctorat%20en%20Teoria%20de%20la%20Literatura%20i%20Literatura%20Comparada',
                      'e%20Doctorat%20en%20Traducci%C3%B3%20i%20Estudis%20Interculturals',
                      'e%20Doctorat%20en%20Turisme', 'e%20Doctorat%20en%20Biotecnologia',
                      'e%20Doctorat%20en%20Ci%C3%A8ncia%20Pol%C3%ADtica%2C%20Pol%C3%ADtiques%20P%C3%BAbliques%20i%20Relacions%20Internacionals',                      
                      'e%20Doctorat%20en%20Economia%2C%20Organitzaci%C3%B3%20i%20Gesti%C3%B3%20%28Business%20Economics%29',
                      'e%20Doctorat%20en%20Electroqu%C3%ADmica%20Ci%C3%A8ncia%20i%20Tecnologia', 'e%20Doctorat%20en%20Geografia',
                      'e%20Doctorat%20en%20Hist%C3%B2ria%20de%20la%20Ci%C3%A8ncia', 'e%20Doctorat%20en%20Immunologia%20Avan%C3%A7ada',
                      'e%20Doctorat%20en%20Lleng%C3%BCes%20i%20Cultures%20Rom%C3%A0niques',
                      'e%20Doctorat%20en%20Psicologia%20Cl%C3%ADnica%20i%20de%20la%20Salut',
                      'e%20Doctorat%20en%20Psicologia%20de%20la%20Comunicaci%C3%B3%20i%20Canvi',
                      'Programa de Doctorat en Arqueologia Clàssica=e%20Doctorat%20en%20Arqueologia%20Cl%C3%A0ssica']

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

prerecs = []
jnlfilename = 'THESES-BarcelonaAutonomaU-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

for page in range(pages):
    tocurl = 'https://ddd.uab.cat/search?cc=tesis&ln=en&rg=' + str(rpp) + '&jrec=' + str(page*rpp+1)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
    time.sleep(2)
    for table in tocpage.body.find_all('table'):
        (rec, keepit) = (False, False)
        for td in table.find_all('td', attrs = {'class' : 'dades'}):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : [], 'keyw' : [], 'autaff' : [], 'supervisor' : []}
            for a in td.find_all('a'):
                if a.has_attr('href'):
                    if re.search('record\/\d', a['href']):
                        rec['link'] = 'https://ddd.uab.cat' + a['href']
                        rec['tit'] = a.text.strip()
                        keepit = True
                    elif re.search('http.*pub.tesis.*\.pdf', a['href']):
                        rec['pdf_url'] = a['href']
        for a in table.find_all('a'):
            if a.has_attr('href') and re.search('p=Departament', a['href']):
                dep = re.sub('.*p=Departament%20d(.*?)\&.*', r'\1', a['href'])
                if dep in departmentstoskip:
                    keepit = False
                else:
                    rec['note'].append(dep)
        if keepit and ejlmod3.checkinterestingDOI(rec['link']):
            prerecs.append(rec)
        elif rec:
            ejlmod3.adduninterestingDOI(rec['link'])
    print('   %i records so far' % (len(prerecs)))
    time.sleep(3)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
    keepit = True
    try:
        req = urllib.request.Request(rec['link'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
        time.sleep(3)
    except:
        try:
            print('retry %s in 180 seconds' % (rec['link']))
            time.sleep(180)
            req = urllib.request.Request(rec['link'], headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features="lxml")
            time.sleep(3)
        except:
            print('no access to %s' % (rec['link']))
            continue        
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_author', 'citation_author_orcid', 'citation_publication_date', 'citation_pdf_url',
                                        'citation_isbn', 'citation_keywords', 'dc.title', 'dc.date', 'dc.keywords', 'dc.creator'])
    ejlmod3.globallicensesearch(rec, artpage)
    #abstract
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_abstract'}):
        if meta.has_attr('content') and meta['content']:
            if re.search(' the ', meta['content']):
                rec['abs'] = meta['content']
            else:
                rec['absspa'] = meta['content']
    rec['autaff'][-1].append(publisher)
    for tr in artpage.body.find_all('tr'):
        for td in tr.find_all('td', attrs = {'class' : 'etiqueta'}):
            tddesc = td.text.strip()
        for td in tr.find_all('td', attrs = {'class' : 'text'}):
            tdt = td.text.strip()
            #pages
            if tddesc == 'Description:':
                if re.search('\d\d p.gines', tdt):
                    rec['pages'] = re.sub('.*?(\d\d+) p.*', r'\1', tdt)
            #license
            elif tddesc == 'Rights:':
                for a in td.find_all('a'):
                    if re.search('creativecommons', a['href']):
                        rec['license'] = {'url' : a['href']}
            #language
            elif tddesc == 'Language:':
                if re.search('Castel', tdt) or re.search('Catal', tdt):
                    rec['language'] = 'Catalan'
                elif re.search('Itali', tdt):
                    rec['language'] = 'Italian'
                elif re.search('Portug', tdt):
                    rec['language'] = 'Portuguese'
                elif re.search('Franc', tdt):
                    rec['language'] = 'French'
                elif not re.search('Angl', tdt):
                    rec['language'] = tdt
            #series
            elif tddesc == 'Series:':
                for a in td.find_all('a'):
                    dep = re.sub('.*p=(.*?)\&.*', r'\1', a['href'])
                    dep = re.sub('^Departament%20d', '', dep)
                    dep = re.sub('^Programa%20d', '', dep)
                    if dep in departmentstoskip:
                        keepit = False
                    else:
                        rec['note'].append('%s=%s' % (tdt, dep))
    #Handle
    for a in artpage.body.find_all('a'):
        if a.has_attr('href') and re.search('hdl.handle.net', a['href']):
            rec['hdl'] = re.sub('.*net\/', '', a['href'])
    #pseudoDOI ?
    if not 'hdl' in list(rec.keys()):
        rec['doi'] = '20.2000/BarcelonaAutonomaU/' + re.sub('\D', '', rec['link'])
    #abstract
    if not 'abs' in list(rec.keys()) and 'absspa' in list(rec.keys()):
        rec['abs'] = rec['absspa']
    #supervisor
    for div in artpage.body.find_all('div', attrs = {'class' : 'pagebody'}):
        for muell in div.find_all(['span', 'table', 'ul']):
            muell.decompose()
        for a in div.find_all('a'):
            if a.has_attr('href'):
                if re.search('orcid.org', a['href']):
                    orcid = re.sub('.*orcid.org\/', 'ORCID:', a['href'])
                    a.replace_with(';;;' + orcid)
        for br in div.find_all('br'):
            br.replace_with('XXXX')
        divt = re.sub('[\n\t\r]', ' ', div.text.strip())
        for part in re.split(' *XXXX *', divt):
            if re.search(' dir\.', part):
                sv = re.sub(' *,? dir\.', '', part)
                sv = re.sub(', \d+.', '', sv)
                sv = re.sub(', *;', ';', sv)
                rec['supervisor'].append(re.split(' *;;; *', sv))
                print('sv->', sv)            
    if keepit:
        if skipalreadyharvested and 'hdl' in rec and rec['hdl'] in alreadyharvested:
            print('   already in backup')
        elif skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
            print('   already in backup')
        else:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
