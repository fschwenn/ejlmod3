# -*- coding: utf-8 -*-
#harvest theses from Bologna U. 
#FS: 2019-09-13

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

skipalreadyharvested = True

publisher = 'Bologna U.'
jnlfilename = 'THESES-UNIBO-%s' % (ejlmod3.stampoftoday())

boring = ["Architettura", u"Traduzione, interpretazione e interculturalità",
          u'Automotive per una mobilità intelligente',
          "Biologia cellulare e molecolare", "Chimica", "Diritto europeo",
          "Scienze mediche generali e scienze dei servizi", "Scienze veterinarie",
          "Scienze pedagogiche", "Meccanica e scienze avanzate dell'ingegneria",
          "Scienze e tecnologie agrarie, ambientali e alimentari",
          "Scienze chirurgiche", "European doctorate in law and economics",
          "Law, science and technology", 'Geofisica',
          "Dese - les litteratures de l'europe unie/ european literatures/ letterature dell'europa unita",
          "Arti visive, performative, mediali", 'Law and economic',
          "Diritto tributario europeo - ph.D in european tax law",
          "Ingegneria civile, chimica, ambientale e dei materiali",
          "Scienze della terra, della vita e dell'ambiente", "Storia culture civilta'",
          "Studi sul patrimonio culturale / cultural heritage studies",
          "Culture letterarie e filologiche", "Ingegneria biomedica, elettrica e dei sistemi",
          "Oncologia, ematologia e patologia", "Philosophy, science, cognition, and semiotics (pscs)",
          "Scienze biomediche e neuromotorie", "Scienze cardio nefro toraciche",
          "Scienze giuridiche - phd in legal studies", "Sociologia e ricerca sociale",
          "Studi globali e internazionali - global and international studies",
          "Studi letterari e culturali", "Economics", "Psicologia", "Studi ebraici",
          "Phd in management", "Architettura e culture del progetto",
          "Lingue, letterature e culture moderne", "Scienze giuridiche",
          "Monitoraggio e gestione delle strutture e dell'ambiente - sehm2",
          "Nanoscienze per la medicina e per l'ambiente",
          "Scienza e cultura del benessere e degli stili di vita",
          "Scienze biotecnologiche, biocomputazionali, farmaceutiche e farmacologiche",
          "Scienze politiche e sociali",  "Storie, culture e politiche del globale", 
          "Scienze storiche e archeologiche. Memoria, civilta' e patrimonio"]
boring += ['BIO/10 Biochimica', 'MED/18 Chirurgia generale', 'ING-IND/08 Macchine a fluido',
           'BIO/08 Antropologia', 'BIO/15 Biologia farmaceutica',
           'L-ART/04 Museologia e critica artistica e del restauro',
           'SECS-P/03 Scienza delle finanze', 'ING-IND/34 Bioingegneria industriale',
           'ING-IND/14 Progettazione meccanica e costruzione di macchine',
           'SECS-S/03 Statistica economica', 'CHIM/08 Chimica farmaceutica',
           'CHIM/11 Chimica e biotecnologia delle fermentazioni',
           "CHIM/12 Chimica dell'ambiente e dei beni culturali",
           'ING-IND/16 Tecnologie e sistemi di lavorazione']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for year in [ejlmod3.year(backwards=1), ejlmod3.year()]:
    tocurl = 'http://amsdottorato.unibo.it/view/year/%i.html' % (year)
    print(tocurl)
    hdr = {'User-Agent' : 'Magic Browser'}
    try:
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    except:
        continue    
    time.sleep(3)
    for p in tocpage.body.find_all('p'):
        keepit = True
        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'keyw' : [], 'note' : []}
        for span in p.find_all('span',  attrs = {'class' : 'nolink'}):
            for a in span.find_all('a'):
                subject = a.text
            if subject == 'Astrofisica':
                rec['fc'] = 'a'
            elif subject == 'Matematica':
                rec['fc'] = 'm'
            elif subject == 'Computer science and engineering':
                rec['fc'] = 'c'
            elif subject in boring:
                keepit = False
            else:
                rec['note'].append(subject)
            span.replace_with('')    
        for a in p.find_all('a'):
            rec['artlink'] =  a['href']
            if keepit and ejlmod3.checkinterestingDOI(rec['artlink']):
                if skipalreadyharvested and rec['artlink'] in alreadyharvested:
                    print('   %s already in backup' % (rec['artlink']))
                elif skipalreadyharvested and re.sub('http:\/\/amsdottorato.unibo.it\/(.*)\/', r'10.48676/unibo/amsdottorato/\1', rec['artlink']) in alreadyharvested:
                    print('   %s already in backup' % (re.sub('http:\/\/amsdottorato.unibo.it\/(.*)\/', r'10.48676/unibo/amsdottorato/\1', rec['artlink'])))
                else:
                    prerecs.append(rec)
i = 0
recs = []
for rec in prerecs:
    keepit = True
    i += 1
    ejlmod3.printprogress('-', [[year], [i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.title', 'eprints.date', 'eprints.keywords', 'DC.identifier',
                                        'DC.language', 'eprints.document_url', 'eprints.abstract'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name') and meta.has_attr('content'):
            #author
            if meta['name'] == 'DC.creator':
                author = re.sub(' *\[.*', '', meta['content'])
                author = re.sub(' <\d.*', '', author)
                rec['autaff'] = [[ author ]]
                rec['autaff'][-1].append('Bologna U.')
            #subject
            elif meta['name'] == 'DC.subject':
                if meta['content'] in boring:
                    keepit = False
                else:
                    rec['note'].append(meta['content'])
    #license            
    for table in artpage.body.find_all('table', attrs = {'class' : 'ep_block'}):
        for a in table.find_all('a'):
            if a.has_attr('href') and re.search('creativecommons.org', a['href']):
                rec['license'] = {'url' : a['href']}
    #DOI
    if not 'doi' in rec:
        for div in artpage.body.find_all('div', attrs = {'class' : 'altmetric-embed'}):
            if div.has_attr('data-doi') and re.search('^10',  div['data-doi']):
                rec['doi'] = div['data-doi']
    #subject
    for div in artpage.body.find_all('div', attrs = {'class' : 'metadato_value'}):
        for a in div.find_all('a'):
            if a.has_attr('href') and re.search('view\/dottorati\/.', a['href']):
                subject = a.text
                if subject in boring:
                    keepit = False
                else:
                    rec['note'].append(subject)
    if keepit:
        if skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
            pass
        elif skipalreadyharvested and 'urn' in rec and rec['urn'] in alreadyharvested:
            pass
        else:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['artlink'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
