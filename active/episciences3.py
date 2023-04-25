# -*- coding: UTF-8 -*-
#program to harvest overlay journals from episciences.org
# FS: 2023-04-13

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

ejldir = '/afs/desy.de/user/l/library/dok/ejl'
pagemax = 2
years = 2

journals = {'arima' : {'publisher' : 'African Society in Digital Science',
                       'jnl' : 'ARIMA',
                       'jnllong' : 'Revue africaine de recherche en informatique et mathématiques appliquées',
                       'license' : 'CC-BY-4.0'},
            'cm' : {'publisher' : 'University of Ostrava',
                    'jnl' : 'Commun.Math.',
                    'jnllong' : 'Communications in Mathematics',
                    'fc' : 'm', 'license' : 'CC-BY-SA-4.0'},
            'dmtcs' : {'publisher': 'Association DMTCS',
                       'jnl' : 'Discrete Math.Theor.Comput.Sci.',
                       'jnllong' : 'Discrete Mathematics & Theoretical Computer Science',
                       'license' : 'CC-BY-4.0'},
            'entics' : {'publisher': 'Inria',
                        'jnl' : 'Electron.Notes Theor.Inform.Comp.Sci.',
                        'jnllong' : 'Electronic Notes in Theoretical Informatics and Computer Science',
                        'fc' : 'c', 'license' : 'CC-BY-4.0', 'tc' : 'C'},
            'gcc' : {'publisher': 'Murray Elder',
                     'jnl' : 'jGCC',
                     'jnllong' : 'journal of Groups, Complexity, Cryptology',
                     'license' : 'CC-BY-4.0'},
            'ocnmp' : {'publisher': 'Norbert Euler',
                       'jnl' : 'Open Commun.Nonlin.Math.Phys.',
                       'jnllong' : 'Open Communications in Nonlinear Mathematical Physics',
                       'fc' : 'm', 'license' : 'CC-BY-4.0'},
            'epiga' : {'publisher': 'Association Épiga',
                       'jnllong' : 'Epijournal de Géométrie Algébrique',
                       'jnl' : 'EPIGA',
                       'fc' : 'm', 'license' : 'CC-BY-SA-4.0'}}

#get volumes that have been harvested
revol = re.compile('.*(episciences_.*).doki')
done = []
for directory in [ejldir+'/backup', ejldir+'/backup/' + str(ejlmod3.year(backwards=1)),
                  ejldir+'/backup/' + str(ejlmod3.year(backwards=2)),
                  ejldir+'/backup/' + str(ejlmod3.year(backwards=3)),
                  ejldir+'/backup/' + str(ejlmod3.year(backwards=4)),
                  ejldir+'/backup/' + str(ejlmod3.year(backwards=5))]:
    for datei in os.listdir(directory):
        if revol.search(datei):
            done.append(revol.sub(r'\1', datei))
print('done', done)

#check available volumes
reconfname = re.compile('[A-Z][A-Za-z][A-Za-z]+ [12]\d\d\d')
hdr = {'User-Agent' : 'Magic Browser'}
todo = []
i = 0
for (k, journal) in enumerate(journals):
    pages = 1
    toctocurl = 'https://%s.episciences.org/browse/volumes' % (journal)
    ejlmod3.printprogress('==', [[k+1, len(journals)], [journal], [toctocurl]])
    req = urllib.request.Request(toctocurl, headers=hdr)
    toctocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
    for ul in toctocpage.find_all('ul', attrs = {'class' : 'pagination'}):
        for a in ul.find_all('a'):
            atext = a.text.strip()
            if re.search('^\d+$', atext):
                if int(atext) > pages and int(atext) <= pagemax:
                    pages = int(atext)                    
    for page in range(pages):
        if page > 0:
            ejlmod3.printprogress('==', [[k+1, len(journals)], [journal], [page+1, pages], [toctocurl]])
            req = urllib.request.Request(toctocurl, headers=hdr)
            toctocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
        for div in toctocpage.body.find_all('div', attrs = {'class' : 'media'}):
            for a in div.find_all('a'):
                if re.search('view\/id', a['href']):
                    jnlfilename = 'episciences_%s_%s' % (journal, re.sub('\D', '', a['href']))
                    if jnlfilename in done:
                        print('    %s already in backup' % (jnlfilename))
                        break
                    else:
                        print('    %s will be harvested: https://%s.episciences.org%s' % (jnlfilename, journal, a['href']))
                        i += 1
                        todo.append((i, journal, jnlfilename, 'https://%s.episciences.org%s' % (journal, a['href'])))
                        break
#            break
        toctocurl = 'https://%s.episciences.org/browse/volumes/page/%i' % (journal, page+1+1)
        time.sleep(5)

ouf = open('episciences.log', 'w')
reconf = re.compile('(orkshop|chool|roceedings|olloquium|onference)')
#harvest individual volumes
for (i, journal, jnlfilename, tocurl) in todo:
    ejlmod3.printprogress('=', [[i, len(todo)], [tocurl]])
    publisher = journals[journal]['publisher']
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
    volname = tocpage.head.title.text.strip()
    recs = []
    for div in tocpage.body.find_all('div', attrs = {'id' : 'papers'}):
        for h3 in div.find_all('h3'):
            for a in h3.find_all('a'):
                rec = {'jnl' : journals[journal]['jnl'], 'tc' : 'P'}
                rec['artlink'] = 'https://%s.episciences.org%s' % (journal, a['href'])
                rec['tit'] = a.text.strip()
                rec['license'] = {'statement' : journals[journal]['license']}
                rec['note'] = [volname]
                rec['p1'] = re.sub('\D', '', a['href'])
                if 'fc' in journals[journal]:
                    rec['fc'] = journals[journal]['fc']
                if 'tc' in journals[journal]:
                    rec['tc'] = journals[journal]['tc']
                recs.append(rec)
    time.sleep(5)
    tooold = False
    for (j, rec) in enumerate(recs):
        ejlmod3.printprogress('-', [[i, len(todo)], [j+1, len(recs)], [rec['artlink']]])
        req = urllib.request.Request(rec['artlink'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req), features='lxml')
        ejlmod3.metatagcheck(rec, artpage, ['citation_doi', 'DC.date', 'citation_keywords',
                                            'citation_abstract', 'citation_author',
                                            'citation_language', 'citation_pdf_url'])
        #pubnote
        for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_volume'}):
            pbn = meta['content']
            if re.search('[12]\d\d\d', pbn):
                rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', pbn)
            if re.search('olume (\d+)', pbn):
                rec['vol'] = re.sub('.*olume (\d+).*', r'\1', pbn)
            elif re.search('[vV]ol\. *\d+:\d+', pbn):
                rec['vol'] = re.sub('.*[vV]ol\. *(d+).*', r'\1', pbn)
                rec['issue'] = re.sub('.*[vV]ol\. *\d+:(\d+).*', r'\1', pbn)
            elif re.search('[Vv]ol\. *\d+,? *no\.? *\d+', pbn):
                rec['vol'] = re.sub('.*[vV]ol\. *(\d+).*', r'\1', pbn)
                rec['issue'] = re.sub('.*[vV]ol\. *\d+,? *no\.? *(\d+).*', r'\1', pbn)
            if re.search('ssue (\d+)', pbn):
                rec['issue'] = re.sub('.*ssue (\d+).*', r'\1', pbn)
            if reconf.search(pbn) or reconf.search(volname):
                rec['tc'] = 'C'
                #print('[%s] -> C' % (volname))
            elif reconfname.search(pbn) or reconfname.search(volname):
                rec['tc'] = 'C'
                #print('[%s] -> C' % (volname))
        #source
        for div in artpage.body.find_all('div', attrs = {'class' : 'small'}):
            if re.search('Source *:', div.text):
                for a in div.find_all('a'):
                    rec['note'].append(a['href'])
                    if re.search('arxiv.org\/abs', a['href']):
                        rec['arxiv'] = re.sub('v\d+$', '', re.sub('.*arxiv.org\/abs\/', '', a['href']))
        ouf.write('TC:::' + rec['tc'] + ' ' + volname + '\n')
        if 'issue' in rec:
            ouf.write('ISSUE:::' + rec['issue'] + ' ' + volname + '\n')
        else:
            ouf.write('NO ISSUE:::' + volname + '\n')
        ejlmod3.printrecsummary(rec)
        if 'year' in rec and int(rec['year']) <= ejlmod3.year(backwards=years):
            tooold = True
            print('  %s is too old!\n\n' % (rec['year']))
            break
        time.sleep(5)
    if not tooold:
        ejlmod3.writenewXML(recs, publisher, jnlfilename)
    time.sleep(60)
ouf.close()
            
