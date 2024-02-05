# -*- coding: UTF-8 -*-
#program to harvest "New Physics: Sae Mulli"
# FS 2017-08-18
# FS 2023-04-11


import os
import ejlmod3
import re
import sys
#import unicodedata
#import string
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup

publisher = 'Korean Physical Society'
tc = 'P'
vol = sys.argv[1]
issue = sys.argv[2]

jnlname = 'New Phys.Sae Mulli'
urltrunk = 'http://www.npsm-kps.org'

jnlfilename = "npsm%s.%s" % (vol, issue)
toclink = "%s/list.html?page=1&sort=&scale=500&all_k=&s_t=&s_a=&s_k=&s_v=%s&s_n=%s&spage=&pn=search&year=" % (urltrunk, vol, issue)
toclink = "%s/journal/list.html?pn=vol&TG=vol&sm=&s_v=%s&s_n=%s&scale=500" % (urltrunk, vol, issue)

print("get table of content... from %s" % (toclink))

try:
    tocpage = BeautifulSoup(urllib.request.urlopen(toclink), features="lxml")
except:
    print('%s not found' % (toclink))
    sys.exit(0)


recs = []
recc = re.compile('http.*creativecommons.org')
repacs = re.compile('PACS numbers:? *')

h4s = tocpage.body.find_all('h4')
for (i, h4) in enumerate(h4s):
    rec = {'jnl' : jnlname, 'tc' : tc, 'issue' : issue, 'note' : [], 'vol' : vol}
    for a in h4.find_all('a'):
        artlink = '%s/%s' % (urltrunk, a['href'])
        ejlmod3.printprogress('-', [[i+1, len(h4s)], [artlink]])
        rec['tit'] = a.text.strip()
        time.sleep(4)
        try:
            artpage = BeautifulSoup(urllib.request.urlopen(artlink), features="lxml")
        except:
            print('%s not found' % (artlink))
            sys.exit(0)
        ejlmod3.metatagcheck(rec, artpage, ['citation_doi', 'citation_pdf_url', 'citation_firstpage',
                                            'citation_lastpage', 'citation_keywords',
                                            'citation_online_date', 'citation_author',
                                            'citation_author_institution'])
        ejlmod3.globallicensesearch(rec, artpage)
        for dd in artpage.body.find_all('div', attrs = {'class' : 'origin_section03'}):
            for h3 in dd.find_all('h3'):
                #abstract
                if re.search('bstract', h3.text):
                    for div in dd.find_all('div', attrs = {'class' : 'go_section'}):
                        if re.search(' the ', div.text):
                            for p in div.find_all('p'):
                                for strong in p.find_all('strong'):
                                    if re.search('eywords', strong.text):
                                        p.decompose()
                            for p in div.find_all('p'):
                                rec['abs'] = p.text.strip()
                #references
                elif re.search('eferences', h3.text):
                    for ol in dd.find_all('ol'):
                        rec['refs'] = []
                        for li in ol.find_all('li'):
                            rdoi = False
                            for a in li.find_all('a'):
                                if a.has_attr('href') and re.search('doi.org\/10', a['href']):
                                    rdoi = re.sub('.*doi.org\/', '', a['href'])
                                    a.decompose()
                            ref = li.text.strip()
                            if rdoi:
                                ref = re.sub('\. *', '', ref) + ',  DOI: '+rdoi
                            rec['refs'].append([('x', ref)])
        recs.append(rec)
        ejlmod3.printrecsummary(rec)

ejlmod3.writenewXML(recs, publisher, jnlfilename)
