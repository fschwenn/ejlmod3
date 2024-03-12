# -*- coding: utf-8 -*-
#harvest theses from Antwerp U.
#FS: 2022-02-11
#FS: 2023-02-27

import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import mechanize

publisher = 'Antwerp U.'
rpp = 20
skipalreadyharvested = True

#need to update the UDses-token/cookie each time
starturl = 'https://repository.uantwerpen.be/submit.phtml?UDses=131032129%3A24586&UDstate=1&UDmode=&UDaccess=&UDrou=%25Start:bopwexe&UDopac=opacirua&UDextra='
starturl = 'https://repository.uantwerpen.be/submit.phtml?UDses=141700795%3A491263&UDstate=1&UDmode=&UDaccess=&UDrou=%25Start:bopwexe&UDopac=opacirua&UDextra='
starturl = 'https://repository.uantwerpen.be/submit.phtml?UDses=142468891%3A333120&UDstate=1&UDmode=&UDaccess=&UDrou=%25Start:bopwexe&UDopac=opacirua&UDextra='
starturl = 'https://repository.uantwerpen.be/submit.phtml?UDses=143880875%3A178106&UDstate=1&UDmode=&UDaccess=&UDrou=%25Start:bopwexe&UDopac=opacirua&UDextra='
starturl = 'https://repository.uantwerpen.be/submit.phtml?UDses=147297258%3A731463&UDstate=1&UDmode=&UDaccess=&UDrou=%25Start:bopwexe&UDopac=opacirua&UDextra='
starturl = 'https://repository.uantwerpen.be/submit.phtml?UDses=150515577%3A877314&UDstate=1&UDmode=&UDaccess=&UDrou=%25Start:bopwexe&UDopac=opacirua&UDextra='
starturl = 'https://repository.uantwerpen.be/submit.phtml?UDses=152220681%3A259347&UDstate=1&UDmode=&UDaccess=&UDrou=%25Start:bopwexe&UDopac=opacirua&UDextra='
starturl = 'https://repository.uantwerpen.be/submit.phtml?UDses=155559552%3A589017&UDstate=1&UDmode=&UDaccess=&UDrou=%25Start:bopwexe&UDopac=opacirua&UDextra='
starturl = 'https://repository.uantwerpen.be/submit.phtml?UDses=163225744%3A85842&UDstate=1&UDmode=&UDaccess=&UDrou=%25Start:bopwexe&UDopac=opacirua&UDextra='
starturl = 'https://repository.uantwerpen.be/submit.phtml?UDses=164707417%3A85922&UDstate=1&UDmode=&UDaccess=&UDrou=%25Start:bopwexe&UDopac=opacirua&UDextra='
starturl = 'https://repository.uantwerpen.be/submit.phtml?UDses=167411909%3A813839&UDstate=1&UDmode=&UDaccess=&UDrou=%25Start:bopwexe&UDopac=opacirua&UDextra='
starturl = 'https://repository.uantwerpen.be/submit.phtml?UDses=169736026%3A209879&UDstate=1&UDmode=&UDaccess=&UDrou=%25Start:bopwexe&UDopac=opacirua&UDextra='
starturl = 'https://repository.uantwerpen.be/submit.phtml?UDses=173742313%3A534051&UDstate=1&UDmode=&UDaccess=&UDrou=%25Start:bopwexe&UDopac=opacirua&UDextra='
starturl = 'https://repository.uantwerpen.be/submit.phtml?UDses=179714210%3A459699&UDstate=1&UDmode=&UDaccess=&UDrou=%25Start:bopwexe&UDopac=opacirua&UDextra='
starturl = 'https://repository.uantwerpen.be/submit.phtml?UDses=185059054%3A825846&UDstate=1&UDmode=&UDaccess=&UDrou=%25Start:bopwexe&UDopac=opacirua&UDextra='
starturl = 'https://repository.uantwerpen.be/submit.phtml?UDses=193415727%3A901451&UDstate=1&UDmode=&UDaccess=&UDrou=%25Start:bopwexe&UDopac=opacirua&UDextra='

br = mechanize.Browser()
br.set_handle_robots(False)   # ignore robots
br.set_handle_refresh(False)  # can sometimes hang without this
br.addheaders = [('User-agent', 'Firefox')]
hdr = {'User-Agent' : 'Firefox'}

#select documents
jnlfilename = 'THESES-ANTWERP-%s' % (ejlmod3.stampoftoday())

if skipalreadyharvested:
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)
response = br.open(starturl)
br.form = list(br.forms())[0]
control = br.form.find_control('FDopc_zv')
control.value = "(facultyac:a::irc.18)(pubtype:a::pt.13)"
control.value = "(facultyac:a::irc.18 OR facultyac:a::irc.19)(pubtype:a::pt.13)"
control.size = "20"
response = br.submit()
tocpage = BeautifulSoup(response.read(), features="lxml")
prerecs = []
for td in tocpage.find_all('td', attrs = {'class' : 'opacshortdescriptionunit'}):
    for a in td.find_all('a'):
       if a.has_attr('href') and re.search('brocade', a['href']): 
           rec = {'tc' : 'T', 'jnl' : 'BOOK', 'supervisor' : [], 'note' : [], 'autaff' : []}
           rec['link'] = 'https://repository.uantwerpen.be' + a['href']
           prerecs.append(rec)

recs = []
i = 0
for rec in prerecs:
    i += 1
    ejlmod3.printprogress("-", [[i, len(prerecs)], [rec['link']], [len(recs)]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(2)
    except:
        print("retry %s in 180 seconds" % (rec['link']))
        time.sleep(180)
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
    ejlmod3.metatagcheck(rec, artpage, ['citation_title', 'citation_author', 'citation_publication_date',
                                        'citation_language', 'citation_pdf_url'])
    #HDL
    for meta in artpage.head.find_all('meta', {'name' : 'citation_abstract_html_url'}):
        if re.search('hdl.handle.net', meta['content']):
            rec['hdl'] = re.sub('.*hdl.handle.net\/', '', meta['content'])
            rec['link'] = meta['content']
    #pages
    for span in artpage.body.find_all('span', attrs = {'class' : 'opaccatco'}):
        spant = span.text.strip()
        if re.search('\d\d', spant):
            rec['pages'] = re.sub('.*?(\d\d+).*', r'\1', spant)
    #abs
    for span in artpage.body.find_all('span', attrs = {'class' : 'opaccatin'}):
        for script in span.find_all('script'):
            rec['abs'] = re.sub("document.write\(unpmarked\('(.*)',''\)\);", r'\1', script.string)
    #supervisor
    for span in artpage.body.find_all('span', attrs = {'class' : 'opaccatnt'}):
        for span2 in span.find_all('span', attrs = {'class' : 'opaccatntheader'}):
            if re.search('Promotor', span2.text):
                span2.decompose()
                sv = re.sub(' *\[Promotor.*', '', span.text.strip())
                sv = re.sub('^: *', '', sv)
                sv = re.sub('\n', '', sv)
                rec['supervisor'].append([sv])
    if skipalreadyharvested and 'hdl' in rec and rec['hdl'] in alreadyharvested:
        print('   %s already in backup' % (rec['hdl']))
    else:
        ejlmod3.printrecsummary(rec)
        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
