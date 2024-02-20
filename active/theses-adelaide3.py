# -*- coding: utf-8 -*-
#harvest theses from  Adelaide U.
#FS: 2020-02-12
#FS: 2023-04-08

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Adelaide U.'
jnlfilename = 'THESES-ADELAIDE-%s' % (ejlmod3.stampoftoday())

pages = 4
rpp = 100
skipalreadyharvested = True

uninterestingdepartments = ['School of Animal and Veterinary Sciences', 'Adelaide Law School',
                            'Adelaide Medical School : Ophthalmology and Visual Sciences',
                            'Australian School of Petroleum', 'Business School',
                            'Centre for Global Food &amp; Resources', 'Politics &amp; International Studies',
                            'School of Architecture and Built Environment',
                            'School of Biological Sciences : Ecology and Environmental Science',
                            'School of Chemical Engineering &amp; Advanced Materials', 'School of Chemical Engineering',
                            'School of Dentistry', 'School of Electrical and Electronic Engineering',
                            'School of Humanities : Art History', 'School of Humanities : History',
                            'School of Mechanical Engineering', 'School of Physical Sciences: Chemistry',
                            'School of Physical Sciences : Earth Sciences', 'School of Psychology',
                            'School of Public Health', 'School of Social Sciences : Politics &amp; International Studies',
                            'School of Social Sciences : Sociology, Criminology &amp; Gender Studies',
                            'The Centre for Global Food and Resources', 'School of Biological Sciences',
                            'School of Biological Sciences : Ecology and Environmental Sciences',
                            'School of Humanities : Media', 'Adelaide Medical School', 'Centre for Global Food and Resources',
                            'Entrepreneurship, Commercialisation and Innovation Centre', 'School of Agriculture, Food and Wine',
                            'School of Civil, Environmental and Mining Engineering', 'School of Economics',
                            'School of Physical Sciences : Chemistry',
                            #'School of Computer Science',
                            'School of Electrical and Electronic', 'Adelaide Business School', 'Adelaide Dental School',
                            'Adelaide Medical School : Psychiatry', 'Adelaide Nursing School',
                            'Anthropology &amp; Development Studies', 'Biological Sciences', 'Centre for Traumatic Stress Studies',
                            'Elder Conservatorium of Music', 'Institute for International Trade', 'Joanna Briggs Institute',
                            'School of Biological Sciences : Australian Centre for Ancient DNA',
                            'School of Biological Sciences : Molecular and Biomedical Science',
                            'School of Chemical Engineering and Advanced Materials', 'School of Education',
                            'School of History and Politics : Politics',
                            'School of Humanities : Classics, Archaeology &amp; Ancient History',
                            'School of Humanities : English &amp; Creative Writing',
                            'School of Humanities : English and Creative Writing', 'School of Humanities : French Studies',
                            'School of Humanities : Philosophy', 'School of Medicine', 'School of Nursing',
                            'School of Population Health : Public Health',
                            'School of Social Sciences : Anthropology and School of Social Sciences : Anthropology and Development Studies',
                            'School of Social Sciences: Anthropology and Development Studies', 'School of Social Sciences : Asian Studies',
                            'School of Social Sciences : Geography, Environment',
                            'School of Social Sciences : Geography, Environment &amp; Population',
                            'School of Social Sciences: Geography, Environment &amp; Population',
                            'School of Social Sciences : Geography, Environment and Population',
                            'School of Social Sciences: Politics &amp; International Studies',
                            'School of Social Sciences : Politics and International Studies',
                            'School of Social Sciences : Sociology, Criminology and Gender Studies',
                            'School of Social Sciences', 'The Joanna Briggs Institute', 'Anthropology &amp; Development Studies',
                            'Centre for Global Food &amp; Resources', 'Physical Sciences', 'Politics &amp; International Studies',
                            'School of Chemical Engineering &amp; Advanced Materials', 'School of Chemical Engineering and Advanced Materials',
                            'School of Humanities : Classics, Archaeology &amp; Ancient History',
                            'School of Humanities : English &amp; Creative Writing',
                            'School of Social Sciences : Anthropology and School of Social Sciences : Anthropology and Development Studies',
                            'School of Social Sciences : Geography, Environment',
                            'School of Social Sciences : Geography, Environment &amp; Population',
                            'School of Social Sciences: Geography, Environment &amp; Population',
                            'School of Social Sciences : Politics &amp; International Studies',
                            'School of Social Sciences: Politics &amp; International Studies',
                            'School of Social Sciences : Sociology, Criminology &amp; Gender Studies', 'The Joanna Briggs Institute',
                            'School of Architecture and Civil Engineering', 'School of Biomedicine',
                            'School of Economics and Public Policy: Centre for Global Food and Resources',
                            'School of Economics and Public Policy', 'School of History',
                            'School of Humanities : European Languages and Linguistics',
                            'School of Humanities : Historical and Classical Studies', 'School of Humanities : Linguistics',
                            'School of Humanities', 'School of Medicine : Psychiatry',
                            'School of Social Sciences : Politics and International Relations',
                            'School of Humanities : English, Creative Writing and Film',
                            'South Australian Immunogenomics Cancer Institute (SAiGENCI)']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for page in range(pages):
    tocurl = 'https://digital.library.adelaide.edu.au/dspace/handle/2440/14760/simple-search?query=&rpp=' + str(rpp) + '&sort_by=dc.date.issued_dt&order=DESC&etal=0&submit_search=Update&start=' + str(page*rpp)
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    try:
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    except:
        print("retry %s in 180 seconds" % (tocurl))
        time.sleep(180)
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req))
    for tr in tocpage.body.find_all('tr'):
        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'supervisor' : [], 'keyw' : [], 'note' : []}
        for a in tr.find_all('a'):
            if a.has_attr('href') and re.search('dspace\/handle', a['href']):
                rec['artlink'] = 'https://digital.library.adelaide.edu.au' + a['href'] #+ '?show=full'
                rec['hdl'] = re.sub('.*handle\/', '', a['href'])
                if not skipalreadyharvested or not rec['hdl'] in alreadyharvested:
                    if ejlmod3.checkinterestingDOI(rec['hdl']):
                        prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(15)

i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(2)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.creator', 'DCTERMS.issued', 'DC.subject',
                                        'DCTERMS.abstract',  'citation_pdf_url'])
    for meta in artpage.head.find_all('meta'):
        if meta.has_attr('name'):
            #supervisor
            if meta['name'] == 'DC.contributor':
                if meta.has_attr('xml:lang'):
                    rec['department'] = meta['content']
                    rec['note'].append(rec['department'])
                else:
                    rec['supervisor'].append([ meta['content'] ])
            #title
            elif meta['name'] == 'DC.title':
                rec['tit'] = re.sub('\[EMBARGOED\] ', '', meta['content'])
    ejlmod3.globallicensesearch(rec, artpage)
    if 'department' in rec and rec['department'] in uninterestingdepartments:
        ejlmod3.adduninterestingDOI(rec['hdl'])
        continue
    else:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
