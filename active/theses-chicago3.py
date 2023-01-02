# -*- coding: utf-8 -*-
#harvest theses from University of Chicago
#FS: 2020-03-03


import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time

publisher = 'Chicago U.'

startyear = ejlmod3.year(backwards=2)
endyear = ejlmod3.year()
recsperpage = 60
pages = 6
skipalreadyharvested = True
dokidir = '/afs/desy.de/user/l/library/dok/ejl/backup'

hdr = {'User-Agent' : 'Magic Browser'}
jnlfilename = 'THESES-CHICAGO-%s' % (ejlmod3.stampoftoday())

alreadyharvested = []
def tfstrip(x): return x.strip()
if skipalreadyharvested:
    filenametrunc = re.sub('\d.*', '*doki', jnlfilename)
    alreadyharvested = list(map(tfstrip, os.popen("cat %s/*%s %s/%i/*%s | grep URLDOC | sed 's/.*=//' | sed 's/;//' " % (dokidir, filenametrunc, dokidir, ejlmod3.year(backwards=1), filenametrunc))))
    print('%i records in backup' % (len(alreadyharvested)))        

recs = []
for page in range(pages):
    tocurl = 'https://catalog.lib.uchicago.edu/vufind/Search/Results?limit=' + str(recsperpage) + '&filter%5B%5D=format%3A%22Dissertations%22&filter%5B%5D=publishDate%3A%22%5B' + str(startyear) + '+TO+' + str(endyear) + '%5D%22&join=AND&bool0%5B%5D=AND&lookfor0%5B%5D=%22University+of+Chicago%22&type0%5B%5D=Author&sort=year&page=' + str(page+1)
    ejlmod3.printprogress('=', [[page+1, pages], [tocurl]])
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req), features="lxml")
    for div in tocpage.body.find_all('div', attrs = {'class' : 'result-body'}):
        rec = {'tc' : 'T', 'jnl' : 'BOOK', 'keyw' : [], 'supervisor' : []}
        for a in div.find_all('a', attrs = {'class' : 'title'}):
            rec['link'] = 'https://catalog.lib.uchicago.edu' + a['href']
            rec['doi'] = '20.2000/Chicago/' + re.sub('\D', '', a['href'])
            if not rec['doi'] in alreadyharvested:
                recs.append(rec)
    print('  %4i records so far' % (len(recs)))


i = 0
for rec in recs:
    i += 1
    ejlmod3.printprogress('-', [[i, len(recs)], [rec['link']]])
    try:
        artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        time.sleep(3)
    except:
        try:
            print("retry %s in 180 seconds" % (rec['link']))
            time.sleep(180)
            artpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(rec['link']), features="lxml")
        except:
            print("no access to %s" % (rec['link']))
            continue
    #title
    for h1 in artpage.body.find_all('h1'):
        rec['tit'] = re.sub('(.*) \/ .*', r'\1', h1.text.strip())
    for tr in artpage.body.find_all('tr'):
        tht = False
        for th in tr.find_all('th'):
            tht = th.text.strip()
        for td in  tr.find_all('td'):
            if tht:
                tdt = re.sub('[a-z]*\.phtml', '', re.sub('[\n\t\r]', '', td.text.strip()))
                #author
                if re.search('^[aA]uthor', tht):
                    rec['autaff'] = [[ re.sub(', author.?', '', tdt) ]]
                    tht == False
                #date
                elif re.search('[Ii]mprint', tht):
                    if re.search('[12]\d\d\d', tdt):
                        rec['year'] = re.sub('.*([12]\d\d\d).*', r'\1', tdt)
                        rec['date'] = rec['year']
                #pages
                elif re.search('escription', tht):
                    if re.search('\d\d+ (pages|p\.)', tdt):
                        rec['pages'] = re.sub('.*?(\d\d+) (pages|p\.).*', r'\1', tdt)
                #language
                elif re.search('[lL]anguage', tht):
                    if tdt != 'English':
                        rec['language'] = tdt
                #subject
                elif re.search('[sS]ubject', tht):
                    for a in td.find_all('a'):
                        rec['keyw'].append(re.sub('[\n\t\r]', '', a.text.strip()))
                #ISBN
                elif re.search('ISBN', tht):
                    rec['isbn'] = tdt
                #supervisor
                elif re.search('[nN]otes', tht):
                    tdt = re.sub(' *Committee.*', '', tdt)
                    tdt = re.sub(' *Includes.*', '', tdt)
                    tdt = re.sub(' *Thesis.*', '', tdt)
                    tdt = re.sub(' *Dissertation.*', '', tdt)
                    tdt = re.sub('([a-z][a-z][a-z])\.$', r'\1', tdt)
                    if re.search('Advisors?:', tdt):
                        for sv in re.split('[;,] ', re.sub('.*Advisors?: *', '', tdt)):
                            rec['supervisor'].append([sv])
                #abstract
                elif re.search('[sS]ummary', tht):
                    rec['abs'] = tdt
    #affiliation
    rec['autaff'][-1].append(publisher)
    #repository link
    for a in artpage.body.find_all('a', attrs = {'class' : 'eLink'}):
        if a.has_attr('href') and re.search('dx.doi.org.*10.6082', a['href']):
            rec['doi'] = re.sub('(&#x25;|%)2F', '/', re.sub('.*(10.6082.*)', r'\1', a['href']))
            doilink = 'https://dx.doi.org/' + rec['doi']
            doifilename = '/tmp/THESES-CHICAGO' +  re.sub('\W', '', rec['doi'])
            if not os.path.isfile(doifilename):
                print('  try %s' % (doilink))
                os.system('wget -T 300 -t 3 -q -O %s "%s"' % (doifilename, doilink))
                time.sleep(6)
            inf = open(doifilename, 'r')
            doipage = BeautifulSoup(''.join(inf.readlines()))
            inf.close()
            #license
            for div in doipage.find_all('div', attrs = {'class' : 'metadata-row'}):
                spans = div.find_all('span')
                if len(spans) == 2:
                    if re.search('Standard Rights Statement', spans[0].text):
                        rec['license'] = {'statement' : re.sub(' ', '-', spans[1].text)}
            ejlmod3.metatagcheck(rec, doipage, ['citation_keywords', 'citation_pdf_url'])
    ejlmod3.printrecsummary(rec)      
                
ejlmod3.writenewXML(recs, publisher, jnlfilename)
