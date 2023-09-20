# -*- coding: utf-8 -*-
#harvest theses from Sachsen
#FS: 2020-07-07
#FS: 2023-03-24
#FS: 2023-08-21


import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import mechanize

pages = 3
skipalreadyharvested = True
startyear = ejlmod3.year(backwards=1)
stopyear = ejlmod3.year()+1

uni = sys.argv[1]

if uni == 'dresden':
    publisher = 'TU, Dresden (main)'
    jnlfilename = 'THESES-DRESDEN-%s' % (ejlmod3.stampoftoday())
    starturl = 'https://tud.qucosa.de/recherche/?tx_dpf_frontendsearch[action]=extendedSearch&tx_dpf_frontendsearch[controller]=SearchFE'
elif uni == 'leipzig':
    publisher = 'Leipzig U.'
    jnlfilename = 'THESES-LEIPZIG-%s' % (ejlmod3.stampoftoday())
    starturl = 'https://ul.qucosa.de/recherche/?tx_dpf_frontendsearch[action]=extendedSearch&tx_dpf_frontendsearch[controller]=SearchFE'
elif uni == 'chemnitz':
    publisher = 'Chemnitz, Tech. U.'
    jnlfilename = 'THESES-CHEMNITZ-%s' % (ejlmod3.stampoftoday())
    starturl = 'https://monarch.qucosa.de/recherche/?tx_dpf_frontendsearch[action]=extendedSearch&tx_dpf_frontendsearch[controller]=SearchFE'
    

br = mechanize.Browser()
br.set_handle_robots(False)   # ignore robots
br.set_handle_refresh(False)  # can sometimes hang without this
br.addheaders = [('User-agent', 'Firefox')]
hdr = {'User-Agent' : 'Firefox'}

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

#select documents
recs = []
prerecs = []
for thesestype in ['doctoral_thesis', 'habilitation_thesis']:
    ejlmod3.printprogress('==', [[thesestype], [starturl]])
    response = br.open(starturl)
    br.form = list(br.forms())[0]
    control = br.form.find_control('tx_dpf_frontendsearch[query][doctype]')
    control.value = [thesestype]
    control = br.form.find_control('tx_dpf_frontendsearch[query][from]')
    control.value = str(startyear)
    control = br.form.find_control('tx_dpf_frontendsearch[query][till]')
    control.value = str(stopyear)
    time.sleep(2)
    response = br.submit()
    baseurl = response.geturl()
    basepage = BeautifulSoup(response, features='lxml')
    for div in basepage.find_all('div', attrs = {'class' : 'search-results'}):
        for span in div.find_all('span'):
            spant = span.text.strip()
            #print spant
            expnr = int(re.sub('\D', '', spant))
            pages = expnr // 20 + 1
            print('  expcecting %i records' % (expnr))
    for page in range(pages):
        tocurl = baseurl + '&tx_dpf_frontendsearch[%40widget_0][currentPage]=' + str(page+1)
        ejlmod3.printprogress("=", [[page+1, pages], [tocurl]])
        response = br.open(tocurl)
        tocpage = BeautifulSoup(response, features='lxml')
        for ol in tocpage.body.find_all('ol', attrs = {'class' : 'tx-dlf-listview-list'}):
            for li in ol.find_all('li'):
                for a in li.find_all('a'):
                    rec = {'tc' : 'T', 'jnl' : 'BOOK', 'supervisor' : [], 'note' : []}
                    rec['link'] = 'https://tud.qucosa.de' + a['href']
                    rec['artlink'] = 'https://tud.qucosa.de' + a['href']
                    if ejlmod3.checkinterestingDOI(rec['artlink']):
                        prerecs.append(rec)
                    #print '  ', a.text.strip()
        print('  %4i records so far' % (len(prerecs)))
        time.sleep(1)

i = 0
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
        time.sleep(2)
    except:
        print("retry %s in 180 seconds" % (rec['link']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
    for dl in artpage.body.find_all('dl'):
        for child in dl.children:
            try:
                cn = child.name
            except:
                cn = ''
                dtt = ''
            if cn == 'dt':
                dtt = child.text.strip()
            elif cn == 'dd':
                #author
                if dtt == 'AutorIn':
                    aff = False
                    for span in child.find_all('span'):
                        aff = span.text.strip()
                        span.decompose()
                    author = child.text.strip()
                    author = re.sub('^Dr\.\-Ing\. ', '', author)
                    author = re.sub('^Dr\.[a-z \.]+', '', author)
                    author = re.sub('Dipl.\-Phys. ', '', author)
                    author = re.sub('Dipl.\-Math. ', '', author)
                    author = re.sub('Diplom-Informatikeri?n? ', '', author)
                    author = re.sub('M\.Sc\. ', '', author)
                    author = re.sub('M\.Ed\. ', '', author)
                    author = re.sub('B\.Sc\. ', '', author)
                    author = re.sub('Diplom.Physikeri?n? ', '', author)
                    rec['autaff'] = [[ author ]]
                    if aff:
                        rec['autaff'][-1].append(aff)
                    else:
                        rec['autaff'][-1].append(publisher)
                #title
                elif dtt == 'Titel':
                    rec['tit'] = child.text.strip()
                #abstract
                elif dtt == 'Abstract (EN)':
                    rec['absen'] = child.text.strip()
                elif dtt == 'Abstract (DE)':
                    rec['absde'] = child.text.strip()
                #ddc
                elif dtt == 'Klassifikation (DDC)':
                    rec['ddc' ] =  child.text.strip()
                #URN
                elif dtt == 'URN Qucosa':
                    rec['urn'] = child.text.strip()
                #language
                elif dtt == 'Sprache des Dokumentes':
                    if child.text.strip() == 'Deutsch':
                        rec['language'] = 'german'
                #date
                elif dtt == 'Datum der Einreichung':
                    parts = re.split('\.', child.text.strip())
                    rec['date'] = '%s-%s-%s' % (parts[2], parts[1], parts[0])
                #presentation
                elif dtt == 'Datum der Verteidigung':
                    parts = re.split('\.', child.text.strip())
                    rec['MARC'] = [('500', [('a', 'Presented on %s-%s-%s' % (parts[2], parts[1], parts[0]))])]
                #link
                elif re.search('^Zitierf', dtt):
                    for a in child.find_all('a'):
                        rec['link'] = a['href']
                #keywords
                elif re.search('^Freie Schlagw.*EN', dtt):
                    rec['keywen'] = re.split(', ', child.text.strip())
                elif re.search('^Freie Schlagw.*DE', dtt):
                    rec['keywde'] = re.split(', ', child.text.strip())
                #supervisor
                elif re.search('^BetreuerIn Hochschule', dtt):
                    supervisors = []
                    for li in child.find_all('li'):
                        supervisors.append(li.text.strip())
                    if not supervisors:
                        supervisors.append(child.text.strip())
                    for supervisor in supervisors:
                        supervisor = re.sub('Univ\.\-Prof\.? ', '', supervisor)
                        supervisor = re.sub('Prof\.? ', '', supervisor)
                        supervisor = re.sub('Dr\.\-Ing\.?[a-z \.]+', '', supervisor)
                        supervisor = re.sub('Dr\.[a-z \.]+', '', supervisor)
                        supervisor = re.sub('PD\.', '', supervisor)
                        rec['supervisor'].append([supervisor])
    #german or english keywords/abstracts
    if 'absen' in list(rec.keys()):
        rec['abs'] = rec['absen']
    elif 'absde' in list(rec.keys()):
        rec['abs'] = rec['absde']
    if 'keywen' in list(rec.keys()):
        rec['keyw'] = rec['keywen']
    elif 'keywde' in list(rec.keys()):
        rec['keyw'] = rec['keywde']
    #license
    for a in artpage.body.find_all('a'):
        if a.has_attr('href') and re.search('creativecommons.org', a['href']):
            rec['licence'] = {'url' : a['href']}
    #FFT
    for meta in artpage.head.find_all('meta', attrs = {'name' : 'citation_pdf_url'}):
        print(meta)
        if 'licence' in list(rec.keys()):
            if not 'FFT' in rec:
                rec['FFT'] = meta['content']
        else:
            if not 'hidden' in rec:
                rec['hidden'] = meta['content']
    #pseudDOI
    if not 'urn' in list(rec.keys()):
        rec['doi'] = '20.2000/' + uni.upper() + '/' + re.sub('.*\/', '', rec['link'])
    if 'ddc' in list(rec.keys()) and not rec['ddc'][:2] in ['50', '51', '52', '53']:
        if rec['ddc'] != '004':
            print('     skip', rec['ddc'])
            ejlmod3.adduninterestingDOI(rec['artlink'])
    else:
        if skipalreadyharvested and 'urn' in rec and rec['urn'] in alreadyharvested:
            print('   already in backup')
        elif skipalreadyharvested and 'doi' in rec and rec['doi'] in alreadyharvested:
            print('   already in backup')
        else:
            ejlmod3.printrecsummary(rec)
            recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)#, retfilename='retfiles_special')
