# -*- coding: utf-8 -*-
#harvest theses from Rio de Janeiro, CBPF
#FS: 2020-03-26
#FS: 2023-03-15

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import mechanize

publisher = 'Rio de Janeiro, CBPF'
jnlfilename = 'THESES-CBPF-%s' % (ejlmod3.stampoftoday())

pages = 1
skipalreadyharvested = True

tocurl = 'http://cbpfindex.cbpf.br/index.php?moduleFile=listPublications&pubType=9'

br = mechanize.Browser()
br.set_handle_robots(False)   # ignore robots
br.set_handle_refresh(False)  # can sometimes hang without this
br.addheaders = [('User-agent', 'Firefox')]
response = br.open(tocurl)

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)

recs = []
print(tocurl)
for page in range(pages):
    tocpage = BeautifulSoup(response.read(), features='lxml')
    ejlmod3.printprogress("=", [[page+1, pages]])
    for a in tocpage.body.find_all('a', attrs = {'title' : 'Ver detalhes'}):
        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'supervisor' : []}        
        rec['link'] = 'http://cbpfindex.cbpf.br/' + a['href']
        rec['doi'] = '20.2000/CBPF/' + re.sub('\D', '', a['href'])
        if skipalreadyharvested and rec['doi'] in alreadyharvested:
            print('  ', rec['link'], 'already in backup')
        else:
            print('  ', rec['link'])
            recs.append(rec)
    #click to next page
    br.form = list(br.forms())[2]
    control = br.form.find_control('start')
    control.readonly = False
    control.value = "%i" % (16*page+32)
    time.sleep(5)
    response = br.submit()
    
i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
        time.sleep(8)
    except:
        print("retry %s in 180 seconds" % (rec['link']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features='lxml')
    #get rid of associated articles
    for fieldset in artpage.body.find_all('fieldset'):
        for legend in fieldset.find_all('legend'):
            if re.search('Artigo', legend.text):
                fieldset.decompose()
                print('  removed related articles from theses metadata page')
    #title
    for td in artpage.body.find_all('td', attrs = {'class' : 'pubTitle'}):
        rec['tit'] = td.text.strip()
    for td in artpage.body.find_all('td'):        
        bt = ''
        bs = td.find_all('b')
        if len(bs) == 1:
            for b in bs:
                bt = b.text.strip()
                b.decompose()
        #date
        if re.search('Publica', bt):
            if re.search('\d\d\/\d\d\/\d\d\d\d', td.text.strip()):
                rec['date'] = re.sub('.*(\d\d).(\d\d).(\d\d\d\d).*', r'\3-\2-\1', td.text.strip())
            elif re.search('\d\d\d\d', td.text.strip()):
                rec['date'] = re.sub('.*(\d\d\d\d).*', r'\1', td.text.strip())
        #author
        elif re.search('Aluno', bt):
            rec['autaff'] = [[td.text.strip().strip(), publisher]]
        #supervisor
        elif re.search('Orientador', bt):
            rec['supervisor'].append([td.text.strip().strip()])
        #department
        #elif re.search('Institui', bt):
        #    rec['department'] = td.text.strip().strip()
        #    rec['note'] = [rec['department']]
        #abstract
        elif re.search('Resum', bt):
            rec['abs'] = td.text.strip().strip()
        #defense date
        elif re.search('Data da defesa', bt):
            if re.search('\d\d\/\d\d\/\d\d\d\d', td.text.strip()):
                rec['MARC'] = [('500', [('a', re.sub('.*(\d\d).(\d\d).(\d\d\d\d).*', r'Presented on \3-\2-\1', td.text.strip()))])]
            elif re.search('\d\d\d\d', td.text.strip()):
                rec['MARC'] = [('500', [('a', re.sub('.*(\d\d\d\d).*', r'Presented on \1', td.text.strip()))])]
    #PDF
    for a in artpage.body.find_all('a'):
        for img in a.find_all('img'):
            if re.search('Download do PDF', a.text):
                rec['hidden'] = 'http://cbpfindex.cbpf.br/' + a['href']
    ejlmod3.printrecsummary(rec)
       

ejlmod3.writenewXML(recs, publisher, jnlfilename)
