# -*- coding: utf-8 -*-
#harvest theses from Cahiers de Topologie et Geometrie Differentielle
#FS: 2020-10-20
#FS: 2023-07-24


import getopt
import sys
import os
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
import re
import ejlmod3
import time
import json


publisher = 'Cahiers'

numofvolumes = 2
hdr = {'User-Agent' : 'Magic Browser'}

tocurl = 'http://cahierstgdc.com/index.php/volumes/'
print(tocurl)
req = urllib.request.Request(tocurl, headers=hdr)
tocpage = BeautifulSoup(urllib.request.urlopen(req))
volurls = []
for li in tocpage.body.find_all('li', attrs = {'class' : 'menu-item'}):
    lit = li.text.strip()
    if re.search('^Volume', lit):
        if len(volurls) < numofvolumes:
            for a in li.find_all('a'):
                volurls.append(a['href'])

def roman_to_int(s):
    rom_val = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    int_val = 0
    for i in range(len(s)):
        if i > 0 and rom_val[s[i]] > rom_val[s[i - 1]]:
            int_val += rom_val[s[i]] - 2 * rom_val[s[i - 1]]
        else:
            int_val += rom_val[s[i]]
    return int_val
    
for volurl in volurls:
    ejlmod3.printprogress("=", [[volurl]])
    recs = []
    req = urllib.request.Request(volurl, headers=hdr)
    volpage = BeautifulSoup(urllib.request.urlopen(req))
    year = re.sub('.*(\d\d\d\d).*', r'\1', volpage.title.text.strip())
    vol = str(roman_to_int(re.sub('Volume ([A-Z]+) .*', r'\1', volpage.title.text.strip())))
    issue = False
    for div in volpage.body.find_all('div', attrs = {'class' : 'entry-content'}):
        for p in div.find_all('p'):
            for a in p.find_all('a'):
                at = a.text.strip()
                if not at: continue
                if re.search('^Issue.*\d$', at):
                    issue = at[-1]
                    ejlmod3.printprogress("-", [[vol], [issue]])
                else:
#                    print ' ', at
                    rec = {'jnl' : 'Cahiers Topo.Geom.Diff.', 'year' : year, 'tc' : 'P', 'vol' : vol}
                    if issue: rec['issue'] = issue
                    rec['FFT'] = a['href']
                    rec['pdf'] = a['href']
                    rec['tit'] = at
                    a.decompose()
                    for br in p.find_all('br'):
                       br.replace_with(' XXX ')
                    parts = re.split(' *XXX ', re.sub('[\n\t\r]', ' ', p.text.strip()))
#                    print ' ', parts
                    #pages
                    rec['p1'] = re.sub('.*?(\d+)\-.*', r'\1', parts[1].strip())
                    rec['p2'] = re.sub('.*\-', '', parts[1].strip())
                    #authors
                    rec['auts'] = re.split(', ', parts[2].strip())
                    recs.append(rec)
                    ejlmod3.printrecsummary(rec)
    jnlfilename = 'cahierstgd%s-%s' % (vol, ejlmod3.stampoftoday())
    time.sleep(2)
    ejlmod3.writenewXML(recs, publisher, jnlfilename)
