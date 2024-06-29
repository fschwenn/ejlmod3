# -*- coding: UTF-8 -*-
#program to harvest Romanian Journal of Physics
# FS 2017-06-27
# FS 2023-04-04

import os
import ejlmod3
import re
import sys
#import unicodedata
#import string
import urllib.request, urllib.error, urllib.parse

from bs4 import BeautifulSoup
import ssl

def tfstrip(x): return x.strip()

publisher = 'Romanian Academy Publishing House'
year = sys.argv[1]
vol = sys.argv[2]
issue = sys.argv[3]

jnl = 'rjp'
jnlname = 'Rom.J.Phys.'

jnlfilename = '%s%s.%s' % (jnl, vol, issue)

url = 'http://www.nipne.ro/%s/%s_%s_%s.html' % (jnl, year, vol, issue)

#bad certificate
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

print("get table of content of %s%s.%s ... via %s" %(jnlname, vol, issue, url))
hdr = {'User-Agent' : 'Magic Browser'}
req = urllib.request.Request(url, headers=hdr)
tocpage = BeautifulSoup(urllib.request.urlopen(req, context=ctx))

tsection = ''
recs = []
for div in tocpage.body.find_all('div'):
    if div.has_attr('class'):
        if 'tsection' in div['class']:
            tsection = div.text.strip()
        elif 'docsource' in div['class']:
            divaidt = re.sub('[\n\r\t]', '', div.text.strip())
            print(divaidt)
            if re.search('Article no. \d+', divaidt):
                rec['p1'] = re.sub('.*Article no. (\d+).*', r'\1', divaidt)
            for a in div.find_all('a'):
                if re.search('Full text', a.text):
                    rec['pdf'] = 'http://www.nipne.ro/rjp/' + a['href']
                    print('   [%s]' % (rec['pdf']))
        elif 'abstract' in div['class']:
            rec['abs'] = div.text.strip()
            recs.append(rec)
    elif div.has_attr('style') and div['style'] == 'vertical-align:top;text-align:left;':
        rec = {'jnl' : jnlname, 'vol' : vol, 'issue' : issue, 'year' : year, 
               'tc' : 'P', 'note' : [tsection], 'auts' : []}
        for span in div.find_all('span', attrs = {'class' : 'toct'}):
            rec['tit'] = span.text.strip()
        for span in div.find_all('span', attrs = {'class' : 'toca'}):
            authors = span.text.strip()
            for author in re.split(' *, *', authors):
                rec['auts'].append(re.sub('(.*) (.*)', r'\2, \1', author))
        for span in div.find_all('span', attrs = {'style' : 'font-size:8pt;'}):
            p1p2 = re.sub('[\r\n\t]', ' ', span.text.strip())            
            p1p2 = re.split('\-', re.sub('.*,.*?(\d+\-?\d+).*', r'\1', p1p2))
            rec['p1'] = p1p2[0]
            if len(p1p2) > 1:
                rec['p2'] = p1p2[1]
        for a in div.find_all('a'):
            if a.has_attr('href') and re.search('doi.org\/10.', a['href']):
                rec['doi'] = re.sub('.*org\/', '', a['href'])        
        ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
