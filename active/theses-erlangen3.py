# -*- coding: utf-8 -*-
#harvest theses from Universität Erlangen-Nürnberg
#FS: 2019-11-04
#FS: 2022-09-22

import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import codecs
import time
import json
skipalreadyharvested = True

numofpages = 1
publisher = 'Erlangen - Nuremberg U.'
boring = ['54', '55', '56', '57', '58', '59']
hdr = {'User-Agent' : 'Magic Browser'}
recs = []
prerecs = []
jnlfilename = 'THESES-ERLANGEN-%s' % (ejlmod3.stampoftoday())

dokidir = '/afs/desy.de/user/l/library/dok/ejl/backup'
alreadyharvested = []
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    filenametrunc = re.sub('\d.*', '*doki', jnlfilename)
    alreadyharvested = list(map(tfstrip, os.popen("cat %s/*%s %s/%i/*%s | grep URLDOC | sed 's/.*=//' | sed 's/;//' " % (dokidir, filenametrunc, dokidir, ejlmod3.year(backwards=1), filenametrunc))))
    print('%i records in backup' % (len(alreadyharvested)))
    
links = []
for dep in ['Department+Physik', 'Department+Mathematik', 'Naturwissenschaftliche+Fakult%C3%A4t']:
    for year in [ejlmod3.year(), ejlmod3.year(backwards=1)]:
        tocurl = 'https://opus4.kobv.de/opus4-fau/solrsearch/index/search/searchtype/simple/query/%2A%3A%2A/browsing/true/doctypefq/doctoralthesis/start/0/rows/100/institutefq/' + dep + '/yearfq/' + str(year)
        ejlmod3.printprogress('=', [[year, dep], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(3)
        for div in tocpage.body.find_all('div', attrs = {'class' : 'results_title'}):
            for a in div.find_all('a'):
                rec = {'tc' : 'T', 'jnl' : 'BOOK', 'note' : []}
                rec['link'] = 'https://opus4.kobv.de' + a['href']
                rec['tit'] = a.text.strip()
                if dep == 'Department+Mathematik':
                    rec['fc'] = 'm'
                if rec['link'] in links:
                    print('  already in list')
                elif ejlmod3.checkinterestingDOI(rec['link']):
                    prerecs.append(rec)
                    links.append(rec['link'])
        print(' %i records so far' % (len(prerecs)))
                

            
i = 0
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress('-', [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(10)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['DC.Description', 'DC.description', 'DC.Subject', 'DC.subject', 'DC.Rights',
                                        'DC.rights', 'citation_pdf_url', 'DC.Identifier', 'DC.identifier', 'citation_language',
                                        'citation_date'])
    for table in artpage.body.find_all('table', attrs = {'class' : 'frontdoordata'}):
        for tr in table.find_all('tr'):
            for th in tr.find_all('th'):
                tht = th.text.strip()
            for td in tr.find_all('td'):
                tdt = td.text.strip()
                #Supervisor
                if tht == 'Advisor:':
                    rec['supervisor'] = [[tdt, 'Erlangen - Nuremberg U.']]
                #number of pages
                elif tht == 'Pagenumber:':
                    if re.search('^\d+$', tdt):
                        rec['pages'] = tdt
                #year
                elif tht == 'Year of Completion:':
                    rec['year'] = tdt
                #Language
                elif tht == 'Language:':
                    if tdt == 'German':
                        rec['language'] = 'german'
                        #translated title
                        for h3 in artpage.body.find_all('h3', attrs = {'class' : 'titlemain'}):
                            rec['transtit'] = h3.text.strip()
                #author (becaus of ORCID)
                elif tht == 'Author:':
                    orcid = False
                    for a in td.find_all('a', attrs = {'class' : 'orcid-link'}):
                        orcid = re.sub('.*\/', 'ORCID:', a['href'])
                        a.replace_with('')
                    tdt = td.text.strip()
                    if orcid: 
                        rec['autaff'] = [[ tdt, orcid, 'Erlangen - Nuremberg U.']]
                    else:
                        rec['autaff'] = [[ tdt, 'Erlangen - Nuremberg U.']]
                #date
                elif tht == 'Release Date:':
                    rec['date'] = tdt
                #DDC
                elif tht == 'Dewey Decimal Classification:':
                    for a in td.find_all('a'):
                        ddc = re.sub('.*\D(\d\d\d?).*', r'\1', a.text)
                        if ddc[:2] in boring or ddc[0] in ['1', '2', '3', '4', '6', '7', '8', '9']:
                            keepit = False
                        elif ddc[:2] == '00':
                            rec['fc'] = 'c'
                        elif ddc[:2] == '51':
                            rec['fc'] = 'm'
                        elif ddc[:2] == '52':
                            rec['fc'] = 'c'
                        else:
                            rec['note'].append(a.text)
    if keepit:
        if skipalreadyharvested and 'urn' in rec and rec['urn'] in alreadyharvested:
            print('    already in backup')
        else:
            recs.append(rec)
            ejlmod3.printrecsummary(rec)
    else:
        ejlmod3.adduninterestingDOI(rec['link'])
            

ejlmod3.writenewXML(recs, publisher, jnlfilename)

