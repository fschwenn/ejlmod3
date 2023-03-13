# -*- coding: utf-8 -*-
#harvest theses from Graz
#FS: 2020-08-28
#FS: 2023-03-13


import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

rpp = 20
skipalreadyharvested = True


publisher = 'Graz U.'
jnlfilename = 'THESES-GRAZ-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
hdr = {'User-Agent' : 'Magic Browser'}
tocurl = 'https://unipub.uni-graz.at/obvugroa/nav/classification/110928?max=' + str(rpp) + '&facets=type%3D%22oaDoctoralThesis%22&o=desc&s=date'
req = urllib.request.Request(tocurl, headers=hdr)
tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
prerecs = []
for div in tocpage.body.find_all('div', attrs = {'class' : 'miniTitleinfo'}):
    rec = {'tc' : 'T', 'keyw' : [], 'jnl' : 'BOOK', 'supervisor' : [], 'note' : []}
    for a in div.find_all('a'):
            rec['link'] = 'https://unipub.uni-graz.at' + a['href']
            rec['tit'] = a.text.strip()
    for div2 in div.find_all('div', attrs = {'class' : 'origin'}):
        if re.search('[12]\d\d\d', div2.text):
            rec['year'] = re.sub('.*?([12]\d\d\d).*', r'\1', div2.text.strip())
            rec['date'] = rec['year']
            if int(rec['year']) > ejlmod3.year(backwards=2):
                prerecs.append(rec)
            else:
                print('  skip', rec['year'])
        else:
            print('(YEAR?)', div2.text)
            prerecs.append(rec)

            
i = 0
recs = []
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        req = urllib.request.Request(rec['link'], headers=hdr)
        artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            req = urllib.request.Request(rec['link'], headers=hdr)
            artpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    ejlmod3.metatagcheck(rec, artpage, ['citation_author', 'citation_pdf_url'])
    rec['autaff'][-1].append(publisher)
    for table in artpage.body.find_all('table', attrs = {'id' : 'titleInfoMetadata'}):
        #supervisor
        for tr in table.find_all('tr', attrs = {'id' : 'mods_name-roleTerm_Censor'}):
            for a in tr.find_all('A'):
                rec['supervisor'].append([a.text.strip()])
        #pages
        for tr in table.find_all('tr', attrs = {'id' : 'mods_physicalDescriptionExtent'}):
            for span in tr.find_all('span', attrs = {'class' : 'extent'}):
                if re.search('\d\d', span.text):
                    rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', span.text.strip())
        #language
        for tr in table.find_all('tr', attrs = {'id' : 'mods_languageLanguageTerm'}):
            for td in tr.find_all('td', attrs = {'class' : 'value'}):
                tdt = td.text.strip()
                if tdt != 'Englisch':
                    rec['language'] = tdt
        #keywords
        for tr in table.find_all('tr', attrs = {'id' : 'mods_subjectAuthority'}):
            for span in tr.find_all('span', attrs = {'class' : 'topic'}):
                rec['keyw'].append(re.sub(' *\/$', '', span.text.strip()))
        #urn
        for tr in table.find_all('tr', attrs = {'id' : 'mods_IdentifierUrn'}):
            for td in tr.find_all('td', attrs = {'class' : 'value'}):
                rec['urn'] = td.text.strip()
    #license
    #for table in artpage.body.find_all('table', attrs = {'id' : 'titleInfoLicenceinfo'}):
    #    for span in table.find_all('span', attrs = {'class' : 'licenseInfo'}):
    #        rec['note'].append(span.text.strip())
    #abstract
    for table in artpage.body.find_all('table', attrs = {'id' : 'titleInfoAbstract'}):
        lang = False
        #check language
        for tr in table.find_all('tr'):
            for td in tr.find_all('td', attrs = {'class' : 'tdSubheader'}):
                if re.search('German', td.text) or re.search('Deutsch', td.text):
                    lang = 'ger'
                elif re.search('Englisc?h', td.text):
                    lang = 'eng'
                else:
                    lang = 'oth'
            #check abstract
            if lang:
                for td in tr.find_all('td', attrs = {'class' : 'titleAddContent'}):
                    rec['abs'+lang] = td.text.strip()
                    lang = False
        #consolidate
        if 'abseng' in list(rec.keys()):
            rec['abs'] = rec['abseng']
        elif 'absoth' in list(rec.keys()):
            rec['abs'] = rec['absoth']
        elif 'absger'in list(rec.keys()):
            rec['abs'] = rec['absger']
    if skipalreadyharvested and 'urn' in rec and rec['urn'] in alreadyharvested:
        pass
    else:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
