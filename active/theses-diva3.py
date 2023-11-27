# -*- coding: utf-8 -*-
#harvest theses from DIVA
#FS: 2019-09-15
#FS: 2023-01-11

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'publisher'

categories = {'physik' : {'Id' : '11520', 'recs' : []},
              'mathe'  : {'Id' : '11501', 'recs' : [], 'fc' : 'm'}}
startyear = str(ejlmod3.year(backwards=1))
stopyear = str(ejlmod3.year())
skipalreadyharvested = True

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested('THESES-DIVA')
else:
    alreadyharvested = []

                
hdr = {'User-Agent' : 'Magic Browser'}
for cate in list(categories.keys()):
    prerecs = []
    p = 1
    complete = False
    artlinks = []
    while not complete:
        tocurl = 'http://www.diva-portal.org/smash/resultList.jsf?p=' + str(p) + '&fs=false&language=en&searchType=RESEARCH&query=&af=%5B%5D&aq=%5B%5B%5D%5D&aq2=%5B%5B%7B%22dateIssued%22%3A%7B%22from%22%3A%22' + startyear + '%22%2C%22to%22%3A%22' + stopyear + '%22%7D%7D%2C%7B%22categoryId%22%3A%22' + categories[cate]['Id'] + '%22%7D%2C%7B%22publicationTypeCode%22%3A%5B%22comprehensiveDoctoralThesis%22%2C%22monographDoctoralThesis%22%2C%22comprehensiveLicentiateThesis%22%2C%22monographLicentiateThesis%22%5D%7D%5D%5D&aqe=%5B%5D&noOfRows=50&sortOrder=author_sort_asc&sortOrder2=title_sort_asc&onlyFullText=false&sf=all'
        ejlmod3.printprogress('=', [[cate], [tocurl]])
        try:
            req = urllib.request.Request(tocurl, headers=hdr)
            tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
            time.sleep(3)
        except:
            time.sleep(30)
            req = urllib.request.Request(tocurl, headers=hdr)
            tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
            time.sleep(3)
            
        for a in tocpage.body.find_all('a', attrs = {'class' : 'titleLink'}):
            if a.text == 'Browse':
                continue
            rec  = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'autaff' : [], 'supervisor' : []}
            rec['artlink'] = 'http://www.diva-portal.org' + a['href']
            if 'fc' in categories[cate]:
                rec['fc'] = categories[cate]['fc']
            if not rec['artlink'] in artlinks:
                prerecs.append(rec)
                artlinks.append(rec['artlink'])
        
        for span in tocpage.body.find_all('span', attrs = {'class' : 'paginInformation'}):
            target = int(re.sub('.*of (\d+).*', r'\1', span.text.strip()))
        ejlmod3.printprogress("  ", [[len(prerecs), target]])
        if len(prerecs) < target and p < target:
            p += 50
        else:
            complete = True
        
    jnlfilename = 'THESES-DIVA-%s_%s' % (cate, ejlmod3.stampoftoday())
    i = 0
    for rec in prerecs:
        i += 1
        ejlmod3.printprogress("-", [[cate], [i, len(prerecs)], [rec['artlink']], [len(categories[cate]['recs'])]])
        try:
            req = urllib.request.Request(rec['artlink'], headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        except:
            time.sleep(30)
            req = urllib.request.Request(rec['artlink'], headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        ejlmod3.metatagcheck(rec, artpage, ['DC.Description', 'DC.Title', 'DC.Identifier.doi',
                                            'DC.Identifier', 'DC.Subject', 'DC.Language',
                                            'citation_publication_date', 'citation_pdf_url'])
        if not 'doi' in list(rec.keys()):
            for link in artpage.head.find_all('link', attrs = {'rel' : 'canonical'}):
                rec['link'] = link['href']
        for div in artpage.body.find_all('div', attrs = {'id' : 'innerEastCenter'}):
             section = ''
             for child in div.children:
                try:
                    name = child.name
                except:
                    continue
                #author
                if name == 'div' and not rec['autaff']:
                    for h3 in child.find_all('h3'):
                        rec['autaff'].append([ h3.text.strip() ])
                        h3.replace_with('')
                    for span in child.find_all('span', attrs = {'class' : 'singleRow'}):
                        spant = re.sub('[\n\t]', '', span.text.strip())
                        spant = re.sub('ORCID ..: *', 'ORCID:', spant)
                        span.replace_with('')
                        rec['autaff'][0].append(spant)
                    for span in child.find_all('span'):
                        spant = re.sub('[\n\t]', '', span.text.strip())
                        if spant:
                            rec['autaff'][0].append(spant)
#                if name == 'span':
#                    for grandchild in child.children:
                if 1 == 1:
                        try:
                            gname = child.name
                        except:
                            gname = ''
                        if gname == 'h5':
                            section = re.sub('[\n\t]', '', child.text.strip())
                        #abstract
                        elif section == 'Abstract [en]' and gname == 'span':
                            rec['abs'] = child.text.strip()
                            section = ''
                        #ISBN
                        elif section == 'Identifiers' and gname == 'span':
                            gtext = child.text.strip()
                            if re.search('ISBN:', gtext):
                                isbn = re.sub('.*(978.*?) .*', r'\1', re.sub('[\n\t]', '', gtext))
                                rec['isbn'] = re.sub('\-', '', isbn)
                                section = ''
                        elif gname == 'script':
                            section = ''
        if skipalreadyharvested and 'urn' in rec and rec['urn'] in alreadyharvested:
            print('    %s already in backup' % (rec['urn']))
        else:
            ejlmod3.printrecsummary(rec)
            time.sleep(10)
            categories[cate]['recs'].append(rec)
        time.sleep(1)
        
    ejlmod3.writenewXML(categories[cate]['recs'], publisher, jnlfilename)
