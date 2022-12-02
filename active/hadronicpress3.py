# -*- coding: UTF-8 -*-
#program to harvest journas from hadronic Press
# FS 2021-01-16
# FS 2022-11-24


import os
import ejlmod3
import re
import sys
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup

publisher = 'Hadronic Press'
tc = ''
jnl = sys.argv[1]
vol = sys.argv[2]
issue = sys.argv[3]

if jnl == 'hj':
    jnlname = 'Hadronic J.'
elif jnl == 'agg':
    jnlname = 'Alg.Groups Geom.'
toclink = 'http://hadronicpress.com/%s/%sVol/%s%s-%s.php' % (jnl.upper(), jnl.upper(), jnl.upper(), vol, issue)
jnlfilename = "hadronic%s%s.%s" % (jnl, vol, issue)

print("get table of content... from %s" % (toclink))

try:
    tocpage = BeautifulSoup(urllib.request.urlopen(toclink), features="lxml")
except:
    print('%s not found' % (toclink))
    sys.exit(0)


recs = []

for title in tocpage.find_all('title'):
    year = re.sub('.*([12]\d\d\d).*', r'\1', title.text.strip())
    print(year)
for article in tocpage.body.find_all('article'):
    for p in article.find_all('p')[1:]:
        rec = {'jnl' : jnlname, 'tc' : tc, 'issue' : issue, 'note' : [], 
               'autaff' : [], 'keyw' : [], 'vol' : vol, 'year' : year}
        strongs = p.find_all('strong')
        #title and page
        titpag = re.sub('[\n\t\r]', ' ', strongs[0].text.strip())
        rec['p1'] = re.sub('.*\D(\d+)$', r'\1', titpag)
        rec['tit']= re.sub('(.*),.*', r'\1', titpag)
        rec['doi'] = '20.2000/HadroniPress/%s/%s/%s/%s' % (jnl, vol, issue, rec['p1'])
        rec['link'] = toclink
        strongs[0].decompose()
        #links
        for a in strongs[-1].find_all('a'):
            rec['link'] = a['href']
            strongs[-1].decompose()
        #authors
        for strong in strongs[1:]:
            st = strong.text.strip()
            strong.replace_with(' YYY ' + st + ' XXX ')
        for br in p.find_all('br'):
            br.replace_with(' ')
        for autaff in re.split(' +YYY +', re.sub('^ *YYY *', '', re.sub('[\n\t\r]', ' ', p.text.strip()))):            
            parts = re.split(' +XXX +', autaff)
            if re.search(' and ', parts[0]):
                for aparts in re.split(' and ', parts[0]):
                    rec['autaff'].append([aparts] + parts[1:])
            else:
                rec['autaff'].append(parts)
        recs.append(rec)
        ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
