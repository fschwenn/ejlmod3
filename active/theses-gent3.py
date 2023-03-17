# -*- coding: utf-8 -*-
#harvest theses from Gent
#FS: 2019-12-09
#FS: 2023-03-17

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import time
import ejlmod3

publisher = 'U. Gent (main)'
jnlfilename = 'THESES-GENT-%s' % (ejlmod3.stampoftoday())

skipalreadyharvested = True
rpp = 20

hdr = {'User-Agent' : 'Magic Browser'}
persdict = {}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

#get details of persons
def getperson(perslink):
    #print(' .  ', perslink)
    try:
        perspage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(perslink), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            perspage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(perslink), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            persdict[perslink] = []
            return 
    #name
    person = []
    for h1 in perspage.find_all('h1', attrs = {'itemprop' : 'name'}):
        name = re.sub('^em\. ', '', h1.text.strip())
        name = re.sub('^prof\. ', '', name)
        name = re.sub('^ereprof\. ', '', name)
        name = re.sub('^dr\. ', '', name)
        name = re.sub('^ir\. ', '', name)
        if re.search(' [vV]an ', name):
            person = [re.sub('(.*) [vV]an (.*)', r'van \2, \1', name)]
        else:
            person = [name]
    #ORCID
    (orcid, mail, address) = ('', '', '')
    for dl in perspage.body.find_all('dl'):
        for child in dl.children:
            try:
                child.name
            except:
                continue
            if child.name == 'dd':
                dd = child.text.strip()
                #ORCID
                if re.search('^ORCID', dt):
                    orcid = 'ORCID:' + dd
                #email
                elif re.search('mail', dt):
                    for a in child.find_all('a'):
                        email = re.sub('mailto:', 'EMAIL:', a['href'])
                #address
                elif re.search('address', dt):
                    address = 'Gent U., ' + re.sub('\n', ', ', dd) + ', Belgium'                                  
            elif child.name == 'dt':
                dt = child.text.strip()
    if orcid:
        person.append(orcid)
    elif mail:
        person.append(mail)
    if address:        
        person.append(address)
    persdict[perslink] = person
    #print('  . ', person)
   
prerecs = []
orgas = [ ('WE01', 'm'), ('WE02', 'm'), ('WE04', 'f'), ('WE05', ''), ('WE11', 'm'),
          ('TW05', ''), ('TW07', ''), ('TW16', 'm'), ('TW17', '')]
i = 0
for (dep, fc) in orgas:
    i += 1
    tocurl = 'https://biblio.ugent.be/publication?limit=' + str(rpp) + '&organization=' + dep + '&type=dissertation'
    ejlmod3.printprogress('=', [[i, len(orgas)], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for span in tocpage.body.find_all('span', attrs = {'class' : 'title'}):
        rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : ['Vorsicht: keine Abstracts!']}
        for a in span.find_all('a'):
            rec['artlink'] = a['href']
            if fc: rec['fc'] = fc
            prerecs.append(rec)
    print('  %4i records so far' % (len(prerecs)))
    time.sleep(2)
        
i = 0
recs = []
for rec in prerecs:
    i += 1
    keepit = True
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['artlink']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['artlink']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['artlink']), features="lxml")
        except:
            print("no access to %s" % (rec['artlink']))
            continue    
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_publication_date',
                                        'DC.subject', 'citation_pdf_url'])
    #license
    ejlmod3.globallicensesearch(rec, artpage)
    #first get handle
    for dl in artpage.body.find_all('dl'):
        for child in dl.children:
            if child.name is None:
                continue
                #handle
            if child.name == 'dd':
                dd = child.text.strip()
                if re.search('Handle', dt):
                    rec['hdl'] = re.sub('.*handle.net\/', '', dd)
                    if skipalreadyharvested and rec['hdl'] in alreadyharvested:
                        print('   already in backup')
                        keepit = False
            elif child.name == 'dt':
                dt = child.text.strip()
    if not keepit:
        continue
    #other metadata
    for dl in artpage.body.find_all('dl'):
        for child in dl.children:
            if child.name is None:
                continue

            if child.name == 'dd':
                dd = child.text.strip()
                #pages
                if re.search('Pages', dt):
                    if re.search('\d', dd):
                        rec['pages'] = re.sub('\D*(\d+).*', r'\1', dd)
                #language
                elif re.search('Language', dt):
                    if not re.search('nglish', dd):
                        rec['language'] = dd
                #author
                elif re.search('Author', dt):
                    if child.find_all('a') == []:
                        author = child.text.split('\n')
                        if author[0] == '':
                            author = author[1]
                        else:
                            author = author[0]
                        rec['autaff'] = [[author, publisher]]
                    else:
                        for a in child.find_all('a'):
                            perslink = 'https://biblio.ugent.be' + a['href']
                            if not perslink in list(persdict.keys()):
                                getperson(perslink)
                            if persdict[perslink]:
                                rec['autaff'] = [ persdict[perslink] ]
                            else:
                                rec['autaff'] = [ a.text.strip() ]
                            if len(rec['autaff'][0]) == 1 or (len(rec['autaff'][0]) == 2 and re.search('ORCID', rec['autaff'][0][1])):
                                rec['autaff'][0].append(publisher)
                #supervisor
                elif re.search('Promoter', dt):
                    for a in child.find_all('a'):
                        if re.search('^\/person', a['href']):
                            perslink = 'https://biblio.ugent.be' + a['href']
                            if not perslink in list(persdict.keys()):
                                getperson(perslink)
                            if persdict[perslink]:
                                rec['supervisor'].append( persdict[perslink] )
                            else:
                                rec['supervisor'].append( a.text.strip() )
            elif child.name == 'dt':
                dt = child.text.strip()
    if keepit:
        recs.append(rec)
        ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
