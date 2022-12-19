# -*- coding: utf-8 -*-
#harvest theses from Manchester
#FS: 2020-09-24
#FS: 2022-12-16

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'U. Manchester (main)'

pages = 12
years = 2
boring = ['Department of Materials', 'Department of Earth and Environmental Sciences',
          'Department of Mechanical, Aerospace & Civil Engineering',
          'Alliance Manchester Business School', 'Department of Chemical Engineering',
          'Department of Chemistry', 'Department of Electrical & Electronic Engineering']
jnlfilename = 'THESES-MANCHESTER-%s' % (ejlmod3.stampoftoday())
hdr = {'User-Agent' : 'Magic Browser'}

prerecs = []
for page in range(pages):
    tocurl = 'https://research.manchester.ac.uk/en/studentTheses/?type=%2Fdk%2Fatira%2Fpure%2Fstudentthesis%2Fstudentthesistypes%2Fstudentthesis%2Fphd&type=%2Fdk%2Fatira%2Fpure%2Fstudentthesis%2Fstudentthesistypes%2Fstudentthesis%2Fdoc&type=%2Fdk%2Fatira%2Fpure%2Fstudentthesis%2Fstudentthesistypes%2Fstudentthesis%2Fdsc&nofollow=true&organisationIds=6c84c61f-cee6-4ccc-8e76-643e407ef501&organisationIds=27f47c8b-1a5a-433b-8a25-24b49a9af000&organisationIds=fb90f3c7-013c-4abd-aea6-2d71fa1ce52e&organisationIds=6e3f13b0-fa6a-4c9b-b0a1-89e1bbd72e06&format=&page=' + str(page)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(4)
    for li in tocpage.body.find_all('li', attrs = {'class' : 'list-result-item'}):
        rec = {'tc' : 'T', 'note' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'keyw' : []}
        for span in li.find_all('span', attrs = {'class' : 'date'}):
            rec['date'] = span.text.strip()
            if re.search('[12]\d\d\d', rec['date']):
                rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', rec['date'])
        for h3 in li.find_all('h3', attrs = {'class' : 'title'}):
            for a in h3.find_all('a'):
                rec['link'] = a['href']
                rec['doi'] = '20.2000/Manchester/' + re.sub('\W', '', re.sub('.*\/', '', a['href'][-50:-4]))
                rec['tit'] = a.text.strip()
                if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
                    pass
                elif ejlmod3.ckeckinterestingDOI(rec['link']):
                    prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))

                    
recs = []
for (i, rec) in enumerate(prerecs):
    keepit = True
    aff = publisher
    ejlmod3.printprogress('-', [[i+1, len(prerecs)], [rec['link']], [len(recs)]])
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
    ejlmod3.metatagcheck(rec, artpage, ['og:title'])
    #author
    for ul in artpage.body.find_all('ul', attrs = {'class' : 'persons'}):
        for li in ul.find_all('li'):
            rec['autaff'] = [[ li.text.strip() ]]        
    #abstract
    for div in artpage.body.find_all('div', attrs = {'class' : 'rendering_studentthesisdetails'}):
        for h3 in div.find_all('h3'):
            h3.decompose()
        rec['abs'] = div.text.strip()
    #supervisor
    for tr in artpage.body.find_all('tr'):
        for th in tr.find_all('th'):
            if re.search('upervisor', th.text):
                for td in tr.find_all('td'):
                    tdt = re.sub('&amp;', ', ', td.text.strip())
                    tdt = re.sub('&', ', ', tdt)
                    tdt = re.sub('\(Supervisor\)', '', tdt)
                    for sv in re.split(' *, *', tdt.strip()):
                        rec['supervisor'].append([sv])                        
    #keywords
    for div in artpage.body.find_all('div', attrs = {'class' : 'keyword-group'}):
        for li in div.find_all('li', attrs = {'class' : 'userdefined-keyword'}):
            rec['keyw'].append(li.text.strip())
    #department
    for ul in artpage.body.find_all('ul', attrs = {'class' : 'organisations'}):
        for a in ul.find_all('a'):
            dep = a.text.strip()
            if dep in boring:
                keepit = False
            elif dep in ['Department of Mathematic', 'Department of Mathematics']:
                rec['fc'] = 'm'
            elif dep in ['Department of Computer Science']:
                rec['fc'] = 'c'
                aff = 'Manchester U., Comp. Sci. Dept.'
            elif dep in ['Department of Physics and Astronomy',
                         'Department of Physics & Astronomy',
                         'Department of Physics &amp; Astronomy']:
                aff = 'Manchester U.'
            else:
                rec['note'].append(dep)
    #fulltext
    for ul in artpage.body.find_all('ul', attrs = {'class' : 'documents'}):
        for a in ul.find_all('a'):
            if a.has_attr('href'):
                rec['hidden'] = 'https://research.manchester.ac.uk' + a['href']
    if keepit:
        rec['autaff'][-1].append(aff)
        recs.append(rec)
        ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])
        
ejlmod3.writenewXML(recs, publisher, jnlfilename)

