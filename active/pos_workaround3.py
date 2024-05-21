# -*- coding: utf-8 -*-
#program to harvest PoS
# FS 2019-06-03

import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time

nr = sys.argv[1]
vol = sys.argv[2]
year = sys.argv[3]
if not re.search('^[12]\d\d\d$', year):
    print('nor a proper year')
    sys.exit(0)
#cnum = sys.argv[4]
#fc = sys.argv[5]
skipalreadyharvested = True



ppdfpath = '/afs/desy.de/group/library/publisherdata/pdf'

publisher = 'SISSA'
jnlfilename = 'pos_%s' % (vol)
jnlfilename = 'pos_%s_%s' % (vol, ejlmod3.stampoftoday())

tocurl = 'https://pos.sissa.it/%s/' % (nr)
tocpage = BeautifulSoup(urllib.request.urlopen(tocurl), features="lxml")

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

note = False
recs = []
recoll = re.compile('.* (with|Measurement|Experimental|Signal|Search).*(ATLAS|ALICE|CMS|DUNE|TOTEM|NA62|MEG|Belle|KM3NeT|KLOE|JUNO|ICARUS|ILD|ICAL|CDF|BABAR|ALEPH|ZEUS|HERA|JAXO).*')
trs = tocpage.body.find_all('tr')
for (i, tr) in enumerate(trs):
    rec = {'vol' : vol, 'tc' : 'C', 'year' : year, 'jnl' : 'PoS', 'auts' : [], 'col' : [], 'fc' : ''}
    #print tr.text
    if tr.has_attr('class'):
        note = tr.text.strip()
        ejlmod3.printprogress("===", [[note]])
    arturl = False
    if note:
        rec['note'] = [note]
        if note in ['Accelerators: Physics, Performance, and R&D for future facilities',
                    'T13 Accelerators for HEP']:
            rec['fc'] += 'b'
        elif note == 'Computing and Data Handling':
            rec['fc'] += 'c'
        elif note in ['Joint T03+T10 Dark Matter + Searches for New Physics',
                      'T10 Searches for New Physics']:
            rec['fc'] += 'e'
        elif note in ['Dark Matter', 'Workshop on Tensions in Cosmology',
                      'S02-AA Astronomy and Astrophysics',
                      'T03 Dark Matter',
                      'Parallel session Cosmology and astroparticle physics',
                      'Astroparticle Physics and Cosmology']:
            rec['fc'] += 'a'
        elif note in ['Parallel session Quantum chromodynamics, strong interactions']:
            rec['fc'] += 'p'
        elif note in ['T01 Astroparticle Physics and Gravitational Waves']:
            rec['fc'] += 'ag'
        elif note in ['Formal Theory', 'Workshop on Holography and the Swampland',
                      'T11 Quantum Field and String Theory',
                      'Workshop on Holography and the Swampland',                      
                      'Workshop on Noncommutative and Generalized Geometry in String Theory, Gauge Theory and Related Physical Models']:
            rec['fc'] += 't'
        elif note in ['Parallel session Aspects of mathematical physics']:
            rec['fc'] = 'm'
        elif note in ['Operation, Performance and Upgrade (incl. HL-LHC) of Present Detectors',
                      'S15-MI Metrology and Instrumentation',
                      'T12 Detector R&D and Data Handling',
                      'Detectors for Future Facilities, R&D, novel techniques', 'Future facilities']:
            rec['fc'] += 'i'
        elif note in ['S03-GC Gravitation and Cosmology', 'Workshop on Features of a Quantum de Sitter Universe',
                      'Parallel session Gravity and its modifications',
                      'T02 Gravitation and Cosmology']:
            rec['fc'] = 'g'
        elif note == 'S06-CMPSP Condensed Matter Physics and Statistical Physics':
            rec['fc'] = 'f'
        elif note in ['S10-MG Meteorology and Geophysics', 'S11-EPASE Environmental Physics – Alternative Sources of Energy',
                      'S13-BMP Biophysics and Medical Physics', 'S14-PEHPP Physics Education, History and Philosophy of Physics',
                      'T14 Outreach, Education and EDI']:
            rec['fc'] = 'o'
    #cnum
    if len(sys.argv) > 4:
        rec['cnum'] = sys.argv[4]
    #fc
    if len(sys.argv) > 5:
        rec['fc'] = sys.argv[5]
    #title
    for span in tr.find_all('span', attrs = {'class' : 'contrib_title'}):
        rec['tit'] = span.text.strip()
        
    #articleID
    for span in tr.find_all('span', attrs = {'class' : 'contrib_code'}):
        for a in span.find_all('a'):
            arturl = 'https://pos.sissa.it' + a['href']
            rec['p1'] = re.sub('.*\/(\d+).*', r'\1',  a['href'])
    if not arturl:
        continue
    if note:
        ejlmod3.printprogress('-', [[i+1, len(trs)], [note], [arturl], [len(recs)]])
    else:
        ejlmod3.printprogress('-', [[i+1, len(trs)], [arturl], [len(recs)]])
    artpage = BeautifulSoup(urllib.request.urlopen(arturl), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_doi', 'citation_abstract'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #authors
            if meta['name'] == 'citation_author':
                if re.search('behalf of', meta['content']):
                    col = re.sub('.*behalf of ', '', meta['content'])
                    col = re.sub('^the ', '', col)
                    col = re.sub(' [Cc]ollaborations?,?$', '', col)
                    rec['col'].append(col)
                else:
                    mc = re.sub(',$', '', meta['content'])
                    if mc in ['IceCube-Gen2', 'FACT', 'Dampe', 'Fermi Large Area Telescope', 'KM3NeT',
                              'The CTA-LST Project', 'Hess', 'Telescope Array', 'Veritas', 'Fermi-LAT',
                              'H.E.S.S.', 'KASCADE Grande', 'LAGO', 'Hawc', 'MAGIC', 'Pierre Auger',
                              'IceCube']:
                        rec['col'].append(mc)
                    else:
                        rec['auts'].append(mc)
            #FFT
            elif meta['name'] == 'citation_pdf_url':
                rec['FFT'] = meta['content']
            #date
            elif meta['name'] == 'citation_online_date':
                rec['date'] = meta['content']
                print(' online_date      ', rec['date'])
            elif meta['name'] == 'citation_publication_date':
                rec['publication_date'] = meta['content']
                print(' publication_date ', rec['publication_date'])
    if not 'date' in list(rec.keys()) and 'publication_date' in list(rec.keys()):
        rec['date'] = rec['publication_date']
    #construct DOI if neccessary
    if not 'doi' in list(rec.keys()):
        rec['doi'] = '10.22323/1.%s.%04i' % (nr, int(rec['p1']))
    if skipalreadyharvested and rec['doi'] in alreadyharvested and rec['doi'] != '10.22323/1.444.1226':
        continue
    #get PDF
    if 'FFT' in list(rec.keys()):
        doi1 = re.sub('[\(\)\/]', '_', rec['doi'])
        doifilename = '%s/10.22323/%s.pdf' % (ppdfpath, doi1)
        if not os.path.isfile(doifilename):
            os.system('wget -q -O %s "%s"' % (doifilename, rec['FFT']))
            time.sleep(10)
        #count pages
        anzahlseiten = os.popen('pdftk %s dump_data output | grep -i NumberO' % (doifilename)).read().strip()
        anzahlseiten = re.sub('.*NumberOfPages. (\d*).*',r'\1',anzahlseiten)
        rec['pages'] = anzahlseiten
        #license
        for div in artpage.find_all('div', attrs = {'class' : 'license'}):
            for a in div.find_all('a'):
                if a.has_attr('href') and re.search('creativecommons.org', a['href']):
                    rec['license'] = {'url' : a['href']}
        recs.append(rec) 
        ejlmod3.printrecsummary(rec)
    #collaboration from title
    if not rec['col'] and recoll.search(rec['tit']):
        collaboration = recoll.sub(r'\2', rec['tit'])
        rec['col'].append(collaboration)
        rec['fc'] += 'e'
        rec['note'].append('COL=%s guessed from TIT=%s' % (collaboration, rec['tit']))

ejlmod3.writenewXML(recs, publisher, jnlfilename)
