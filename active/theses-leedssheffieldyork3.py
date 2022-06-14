# -*- coding: utf-8 -*-
#harvest theses from Universities of Leeds, Sheffield, and York
#FS: 2020-03-25
import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
import urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import codecs
import datetime
import time
import json

publisher = 'whiterose.ac.uk'

pages = 5

jnlfilename = 'THESES-LeedsSheffieldYork-%s' % (ejlmod3.stampoftoday())

boringaffs = ['University of Leeds, Department of Colour and Polymer Chemistry (Leeds), United Kindgom',
              'University of Leeds, Faculty of Biological Sciences (Leeds), School of Chemistry (Leeds), United Kindgom',
              'University of Leeds, Faculty of Biological Sciences (Leeds), School of Physics and Astronomy (Leeds), Institute for Molecular and Cellular Biology (Leeds), United Kindgom',
              'University of Leeds, Faculty of Biological Sciences (Leeds), School of Physics and Astronomy (Leeds), United Kindgom',
              'University of Leeds, Faculty of Environment (Leeds), Faculty of Maths and Physical Sciences (Leeds), School of Earth and Environment (Leeds), Institute for Atmospheric Science (Leeds), School of Physics and Astronomy (Leeds), United Kindgom',
              'University of Leeds, Faculty of Environment (Leeds), Food Science (Leeds), United Kindgom',
              'University of Leeds, Faculty of Maths and Physical Sciences (Leeds), Astbury Centre for Structural Molecular Biology (Leeds), United Kindgom',
              'University of Leeds, Faculty of Maths and Physical Sciences (Leeds), Food Science (Leeds), United Kindgom',
              'University of Leeds, Faculty of Maths and Physical Sciences (Leeds), School of Chemistry (Leeds), Astbury Centre for Structural Molecular Biology (Leeds), United Kindgom',
              'University of Leeds, Faculty of Maths and Physical Sciences (Leeds), School of Chemistry (Leeds), Department of Colour and Polymer Chemistry (Leeds), United Kindgom',
              'University of Leeds, Faculty of Maths and Physical Sciences (Leeds), School of Chemistry (Leeds), United Kindgom',
              'University of Leeds, Food Science (Leeds), School of Geography (Leeds), School of Medicine (Leeds), United Kindgom',
              'University of Leeds, Food Science (Leeds), School of Medicine (Leeds), United Kindgom',
              'University of Leeds, Food Science (Leeds), United Kindgom',
              'University of Leeds, Imaging Science (Leeds), Statistics (Leeds), United Kindgom',
              'University of Leeds, Institute for Atmospheric Science (Leeds), Applied Mathematics (Leeds), United Kindgom',
              'University of Leeds, Oral Biology (Leeds), School of Electronic & Electrical Engineering (Leeds), School of Physics and Astronomy (Leeds), United Kindgom',
              'University of Leeds, School of Chemistry (Leeds), Astbury Centre for Structural Molecular Biology (Leeds), United Kindgom',
              'University of Leeds, School of Chemistry (Leeds), Centre for Technical Textiles (Leeds), United Kindgom',
              'University of Leeds, School of Chemistry (Leeds), Institute for Molecular and Cellular Biology (Leeds), United Kindgom',
              'University of Leeds, School of Chemistry (Leeds), School of Chemical and Process Engineering (Leeds), United Kindgom',
              'University of Leeds, School of Chemistry (Leeds), School of Earth and Environment (Leeds), United Kindgom',
              'University of Leeds, School of Chemistry (Leeds), School of Mechanical Engineering (Leeds), United Kindgom',
#              'University of Leeds, School of Computing (Leeds), School of Chemistry (Leeds), United Kindgom',
              'University of Leeds, School of Earth and Environment (Leeds), Food Science (Leeds), School of Medicine (Leeds), United Kindgom',
              'University of Leeds, School of Education (Leeds), School of Physics and Astronomy (Leeds), United Kindgom',
              'University of Leeds, School of Electronic & Electrical Engineering (Leeds), School of Physics and Astronomy (Leeds), United Kindgom',
              'University of Leeds, School of Mathematics (Leeds), School of Chemical and Process Engineering (Leeds), United Kindgom',
              'University of Leeds, School of Mathematics (Leeds), School of Mechanical Engineering (Leeds), United Kindgom',
              'University of Leeds, School of Physics and Astronomy (Leeds), Institute for Materials Research (Leeds), United Kindgom',
              'University of Leeds, School of Physics and Astronomy (Leeds), School of Chemical and Process Engineering (Leeds), United Kindgom',
              'University of Sheffield, Animal and Plant Sciences (Sheffield), Chemical and Biological Engineering (Sheffield), United Kindgom',
              'University of Sheffield, Animal and Plant Sciences (Sheffield), Faculty of Science (Sheffield), School of Mathematics and Statistics (Sheffield), United Kindgom',
              'University of Sheffield, Animal and Plant Sciences (Sheffield), Faculty of Science (Sheffield), United Kindgom',
              'University of Sheffield, Animal and Plant Sciences (Sheffield), Geography (Sheffield), United Kindgom',
              'University of Sheffield, Animal and Plant Sciences (Sheffield), Materials Science and Engineering (Sheffield), United Kindgom',
              'University of Sheffield, Animal and Plant Sciences (Sheffield), Molecular Biology and Biotechnology (Sheffield), United Kindgom',
              'University of Sheffield, Animal and Plant Sciences (Sheffield), Physics and Astronomy (Sheffield), United Kindgom',
              'University of Sheffield, Animal and Plant Sciences (Sheffield), United Kindgom',
              'University of Sheffield, Archaeology (Sheffield), Faculty of Arts and Humanities (Sheffield), United Kindgom',
              'University of Sheffield, Archaeology (Sheffield), United Kindgom',
              'University of Sheffield, Automatic Control and Systems Engineering (Sheffield), Psychology (Sheffield), United Kindgom',
              'University of Sheffield, Biomedical Science (Sheffield), Chemistry (Sheffield), United Kindgom',
              'University of Sheffield, Biomedical Science (Sheffield), Dentistry (Sheffield), United Kindgom',
              'University of Sheffield, Biomedical Science (Sheffield), Faculty of Medicine, Dentistry and Health (Sheffield), Medicine (Sheffield), United Kindgom',
              'University of Sheffield, Biomedical Science (Sheffield), Faculty of Science (Sheffield), United Kindgom',
              'University of Sheffield, Biomedical Science (Sheffield), Molecular Biology and Biotechnology (Sheffield), United Kindgom',
              'University of Sheffield, Biomedical Science (Sheffield), United Kindgom',
              'University of Sheffield, Chemical and Biological Engineering (Sheffield), Molecular Biology and Biotechnology (Sheffield), United Kindgom',
              'University of Sheffield, Chemistry (Sheffield), Faculty of Medicine, Dentistry and Health (Sheffield), United Kindgom',
              'University of Sheffield, Chemistry (Sheffield), Faculty of Science (Sheffield), Medicine (Sheffield), United Kindgom',
              'University of Sheffield, Chemistry (Sheffield), Faculty of Science (Sheffield), United Kindgom',
              'University of Sheffield, Chemistry (Sheffield), Information School (Sheffield), United Kindgom',
              'University of Sheffield, Chemistry (Sheffield), Medicine (Sheffield), United Kindgom',
              'University of Sheffield, Chemistry (Sheffield), Molecular Biology and Biotechnology (Sheffield), United Kindgom',
              'University of Sheffield, Chemistry (Sheffield), Physics and Astronomy (Sheffield), United Kindgom',
              'University of Sheffield, Chemistry (Sheffield), United Kindgom',
              'University of Sheffield, Chemistry (Sheffield), Urban Studies and Planning (Sheffield), United Kindgom',
              'University of Sheffield, Computer Science (Sheffield), Human Communication Sciences (Sheffield), United Kindgom',
              'University of Sheffield, Computer Science (Sheffield), Landscape (Sheffield), United Kindgom',
              'University of Sheffield, Computer Science (Sheffield), Psychology (Sheffield), United Kindgom',
              'University of Sheffield, Electronic and Electrical Engineering (Sheffield), Physics and Astronomy (Sheffield), United Kindgom',
#              'University of Sheffield, Faculty of Engineering (Sheffield), Computer Science (Sheffield), United Kindgom',
              'University of Sheffield, Faculty of Science (Sheffield), Animal and Plant Sciences (Sheffield), United Kindgom',
              'University of Sheffield, Faculty of Science (Sheffield), Chemistry (Sheffield), United Kindgom',
              'University of Sheffield, Faculty of Science (Sheffield), Geography (Sheffield), United Kindgom',
              'University of Sheffield, Faculty of Science (Sheffield), Molecular Biology and Biotechnology (Sheffield), Medicine (Sheffield), United Kindgom',
              'University of Sheffield, Faculty of Science (Sheffield), Molecular Biology and Biotechnology (Sheffield), Physics and Astronomy (Sheffield), United Kindgom',
              'University of Sheffield, Faculty of Science (Sheffield), Molecular Biology and Biotechnology (Sheffield), United Kindgom',
              'University of Sheffield, Faculty of Science (Sheffield), Psychology (Sheffield), United Kindgom',
              'University of Sheffield, Faculty of Science (Sheffield), Psychology (Sheffield), Urban Studies and Planning (Sheffield), United Kindgom',
              'University of Sheffield, Landscape (Sheffield), Psychology (Sheffield), United Kindgom',
              'University of Sheffield, Molecular Biology and Biotechnology (Sheffield), United Kindgom',
              'University of Sheffield, Psychology (Sheffield), Faculty of Science (Sheffield), United Kindgom',
              'University of Sheffield, Psychology (Sheffield), Music (Sheffield), United Kindgom',
              'University of Sheffield, Psychology (Sheffield), United Kindgom']
boringaffs += ['The University of Sheffield, Faculty of Science (Sheffield), Animal and Plant Sciences (Sheffield), United Kindgom',
               'The University of Sheffield, Faculty of Arts and Humanities (Sheffield), Archaeology (Sheffield)The University of Sheffield, Faculty of Science (Sheffield), Archaeology (Sheffield), United Kindgom',
               'The University of Sheffield, Faculty of Science (Sheffield), Biomedical Science (Sheffield), United Kindgom',
               'The University of Sheffield, Faculty of Science (Sheffield), Psychology (Sheffield), United Kindgom',
               'The University of Leeds, Faculty of Maths and Physical Sciences (Leeds), School of Chemistry (Leeds)The University of Leeds, Faculty of Maths and Physical Sciences (Leeds), Department of Colour and Polymer Chemistry (Leeds), United Kindgom',
               'The University of Leeds, Faculty of Maths and Physical Sciences (Leeds), School of Chemistry (Leeds)The University of Leeds, University of Leeds Research Centres and Institutes, Astbury Centre for Structural Molecular Biology (Leeds), United Kindgom',
               'The University of Leeds, Faculty of Maths and Physical Sciences (Leeds), School of Chemistry (Leeds), United Kindgom',
               'The University of Sheffield, Faculty of Science (Sheffield), Molecular Biology and Biotechnology (Sheffield), United Kindgom',
               'The University of Sheffield, Faculty of Science (Sheffield)The University of Sheffield, Faculty of Science (Sheffield), Molecular Biology and Biotechnology (Sheffield), United Kindgom',
               'The University of Sheffield, Faculty of Science (Sheffield)The University of Sheffield, Faculty of Science (Sheffield), Psychology (Sheffield), United Kindgom',
               'The University of Sheffield, Faculty of Science (Sheffield), Chemistry (Sheffield), United Kindgom']



hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
dois = []
for i in range(pages):
    tocurl = 'http://etheses.whiterose.ac.uk/cgi/search/archive/advanced?exp=0|1|-date%2Fcreators_name%2Ftitle|archive|-|iau%3Aiau%3AANY%3AEQ%3ALeeds.FA-MAPH+Leeds.RC-MATH+Leeds.SU-MTHA+Leeds.SU-MTHP+Leeds.RC-PHAS+Sheffield.FCP+Sheffield.PHY+Sheffield.SOM+York.YOR16+York.YOR21|-|eprint_status%3Aeprint_status%3AANY%3AEQ%3Aarchive|metadata_visibility%3Ametadata_visibility%3AANY%3AEQ%3Ashow&_action_search=1&order=-date%2Fcreators_name%2Ftitle&screen=Search&search_offset=' + str(20*i)
    ejlmod3.printprogress('=', [[i, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(2)
    for tr in tocpage.body.find_all('tr', attrs = {'class' : 'ep_search_result'}):
        if re.search('MSc ', tr.text) or re.search('MPhil ', tr.text):
            print('  skip Master')
        else:
            for td in tr.find_all('td'):
                for span in td.find_all('span'):
                    for a in td.find_all('a'):
                        if a.has_attr('href') and re.search('etheses.whiterose.ac.uk', a['href']):
                            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'note' : []}
                            rec['link'] = a['href']
                            rec['doi'] = '20.2000/' + re.sub('\W', '', a['href'])
                            if ejlmod3.ckeckinterestingDOI(rec['doi']) and not rec['doi'] in dois:
                                prerecs.append(rec)
                                dois.append(rec['doi'])

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(prerecs)], [len(recs)], [rec['link']]])
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
    aff = []
    restricted = False
    ejlmod3.metatagcheck(rec, artpage, ['eprints.title', 'eprints.date', 'eprints.keywords', 'DC.rights', 'eprints.abstract', 'eprints.document_url'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'eprints.creators_name':
                author = meta['content']
                author = re.sub(',', ';', author, count=1)
                author = re.sub(' *, *', ' ', author)
                author = re.sub(';', ',', author)
                rec['autaff'] = [[ author ]]
            #orcid
            elif meta['name'] == 'eprints.creators_orcid':
                rec['autaff'][-1].append('ORCID:' + meta['content'])
            #email
            elif meta['name'] == 'eprints.creators_id':
                rec['autaff'][-1].append('EMAIL:' + meta['content'])
            #thesis type
            elif meta['name'] == 'eprints.thesis_type':
                rec['note'].append(meta['content'])
            #restricted PDF?
            elif meta['name'] == 'eprints.full_text_status':
                if  meta['content'] == 'restricted':
                    restricted = True
            #aff
            elif meta['name'] == 'DC.publisher':
                aff.append(meta['content'])
            #references
            elif meta['name'] == 'eprints.referencetext':
                rec['refs'] = []
                bulk = re.sub('\n', ' ', meta['content'])
                bulk = re.sub('\[(\d+)\]', r'XXXX[\1]', bulk)
                lines = re.split('XXXX', bulk)
                if len(lines) > 50:
                    lines = lines[1:]
                else:
                    lines = re.split('\n', meta['content'])
                for ref in lines:
                     rec['refs'].append([('x', ref)])

    if aff:
        aff.append('United Kindgom')
        combinedaff = ', '.join(aff)
    else:
        for tr in artpage.body.find_all('tr'):
            for th in tr.find_all('th'):
                if th.text.strip() == 'Academic Units:':
                    for td in tr.find_all('td'):
                        combinedaff = re.sub(' > ', ', ', td.text.strip()) + ', United Kindgom'

    if combinedaff in boringaffs:
        print('  skip "%s"' % (combinedaff))
        ejlmod3.adduninterestingDOI(rec['doi'])
    else:
        rec['autaff'][-1].append(combinedaff)
        #license
        ejlmod3.globallicensesearch(rec, artpage)
        if not restricted:
            if 'license' in rec:
                rec['FFT'] = rec['pdf_url']
            else:
                rec['hidden'] = rec['pdf_url']
        else:
            print('  PDF is restricted')
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
ejlmod3.writeretrival(jnlfilename)
