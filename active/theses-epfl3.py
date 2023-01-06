# -*- coding: utf-8 -*-
#harvest theses from EPFL
#FS: 2019-10-28

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

insttoskip = ['CDH', 'CDM', 'SV', 'SB/ISIC', 'SB/CIBM', 'STI/IBI-STI', 'STI/IMX/LMC', 'STI/IMX/SMAL',
              'IC/IINFCOM/CHILI', 'ENAC']
reharvest = True

#check already harvested
ejldirs = ['/afs/desy.de/user/l/library/dok/ejl/backup',
           '/afs/desy.de/user/l/library/dok/ejl/backup/%i' % (ejlmod3.year(backwards=1)),
           '/afs/desy.de/user/l/library/dok/ejl/backup/%i' % (ejlmod3.year(backwards=2))]
redoki = re.compile('THESES.EPFL.*doki$')
rehttp = re.compile('^I\-\-(http.*\d).*')
bereitsin = []
for ejldir in ejldirs:
    #print(ejldir)
    for datei in os.listdir(ejldir):
        if redoki.search(datei):
            inf = open(os.path.join(ejldir, datei), 'r')
            for line in inf.readlines():
                if len(line) > 1 and line[0] == 'I':
                    if rehttp.search(line):
                        http = rehttp.sub(r'\1', line.strip())
                        if not http in bereitsin:
                            bereitsin.append(http)
            #print('  %6i %s' % (len(bereitsin), datei))

                  
publisher = 'Ecole Polytechnique, Lausanne'
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
recs = {}
for year in [ejlmod3.year(), ejlmod3.year(backwards=1)]: 
    prerecs = []
    tocurl = 'https://infoscience.epfl.ch/search?ln=en&cc=Infoscience%2FResearch%2FThesis&p=&f=&rm=&ln=en&sf=year&so=d&rg=500&c=Infoscience%2FResearch%2FThesis&c=&of=hb&fct__3=' + '%i' % (year)
    ejlmod3.printprogress('=', [[year], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    time.sleep(30)
    for div in tocpage.body.find_all('div', attrs = {'class' : 'result-title'}):
        for a in div.find_all('a'):
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'year' : str(year), 'keyw' : [], 'inst' : '', 'date' : str(year), 'supervisor' : [], 'note' : []}
            rec['artlink'] = 'https://infoscience.epfl.ch' + a['href']
            rec['tit'] = a.text.strip()
            if ejlmod3.checkinterestingDOI(rec['artlink']):
                if reharvest or not rec['artlink'] in bereitsin:
                    prerecs.append(rec)
                
    j = 0
    for rec in prerecs:
        keepit = True
        j += 1
        recsstat = [len(recs[inst]) for inst in recs]
        ejlmod3.printprogress('-', [[year], [j, len(prerecs)], [rec['artlink']], recsstat, [sum(recsstat)]])
        try:
            req = urllib.request.Request(rec['artlink'])
            artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
            time.sleep(10)
        except:
            print('wait 10 minutes')
            time.sleep(600)
            req = urllib.request.Request(rec['artlink'])
            artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
            time.sleep(30)
        ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'description', 'citation_keywords', 'citation_doi', 'citation_pdf_url'])
        rec['autaff'][-1].append('Ecole Polytechnique, Lausanne')
        for a in artpage.body.find_all('a'):
            if a.has_attr('href'):
                if re.search('\/collection\/Infoscience\/Research\/[A-Z]', a['href']):
                    inst = re.sub('.*Research\/(.*)\?.*', r'\1', a['href'])
                    if inst != 'Thesis':
                        #print(' . ', inst)
                        if inst in insttoskip:
                            keepit = False
                        elif inst in ['SB/Mathematics', 'SB/MATH']:
                            rec['fc'] = 'm'
                        elif inst in ['SB/IPHYS/C3MP', 'SB/IPHYS/CTMC']:
                            rec['fc'] = 'f'
                        elif inst in ['SB/IPHYS/LASTRO', 'SB/IPHYS/LPPC']:
                            rec['fc'] = 'a'
                        elif inst in ['SB/IPHYS/LQM', 'SB/IPHYS/LQP']:
                            rec['fc'] = 'k'
                        elif inst in ['IC']:
                            rec['fc'] = 'c'
                        if len(inst) > len(rec['inst']):
                            rec['inst'] = inst
                            rec['note'] = [ inst ]
        rec['inst'] = re.sub('\/.*', '', rec['inst'])
        for div in artpage.body.find_all('div', attrs = {'class' : 'metadata-row'}):
            for span in div.find_all('span', attrs = {'class' : 'title'}):
                title = span.text.strip()
            for span in div.find_all('span', attrs = {'class' : 'value'}):
                #pages
                if title == 'Pagination':
                    if re.search('^\d+$', span.text.strip()):
                        rec['pages'] = span.text.strip()
                #supervisor
                elif title == 'Advisor(s)':
                    for a in span.find_all('a'):
                        rec['supervisor'].append([a.text])    
        if keepit:
            if rec['inst'] in recs:
                recs[rec['inst']].append(rec)
            else:
                recs[rec['inst']] = [rec]
            rec['note'].append(rec['artlink'])
            ejlmod3.printrecsummary(rec)
        else:
            #print('skip thesis from %s' % (rec['inst']))
            ejlmod3.adduninterestingDOI(rec['artlink'])

for inst in list(recs.keys()):                
    jnlfilename = 'THESES-EPFL-%s_%s' % (ejlmod3.stampoftoday(), inst)            
    ejlmod3.writenewXML(recs[inst], publisher, jnlfilename)
