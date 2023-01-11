# -*- coding: utf-8 -*-
#harvest theses from Lund
#FS: 2020-08-15
#FS: 2023-01-10

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Lund U. (main)'

jnlfilename = 'THESES-LUND-%s' % (ejlmod3.stampoftoday())
rpp = 20
pages = 1
skipalreadyharvested = True

departments = [('Nuclear Physics', 'Lund U. (main)', 100062),
               ('Atomic Physics', 'Lund U. (main)', 1000622),
               ('Mathematical Physics', 'Lund U. (main)', 1000630),
               ('Particle Physics', 'Lund U.', 1000632),
               ('Solid State', 'Lund U. (main)', 1000623),
               ('Lund Observatory', 'Lund Observ.', 1000643),
	       ('Mathematics', 'Lund U. (main)', 1000665),	  
               ('Theoretical Particle Physics', 'Lund U., Dept. Theor. Phys.', 1000645)]

dokidir = '/afs/desy.de/user/l/library/dok/ejl/backup'
alreadyharvested = []
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    filenametrunc = re.sub('\d.*', '*doki', jnlfilename)
    alreadyharvested = list(map(tfstrip, os.popen("cat %s/*%s %s/%i/*%s | grep URLDOC | sed 's/.*=//' | sed 's/;//' " % (dokidir, filenametrunc, dokidir, ejlmod3.year(backwards=1), filenametrunc))))
    print('%i records in backup' % (len(alreadyharvested)))
    
hdr = {'User-Agent' : 'Magic Browser'}
recs = []
for (department, aff, dnr) in departments:
    for page in range(pages):
        tocurl = 'https://lup.lub.lu.se/search/publication?limit=%i&q=documentType+exact+thesis&q=department+exact+v%i&sort=year.desc&start=%i' % (rpp, dnr, rpp*page)
        ejlmod3.printprogress("-", [[department], [page+1, pages], [tocurl]])
        req = urllib.request.Request(tocurl, headers=hdr)
        tocpage = BeautifulSoup(urllib.request.urlopen(req))
        for li in tocpage.body.find_all('li', attrs = {'class' : 'unmarked-record'}):
            rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'note' : [department],
                   'supervisor' : []}
            for span in li.find_all('span', attrs = {'class' : 'title'}):
                for a in span.find_all('a'):
                    rec['link'] = a['href']
                    rec['doi'] = '20.2000/LUND/' + re.sub('.*\/', '', a['href'])
                    rec['tit'] = a.text.strip()
                    rec['aff'] = aff
            if department in ['Atomic Physics', 'Solid State']:
                rec['fc'] = 'q'
            elif department in ['Mathematical Physics', 'Mathematics']:
                rec['fc'] = 'm'
            elif department =='Lund Observatory':
                rec['fc'] = 'a'
            if rec['doi'] in alreadyharvested:
                print('    %s already in backup' % (rec['link']))
            else:
                recs.append(rec)
        time.sleep(3)

i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']))
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']))
        except:
            print("no access to %s" % (rec['link']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_title', 'citation_publication_date',
                                        'dc.subject', 'dc.description', 'dc.language', 'citation_pdf_url',
                                        'citation_isbn'])
    for dl in artpage.body.find_all('dl'):
        for child in dl.children:
            try:
                child.name
            except:
                continue
            if child.name == 'dt':
                dtt = child.text
            elif child.name == 'dd':
                #author's ORCID
                if dtt == 'author':
                    for a in child.find_all('a'):
                        if a.has_attr('href') and re.search('orcid.org\/', a['href']):
                            rec['autaff'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', a['href']))
                #supervisor
                elif dtt == 'supervisor':
                    for li in child.find_all('li'):
                        for span in li.find_all('span', attrs = {'class' : 'fn'}):
                            rec['supervisor'].append([span.text.strip()])
                            for a in span.find_all('a'):
                                if a.has_attr('href') and re.search('orcid.org\/', a['href']):
                                    rec['supervisor'][-1].append(re.sub('.*orcid.org\/', 'ORCID:', a['href']))
                #pages
                elif dtt == 'pages':
                    if re.search('\d\d', child.text):
                        rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', child.text.strip())
    #author's affiliation
    rec['autaff'][-1].append(rec['aff'])
    ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
