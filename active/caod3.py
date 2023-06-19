# -*- coding: utf-8 -*-
#program to harvest from "China/Asia on Demand"a
# FS 2019-05-25
# FS 2023-06-19
import sys
import os
import ejlmod3
import re
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import time

jnl = sys.argv[1]
year = sys.argv[2]
isu = sys.argv[3]

if jnl == 'justc':
    jnlname = 'J.Univ.Sci.Tech.China'
    tc = 'P'
    publisher = 'Chinese Academy of Sciences, China University of Science and Technology'
    toclink = 'http://caod.oriprobe.com/journals/zgkxjsdxxb/Journal_of_University_of_Science_and_Technology_of_China.htm'
elif jnl == 'cjcp':
    jnlname = 'Chin.J.Comput.Phys.'
    tc = 'P'
    publisher = 'publisher'
    toclink = 'http://caod.oriprobe.com/journals/jswl/Chinese_Journal_of_Computational_Physics.htm'
elif jnl == 'aas':
    jnlname = 'Acta Astron.Sin.'
    tc = 'P'
    publisher = 'publisher'
    toclink = 'http://caod.oriprobe.com/journals/twxb/Acta_Astronomica_Sinica.htm'
else:
    print(' do not know journal "%s"' % (jnl))

#search for link to issue
tocpage = BeautifulSoup(urllib.request.urlopen(toclink), features='lxml')
for div in tocpage.body.find_all('div', attrs = {'class' : 'jinfoybig'}):
    for a in div.find_all('a', attrs = {'name' : 'year%s' % (year)}):
        for idiv in div.find_all('div', attrs = {'itemprop' : 'hasPart'}):
            for ia in idiv.find_all('a'):
                for span in ia.find_all('span'):
                    if re.sub('Issue ', '', span.text.strip()) == isu:
                        isutoclink = 'http://caod.oriprobe.com' + ia['href']
print('link to TOC: %s' % (isutoclink))
isutocpage = BeautifulSoup(urllib.request.urlopen(isutoclink), features='lxml')
#search volume number
for span in isutocpage.body.find_all('span', attrs = {'itemprop' : 'volumeNumber'}):
    vol = span.text.strip()
#missing metadata on some pages
if jnl == 'justc':
    vol = str(int(year)-1970)


    
recs = []
divs = isutocpage.body.find_all('div', attrs = {'class' : 'searchrl'})
for  (i, div) in enumerate(divs):
    ejlmod3.printprogress('-', [[i+1, len(divs)]])
    rec = {'jnl' : jnlname, 'vol' : vol, 'issue' : isu, 'year' : year, 'tc' : tc,
           'auts' : [], 'keyw' : []}
    #authors
    for authors in div.find_all('div', attrs = {'itemprop' : 'author'}):
        for author in authors.find_all('a'):
            rec['auts'].append(re.sub('([A-Z]+) (.*)', r'\1, \2', author.text.strip()).title())
    #title
    for title in div.find_all('a', attrs = {'itemprop' : 'name'}):
        rec['tit'] = title.text.strip()
        rec['link'] = 'http://caod.oriprobe.com' + title['href']
    #pages
    for span in div.find_all('span', attrs = {'itemprop' : 'pageStart'}):
        rec['p1'] = span.text.strip()
    for span in div.find_all('span', attrs = {'itemprop' : 'pageEnd'}):
        rec['p2'] = span.text.strip()
    if rec['auts']:
        recs.append(rec)
    ejlmod3.printrecsummary(rec)

for (i, rec) in enumerate(recs):
    ejlmod3.printprogress('-', [[i+1, len(recs)], [rec['link']]])
    try:
        time.sleep(2)
        artpage = BeautifulSoup(urllib.request.urlopen(rec['link']), features='lxml')
        #keywords
        for span in artpage.body.find_all('span', attrs = {'itemprop' : 'headline'}):
            for a in span.find_all('a'):
                rec['keyw'].append(a.text)
        #abstract
        for span in artpage.body.find_all('span', attrs = {'itemprop' : 'description'}):
            rec['abs'] = span.text.strip()
            if len(rec['abs']) > 10 and not re.search('[A-Za-z]', rec['abs']):
                rec['note'] = [ 'abstract in Chinese?' ]
    except:
        rec['note'] = [ 'could not get abstract nor keywords' ]
    ejlmod3.printrecsummary(rec)

jnlfilename = 'caod_%s%s.%s'  % (jnl, vol, isu)
ejlmod3.writenewXML(recs, publisher, jnlfilename)
