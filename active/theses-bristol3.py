# -*- coding: utf-8 -*-
#harvest theses from Bristol U.
#FS: 2021-11-30

import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import codecs
import datetime
import time

jnlfilename = 'THESES-BRISTOL-%s' % (ejlmod3.stampoftoday())

years = [ejlmod3.year(), ejlmod3.year(backwards=1)]
rpp = 50
skipalreadyharvested = True
pages = 5
publisher = 'Bristol U.'
boringdeps = ['School of Geographical Sciences', 'Bristol Composites Institute (ACCIS)', 'Bristol Dental School',
              'Bristol Medical School (PHS)', 'Bristol Medical School', 'Bristol Medical School (THS)',
              'Bristol Population Health Science Institute', 'Bristol Poverty Institute',
              'Bristol Robotics Laboratory',
              'Bristol Veterinary School', 'Cabot Institute for the Environment',
              'Centre for Academic Primary Care', 'Centre for Assessment and Evaluation Research in Education',
              'Centre for Comparative and International Research in Education',
              'Centre for Higher Education Transformations',
              'Centre for Psychological Approaches for Studying Education',
              'Centre for Teaching, Learning and Curriculum', 'Department of Aerospace Engineering',
              'Department of Anthropology and Archaeology', 'Department of Civil Engineering',
              'Department of Classics & Ancient History',
              'Department of Electrical & Electronic Engineering', 'Department of Engineering Mathematics',
              'Department of English', 'Department of Film and Television', 'Department of German',
              'Department of Hispanic, Portuguese and Latin American Studies',
              'Department of History (Historical Studies)', 'Department of Italian',
              'Department of Mechanical Engineering', 'Department of Music', 'Department of Philosophy',
              'Department of Religion and Theology', 'Department of Theatre', 'Educational Futures Network',
              'EPSRC Centre for Doctoral Training in Communications',
              'EPSRC Centre for Doctoral Training in Future Autonomous and Robotic Systems: FARSCOPE',
              'EPSRC Centres for Doctoral Training in Chemical Synthesis (BCS) and Technology Enhanced Chemical Synthesis (TECS)',
              'Fluid and Aerodynamics', 'Global Insecurities', 'Interface Analysis Centre',
              'Language, Literacies and Education Network', 'Mathematics Education Research Network (MERN)',
              'Migration Mobilities Bristol', 'MRC Integrative Epidemiology Unit', 'ReMemBr Group',
              'School for Policy Studies', 'School of Accounting and Finance', 'School of Biochemistry',
              'School of Biological Sciences', 'School of Cellular and Molecular Medicine', 'School of Chemistry',
              'School of Earth Sciences', 'School of Economics', 'School of Education', 'School of Management',
              'School of Modern Languages', 'School of Physiology, Pharmacology & Neuroscience',
              'School of Psychological Science', 'School of Sociology, Politics and International Studies',
              'SPAIS Gender Research Centre', 'Stroke Research Group',
              'The Hadley Centre for Adoption and Foster Care Studies', 'University of Bristol Law School',
              'Department of History of Art (Historical Studies)', 'Department of Russian',
              'School of Civil, Aerospace and Mechanical Engineering',
              'Department of French', 'Early Modern Studies', 'Health Protection Research Unit (HPRU)',
              'Health Sciences Faculty Office', 'Transnational Modernisms Research Cluster',
              'School of Arts', 'School of Civil, Aerospace and Mechanical Engineering']

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

hdr = {'User-Agent' : 'Magic Browser'}
prerecs = []
for year in years:
    tocurl = 'https://research-information.bris.ac.uk/en/studentTheses/?type=%2Fdk%2Fatira%2Fpure%2Fstudentthesis%2Fstudentthesistypes%2Fstudentthesis%2Fdoc%2Fphd&nofollow=true&format=&year=' + str(year)
    ejlmod3.printprogress('=', [[year], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpages = [BeautifulSoup(urllib.request.urlopen(req), features="lxml")]
    time.sleep(10)
    for li in tocpages[0].find_all('li', attrs = {'class' : 'search-pager-information'}):
        numoftheses = int(re.sub('\D', '', re.sub('.*of', '', li.text.strip())))
        pages = 1 + (numoftheses-1) // rpp
    for page in range(pages-1):
        tocurl = 'https://research-information.bris.ac.uk/en/studentTheses/?type=%2Fdk%2Fatira%2Fpure%2Fstudentthesis%2Fstudentthesistypes%2Fstudentthesis%2Fdoc%2Fphd&nofollow=true&format=&year=' + str(year) + '&page=' + str(page+1)
        ejlmod3.printprogress('=', [[year], [page+2, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpages.append(BeautifulSoup(urllib.request.urlopen(req), features="lxml"))
        time.sleep(10)
    for tocpage in tocpages:
        divs = tocpage.body.find_all('div', attrs = {'class' : 'result-container'})
        for div in divs:
            rec = {'tc' : 'T', 'note' : [], 'jnl' : 'BOOK', 'supervisor' : []}
            for h3 in div.find_all('h3'):
                for a in h3.find_all('a'):
                    rec['link'] = a['href']
                    rec['tit'] = a.text.strip()
                    rec['doi'] = '20.2000/Bristol/' + re.sub('\W', '', a['href'])[41:]
                    if skipalreadyharvested and rec['doi'] in alreadyharvested:
                        print('  %s already in backup' % (rec['doi']))
                    elif ejlmod3.checkinterestingDOI(rec['doi']):
                        prerecs.append(rec)
        print('  %4i records so far'  % (len(prerecs)))

i = 0
recs = []
for rec in prerecs:
    i += 1
    keepit = True
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
    #title
    if not 'tit' in rec.keys():
        ejlmod3.metatagcheck(rec, artpage, ['og:title', 'DC.identifier'])
    else:
        ejlmod3.metatagcheck(rec, artpage, ['DC.identifier'])
    #department
    for a in artpage.find_all('a', attrs = {'rel' : 'Organisation'}):
        dep = a.text.strip()
        if dep in boringdeps:
            keepit = False
        else:
            rec['note'].append(dep)
            if re.search('Math', dep):
                rec['fc'] = 'm'
            elif dep == 'Quantum Engineering Centre for Doctoral Training (EPSRC)':
                rec['fc'] = 'k'
            elif dep == 'Department of Computer Science':
                rec['fc'] = 'c'
    #author
    for ul in artpage.find_all('ul', attrs = {'class' : 'relations persons'}):
        rec['autaff'] = [[ ul.text.strip(), publisher ]]
    for table in artpage.find_all('table', attrs = {'class' : 'properties'}):
        for tr in table.find_all('tr'):
            for th in tr.find_all('th'):
                tht = th.text.strip()
            for td in tr.find_all('td'):
                #supervisor
                if tht == 'Supervisor':
                    for span in td.find_all('span'):
                        rec['supervisor'].append([re.sub(' \(.*', '', span.text.strip())])
                #date
                elif tht == 'Date of Award':
                    rec['date'] = td.text.strip()
        table.decompose()
    #PDF
    for div in artpage.find_all('div', attrs = {'class' : 'documents'}):
        for a in div.find_all('a'):
              if a.has_attr('href') and re.search('pdf$', a['href']):
                  rec['hidden'] = 'https://research-information.bris.ac.uk' + a['href']
    #abstract
    for div in artpage.find_all('div', attrs = {'class' : 'content-content'}):
        div2 = div.find_all('div', attrs = {'class' : 'rendering'})[0]
        for h3 in div2.find_all('h3'):
            h3.decompose()
        rec['abs'] = div2.text
    if keepit:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['doi'])

ejlmod3.writenewXML(recs, publisher, jnlfilename)

