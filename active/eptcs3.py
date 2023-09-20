# -*- coding: UTF-8 -*-
#program to harvest Electronic Proceedings in Theoretical Computer Science
# FS 2016-01-06
# FS 2023-09-19

import os
import ejlmod3
import re
import sys
import unicodedata
import urllib.request, urllib.error, urllib.parse
import time
from bs4 import BeautifulSoup


tmpdir = '/tmp'
def tfstrip(x): return x.strip()


publisher = 'EPTCS'
confid = sys.argv[1]
jnlfilename = 'eptcs' + confid
if len(sys.argv) > 2:
    cnum = sys.argv[2]
    jnlfilename = 'eptcs' + confid + '.' + cnum


url = 'http://eptcs.web.cse.unsw.edu.au/content.cgi?' + confid
url = 'https://cgi.cse.unsw.edu.au/~eptcs/content.cgi?' + confid
print(url)


tocpage = BeautifulSoup(urllib.request.urlopen(url), features='lxml')

artlinks = []
for a in tocpage.body.find_all('a'):
    if a.has_attr('href') and re.search('^paper.cgi', a['href']):
        #artlinks.append('http://eptcs.web.cse.unsw.edu.au/' + a['href'])
        artlinks.append('https://cgi.cse.unsw.edu.au/~eptcs/' + a['href'])

print('found %i links to articles' % (len(artlinks)))

typecode = 'C'
recs = []
for (i, artlink) in enumerate(artlinks):
    time.sleep(1)
    rec = {'jnl' : 'EPTCS', 'autaff' : [], 'tc' : typecode, 'refs' : []}
    if len(sys.argv) > 2:
        rec['cnum'] = sys.argv[2]
    ejlmod3.printprogress('-', [[i+1, len(artlinks)], [artlink]])
    artpage = BeautifulSoup(urllib.request.urlopen(artlink), features='lxml')
    ejlmod3.metatagcheck(rec, artpage, ['citation_volume', 'citation_publication_data',
                                        'citation_firstpage', 'citation_lastpage',
                                        'citation_pdf_url' ])
    #title
    for h2 in artpage.body.find_all('h2'):
        rec['tit'] = h2.text
    #tables
    tables = artpage.body.find_all('table')
    #authors    
    for td in tables[0].find_all('td'):
        for font in td.find_all('font'):
            if font.has_attr('color') and font['color'] == 'darkblue':
                for font2 in font.find_all('font'):
                    if font2['color'] == 'blue':
                        surname = font2.text
                    font2.replace_with('')
                givenname = font.text.strip()
                autaff = ['%s, %s' % (surname, givenname)]
            elif font.has_attr('size'):
                autaff.append(re.sub('^\((.*)\)$', r'\1', font.text))
        rec['autaff'].append(autaff)
    #abstract
    rec['abs'] = tables[1].text.strip()
    #unique ids
    for a in tables[2].find_all('a'):
        if a.has_attr('href'):
            if re.search('arxiv.org', a['href']):
                rec['arxiv'] = re.sub('.*\/', '', a['href'])
            elif re.search('dx.doi.org', a['href']):
                rec['doi'] = re.sub('.*dx.doi.org.', '', a['href'])
    #references
    reflink = re.sub('.*\?(.*)', r'https://cgi.cse.unsw.edu.au/~eptcs/references.cgi?\1.html', artlink)
    ejlmod3.printprogress('-', [[i+1, len(artlinks)], [reflink]])
    time.sleep(2)
    refpage = BeautifulSoup(urllib.request.urlopen(reflink), features='lxml')
    for li in refpage.find_all('li'):
        rec['refs'].append([('x', li.text.strip())])
    
    recs.append(rec)
    ejlmod3.printrecsummary(rec)


ejlmod3.writenewXML(recs, publisher, jnlfilename)
