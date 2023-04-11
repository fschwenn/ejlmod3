# -*- coding: utf-8 -*-
#harvest theses from Louisiana State U.
#FS: 2021-09-17
#FS: 2023-04-11

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

numofpages = 2
skipalreadyharvested = True

publisher = 'Louisiana State U.'
jnlfilename = 'THESES-LouisianaStateU-%s' % (ejlmod3.stampoftoday())

uninteresting = [re.compile('Master of ')]
uninteresting += [re.compile('Pharmaceutical'), re.compile('Physiology'), re.compile('Dentistry'),
                  re.compile('Chemistry'), re.compile('Biomedical'), re.compile('Biostatistics'),
                  re.compile('Chemical'), re.compile('Clinical'), re.compile('Education'),
                  re.compile('Electrical '), re.compile('English'), re.compile('Epidemiology'),
                  re.compile('Graphic'), re.compile('Health'), re.compile('History'),
                  re.compile('Human'), re.compile('Integrative Life Sciences'), re.compile('Pharmacy'),
                  re.compile('Interior Design'), re.compile('Kinetic Imaging'),
                  re.compile('Microbiology'), re.compile('Immunology'), re.compile('Neuroscience'),
                  re.compile('Nursing'), re.compile('Painting'), re.compile('Printmaking'),
                  re.compile('Photography'), re.compile('Film'), re.compile('Psychology'),
                  re.compile('Public Policy'), re.compile('Administration'), re.compile('Sculpture'),
                  re.compile('Extended Media'), re.compile('Special Education'), re.compile('Medical'),
                  re.compile('Systems Modeling'), re.compile('Theatre'), re.compile('Business'),
                  re.compile('Urban and Regional Planning'), re.compile('Biochemistry'),
                  re.compile('Nanoscience'), re.compile('Pharmacology'), re.compile('Toxicology'),
                  re.compile('Media'), re.compile('Biology'), re.compile('Therapy'),
                  re.compile('Rehabilitation'), re.compile('Social'), re.compile('Anatomy')]
uninteresting += [re.compile('Nutrition'), re.compile('Accounting'), re.compile('Textile'),
                  re.compile('Biological'), re.compile('Civil'), re.compile('Agricultural'),
                  re.compile('Oceanography'), re.compile('Pathobiological'), re.compile('Music'),
                  re.compile('Geography'), re.compile('Geology'), re.compile('Geophysics'),
                  re.compile('Sociology'), re.compile('Kinesiology'), re.compile('Natural'),
                  re.compile('Literature'), re.compile('Entomology'), re.compile('Finance'),
                  re.compile('Petroleum'), re.compile('Management'), re.compile('Medicine'),
                  re.compile('Economics'), re.compile('Communication'), re.compile('Enviromental'),
                  re.compile('Textiles,'), re.compile('Marketing'), re.compile('Animal'), 
                  re.compile('Political'), re.compile('Environmental'), re.compile('French')]

hdr = {'User-Agent' : 'Magic Browser'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for i in range(numofpages):
    if i == 0:
        tocurl = 'https://digitalcommons.lsu.edu/gradschool_dissertations/index.html'
    else:
        tocurl = 'https://digitalcommons.lsu.edu/gradschool_dissertations/index.%i.html' % (i+1)
    ejlmod3.printprogress("=", [[i+1, numofpages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(3)
    for p in tocpage.body.find_all('p', attrs = {'class' : 'article-listing'}):
        for a in p.find_all('a'):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : []}
            rec['artlink'] = a['href']
            if ejlmod3.checkinterestingDOI(rec['artlink']):
                prerecs.append(rec)

i = 0
recs = []
for rec in prerecs:
    i += 1
    disstyp = False
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
    #license
    for link in artpage.head.find_all('link', attrs = {'rel' : 'license'}):
        rec['license'] = {'url' : link['href']}
    ejlmod3.metatagcheck(rec, artpage, ['bepress_citation_title', 'bepress_citation_date',
                                        'description', 'bepress_citation_pdf_url', 'bepress_citation_doi'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #author
            if meta['name'] == 'bepress_citation_author':
                author = re.sub(' *\[.*', '', meta['content'])
                rec['autaff'] = [[ author ]]
                for div in artpage.body.find_all('div', attrs = {'id' : 'orcid'}):
                    for p in div.find_all('p'):
                        rec['autaff'][-1].append('ORCID:%s' % (p.text.strip()))
                rec['autaff'][-1].append(publisher)

            #typ of dissertation
            elif meta['name'] == 'bepress_citation_dissertation_name':
                disstyp = meta['content'].strip()
                rec['note'].append(disstyp)
    if not 'doi' in list(rec.keys()):
        rec['doi'] = '30.3000/LousianaStateU/' + re.sub('\D', '', rec['artlink'])
        rec['link'] = rec['artlink']
    skipit = False
    if disstyp:
        for regexpr in uninteresting:
            if regexpr.search(disstyp):
                skipit = True
                print('    skip %s' % (disstyp))
                break
    #Department
    if not skipit:
        for div in artpage.body.find_all('div', attrs = {'id' : 'department'}):
            for p in div.find_all('p'):
                dep = p.text.strip()
                rec['note'].append(dep)
                for regexpr in uninteresting:
                    if regexpr.search(dep):
                        skipit = True
                        print('    skip %s' % (dep))
                        break
    if skipit:
        ejlmod3.adduninterestingDOI(rec['artlink'])
    else:
        if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
