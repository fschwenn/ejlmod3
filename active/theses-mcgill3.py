# -*- coding: utf-8 -*-
#harvest theses from McGill U.
#FS: 2020-02-07
#FS: 2022-11-28

import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

irrelevantsubjects = []

publisher = 'McGill U., Montreal (main)'
articlesperpage = 20
skipalreadyharvested = True
pages = 1
years = 2
departments = [('Department+of+Physics', 'McGill U.', 'PHYSICS'),
               ('Department+of+Electrical+and+Computer+Engineering', publisher, 'ENGINEERING'),
               ('Department+of+Mathematics+and+Statistics', 'McGill U., Math. Stat.', 'MATHEMATICS')]
urltrunc = 'https://escholarship.mcgill.ca'

hdr = {'User-Agent' : 'Magic Browser'}

links = []
jnlfilename = 'THESES-MCGILL-%s' % (ejlmod3.stampoftoday())
if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

prerecs = []
for (affurl, aff, affname) in departments:
    for page in range(pages):
        tocurl = urltrunc + '/catalog?f%5Bdegree_sim%5D%5B%5D=Doctor+of+Philosophy&f%5Bdepartment_sim%5D%5B%5D=' + affurl + '&f%5Brtype_sim%5D%5B%5D=Thesis&locale=en&page=' + str(page+1) + '&per_page=' + str(articlesperpage) + '&sort=system_create_dtsi+desc'
        ejlmod3.printprogress('=', [[affname], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        for li in tocpage.body.find_all('li', attrs = {'class' : 'document'}):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'affiliation' : aff}
            for h4 in li.find_all(['h3', 'h4'], attrs = {'class' : 'search-result-title'}):
                for a in h4.find_all('a'):
                    rec['link'] = urltrunc + a['href']
                    rec['tit'] = a.text.strip()
            if not 'link' in rec:
                print('???', li)                
            elif not rec['link'] in links:
                links.append(links)
                if affname == 'MATHEMATICS':
                    rec['fc'] = 'm'
                for dd in li.find_all('dd'):
                    ddt = dd.text.strip()
                    if re.search('^[12]\d\d\d', ddt):
                        rec['date'] = ddt
                        rec['year'] = re.sub('.*(\d\d\d\d).*', r'\1', ddt)
                        if int(rec['year']) > ejlmod3.year(backwards=years):
                            prerecs.append(rec)
        print('   %i theses so far' % (len(prerecs)))
        time.sleep(5)

j = 0
recs = []
for rec in prerecs:
    j += 1
    ejlmod3.printprogress('-' , [[j, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        req = urllib.request.Request(rec['link'])
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(20)
    except:
        print('wait 10 minutes')
        time.sleep(600)
        req = urllib.request.Request(rec['link'])
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(30)
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_pdf_url', 'citation_title'])
    rec['autaff'][-1].append(rec['affiliation'])
    #supervisor
    for dd in artpage.body.find_all('dd', attrs = {'class' : 'custom-dd-contributor'}):
        rec['supervisor'] = []
        for a in dd.find_all('a'):
            at = a.text.strip()
            if re.search('Supervisor', at):
                rec['supervisor'].append([re.sub(' *\(.*', '', at)])
    #abstract
    for dd in artpage.body.find_all('dd', attrs = {'class' : 'custom-dd-abstract'}):
        for div in dd.find_all('div', attrs = {'class' : 'panel'}):
            for h5 in div.find_all('h5'):
                if re.search('English', h5.text):
                    h5.replace_with('')
                    rec['abs'] = div.text.strip()
    #link
    for dd in artpage.body.find_all('dd', attrs = {'class' : 'custom-dd-identifier'}):
        for a in dd.find_all('a'):
            rec['link'] = a['href']
            rec['doi'] = '20.2000/McGill/' + re.sub('.*\/(.+)', r'\1', a['href'])
    #license
    for dd in artpage.body.find_all('dd', attrs = {'class' : 'custom-dd-rights'}):
        for a in dd.find_all('a'):
            if re.search('creativecommons', a['href']):
                rec['license'] = {'url' : a['href']}
    if not 'doi' in rec:
        rec['doi'] = '30.3000/McGill/' + re.sub('.*\/(.+)', r'\1', rec['link'])
    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
