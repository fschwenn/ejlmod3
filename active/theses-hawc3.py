# -*- coding: utf-8 -*-
#harvest HAWC theses
#FS: 2020-11-16
#FS: 2023-04-05

import sys
#import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import ssl

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
hdr = {'User-Agent' : 'Magic Browser'}

publisher = 'HAWC'
jnlfilename = 'THESES-HAWC-%s' % (ejlmod3.stampoftoday())

skipalreadyharvested = True
years = 3

recs = []

tocurl = 'https://www.hawc-observatory.org/publications'
try:
    req = urllib.request.Request(tocurl, headers=hdr)
    tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx), features='lxml')
except:
    print("retry %s in 180 seconds" % (tocurl))
    time.sleep(180)
    tocpage = BeautifulSoup(urllib.request.build_opener(urllib.request.HTTPCookieProcessor).open(tocurl), features='lxml')

if skipalreadyharvested:    
    alreadyharvested = ejlmod3.getalreadyharvested(jnlfilename)


section = ''
for div in tocpage.find_all('div', attrs = {'class' : 'content'}):
    for child in div.children:
        try:
            child.name
        except:
            continue
        if child.name == 'h5':
            for a in child.find_all('a'):
                if a.has_attr('name'):
                    section = a['name']
                    ejlmod3.printprogress("=", [[section]])
            rec = {'tc' : 'T', 'jnl' : 'BOOK', 'MARC' : []}
        elif child.name == 'p':
            if section == 'thesis':
                rec = {'jnl' : 'BOOK', 'tc' : 'T', 'exp' : 'HAWC'}
                for a in child.find_all('a'):
                    if re.search('http:', a['href']):
                        rec['link'] = a['href']
                        if re.search('pdf$', a['href']):
                            rec['hidden'] = a['href']
                    else:
                        rec['link'] = 'https://www.hawc-observatory.org/' + a['href']
                        if re.search('pdf$', a['href']):
                            rec['hidden'] = 'https://www.hawc-observatory.org/' + a['href']
                    rec['tit'] = re.sub('[\n\t\r]', '', a.text.strip())
                    rec['doi'] = '20.2000/HAWC/' + re.sub('\W', '', a['href'])
                for br in child.find_all('br'):
                    br.replace_with(' XXX ')
                pt = re.split(' XXX ', re.sub('[\n\t\r]', '', child.text.strip()))
                rec['autaff'] = [[ pt[1] ]]
                if re.search('[12]\d\d\d', pt[2]):
                    rec['date'] = re.sub('.*([12]\d\d\d).*', r'\1', pt[2])
                rec['autaff'][-1].append(re.sub(' *\([12].*', '', pt[2]))
                if 'date' in list(rec.keys()) and int(rec['date']) <= ejlmod3.year(backwards=years):
                    print('  skip')
                else:
                    if not skipalreadyharvested or not rec['doi'] in alreadyharvested:
                        ejlmod3.printrecsummary(rec)
                        recs.append(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
