# -*- coding: utf-8 -*-
#harvest theses from Naples U.
#FS: 2020-02-24
#FS: 2023-03-13

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

pages = 5
skipalreadyharvested = True

publisher = 'Naples U.'
jnlfilename = 'THESES-NAPLES-%s' % (ejlmod3.stampoftoday())

uninterestingdepartments = ["Scienze Biomediche Avanzate", "Economia, Management e Istituzioni",
                            "Medicina Veterinaria e Produzioni Animali",
                            "Agraria", "Biologia", "Farmacia",
                            "Giurisprudenza", "Ingegneria Industriale",
                            "Ingegneria Civile, Edile e Ambientale",
                            "Medicina Clinica e Chirurgia", "Architettura",
                            "Ingegneria Chimica, dei Materiali e della Produzione Industriale",
                            "Ingegneria Elettrica e delle Tecnologie dell'Informazione",
                            'Matematica e Applicazioni "Renato Caccioppoli"',
                            "Neuroscienze e Scienze Riproduttive ed Odontostomatologiche",
                            "Scienze Mediche Traslazionali", "Scienze Sociali",
                            "Scienze della Terra, dell'Ambiente e delle Risorse",
                            "Scienze Economiche e Statistiche",
                            "Strutture per l'Ingegneria e l'Architettura",
                            "Medicina Molecolare e Biotecnologie Mediche",
                            "Sanità Pubblica", "Scienze Politiche",
                            "Scienze Chimiche", "Studi Umanistici"]

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
                            

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for page in range(pages):
    tocurl = 'http://www.fedoa.unina.it/cgi/search/archive/advanced?exp=0%7C1%7C-date%2Fcreators_name%2Ftitle%7Carchive%7C-%7Ctype%3Atype%3AANY%3AEQ%3Athesis_phd%7C-%7Ceprint_status%3Aeprint_status%3AANY%3AEQ%3Aarchive%7Cmetadata_visibility%3Ametadata_visibility%3AANY%3AEQ%3Ashow&_action_search=1&order=-date%2Fcreators_name%2Ftitle&screen=Search&cache=51779&search_offset=' + str(20*page)
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(5)
    for tr in tocpage.body.find_all('tr', attrs = {'class' : 'ep_search_result'}):
        for a in tr.find_all('a'):
            if a.has_attr('href') and re.search('unina.it.\d+', a['href']):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : []}
                rec['link'] = a['href']
                rec['doi'] = '20.2000/NAPLES/' + re.sub('\D', '', a['href'])
                if ejlmod3.checkinterestingDOI(rec['doi']):
                    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                        prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))


i = 0
recs = []
for rec in prerecs:
    interesting = True
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    #author
    ejlmod3.metatagcheck(rec, artpage, ['eprints.creators_name', 'eprints.creators_id',
                                        'eprints.title', 'eprints.abstract',
                                        'eprints.language', 'eprints.tutors_name',
                                        'eprints.document_url', 'eprints.date',
                                        'eprints.pages', 'eprints.keywords'])
    for meta in artpage.find_all('meta', attrs = {'name' : 'eprints.department'}):
        if meta['content'] in uninterestingdepartments:
            print(' skip ', meta['content'])
            interesting = False
        else:
            rec['note'].append(meta['content'])
    if interesting:
        rec['autaff'][-1].append(publisher)
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['doi'])


ejlmod3.writenewXML(recs, publisher, jnlfilename)
