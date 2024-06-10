# -*- coding: utf-8 -*-
#harvest theses from SISSA
#FS: 2018-01-30
#FS: 2024-07-0

import undetected_chromedriver as uc
import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import os

rpp = 100
pages = 1
pagesgeneral = 20
skipalreadyharvested = True
boring = ['Universidade Estadual Paulista Unesp, Centro de Oncologia Bucal, Araçatuba',
          'Universidade Estadual Paulista (Unesp), Faculdade de Arquitetura, Artes, Comunicação e Design, Bauru',
          'Universidade Estadual Paulista (Unesp), Faculdade de Ciências Humanas e Sociais, Franca',
          'Universidade Estadual Paulista (Unesp), Faculdade de Medicina Veterinária, Araçatuba',
          'Universidade Estadual Paulista (Unesp), Faculdade de Odontologia, Araraquara',
          'Universidade Estadual Paulista (Unesp), Instituto de Artes, São Paulo',
          'Universidade Estadual Paulista (Unesp), Faculdade de Ciências Farmacêuticas, Araraquara',
          'Universidade Estadual Paulista (Unesp), Instituto de Biociências, Rio Claro',
          'Universidade Estadual Paulista (Unesp), Faculdade de Medicina Veterinária e Zootecnia, Botucatu',
          'Universidade Estadual Paulista (Unesp), Faculdade de Odontologia, Araçatuba',
          'Universidade Estadual Paulista (Unesp), Faculdade de Ciências e Letras, Assis',
          'Universidade Estadual Paulista (Unesp), Instituto de Biociências, Botucatu',
          'Universidade Estadual Paulista (Unesp), Instituto de Biociências, Letras e Ciências Exatas, São José do Rio Preto',
          'Universidade Estadual Paulista (Unesp), Faculdade de Ciências Agronômicas, Botucatu',
          'Universidade Estadual Paulista (Unesp), Faculdade de Ciências e Letras, Araraquara',
          'Universidade Estadual Paulista (Unesp), Faculdade de Ciências Agrárias e Veterinárias, Jaboticabal',
          'Universidade Estadual Paulista (Unesp), Faculdade de Medicina, Botucatu']
boring += ['Desastres naturais', 'Geociências e meio ambiente', 'Educação', 'Biotecnologia',
           'Ensino e aprendizagem da matemática e seus fundamentos filosófico-científicos',
           'Desastres associados a eventos extremos, inundações e movimentos de massa',
           'Ensino de Geografia, Cartografia e Cartografia Escolar',
           'Estudos sobre microbiologia, imunologia e terapia em periodontia e implantodontia',
           'Linguagem, discurso e Ensino de Ciências', 'Teoria e práticas pedagógicas',
           'Tratamento de efluentes, preservação e recuperação ambiental', 'Agronegócio e desenvolvimento',
           'Diagnóstico, tratamento e recuperação ambiental', 'Organização do espaço', 'Periodontia',
           'Fundamentos e modelos psico-pedagógicos no Ensino de Ciências e Matemática',
           'Agentes antimicrobianos e métodos de controle para infecções de interesse médico-odontológico',
           'Microbiologia e imunologia', 'Biodinâmica do movimento', 'Dentística']
boring += ['Geografia - FCT 33004129042P3', 'Geografia - IGCE 33004137004P0', 'Fonoaudiologia - FFC',
           'Agronomia - FEIS 33004099079P1', 'Agronomia - FEIS', 'Estudos Linguísticos - IBILCE',
           'Microbiologia', 'Prótese dentária', 'Teoria e estudos literários']
boring += ['Alimentos, Nutrição e Engenharia de Alimentos - IBILCE', 'Aquicultura - CAUNESP 33004102049P7',
           'Aquisição, análise e representação de informações espaciais', 'Atividade física e saúde',
           'Avaliação e intervenção em fisioterapia', 'Biociências - IBILCE',
           'Biodinâmica da motricidade humana', 'Biodiversidade',
           'Biodiversidade Aquática - IBCLP 33004161001P7',
           'Biodiversidade de Ambientes Costeiros - São Vicente', 'Biodiversidade - IBILCE',
           'Bioenergia - IPB', 'Biofísica molecular', 'Biofísica Molecular - IBILCE', 'Biologia animal',
           'Biologia Animal - IBILCE', 'Biologia celular estrutural e funcional',
           'Biologia estrutural e funcional', 'Biopatologia Bucal - ICT',
           'Ciência e Tecnologia Aplicada à Odontologia - ICT', 'Ciência e tecnologia de alimentos',
           'Ciências Ambientais - Sorocaba', 'Ciências Cartográficas - FCT',
           'Ciências da Motricidade - FC', 'Ciências da Motricidade - FCT',
           'Ciências do Movimento - FCT', 'Ciências sociais', 'Ciências Sociais - FFC',
           'Desenvolvimento territorial', 'Educação - FCT', 'Educação - FFC', 'Educação inclusiva',
           'Educação para a Ciência - FC', 'Educação para a Ciência - FC 33004056079P0', 'Endodontia',
           'Engenharia Civil e Ambiental - FEB', 'Engenharia Civil e Ambiental - FEB 33004056089P5',
           'Engenharia de alimentos', 'Engenharia de Produção - FEB',
           'Engenharia de Produção - FEB 33004056086P6', 'Engenharia e Ciência de Alimentos - IBILCE',
           'Fisiologia', 'Fisioterapia - FCT', 'Genética e biologia evolutiva',
           'Geociências e Meio Ambiente - IGCE', 'Geografia - FCT', 'Geografia - IGCE', 'Geotecnia',
           'Gestão de operações e sistemas', 'Gestão de sistemas produtivos', 'Gestão e otimização',
           'Instituições, processos e atores', 'Intervenção pelo movimento na saúde e no desempenho',
           'Letras - IBILCE', 'Mecânica dos sólidos', 'Microbiologia aplicada',
           'Microbiologia - IBILCE', 'Odontologia Restauradora - ICT', 'Patologia',
           'Paz, defesa e segurança internacional', 'Produção do espaço geográfico', 'Projeto mecânico',
           'Políticas públicas e administração da educação brasileira', 'Processos de fabricação',           
           'Psicologia do Desenvolvimento e Aprendizagem - FC', 'Química', 'Química ambiental',
           'Química dos materiais', 'Química - IBILCE', 'Química - IQ', 'Química - IQ 33004030072P8',
           'Química - IQAR 33004030072P8', 'Recursos hídricos e tecnologias ambientais',
           'Relações Internacionais - IPPRI 33004110044P0', 'Transmissão e conversão de energia',
           'Relações Internacionais (UNESP - UNICAMP - PUC-SP) - FFC',
           'Relações Internacionais (UNESP - UNICAMP - PUC-SP) - IPPRI', 'Saneamento ambiental',
           'Saúde pública', 'Sistemas de produção', 'Sociologia', 'Teorias e crítica da literatura',           
           'Universidade Estadual Paulista (Unesp), Instituto de Biociências, São Vicente',
           'Universidade Estadual Paulista (Unesp), Instituto de Pesquisa em Bioenergia, Rio Claro',
           'Universidade Estadual Paulista (Unesp), Instituto de Políticas Públicas e Relações Internacionais, São Paulo',
           'Universidade Estadual Paulista (Unesp), Instituto de Química, Araraquara']


publisher = 'UNESP'
jnlfilename = 'THESES-UNESP-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
else:
    alreadyharvested = []
alreadyharvested += ['11449/252261']

options = uc.ChromeOptions()
options.binary_location='/usr/bin/chromium'
options.add_argument('--headless')
options.binary_location='/usr/bin/google-chrome'
chromeversion = int(re.sub('.*?(\d+).*', r'\1', os.popen('%s --version' % (options.binary_location)).read().strip()))
driver = uc.Chrome(version_main=chromeversion, options=options)

baseurl = 'https://repositorio.unesp.br'
driver.get(baseurl)
time.sleep(2)

collections = [('8f3a79b0-1ef8-4b46-90eb-b695174ae8c6', '', publisher), #Faculdade de Ciências e Tecnologia, Presidente Prudente
               ('70eb1f18-46eb-481a-97a1-72468bd3c7cf', '', 'FACENS, Sorocaba'), #Instituto de Ciência e Tecnologia, Sorocaba
               ('f1dd9cff-97a3-450e-8073-c604530d1e6d', '', publisher), #Instituto de Ciência e Tecnologia, São José dos Campos
               ('897c8802-a0bc-4d1c-932a-6c550877bed1', '', 'Sao Paulo, IFT'), #Instituto de Física Teórica (IFT), São Paulo
               ('8f9b5cff-6a9b-4200-a0cd-9b774e7d909c', '', publisher), #Instituto de Geociências e Ciências Exatas, Rio Claro
               ('7495bc46-ba6c-43b6-946d-f3b7ca966a98', '', publisher), #Faculdade de Ciências, Bauru
               ('fef0c91d-dcf2-4a3d-95de-9838f0f3ea4b', '', publisher)] #Faculdade de Ciências e Engenharia, Tupã
tags = ['dc.contributor.advisor', 'dc.contributor.author', 'dc.description.abstract',
        'dc.date.issued', 'dc.identifier.uri', 'dc.language.iso', 'dc.subject', 'dc.title',
	'dc.title.alternative', 'unesp.campus', 'unesp.graduateProgram',
        'unesp.knowledgeArea', 'unesp.researchArea', 'dc.rights.accessRights',
        'unesp.graduateProgram']
imax = len(collections)*pages + pagesgeneral
i = 0
recs = []
for (collection, fc, aff) in collections:
    for page in range(pages):
        i += 1
        tocurl = baseurl + '/collections/' + collection + '?cp.page=' + str(page+1) + '&cp.rpp=' + str(rpp)
        ejlmod3.printprogress('=', [[i, imax], [tocurl]])
        try:
            driver.get(tocurl)
            time.sleep(5)
            tocpage = BeautifulSoup(driver.page_source, features="lxml")
        except:
            time.sleep(60)
            driver.get(tocurl)
            tocpage = BeautifulSoup(driver.page_source, features="lxml")
        for rec in ejlmod3.ngrx(tocpage, baseurl, tags, boring=boring, alreadyharvested=alreadyharvested):
            if 'autaff' in rec and rec['autaff']:
                rec['autaff'][-1].append(aff)
                if fc:
                    rec['fc'] = fc
                if not rec['hdl'] in alreadyharvested:
                    recs.append(rec)
                    alreadyharvested.append(rec['hdl'])
                    ejlmod3.printrecsummary(rec)
                #print(rec['thesis.metadata.keys'])
            else:
                print('???', rec['link'])
        print('  %i records so far' % (len(recs)))
        time.sleep(10)

for page in range(pagesgeneral):
    i += 1
    tocurl = baseurl + '/search?spc.page=' + str(page+1) + '&spc.sf=dc.date.issued&spc.sd=DESC&f.itemtype=Tese%20de%20doutorado,equals&spc.rpp=' + str(rpp)
    ejlmod3.printprogress('=', [[i, imax], [tocurl]])
    try:
        driver.get(tocurl)
        time.sleep(5)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    except:
        time.sleep(60)
        driver.get(tocurl)
        tocpage = BeautifulSoup(driver.page_source, features="lxml")
    for rec in ejlmod3.ngrx(tocpage, baseurl, tags, boring=boring, alreadyharvested=alreadyharvested):
        if 'autaff' in rec and rec['autaff']:
            rec['autaff'][-1].append(publisher)
            rec['note'].append('general')
            if not rec['hdl'] in alreadyharvested:
                recs.append(rec)
                alreadyharvested.append(rec['hdl'])
                ejlmod3.printrecsummary(rec)
        else:
            print('???', rec['link'])
    print('  %i records so far' % (len(recs)))
    time.sleep(10)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
