# -*- coding: utf-8 -*-
#harvest Connecticut U. theses
#FS: 2023-04-18
#FS: 2024-06-03

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Connecticut U.'
jnlfilename = 'THESES-CONNECTICUT-%s' % (ejlmod3.stampoftoday())

pages = 40 
skipalreadyharvested = True
years = 2
rpp = 200

boring = ['Biomedical Science', 'Kinesiology', 'Communication Sciences',
          'Psychology', 'Nursing', 'Business Administration', 'Philosophy',
          'Agricultural and Resource Economics', 'Animal Science', 'Anthropology',
          'Biomedical Engineering', 'Chemical Engineering', 'Chemistry',
          'Ecology & Evolutionary Biology', 'Kinesoology', 'Political Science',
          'Civil Engineering', 'Curriculum and Instruction', 'Educational Leadership',
          'Ecology and Evolutionary Biology', 'Economics', 'Italian', 'History',
          'Educational Psychology', 'Electrical Engineering', 'English',
          'Genetics and Genomics', 'Geography', 'Geological Sciences', 'German', 
          'Human Development and Family Studies', 'Educational Leadership (Ed.D.)',
          'Learning, Leadership, and Education Policy', 'Linguistics',
          'Literatures, Languages, and Cultures', 'Materials Science and Engineering',
          'Materials Science', 'Mechanical Engineering', 'Medieval Studies',
          'Molecular and Cell Biology', 'Natural Resources: Land, Water, and Air',
          'Nutritional Science', 'Oceanography', 'Pharmaceutical Science',
          'Physiology and Neurobiology', 'Plant Science', 'Political science',
          'Polymer Science', 'Social Work', 'Sociology', 'Education Administration',
          'Adult Learning', 'Biochemistry', 'Cell Biology',
          'Comparative Literary and Cultural Studies', 'Educational Technology',
          'Environmental Engineering', 'French', 'Microbiology', 'Music',
          'Natural Resources: Land, Water, and Air', 'Pathobiology', 'Public Health',
          'Spanish', 'Special Education', 'Structural Biology and Biophysics',
          'Speech, Language, and Hearing Sciences', 'Nutritional Sciences',
          'Human Development and Family Sciences']
boring += ['Doctor of Education']

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

reclinks = []
for page in range(pages):
    tocurl = 'https://collections.ctdigitalarchive.org/islandora/object/20002%3AUniversityDissertations?page=' + str(page) + '&sort=fgs_createdDate_dt%20desc&islandora_solr_search_navigation=0'
    #eigentlichh sort_by=field_edtf_date_created , aber das funzt nicht
    tocurl = 'https://collections.ctdigitalarchive.org/node/5324?page=' + str(page) + '&items_per_page=' + str(rpp) + '&sort_by=title&sort_order=DESC'
    ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for div in tocpage.body.find_all('div', attrs = {'class' : 'result-count'}):
        pages = (int(re.sub('\D', '', div.text.strip()))-1) // rpp + 1
    for toc in tocpage.body.find_all('div', attrs = {'class' : 'solr-search-row-content'}):
        for div in toc.find_all('div', attrs = {'class' : 'views-row'}):
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : [], 'embargo' : False}
            divt = re.sub('[\n\t\r]', '', div.text.strip())
            if re.search('[12]\d\d\d$', divt):
                rec['year'] = divt[-4:]
            if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
                print('   %s too old' % (rec['year']))
            else:
                for a in div.find_all('a'):
                    if 'node' in a['href']:
                        rec['link'] = 'https://collections.ctdigitalarchive.org' + a['href']
                        if not rec['link'] in reclinks:
                            if skipalreadyharvested and rec['link'] in alreadyharvested:
                                print('    %s already in backup' % (rec['link']))
                            elif ejlmod3.checkinterestingDOI(rec['link']):                        
                                prerecs.append(rec)
                            else:
                                print('    %s uninteresting' % (rec['link']))
                            reclinks.append(rec['link'])
    print('  %4i records so far' % (len(prerecs)))
    if page+1 >= pages:
        break
    time.sleep(5)
    

i = 0
recs = []
repages = re.compile('.*?(\d\d+) (leaves|pages).*')
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(4)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    #Handle
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'field field--name-field-handle'}):
        for div in tr.find_all('div', attrs = {'class' : 'field--item'}):
            rec['hdl'] = re.sub('.*handle.net\/', '', div.text.strip())
    #persons
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'field-linked-agent'}):
        for div in tr.find_all('div', attrs = {'class' : 'field--item'}):
            for a in div.find_all('a'):
                if re.search('\(cre\)', div.text.strip()):
                    rec['autaff'] = [[ a.text.strip(), publisher ]]
                elif re.search('\(mja\)', div.text.strip()):
                    if not [ a.text.strip() ] in rec['supervisor']:
                        rec['supervisor'].append([ a.text.strip() ])
    if not 'autaff' in rec:
        rec['autaff'] = [[ 'Doe, John' ]]
        rec['note'].append('--- MISSING AUTHOR ---')
    #title
    for h1 in artpage.body.find_all('h1'):
        title = h1.text.strip()
        if re.search(' \-\- embargoed', title):
            rec['tit'] = re.sub(' *\-\- embargoed.*', '', title)
            rec['embargo'] = True
        else:
            rec['tit'] = title
    #genre
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'field-genre'}):
        for div in tr.find_all('div', attrs = {'class' : 'field--item'}):
            genre = div.text.strip()
            if not genre in ['doctoral dissertations']:
                if not 'GENRE:::' + genre in rec['note']:
                    rec['note'].append('GENRE:::' + genre)
    #pages
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'field-extent'}):
        for div in tr.find_all('div', attrs = {'class' : 'field--item'}):
            if repages.search(div.text.strip()):
                rec['pages'] = repages.sub(r'\1', div.text.strip())
    #Rights
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'field-rights-statement'}):
        for div in tr.find_all('div', attrs = {'class' : 'field--item'}):
            rec['note'].append('RIGHTS:::' + div.text.strip())
    #abstract
    for tr in artpage.body.find_all('div', attrs = {'class' : 'field field--name-field-description'}):
        for div in tr.find_all('div', attrs = {'class' : 'field--item'}):
            rec['abs'] = div.text.strip()
    #degree
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'field-degree-name'}):
        for div in tr.find_all('div', attrs = {'class' : 'field--item'}):
            degree = div.text.strip()
            if degree in boring:
                print('   skip', degree)
            elif not div.text.strip() in ['Doctor of Philosophy']:
                if not 'DEGREE:::' + degree in rec['note']:
                    rec['note'].append('DEGREE:::' + degree)
    #Discipline
    for tr in artpage.body.find_all('tr', attrs = {'class' : 'field-degree-discipline'}):
        for div in tr.find_all('div', attrs = {'class' : 'field--item'}):
            discipline = div.text.strip()
            if discipline in boring:
                print('   skip', discipline)
                keepit = False
            elif discipline == 'Mathematics':
                rec['fc'] = 'm'
            elif discipline == 'Statistics':
                rec['fc'] = 's'                            
            elif not discipline in ['Physics']:
                if not 'DISCIPLINE:::' + discipline in rec['note']:
                    rec['note'].append('DISCIPLINE:::' + discipline)                
    #keywords
    for tr in artpage.body.find_all('div', attrs = {'class' : 'field field--name-field-note'}):
        for div in tr.find_all('div', attrs = {'class' : 'field--item'}):
            rec['keyw'] = re.split(', ', div.text.strip())
    #PDF
    if not rec['embargo']:
        for iframe in artpage.body.find_all('iframe', attrs = {'class' : 'pdf'}):
            rec['pdf_url'] = iframe['data-src']

        

    if keepit:
        if not skipalreadyharvested or not 'hdl' in rec or not rec['hdl'] in alreadyharvested:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)
